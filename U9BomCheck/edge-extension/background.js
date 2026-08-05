/**
 * U9 BOM 只读采集 —— background.js (Manifest V3 Service Worker)
 *
 * 职责：
 *   1. 向指定 tab 的 content script 发送消息，只读采集当前 U9 BOM 页面数据。
 *   2. 校验页面类型、组装 U9BomCheck 协议 JSON。
 *   3. 通过 content script 将 JSON 写入剪贴板（Service Worker 无法可靠访问
 *      navigator.clipboard，复制动作交给 content script 完成）。
 *
 * 只读约束：本文件不执行任何 click / dispatchEvent / 修改 value / 保存 / 提交。
 */

const U9_PROTOCOL = "U9BomCheck";
const U9_VERSION = "1.0";
const U9_PAGE_TYPE = "MaterialBom";
const U9_PAGE_ID = "CBO.MFG.BOM.BOM";

/**
 * 向指定标签页发送消息，并等待 content script 返回。
 * @param {number} tabId
 * @param {*} message
 * @returns {Promise<*>}
 */
async function sendToTab(tabId, message) {
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(tabId, message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      resolve(response);
    });
  });
}

/**
 * 校验采集结果是否满足 U9BomCheck 协议要求。
 * 不符合时返回带 error 的失败 JSON，不做任何猜测、不继续核对。
 * @param {object} raw  content script 返回的原始采集数据
 * @returns {object} U9BomCheck JSON
 */
function buildU9BomJson(raw) {
  const now = new Date().toISOString();

  if (!raw || raw.success !== true) {
    return {
      protocol: U9_PROTOCOL,
      version: U9_VERSION,
      success: false,
      source: "U9",
      pageType: raw && raw.pageType ? raw.pageType : U9_PAGE_TYPE,
      collectedAt: now,
      parentItemCode: raw && raw.parentItemCode ? raw.parentItemCode : "",
      components: [],
      error: raw && raw.error ? raw.error : "页面采集失败或未返回数据。"
    };
  }

  if (raw.pageType !== U9_PAGE_TYPE) {
    return {
      protocol: U9_PROTOCOL,
      version: U9_VERSION,
      success: false,
      source: "U9",
      pageType: raw.pageType || U9_PAGE_TYPE,
      collectedAt: now,
      parentItemCode: raw.parentItemCode || "",
      components: [],
      error:
        "当前页面不是物料清单(BOM)页面，期望页面类型 " +
        U9_PAGE_TYPE +
        "，实际为 " +
        (raw.pageType || "未知") +
        "。"
    };
  }

  if (!Array.isArray(raw.components)) {
    return {
      protocol: U9_PROTOCOL,
      version: U9_VERSION,
      success: false,
      source: "U9",
      pageType: U9_PAGE_TYPE,
      collectedAt: now,
      parentItemCode: raw.parentItemCode || "",
      components: [],
      error: "页面子件表格数据格式无效（components 不是数组）。"
    };
  }

  return {
    protocol: U9_PROTOCOL,
    version: U9_VERSION,
    success: true,
    source: "U9",
    pageType: U9_PAGE_TYPE,
    collectedAt: now,
    parentItemCode: raw.parentItemCode || "",
    components: raw.components.map((c, idx) => ({
      sequence: String(c.sequence != null ? c.sequence : ""),
      itemCode: String(c.itemCode != null ? c.itemCode : ""),
      itemName: String(c.itemName != null ? c.itemName : ""),
      usageQty: c.usageQty != null ? Number(c.usageQty) : 0,
      usageUom: String(c.usageUom != null ? c.usageUom : "")
    })),
    error: ""
  };
}

/**
 * 只读采集指定 tabId 中的 U9 BOM 页面数据。
 * @param {object} options { tabId }
 * @returns {Promise<object>} U9BomCheck JSON
 */
globalThis.u9CollectBomForExcel = async function (options = {}) {
  const tabId = options.tabId != null ? options.tabId : null;

  if (tabId == null) {
    return failJson("缺少 tabId，无法定位 U9 BOM 页面。");
  }

  try {
    const raw = await sendToTab(tabId, { type: "U9_COLLECT_BOM" });
    return buildU9BomJson(raw);
  } catch (err) {
    return failJson(
      "无法读取页面数据：" + (err && err.message ? err.message : String(err))
    );
  }
};

/**
 * 采集 U9 BOM 页面数据，并通过 content script 将 JSON 写入剪贴板。
 * @param {object} options { tabId }
 * @returns {Promise<object>}
 */
globalThis.u9CopyBomForExcel = async function (options = {}) {
  const tabId = options.tabId != null ? options.tabId : null;

  const result = await globalThis.u9CollectBomForExcel(options);

  if (!result.success) {
    return result;
  }

  if (tabId == null) {
    return failJson("缺少 tabId，无法复制。");
  }

  const jsonText = JSON.stringify(result, null, 2);

  try {
    const copyResult = await sendToTab(tabId, {
      type: "U9_COPY_JSON",
      json: jsonText
    });

    if (!copyResult || copyResult.success !== true) {
      return failJson(
        "已采集数据，但写入剪贴板失败：" +
          ((copyResult && copyResult.error) || "未知原因")
      );
    }

    return {
      success: true,
      checkpoint: "BOM_JSON_COPIED",
      protocol: U9_PROTOCOL,
      version: U9_VERSION,
      parentItemCode: result.parentItemCode,
      componentCount: result.components.length,
      collectedAt: result.collectedAt
    };
  } catch (err) {
    return failJson(
      "已采集数据，但写入剪贴板失败：" +
        (err && err.message ? err.message : String(err))
    );
  }
};

function failJson(message) {
  return {
    protocol: U9_PROTOCOL,
    version: U9_VERSION,
    success: false,
    source: "U9",
    pageType: U9_PAGE_TYPE,
    collectedAt: new Date().toISOString(),
    parentItemCode: "",
    components: [],
    error: message
  };
}

// 供 popup 直接调用
if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.type === "U9_POPUP_COLLECT") {
      globalThis
        .u9CollectBomForExcel({ tabId: msg.tabId })
        .then((data) => sendResponse({ ok: true, data }))
        .catch((err) =>
          sendResponse({ ok: false, error: String(err && err.message) })
        );
      return true; // 保持消息通道以支持异步 sendResponse
    }
    if (msg && msg.type === "U9_POPUP_COPY") {
      globalThis
        .u9CopyBomForExcel({ tabId: msg.tabId })
        .then((data) => sendResponse({ ok: true, data }))
        .catch((err) =>
          sendResponse({ ok: false, error: String(err && err.message) })
        );
      return true;
    }
    return false;
  });
}