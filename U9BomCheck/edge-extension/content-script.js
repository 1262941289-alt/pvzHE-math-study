/**
 * U9 BOM 只读采集 —— content-script.js
 *
 * 职责：
 *   1. 监听 background 消息，只读采集 U9 物料清单页面数据。
 *   2. 将 U9BomCheck JSON 写入剪贴板（带降级方案）。
 *
 * 只读约束：本文件只允许 querySelector / 读取 textContent / 读取 input.value /
 * 读取表格数据模型 / 生成 JSON / 写剪贴板。
 * 禁止 click、dispatchEvent、修改 value、新增行、删除行、保存、提交。
 */

// 目标页面标识与子件表格选择器（可在加载前按需覆盖）
const U9_PAGE_ID = "CBO.MFG.BOM.BOM";
const U9_GRID_SELECTOR = "#u_M_p0_DataGrid1";

/**
 * 读取单元格文本。优先取 input/textarea 的 value，否则取 textContent。
 * 只读，不修改任何值。
 */
function readCellText(cell) {
  if (!cell) {
    return "";
  }
  const editable = cell.querySelector("input, textarea");
  if (editable && editable.value != null) {
    return String(editable.value).trim();
  }
  return String(cell.textContent || "").trim();
}

/**
 * 从表头行中建立“字段名 -> 列号”映射。
 * 识别关键字：子项料号/料号、用量/用量数量/数量、单位/基本单位、品名/名称、子件项次/项次/序号。
 */
function buildHeaderMap(headerCells) {
  const map = {
    itemCode: -1,
    usageQty: -1,
    usageUom: -1,
    itemName: -1,
    sequence: -1
  };

  headerCells.forEach((h, i) => {
    const t = readCellText(h);
    if (!t) {
      return;
    }
    if (/料号/.test(t) || /料品编码/.test(t) || t === "编码") {
      if (map.itemCode === -1) map.itemCode = i;
    } else if (/用量/.test(t) || /数量/.test(t)) {
      if (map.usageQty === -1) map.usageQty = i;
    } else if (/单位/.test(t)) {
      if (map.usageUom === -1) map.usageUom = i;
    } else if (/品名/.test(t) || /名称/.test(t)) {
      if (map.itemName === -1) map.itemName = i;
    } else if (/项次/.test(t) || /序号/.test(t) || /行号/.test(t)) {
      if (map.sequence === -1) map.sequence = i;
    }
  });

  return map;
}

/**
 * 判断当前页面是否为 U9 物料清单页面。
 */
function detectPageId() {
  const bodyText = document.body ? document.body.textContent || "" : "";
  if (bodyText.indexOf(U9_PAGE_ID) !== -1) {
    return U9_PAGE_ID;
  }
  // 兜底：页面上是否包含目标表格
  if (document.querySelector(U9_GRID_SELECTOR)) {
    return U9_PAGE_ID;
  }
  return "";
}

/**
 * 尝试读取母件料号。
 * 因不同 U9 版本 DOM 结构不同，这里给出常见候选选择器；可在此处按环境补充。
 */
function readParentItemCode() {
  const candidates = [
    "input[id*='ItemCode']",
    "input[id*='itemCode']",
    "input[name*='ItemCode']",
    "input[id*='ParentItem']",
    "input[id*='MasterItem']"
  ];
  for (const sel of candidates) {
    const el = document.querySelector(sel);
    if (el && el.value != null && String(el.value).trim() !== "") {
      return String(el.value).trim();
    }
  }
  return "";
}

/**
 * 只读采集 U9 BOM 子件表格数据。
 * @returns {object} { success, pageType, parentItemCode, components, error }
 */
function collectBomOnPage() {
  const grid = document.querySelector(U9_GRID_SELECTOR);
  if (!grid) {
    return {
      success: false,
      pageType: detectPageId(),
      parentItemCode: readParentItemCode(),
      components: [],
      error: "未找到子件表格 " + U9_GRID_SELECTOR + "。"
    };
  }

  // 提取所有表格行（表头 + 数据行）
  const rows = Array.prototype.slice.call(grid.querySelectorAll("tr"));

  // 判断分页：若无可用表头，动态补一行空的表头行
  const headerRow = rows[0];

  // 读取表头与数据行
  const headerCells = Array.prototype.slice.call(
    (headerRow ? headerRow.querySelectorAll("th, td") : [])
  );

  const fm = buildHeaderMap(headerCells);

  if (fm.itemCode === -1) {
    return {
      success: false,
      pageType: detectPageId(),
      parentItemCode: readParentItemCode(),
      components: [],
      error: "子件表格中未识别到“子项料号”列，请检查表头。"
    };
  }

  const components = [];

  for (let r = 1; r < rows.length; r++) {
    const cells = Array.prototype.slice.call(rows[r].querySelectorAll("td"));
    if (cells.length === 0) {
      continue;
    }

    const itemCode = fm.itemCode >= 0 ? readCellText(cells[fm.itemCode]) : "";

    // 空行跳过
    if (itemCode === "" && cells.every((c) => readCellText(c) === "")) {
      continue;
    }

    const rawQty = fm.usageQty >= 0 ? readCellText(cells[fm.usageQty]) : "";
    const usageQty = parseFloat(String(rawQty).replace(/,/g, "").trim());

    components.push({
      sequence: fm.sequence >= 0 ? readCellText(cells[fm.sequence]) : "",
      itemCode: itemCode,
      itemName: fm.itemName >= 0 ? readCellText(cells[fm.itemName]) : "",
      usageQty: isNaN(usageQty) ? 0 : usageQty,
      usageUom: fm.usageUom >= 0 ? readCellText(cells[fm.usageUom]) : ""
    });
  }

  return {
    success: true,
    pageType: detectPageId(),
    parentItemCode: readParentItemCode(),
    components: components,
    error: ""
  };
}

/**
 * 将文本写入剪贴板。优先使用 Clipboard API，失败时降级为隐藏 textarea + execCommand。
 * 只读页面，不修改页面内容本身。
 */
async function copyTextToClipboard(text) {
  // 优先 Clipboard API（需 https 或 localhost，且扩展具有 clipboardWrite 权限）
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return { success: true };
    } catch (e) {
      // 继续降级方案
    }
  }

  // 降级方案：临时 textarea + execCommand('copy')
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    ta.style.top = "0";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, ta.value.length);
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (e) {
      ok = false;
    }
    document.body.removeChild(ta);
    return ok ? { success: true } : { success: false, error: "execCommand('copy') 失败" };
  } catch (e) {
    return { success: false, error: String(e && e.message) };
  }
}

// 监听来自 background 的消息
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.type === "U9_COLLECT_BOM") {
    const data = collectBomOnPage();
    sendResponse(data);
    return false;
  }

  if (msg && msg.type === "U9_COPY_JSON") {
    copyTextToClipboard(msg.json || "").then((res) => {
      sendResponse(res);
    });
    return true; // 异步响应
  }

  return false;
});

// 暴露到全局，便于 F12 控制台手动测试（只读采集不复制）
globalThis.u9CollectBomOnPage = collectBomOnPage;