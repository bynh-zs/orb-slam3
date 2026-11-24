# ORB-SLAM3 官方框架复现记录

这里记录**官方框架**的复现过程：怎么拿源码、怎么编、用了哪些配置、跑出来什么。框架源码本身不在此仓库 —— 它有自己的上游仓库和许可，重托管没有意义。

## 获取源码

到官方仓库 <https://github.com/UZ-SLAMLab/ORB_SLAM3> 点 **Fork** 到自己账号，再 clone 到本地：

```bash
git clone https://github.com/<你的账号>/ORB_SLAM3.git
```

Fork 而不是直接 clone，是为了之后如果要改配置、打补丁，有一个自己能推的副本。

## 环境

Ubuntu 20.04 / WSL2。依赖：Pangolin、OpenCV、Eigen3，以及 DBoW2 / g2o / Sophus 三个 Thirdparty（随源码附带的子模块，需按官方 README 逐个编译）。

编译注意：官方脚本默认 `make -j`，内存小的机器会直接 OOM 被 kill，改成串行 `make` 更稳。

## 运行

按官方 README 的 Stereo-Inertial / EuRoC 小节。EuRoC 序列先用 `MH_01_easy`，参数文件在 `ORB_SLAM3/Examples/Stereo-Inertial/`。

## 与手写实现的关系

`handwritten/` 里的三条线是把框架的关键步骤拆开自己写一遍，用来回答「这一步到底在算什么」。跑通框架回答的是另一个问题：「端到端能跑成什么样，误差量级多少」。

两者不能互相替代：手写实现没有回环、没有多线程、没有地图管理，轨迹精度必然不如框架；框架跑得再好也解释不了 `initial_sfm` 里那个五点法为什么这么选帧。

## 待补

跑通之后在这里补：使用的序列、参数文件、实际命令、轨迹（`CameraTrajectory.txt` / `KeyFrameTrajectory.txt`，两张小文件可以入库）、与手写实现的误差对比。
