#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EuRoC MAV 数据集单序列下载器（ASL 格式，ORB-SLAM3 可直接使用）
================================================================
ETH 官方现在只提供 6~13 GB 的整包（machine_hall.zip / vicon_room1.zip /
vicon_room2.zip），且旧的单序列服务器 robotics.ethz.ch 经常无法访问。
本脚本利用 HTTP Range 请求只读取整包中央目录、并只下载指定序列那一段，
无需下载整包，纯 Python 标准库实现，Windows / Linux / macOS 通用。

用法：
    python download_euroc.py --list                 # 列出全部 11 个序列
    python download_euroc.py MH_01_easy             # 下载单个序列到 ./Datasets/EuRoC
    python download_euroc.py MH_01_easy --out D:/datasets/EuRoC
    python download_euroc.py MH_01_easy V1_01_easy  # 同时下载多个序列

下载中断后重新执行同一命令会自动断点续传。
"""
import argparse
import io
import os
import struct
import sys
import time
import zlib
import urllib.request
import zipfile

API = "https://www.research-collection.ethz.ch/server/api/core/bitstreams/{}/content"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"
CHUNK = 8 << 20  # 每次 Range 请求拉取 8 MiB
RETRY = 5

# 三个外层整包的 bitstream UUID（来自 ETH Research Collection, DOI 10.3929/ethz-b-000690084）
PACKAGES = {
    "machine_hall": "7b2419c1-62b5-4714-b7f8-485e5fe3e5fe",
    "vicon_room1": "02ecda9a-298f-498b-970c-b7c44334d880",
    "vicon_room2": "ea12bc01-3677-4b4c-853d-87c7870b8c44",
}
# 11 个标准序列分别属于哪个外层整包
SEQUENCES = {
    "MH_01_easy": "machine_hall", "MH_02_easy": "machine_hall",
    "MH_03_medium": "machine_hall", "MH_04_difficult": "machine_hall",
    "MH_05_difficult": "machine_hall",
    "V1_01_easy": "vicon_room1", "V1_02_medium": "vicon_room1",
    "V1_03_difficult": "vicon_room1",
    "V2_01_easy": "vicon_room2", "V2_02_medium": "vicon_room2",
    "V2_03_difficult": "vicon_room2",
}


def http_request(url, headers, timeout=180):
    last = None
    for attempt in range(RETRY):
        try:
            req = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:  # 限流/断流时退避重试
            last = e
            time.sleep(2 * (attempt + 1))
    raise IOError(f"请求失败: {last}")


class RemoteRangeFile(io.RawIOBase):
    """把远程文件伪装成可 seek 的本地文件，zipfile 靠它只读中央目录。"""

    def __init__(self, url):
        self.url = url
        self.pos = 0
        with http_request(url, {"User-Agent": UA, "Range": "bytes=0-0"}, 60) as r:
            self.total = int(r.headers["Content-Range"].split("/")[1])

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, off, whence=0):
        if whence == 0:
            self.pos = off
        elif whence == 1:
            self.pos += off
        else:
            self.pos = self.total + off
        return self.pos

    def tell(self):
        return self.pos

    def readinto(self, buf):
        end = min(self.pos + len(buf) - 1, self.total - 1)
        if end < self.pos:
            return 0
        with http_request(self.url,
                          {"User-Agent": UA, "Range": f"bytes={self.pos}-{end}"}) as r:
            data = r.read()
        buf[:len(data)] = data
        self.pos += len(data)
        return len(data)


def open_remote_zip(pkg_key):
    url = API.format(PACKAGES[pkg_key])
    rf = RemoteRangeFile(url)
    return url, zipfile.ZipFile(io.BufferedReader(rf, 1 << 20))


def find_member(zf, seq):
    """在外层整包中定位 <seq>/<seq>.zip（ASL 格式）成员。"""
    target = f"{seq}/{seq}.zip".lower()
    for zi in zf.infolist():
        if zi.filename.lower().endswith(target):
            return zi
    raise KeyError(f"整包中找不到 {seq}.zip")


def parse_local_header(url, zi):
    """读取本地文件头，返回压缩数据起始绝对偏移与压缩方法。"""
    with http_request(url, {"User-Agent": UA,
                            "Range": f"bytes={zi.header_offset}-{zi.header_offset + 29}"}) as r:
        head = r.read()
    if head[:4] != b"PK\x03\x04":
        raise IOError("本地文件头签名错误")
    nlen, elen = struct.unpack("<HH", head[26:30])
    data_start = zi.header_offset + 30 + nlen + elen
    return data_start


def download_range(url, start, size, part_path):
    """把 [start, start+size) 分块下载到 part_path，支持断点续传。"""
    have = os.path.getsize(part_path) if os.path.exists(part_path) else 0
    if have > size:
        os.remove(part_path)
        have = 0
    mode = "ab" if have else "wb"
    t0 = time.time()
    with open(part_path, mode) as f:
        while have < size:
            end = min(start + have + CHUNK - 1, start + size - 1)
            with http_request(url, {"User-Agent": UA,
                                    "Range": f"bytes={start + have}-{end}"}) as r:
                blob = r.read()
            if not blob:
                raise IOError("空响应块")
            f.write(blob)
            have += len(blob)
            pct = have * 100.0 / size
            speed = have / max(time.time() - t0, 1e-6) / 1e6
            sys.stdout.write(f"\r  下载中 {pct:5.1f}%  {have/1e6:7.1f}/{size/1e6:.1f} MB  {speed:5.2f} MB/s")
            sys.stdout.flush()
    print()


def inflate_part(part_path, method, inner_zip_path):
    """外层 deflate 流 -> 内层完整 zip 文件（流式，避免占内存）。"""
    dobj = zlib.decompressobj(-15) if method == 8 else None
    with open(part_path, "rb") as fin, open(inner_zip_path, "wb") as fout:
        while True:
            blob = fin.read(CHUNK)
            if not blob:
                break
            fout.write(dobj.decompress(blob) if dobj else blob)
        if dobj:
            fout.write(dobj.flush())


def fetch_sequence(seq, out_dir):
    if seq not in SEQUENCES:
        raise KeyError(f"未知序列 {seq}，可用 --list 查看")
    pkg = SEQUENCES[seq]
    print(f"[{seq}] 位于外层整包 {pkg}，正在读取远程目录 ...")
    url, zf = open_remote_zip(pkg)
    zi = find_member(zf, seq)
    data_start = parse_local_header(url, zi)
    print(f"[{seq}] ASL 压缩包大小 {zi.compress_size/1e9:.2f} GB，开始下载（可随时中断，重跑续传）")

    os.makedirs(out_dir, exist_ok=True)
    part_path = os.path.join(out_dir, f"{seq}.part")
    inner_path = os.path.join(out_dir, f"{seq}.inner.zip")
    download_range(url, data_start, zi.compress_size, part_path)

    print(f"[{seq}] 下载完成，正在解压 ...")
    inflate_part(part_path, zi.compress_type, inner_path)
    os.remove(part_path)

    dest = os.path.join(out_dir, seq)
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(inner_path) as inner:
        inner.extractall(dest)  # 内层 zip 顶层即 mav0/，解压到 <out>/<seq>/mav0
    os.remove(inner_path)

    # 校验 ORB-SLAM3 需要的目录（sequence path 填 dest，里面应能看到 mav0）
    mav0 = os.path.join(dest, "mav0")
    if not os.path.isdir(mav0):
        for root, dirs, _ in os.walk(dest):  # 兼容个别压缩包多嵌套一层
            if "mav0" in dirs:
                mav0 = os.path.join(root, "mav0")
                break
    required = ["cam0", "cam1", "imu0"]
    missing = [d for d in required if not os.path.isdir(os.path.join(mav0, d))]
    if missing:
        print(f"[{seq}] 警告：缺少 {missing}，请检查解压结果 {dest}")
    else:
        print(f"[{seq}] 完成！ORB-SLAM3 的 sequence path 填: {os.path.abspath(dest)}")


def main():
    ap = argparse.ArgumentParser(description="EuRoC MAV 单序列下载器（ASL 格式）")
    ap.add_argument("sequences", nargs="*", help="序列名，如 MH_01_easy")
    ap.add_argument("--out", default=os.path.join("Datasets", "EuRoC"),
                    help="输出目录，默认 Datasets/EuRoC")
    ap.add_argument("--list", action="store_true", help="列出全部序列")
    args = ap.parse_args()

    if args.list or not args.sequences:
        print("EuRoC MAV 共 11 个序列（ASL 格式，双目 + IMU）：")
        for s, p in SEQUENCES.items():
            print(f"  {s:15s} -> {p}")
        print("\n示例: python download_euroc.py MH_01_easy")
        return 0

    for seq in args.sequences:
        for attempt in range(RETRY):
            try:
                fetch_sequence(seq, args.out)
                break
            except Exception as e:
                print(f"\n[{seq}] 第 {attempt+1} 次尝试失败: {e}")
                if attempt == RETRY - 1:
                    raise
                time.sleep(3 * (attempt + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
