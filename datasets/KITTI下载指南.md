# KITTI Odometry 数据集下载指南（室外车载双目）

KITTI 下载需要用邮箱注册获取临时下载链接，无法用脚本直接拉取，按下面步骤手动下载。

## 1. 打开官网

视觉里程计/SLAM 基准页：<https://www.cvlibs.net/datasets/kitti/eval_odometry.php>

## 2. 需要下载的三个文件

在页面 "Download KITTI Odometry data" 区域：

| 文件 | 大小 | 是否必需 | 说明 |
|---|---|---|---|
| odometry data set **(grayscale)** | 22 GB | 必需 | 灰度双目图像，跑 ORB-SLAM3 选这个即可 |
| odometry ground truth poses | 很小 | 必需 | 00–10 序列的真值轨迹 |
| odometry calibration data | 1 MB | 必需 | 相机标定参数 |

> color 彩色版 65 GB、velodyne 激光 80 GB，做纯双目 SLAM 都不需要，别下。
> 想先试单个序列，页面下方有 "Download individual sequences" 的入口。

## 3. 注册流程

1. 点 "grayscale, 22 GB" 链接，会跳到一个表单
2. 填写邮箱（**教育邮箱最稳**，如天大校园邮箱；常用个人邮箱也可）、姓名、单位（Tianjin University）
3. 提交后下载链接会发到邮箱，链接有时效（通常几天），收到后尽快下
4. 国内直连较慢，建议用校园网或支持断点续传的下载器（如 IDM、迅雷、`wget -c "链接"`）

## 4. 下载后的目录结构（ORB-SLAM3 要求）

```
Datasets/KITTI/
└── dataset/
    └── sequences/
        ├── 00/
        │   ├── image_0/   # 左目灰度
        │   ├── image_1/   # 右目灰度
        │   └── calib.txt
        ├── 01/ ...
        └── poses/          # 来自 ground truth poses 压缩包
```

## 5. 在 ORB-SLAM3 中运行（Stereo 纯双目）

```bash
./stereo_kitti ../../Vocabulary/ORBvoc.txt \
  Examples/Stereo/KITTI00-02.yaml \
  /path/to/Datasets/KITTI/dataset/sequences/00
```

注意配置文件按序列编号选择：00–02 用 `KITTI00-02.yaml`，03 用 `KITTI03.yaml`，04–12 用 `KITTI04-12.yaml`。

## 6. 备注

- KITTI Odometry 标准 benchmark 是**纯双目**；原始数据 raw_data.php 里虽有 GPS/IMU，
  但 ORB-SLAM3 官方 KITTI 例程不使用 IMU。要练"双目+IMU"请用 EuRoC / TUM-VI。
- 备用镜像与百度网盘资源可在 CSDN / 知乎搜索 "KITTI odometry 下载"，但优先用官网，避免文件被改动。
