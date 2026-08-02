# Harness 工具模板说明

本目录提供可复制到项目 `harness/tools/` 的通用文档维护工具。工具只在项目审查、验证和文档维护阶段使用，业务运行不得依赖 `harness/` 存在。

实例化项目时，应根据实际交付目录、源码目录、测试目录和文档标题填写命令参数。工具脚本本身不得写入具体项目名称、模块名称或固定业务路径。

## 架构依赖图

`sync_architecture_graph.py` 扫描指定 Python 包中的项目内部 import，生成模块级 Mermaid 依赖图。它不生成完整函数调用图，不展示第三方库，也不修改人工维护的业务数据流图。

通用调用形式：

```bash
python harness/tools/sync_architecture_graph.py \
  --source [业务源码包目录] \
  --document [交付目录]/docs/Developer_Guide.md \
  --section "### [模块依赖章节标题]"
```

增加 `--check` 时只检查依赖图是否与源码一致，不修改文档。

工具根据 `--section` 指定的 Markdown 标题定位章节，只替换该章节中的第一个 Mermaid 代码块。交付文档不保存 HTML 注释或其他同步标记。

新增、删除、重命名模块或改变项目内部 import 后，Agent 应先审查并更新业务数据流图，再同步模块依赖图，检查两张图是否一致，最后交给用户审核。

## 测试报告

`generate_test_report.py` 使用指定 Python 解释器运行完整测试，通过临时 JUnit XML 获取实际执行结果，并更新测试报告中的执行摘要。临时结果和精确测试节点在本次运行结束后丢弃，不写入项目目录。

通用调用形式：

```bash
python harness/tools/generate_test_report.py \
  --project-root [测试运行目录] \
  --tests [相对测试目录] \
  --output [交付目录]/docs/Test_Report.md \
  --section "## [执行摘要章节标题]" \
  --python [已安装测试依赖的 Python 解释器]
```

工具根据 `--section` 指定的 Markdown 标题替换该章节正文。测试报告中的业务场景、关键输入、预期结果、可靠性判断和未覆盖范围由 Agent 对照测试实现维护，并交给用户审核。

需要查看测试框架实际收集到的技术节点时，直接使用测试框架的收集命令，不保存派生节点清单。
