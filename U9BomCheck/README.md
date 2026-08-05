# U9 BOM 自动核对工具

U9 BOM 页面数据与 Excel BOM 数据的自动核对工具。

## 架构

```text
U9 BOM 页面
    ↓ 只读采集
Edge 插件 (edge-extension/)          → protobuf 无需，JSON 协议 U9BomCheck v1.0
    ↓ JSON 写入剪贴板
Excel VBA 加载项 (excel-addin/)      → 读取当前工作表 BOM
    ↓ 自动核对
输出差异结果
```

- **Edge 插件只读采集**当前 U9 物料清单页面数据。
- **Excel VBA 加载项**读取剪贴板页面数据 + 当前工作簿数据，完成标准化、差异比较与结果输出。
- 不修改 U9 页面、不执行新增/删除/保存/提交/审批，不自动保存 Excel 原始工作簿。

## 目录

| 目录 | 内容 |
|---|---|
| `edge-extension/` | Edge（Chromium）扩展，只读采集页面数据并复制到剪贴板 |
| `excel-addin/` | Excel VBA 加载项 `.bas` 模块，打包为 `U9BomCheck.xlam` |

## 固定核对范围（第一版）

- 主键：子项料号
- 比较字段：用量（容差 0.0001）
- 辅助字段：单位、品名、子件项次
- 差异状态：一致 / 页面缺少 / 页面多余 / 用量不一致 / 单位不一致 / Excel重复 / 页面重复 / Excel数据无效 / 页面数据无效

第一版不处理：替代料、多版本 BOM、生效/失效日期、供应地点、工序维度、批量母件处理、页面写入/保存。

## 快速开始

1. **Edge 插件**：参见 `edge-extension/README.md`，开发者模式加载，在 BOM 页面「采集并复制到剪贴板」。
2. **Excel 加载项**：参见 `excel-addin/README.md`，导入 `.bas` 打包为 `U9BomCheck.xlam` 并安装。
3. 在 `BOM核对` 工作表（第 1 行标题，数据从第 2 行起）按 `Alt+F8` 执行 `U9_执行BOM核对`。

## 两端的协议约定

- 页面数据统一为 `U9BomCheck` 协议（`protocol=U9BomCheck`, `version=1.0`, `success`, `source=U9`, `pageType=MaterialBom`, `collectedAt`, `parentItemCode`, `components[]`, `error`）。
- VBA 先校验协议字段，不符合立即停止，不猜测、不继续核对。
- 页面差异属于业务结果，不作为程序异常；页面采集/Excel 核对均为只读处理。