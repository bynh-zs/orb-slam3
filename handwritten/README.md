# 手写 OpenCV 实现

三条线，同一套做法：把一条完整 SLAM 流水线拆成若干步，每步独立编译、独立运行、独立出一张验收图，跑不通就不往下走。

| 线 | 步数 | 输入 | 输出 | 每一步的说明 |
|---|---|---|---|---|
| `mono/` | 12 | EuRoC cam0 | 单目位姿与稀疏点云 | 见 `docs/notes/` 中单目部分（待补） |
| `stereo/` | 12 | EuRoC cam0 + cam1 | 带真实尺度的位姿与点云 | 见 `docs/notes/` 中双目部分（待补） |
| `vins/` | 7 | EuRoC cam0 + imu0 | 米制轨迹 | [`docs/notes/vins/00-pipeline.md`](../docs/notes/vins/00-pipeline.md) |

## 为什么「拆步」比「跑框架」更值得做一遍

跑框架能得到一条轨迹，但得到轨迹不等于看懂轨迹。`recoverPose` 为什么给四个解、`solvePnPRansac` 的内点阈值该设多少、三角化出来的点为什么一半在相机后面 —— 这些问题在框架里都被封装好了，只有自己写一遍才会撞上。

拆步的另一个好处是可验收：每一步有一个数字指标（跟踪成功率、预积分恒定性、重投影误差），不达标就有明确的下手点，而不是「轨迹飘了，不知道哪飘的」。

## 目录约定

```
handwritten/
├── <线>/
│   ├── step1/                 源码 + CMakeLists.txt（build/ 不入库）
│   ├── step2/
│   ├── ...
│   └── results/
│       ├── step1/             输出图与数值结果
│       └── step2/
```

代码与产物分开，是为了让 `git log` 里「改算法」和「出新图」不互相淹没。

## 编译

```bash
bash scripts/build_all.sh            # 全部
bash scripts/build_all.sh vins 4     # 只编 vins 的 step4
```

单步手动编译：

```bash
cd handwritten/vins/step4
mkdir -p build && cd build
cmake .. && make
```

## 一个小提醒

`make` 失败时 `build/` 里往往还躺着上一次成功的二进制。此时运行它得到的数字是**旧代码**的结果，看起来「跑通了」，实际验收无效。每次编译后先确认输出里有 `Built target`，再运行。
