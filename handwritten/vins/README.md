# VINS 前端 · 7 步手写实现

数据：EuRoC `MH_01_easy`（单目 cam0 + 200Hz IMU）。目标：纯 OpenCV + 手写优化，从 IMU 原始数据一路推到米制轨迹，每一步都能单独验收。

## 七步

| 步 | 做什么 | 验收指标 | 状态 |
|---|---|---|---|
| [step1](step1/) | 读 IMU，摸清频率、零偏、重力方向 | 采样间隔恒 5.000ms = 200Hz | ✅ |
| [step2](step2/) | FAST 角点 + KLT 金字塔光流 | 跟踪成功率 > 90% | ✅ |
| [step3](step3/) | IMU 预积分 ΔR / Δv / Δp | 同帧对 Δp 恒等 | ✅ |
| [step4](step4/) | 滑窗 SfM 初始化（无尺度） | BA 平均重投影 < 1px | 🚧 |
| [step5](step5/) | 视觉惯性对齐（解 s / g / v / bg） | 尺度量级合理、重力方向收敛 | ⬜ |
| [step6](step6/) | 滑窗紧耦合 + 边缘化 | 优化后残差下降且滑窗边界不跳 | ⬜ |
| [step7](step7/) | 主循环出轨迹 | 与真值形状同构 | ⬜ |

每步的原理、参数、图怎么读，见 [`docs/notes/vins/`](../../docs/notes/vins/)：
[总览](../../docs/notes/vins/00-pipeline.md) ·
[STEP1](../../docs/notes/vins/01-step1-imu.md) ·
[STEP2](../../docs/notes/vins/02-step2-optical-flow.md) ·
[STEP3](../../docs/notes/vins/03-step3-preintegration.md) ·
[STEP4](../../docs/notes/vins/04-step4-sfm-init.md) ·
[STEP5](../../docs/notes/vins/05-step5-visual-inertial-alignment.md) ·
[STEP6](../../docs/notes/vins/06-step6-sliding-window.md) ·
[STEP7](../../docs/notes/vins/07-step7-trajectory.md)

实测数字：[`docs/notes/vins/results.md`](../../docs/notes/vins/results.md)
踩坑记录：[`docs/notes/vins/pitfalls.md`](../../docs/notes/vins/pitfalls.md)

## 数据与内参

```
~/Datasets/EuRoC/MH_01_easy/mav0/
├── cam0/data/        752x480 灰度 PNG，文件名 = 纳秒时间戳
└── imu0/data.csv     200Hz
```

```
fx 458.654  fy 457.296  cx 367.215  cy 248.375
k1 -0.28340811  k2 0.07395907  p1 0.00019359  p2 1.76187114e-05
```

`k1` 接近 -0.28 是强畸变，这一点决定了所有几何计算必须在去畸变归一化坐标里做（见 pitfalls 第 2 条）。

## 运行

```bash
cd step1 && mkdir -p build && cd build && cmake .. && make
./step1_read_imu ~/Datasets/EuRoC/MH_01_easy/mav0/imu0/data.csv
```

各步参数不同，具体数据路径写在各步笔记的末尾。

## 当前卡点（如实记录）

STEP4 已迭代到 v3（归一化坐标空间）。当前症状：419 个 F 内点里 416 个通过深度检查，但重投影检查只保留 5~10 个，BA 前平均重投影 0.48~586（归一化）不收敛。已排除 t 符号、参考帧位姿、重投影阈值、F 输入空间四项，正在查 `triangulatePoints` 的齐次符号与位姿矩阵一致性。

细节与七次尝试的对照数据见 `docs/notes/vins/results.md`。未通过前进 STEP5 没有意义 —— 对齐的输入就是错的。
