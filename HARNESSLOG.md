# Harness 骨架演化记录 (HARNESSLOG.md)

本文件只记录 `harness_template/` 骨架自身的演化，不记录具体项目开发进度。

`HARNESSLOG.md` 只存在于模板维护场景。根据模板生成具体项目的 `harness/` 时，不应默认生成本文件；具体项目内也不应由 Agent 自行新建 `HARNESSLOG.md`。

## [Unreleased] - 2026-08-02

### Added

- 完善根目录 `README.md`，补充模板定位、使用流程、文档导航、工具入口和交付边界。
- 新增通用架构依赖图同步工具和测试报告生成工具，均通过参数指定业务源码、交付文档和目标标题，不绑定具体项目。
- 新增架构视图与测试报告的通用维护标准：机器生成事实来自源码或真实测试执行，语义解释由 Agent 维护并由用户审核。
- 新增 `harness_template/`，用于从当前项目协作经验中抽象可复用 harness 骨架。
- 新增 `HARNESSLOG.md`，专门记录 harness 模板自身的结构和规则演化。

### Changed

- 将 `Architecture.md` 收敛为架构原则、依赖边界和视图维护规则；当前实现效果统一由交付目录中的 `Developer_Guide.md` 承载。
- 将自动化测试项目的默认最小文档集合扩展为 `User_Manual.md`、`Developer_Guide.md` 和 `Test_Report.md`。
- 明确最终交付文档不得依赖 `harness/` 才能理解当前实现，生成工具通过标题定位内容，不在交付文档中保留 HTML 同步标记。
- 明确测试报告不持久化派生测试节点清单，每次更新都应真实执行完整测试。
- 将模板状态文档从 `Project_Status.md` 重命名为 `STATUS.md`，降低项目实例化后的命名负担。
- 收敛 `AGENTS.md` 职责，只保留通用行为公约、文档索引和更新路由。
- 将架构演化原则保留在 `Architecture.md`，避免在 `AGENTS.md` 中重复展开。
- 将 changelog 维护规则保留在 `CHANGELOG.md`，避免在 `AGENTS.md` 中重复展开。
- 将 `AGENTS.md` 中残留的结构演化类表述改为引用 `Architecture.md`，继续收敛文档职责边界。
- 明确 `shared/` 在模板中默认不包含共享资产，具体项目需要共享资产时再手动放入。
- 明确 `HARNESSLOG.md` 只属于模板维护场景，不属于具体项目实例的默认 `harness/` 文件。
- 将交付文档默认纳入最终交付目录的 `docs/` 范围，并收敛为 `User_Manual.md` 与 `Developer_Guide.md` 两个最小文档入口。
- 新增交付文档维护的三段式触发机制：广度触发、深度触发和交付触发。

### Removed

- 移除 `shared/README.md` 中关于资产变更、状态或历史的记录职责，仅保留目录用途说明。
