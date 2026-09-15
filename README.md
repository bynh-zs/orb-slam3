# orb-slam3 学习复现记录

本仓库用于记录 ORB-SLAM3（双目 + IMU 视觉惯性 SLAM）的学习、复现与实验过程。

## 目录结构

```
orb-slam3/
├── README.md                 # 本文件
├── datasets/                 # 数据集获取方式与下载脚本（数据文件本身不进 Git）
│   ├── README.md             # EuRoC / KITTI 数据集详细说明
│   ├── download_euroc.py     # EuRoC 单序列一键下载脚本（只下需要的序列，不用下整包）
│   └── KITTI下载指南.md       # KITTI 需邮箱注册，按指南手动下载
└── Datasets/                 # （本地）真正的数据文件，已被 .gitignore 忽略
```

> 为什么数据集不直接传进仓库？GitHub 单文件上限 100 MB，而 EuRoC 单个序列约 1.5 GB、
> KITTI 灰度包 22 GB，推送会被拒绝。标准做法是：**仓库只放下载脚本和说明，数据放本地磁盘**。

## 复现路线

1. 获取公开数据集（先用 EuRoC 的 `MH_01_easy` 跑通），见 [`datasets/README.md`](datasets/README.md)
2. 获取 ORB-SLAM3 源码：到官方仓库 <https://github.com/UZ-SLAMLab/ORB_SLAM3> 点 **Fork** 到自己账号，再 `git clone` 到本地
3. Ubuntu / WSL2 环境下安装依赖（Pangolin、OpenCV、Eigen3）并编译
4. 按官方 README 的 Stereo-Inertial / EuRoC 小节运行

## Git 小抄

```bash
git pull                 # 开工前先拉最新
# 修改文件 ...
git add .                # 暂存改动
git commit -m "说明"      # 本地存档
git push                 # 推送到 GitHub
git status               # 不知道当前状态就输它
```
