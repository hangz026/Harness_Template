# Harness 骨架演化记录 (HARNESSLOG.md)

本文件只记录 `harness_template/` 骨架自身的演化，不记录具体项目开发进度。

`HARNESSLOG.md` 只存在于模板维护场景。根据模板生成具体项目的 `harness/` 时，不应默认生成本文件；具体项目内也不应由 Agent 自行新建 `HARNESSLOG.md`。

## [Unreleased] - 2026-06-26

### Added

- 新增 `harness_template/`，用于从当前项目协作经验中抽象可复用 harness 骨架。
- 新增 `HARNESSLOG.md`，专门记录 harness 模板自身的结构和规则演化。

### Changed

- 将模板状态文档从 `Project_Status.md` 重命名为 `STATUS.md`，降低项目实例化后的命名负担。
- 收敛 `AGENTS.md` 职责，只保留通用行为公约、文档索引和更新路由。
- 将架构演化原则保留在 `Architecture.md`，避免在 `AGENTS.md` 中重复展开。
- 将 changelog 维护规则保留在 `CHANGELOG.md`，避免在 `AGENTS.md` 中重复展开。
- 将 `AGENTS.md` 中残留的结构演化类表述改为引用 `Architecture.md`，继续收敛文档职责边界。
- 明确 `shared/` 在模板中默认不包含共享资产，具体项目需要共享资产时再手动放入。
- 明确 `HARNESSLOG.md` 只属于模板维护场景，不属于具体项目实例的默认 `harness/` 文件。

### Removed

- 移除 `shared/README.md` 中关于资产变更、状态或历史的记录职责，仅保留目录用途说明。
