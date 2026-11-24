# SLAM 学习与复现记录

这是一个 SLAM 的总仓库：一端是**手写 OpenCV 实现**（把算法拆成可验证的小步，自己写一遍），另一端是**官方框架复现**（ORB-SLAM3 跑通并记录配置）。两者并存，是因为它们回答的是不同的问题 —— 前者回答「它到底在算什么」，后者回答「它端到端能跑成什么样」。

数据集只放下载脚本与说明，数据文件本身不入库。

## 仓库地图

```
orb-slam3/
├── handwritten/              手写 OpenCV 实现（核心资产）
│   ├── mono/                 单目前端 12 步
│   ├── stereo/               双目前端 12 步
│   └── vins/                 VINS 前端 7 步
├── framework/                官方框架复现记录（ORB-SLAM3）
├── calibration/              标定流程、参数与脚本（原始图片不入库）
├── docs/
│   └── notes/                分主题技术笔记
│       └── vins/             VINS 七步逐篇说明 + 踩坑记录 + 实测数据
├── datasets/                 数据集获取方式与下载脚本
└── scripts/                  同步与批量编译工具
```

## 三条线的进度

| 线 | 内容 | 代码 | 状态 |
|---|---|---|---|
| 单目前端 | 12 步手写：角点 → 描述子 → 匹配 → 三角化 → PnP → 位姿 | `handwritten/mono/` | 流程已跑通，代码待同步 |
| 双目前端 | 12 步手写：双目三角化 + PnP 联合求解 | `handwritten/stereo/` | 流程已跑通，代码待同步 |
| VINS 前端 | 7 步手写：IMU → 光流 → 预积分 → 初始化 SfM → 惯性对齐 → 滑窗 → 轨迹 | `handwritten/vins/` | STEP1–3 通过，STEP4 调试中，STEP5–7 未开始 |

「代码待同步」不是占位套话：代码实际跑在另一台 Ubuntu 工作机上，用 `scripts/collect.sh` 一键同步进来。这样做的好处是仓库里的代码永远等于验收通过的那份代码，不会出现「仓库版本」和「实际运行版本」两套并行。

## 怎么用这个仓库

想理解 VINS 每一步在算什么：从 [`docs/notes/vins/00-pipeline.md`](docs/notes/vins/00-pipeline.md) 开始，那是七步与 VINS-Mono 真实模块的对照图。

想看实际踩过的坑：直接读 [`docs/notes/vins/pitfalls.md`](docs/notes/vins/pitfalls.md)。八条都是有实测输出支撑的结论，不是经验之谈。

想复现某一步：进 `handwritten/<线>/step<N>/`，`cmake` + `make` 即可，数据路径与验收标准写在对应笔记里。

想跑官方框架：见 [`framework/README.md`](framework/README.md)。

想拿数据集：见 [`datasets/README.md`](datasets/README.md)（EuRoC 用脚本按序列下载，KITTI 需邮箱注册后手动下载）。

## 目录约定

三条线共用一套约定，方便横向对照：

- `handwritten/<线>/stepN/` 放该步源码与 `CMakeLists.txt`，`build/` 不入库。
- `handwritten/<线>/results/stepN/` 放该步输出图与数值结果。图和代码分开放，是为了让 `git log` 里「改代码」和「出结果」两类变更不互相淹没。
- 每步的说明文档统一在 `docs/notes/<线>/`，编号与 `stepN` 对齐。

## 为什么笔记不是 Word

课程用的 Word 讲义另存，不入库。仓库里的笔记是 markdown：能 diff、能搜、能在网页上直接读，公式与表格改起来也不费劲。二进制文档一进 Git 就成了不可读的黑盒，还每次提交都翻倍占体积。

## 本地工具

两个脚本都在 `scripts/`，纯 bash，无额外依赖。

**同步（在工作机 Ubuntu 上跑）**

```bash
bash scripts/collect.sh                                  # 自动探测 ~/vins/1steps 等目录
bash scripts/collect.sh --vins ~/vins/1steps --mono ~/slam/1steps
```

把 `stepN/` 下的源码收进 `handwritten/<线>/stepN/`，把图与结果收进 `handwritten/<线>/results/stepN/`，`build/` 自动排除。收完自动 `git add` + `git commit`，**不 push**。

**批量编译**

```bash
bash scripts/build_all.sh              # 全部
bash scripts/build_all.sh vins         # 只编 VINS
bash scripts/build_all.sh vins 4       # 只编 VINS 的 step4
```

有 `CMakeLists.txt` 走 cmake，否则 `g++ + pkg-config opencv4` 直编。

## Git 小抄

```bash
git pull                 # 开工前先拉最新
git add .                # 暂存改动
git commit -m "说明"      # 本地存档
git push                 # 推送到 GitHub
git status               # 不知道当前状态就输它
```
