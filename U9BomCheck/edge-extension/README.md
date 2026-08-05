# U9 BOM 只读采集 · Edge 扩展

只读采集 U9 物料清单(BOM)页面数据，通过剪贴板传递给 Excel VBA 加载项核对。

## 文件

| 文件 | 作用 |
|---|---|
| `manifest.json` | Manifest V3 清单 |
| `background.js` | 采集/复制入口（Service Worker） |
| `content-script.js` | 页面只读采集 + 剪贴板复制 |
| `popup.html` / `popup.js` | 扩展弹窗（采集/复制） |

## 安装（开发者模式加载）

1. Edge 地址栏输入 `edge://extensions`。
2. 打开右上角「开发人员模式」。
3. 点「加载解压缩的扩展」，选择本 `edge-extension` 目录。
4. 已加载后，工具列出现「U9 BOM 只读采集」图标。

## 使用

1. 打开目标 U9 BOM 页面（页面标识 `CBO.MFG.BOM.BOM`，子件表格 `#u_M_p0_DataGrid1`）。
2. 点扩展图标 → 「采集并复制到剪贴板」。
3. 切到 Excel，执行 `U9_执行BOM核对`。

## 控制台手动测试

在 U9 页面按 `F12` 打开控制台，在 content script 上下文调用只读采集（不复制）：

```javascript
const data = globalThis.u9CollectBomOnPage();
console.log(JSON.stringify(data, null, 2));
```

在 Service Worker 控制台（`edge://extensions` → 扩展「详细信息」→「查看 Service Worker」）可调用：

```javascript
const data = await globalThis.u9CollectBomForExcel({ tabId: 目标标签ID });
console.log(JSON.stringify(data, null, 2));
```

## 输出协议（U9BomCheck v1.0）

```json
{
  "protocol": "U9BomCheck",
  "version": "1.0",
  "success": true,
  "source": "U9",
  "pageType": "MaterialBom",
  "collectedAt": "2026-08-05T10:30:00+08:00",
  "parentItemCode": "6800000-XXXX",
  "components": [
    {
      "sequence": "10",
      "itemCode": "6804138-H11-A1",
      "itemName": "示例名称",
      "usageQty": 1,
      "usageUom": "EA"
    }
  ],
  "error": ""
}
```

## 只读约束

允许：`querySelector`、读取 `textContent`、读取 `input.value`、读取表格数据模型、生成 JSON、写剪贴板。

禁止：`click`、`dispatchEvent`、修改 `value`、新增/删除行、保存、提交。

> 采集后页面不应出现「未保存的更改」提示。

## 母件料号提示

不同 U9 版本母件料号输入框的 DOM 不同。`content-script.js` 中的 `readParentItemCode()` 提供了一组常见候选选择器，若你的环境采集不到母件料号，请按实际 DOM 补充该函数中的选择器（只读 `input.value`）。

## 剪贴板说明

MV3 Service Worker 无法可靠访问 `navigator.clipboard`，因此实际复制由 `content-script.js` 完成：优先 Clipboard API，失败时降级为隐藏 `textarea` + `execCommand('copy')`。在非 HTTPS 的 http:// 页面，降级方案仍可工作。