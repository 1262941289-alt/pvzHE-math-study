# U9 BOM 自动核对工具 · Excel VBA 加载项

> 加载项文件名：`U9BomCheck.xlam`（由本目录下的 `.bas` 模块打包而成）
> 建议安装目录：`C:\Users\tingwuliu\AppData\Roaming\Microsoft\AddIns`

## 模块清单

| 文件 | 模块 | 职责 |
|---|---|---|
| `JsonConverter.bas` | JsonConverter | 自包含 JSON 解析器（无外部依赖） |
| `modClipboard.bas` | modClipboard | 剪贴板文本读取 |
| `modJson.bas` | modJson | 剪贴板 JSON 读取 + U9BomCheck 协议校验 |
| `modBomCompare.bas` | modBomCompare | 数据标准化、差异比较、计数 |
| `modResultWriter.bas` | modResultWriter | 结果写入 E:I 列（只写输出列） |
| `modBomCheckEntry.bas` | modBomCheckEntry | 公共入口宏 |

## 如何打包成 .xlam

`.xlam` 是二进制文件，无法用文本直接生成。请按以下步骤导入全部 `.bas` 并另存为加载项：

1. 打开 Excel → 新建空白工作簿。
2. 按 `Alt+F11` 打开 VBE。
3. 菜单 → 文件 → 导入文件（或右键工程 → 导入文件），依次导入本目录下全部 6 个 `.bas` 文件。
4. 确认工程窗口中已出现以下模块：`JsonConverter`、`modClipboard`、`modJson`、`modBomCompare`、`modResultWriter`、`modBomCheckEntry`。
5. 关闭 VBE，回到 Excel。
6. 文件 → 另存为 → 类型选 **Excel 加载项 (*.xlam)**，文件名 `U9BomCheck`。
   - 若另存时找不到 `AddIns` 目录，可手动粘贴到 `C:\Users\tingwuliu\AppData\Roaming\Microsoft\AddIns`。

## 安装加载项

```text
Excel
→ 文件
→ 选项
→ 加载项
→ 管理：Excel 加载项
→ 转到
→ 浏览并勾选 U9BomCheck.xlam
→ 确定
```

## 使用

打开任意工作簿，在 `BOM核对` 工作表录入数据（第 1 行标题，数据从第 2 行开始），按 `Alt+F8` 执行宏：

| 宏 | 作用 |
|---|---|
| `U9_执行BOM核对` | 读取剪贴板页面数据，核对当前工作表，输出到 E:I |
| `U9_清除核对结果` | 清除 E:I 列输出 |
| `U9_查看页面数据` | 查看剪贴板中的页面采集数据 |

## 输入表结构（工作表名：BOM核对）

| 列 | 字段 | 类型 | 说明 |
|---|---|---|---|
| A | 子项料号 | 输入 | Excel BOM 中的子项料号 |
| B | Excel用量 | 输入 | 用量 |
| C | Excel单位 | 输入 | 单位 |
| D | 品名 | 输入 | 可选辅助字段 |
| E | 核对结果 | 输出 | 一致/页面缺少/用量不一致 等 |
| F | 页面用量 | 输出 | U9 采集的用量 |
| G | 页面单位 | 输出 | U9 采集的单位 |
| H | 差异说明 | 输出 | 具体差异描述 |
| I | 核对时间 | 输出 | 本次核对时间 |

## 差异状态

`一致 / 页面缺少 / 页面多余 / 用量不一致 / 单位不一致 / Excel重复 / 页面重复 / Excel数据无效 / 页面数据无效`

数量比较容差：`0.0001`。

## 说明与约束

- 本加载项**只读**：不修改 A:D 输入列，不自动保存工作簿，不写入加载项自身工作簿。
- 核对对象明确为 `ActiveWorkbook` 的当前 `ActiveSheet`。
- 页面额外发现（页面多余/页面重复/页面数据无效）会追写在数据区下方（起始行 = 最后输入行 + 2），只占 E:I，不扩展 A 列数据范围，保证重复运行不发散。
- 依赖 `Scripting.Dictionary`（系统自带，无需额外引用）。