# SLAM 公开数据集获取指南（双目 + IMU）

本目录解决一个问题：**ORB-SLAM3 要用的公开数据集去哪下、下哪个、下完长什么样。**

---

## 1. 数据集总览

| 数据集 | 场景 | 传感器 | 在 ORB-SLAM3 中的模式 | 体量 | 获取方式 |
|---|---|---|---|---|---|
| **EuRoC MAV**（先用这个） | 室内无人机 | 双目灰度相机 + 200Hz IMU，硬件同步 | Stereo-Inertial（双目-IMU） | 单序列约 1.5 GB | 本目录脚本可直接下 |
| **KITTI Odometry** | 室外车载街道 | 双目相机（灰度/彩色） | Stereo（纯双目） | 灰度整包 22 GB | 官网注册后下载，见《KITTI下载指南.md》 |
| TUM VI（拓展） | 室内手持 | 双目 + IMU | Stereo-Inertial | 单序列数百 MB | <https://cvg.cit.tum.de/data/datasets/visual-inertial-dataset> |

学习顺序建议：**EuRoC MH_01_easy 跑通双目-IMU → EuRoC 其余序列 → KITTI 跑室外纯双目。**

---

## 2. EuRoC MAV（重点）

### 2.1 11 个序列

| 序列 | 场景 | 难度 |
|---|---|---|
| MH_01_easy / MH_02_easy / MH_03_medium / MH_04_difficult / MH_05_difficult | 机器大厅 Machine Hall | 易→难 |
| V1_01_easy / V1_02_medium / V1_03_difficult | Vicon 房间 1 | 易→难 |
| V2_01_easy / V2_02_medium / V2_03_difficult | Vicon 房间 2 | 易→难 |

每个序列都包含：左右目图像（cam0/cam1）、IMU 测量（imu0）、运动捕捉真值轨迹（state_groundtruth_estimate0）。

### 2.2 方式一：脚本下载（推荐，已验证可用）

ETH 官方现在只提供 6~13 GB 的整包，旧的单序列服务器经常连不上。
`download_euroc.py` 通过 HTTP Range 只下载指定序列那一段，**不用下整包**，纯 Python 标准库、
Windows / Linux / macOS 通用，且支持断点续传。

```bash
# 列出全部序列
python download_euroc.py --list

# 下载第一个序列（默认存到 ./Datasets/EuRoC/）
python download_euroc.py MH_01_easy

# 指定存放位置 / 一次下多个
python download_euroc.py MH_01_easy V1_01_easy --out Datasets/EuRoC
```

下载中断后重新执行同一条命令即可自动续传。

### 2.3 方式二：官网手动下载（备用）

- 数据集主页：<https://ethz-asl.github.io/datasets/euroc-mav/>
- 下载落地页（ETH Research Collection，DOI: 10.3929/ethz-b-000690084）：
  <https://www.research-collection.ethz.ch/handle/20.500.11850/690084>
- 文件：`machine_hall.zip`（MH 全部，12.7 GB）、`vicon_room1.zip`、`vicon_room2.zip`、`calibration_datasets.zip`
- 格式选 **ASL Dataset（.zip）**，不要下 ROS bag（除非你用 ROS）

### 2.4 下载后的正确目录结构（ORB-SLAM3 要求）

```
Datasets/EuRoC/MH_01_easy/
└── mav0/
    ├── cam0/        # 左目图像 + sensor 标定 yaml
    ├── cam1/        # 右目图像
    ├── imu0/        # IMU 数据 data.csv + 噪声标定 sensor.yaml
    └── state_groundtruth_estimate0/   # 真值轨迹（评估精度用）
```

ORB-SLAM3 命令里的 `path_to_sequence` 填到 **`MH_01_easy` 这一层**（里面能看到 mav0）。

### 2.5 在 ORB-SLAM3 中运行（Stereo-Inertial）

```bash
# Vocabulary / 配置 / 序列路径 / 时间戳文件（仓库自带）
./stereo_inertial_euroc ../../Vocabulary/ORBvoc.txt \
  Examples/Stereo-Inertial/EuRoC.yaml \
  /path/to/Datasets/EuRoC/MH_01_easy \
  Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt
```

---

## 3. KITTI Odometry

需要邮箱注册、且体量较大，单独见 **[KITTI下载指南.md](KITTI下载指南.md)**。
注意：KITTI 在 ORB-SLAM3 中走 **Stereo 纯双目**例程（`Examples/Stereo`），不是 Stereo-Inertial。

---

## 4. 常见问题

- **Q：为什么不把数据集直接 push 到 GitHub？**
  A：GitHub 单文件硬上限 100 MB，仓库超过 1 GB 会被限流甚至拒绝推送；数据和代码分离是行业惯例。
- **Q：下载很慢/中断怎么办？**
  A：脚本支持断点续传，重跑同一命令即可；也可挂校园网/VPN 后再下。
- **Q：ASL 和 ROS bag 选哪个？**
  A：不用 ROS 就选 ASL（解压即 mav0 目录），ORB-SLAM3 官方例程用的就是 ASL 格式。
- **Q：报错时去哪查？**
  A：ORB-SLAM3 官方仓库 Issues：<https://github.com/UZ-SLAMLab/ORB_SLAM3/issues>，先搜报错关键词。
