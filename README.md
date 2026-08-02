# Harness Template

一套面向 Agent 协作开发的轻量项目治理模板，用文档明确需求、硬约束、架构边界、审批流程和交付责任，让项目修改具备可审查、可验证、可追踪的上下文。

本仓库不是业务代码框架，也不规定具体技术栈。使用时应根据目标项目填写模板中的占位内容，并让业务项目保持独立运行，不依赖 harness 文档或工具存在。

## 适用场景

- 使用 AI Agent 参与需求澄清、编码、验证和文档维护
- 希望在修改前明确边界，并保留方案审批与用户审核环节
- 需要区分需求、硬约束、架构、项目状态和变更历史
- 希望将可复用经验、外部依据和共享资产分开管理
- 需要从真实源码或测试执行结果同步架构视图与测试报告

## 核心工作方式

```text
审查现状 -> 确认边界 -> 提出最小方案 -> 用户批准 -> 修改 -> 验证 -> 用户审核
```

主要原则：

- 冲突时依次以 `Rule.md`、`Spec.md`、`Architecture.md`、`lessons/` 和其他文档为准。
- 先复用现有代码、文档、库和资产，再考虑新增接口或抽象。
- 代码和文档改动都按最小可验证单元推进。
- 未经明确授权不创建 commit；commit 和 push 分别授权。
- 机器生成的架构或测试事实必须来自当前源码或真实执行结果，并经过 Agent 检查和用户审核。

完整协作约定见 [AGENTS.md](AGENTS.md)。

## 快速开始

1. 将本模板作为目标项目的协作骨架，按项目约定放置所需文件和目录。
2. 优先填写 [Rule.md](Rule.md) 和 [Spec.md](Spec.md)，明确不可协商的限制、用户需求、输入输出和交付物。
3. 在 [Architecture.md](Architecture.md) 中确定最小架构、依赖边界和允许的演化方向。
4. 用 [STATUS.md](STATUS.md) 记录当前真实进展，用 [CHANGELOG.md](CHANGELOG.md) 追加项目重要变更。
5. 将领域依据放入 `docs/`，按需加入 `shared/` 资产，并在相关技术任务开始前检查 `lessons/`。
6. 开始修改前按 [AGENTS.md](AGENTS.md) 完成审查、提出方案并取得用户批准。

模板中的 `[填写]`、示例路径和示例阶段都需要结合实际项目替换。当前仓库不提供一键初始化命令，也不会替目标项目推断业务规则。

## 目录与文档职责

| 路径 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | Agent 通用工作方式、审批链路、验证和 Git 规则 |
| [Rule.md](Rule.md) | 不可协商的项目硬约束 |
| [Spec.md](Spec.md) | 用户可见需求、输入输出、界面范围和交付标准 |
| [Architecture.md](Architecture.md) | 架构原则、依赖与职责边界、演化及视图维护规则 |
| [STATUS.md](STATUS.md) | 当前状态、已完成事项、风险和下一步 |
| [CHANGELOG.md](CHANGELOG.md) | 具体项目的重要变更历史 |
| [HARNESSLOG.md](HARNESSLOG.md) | 仅用于维护本模板自身的演化记录 |
| [docs/](docs/README.md) | 领域知识、公式、接口协议和外部依据 |
| [shared/](shared/README.md) | 项目按需放入的共享资产；模板默认留空 |
| [lessons/](lessons/README.md) | 独立于具体项目的可复用经验、陷阱和检查清单 |
| [tools/](tools/README.md) | 审查、验证和交付文档同步工具 |

文档应各守职责。需求变化进入 `Spec.md`，硬约束变化进入 `Rule.md`，架构边界变化进入 `Architecture.md`，项目状态和历史分别进入 `STATUS.md` 与 `CHANGELOG.md`，避免在多个位置维护同一份事实。

## 辅助工具

`tools/` 当前提供两个参数化的 Python 工具：

- `sync_architecture_graph.py`：扫描指定 Python 包的项目内部 import，并更新开发指南中的模块级 Mermaid 依赖图；使用 `--check` 可只检查、不写入。
- `generate_test_report.py`：在指定项目目录真实运行 pytest，通过临时 JUnit XML 汇总执行事实，并更新测试报告中的目标章节。

工具不会替代人工维护的业务数据流、测试场景解释、可靠性判断或用户审核。命令参数、目标文档要求和使用边界见 [tools/README.md](tools/README.md)。

## 交付边界

- harness 默认属于协作、治理和知识区域，不属于最终业务交付物，除非 `Rule.md` 或 `Spec.md` 明确要求。
- 业务运行所需的源码、资源、配置和第三方资产必须进入最终交付目录。
- 交付文档应能在脱离 harness 后独立说明产品使用方式、已实现架构和测试可靠性。
- `lessons/` 中的内容是通用经验，不自动成为具体项目的业务规则。
- `HARNESSLOG.md` 只随模板维护；实例化后的具体项目不应默认创建或保留它。

## 当前范围

- 模板本身不包含业务实现或通用构建系统。
- 架构依赖图工具当前面向 Python 源码。
- 测试报告工具当前面向 pytest，并要求目标环境已安装 pytest。
- 模板不会自动创建交付目录中的 `User_Manual.md`、`Developer_Guide.md` 或 `Test_Report.md`；是否需要及其位置由目标项目的规格和规则确定。
