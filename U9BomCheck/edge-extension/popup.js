// popup.js —— 触发 background 采集/复制，并展示结果
const statusEl = document.getElementById("status");

function show(text, cls) {
  statusEl.textContent = text;
  statusEl.className = cls || "";
}

async function getActiveTabId() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab ? tab.id : null;
}

document.getElementById("collect").addEventListener("click", async () => {
  const tabId = await getActiveTabId();
  if (tabId == null) {
    show("未找到当前标签页。", "err");
    return;
  }
  show("采集中…", "");
  chrome.runtime.sendMessage({ type: "U9_POPUP_COLLECT", tabId }, (resp) => {
    if (!resp || !resp.ok) {
      show("采集失败：" + ((resp && resp.error) || "未知错误"), "err");
      return;
    }
    const d = resp.data;
    if (!d.success) {
      show("采集失败：" + d.error, "err");
      return;
    }
    show(
      "母件料号：" + d.parentItemCode +
      "\n子项数量：" + d.components.length +
      "\n采集时间：" + d.collectedAt +
      "\n\n" + JSON.stringify(d, null, 2),
      "ok"
    );
  });
});

document.getElementById("copy").addEventListener("click", async () => {
  const tabId = await getActiveTabId();
  if (tabId == null) {
    show("未找到当前标签页。", "err");
    return;
  }
  show("采集中…", "");
  chrome.runtime.sendMessage({ type: "U9_POPUP_COPY", tabId }, (resp) => {
    if (!resp || !resp.ok) {
      show("复制失败：" + ((resp && resp.error) || "未知错误"), "err");
      return;
    }
    const d = resp.data;
    if (!d.success) {
      show("复制失败：" + d.error, "err");
      return;
    }
    show(
      "已复制到剪贴板 ✔\n" +
      "检查点：" + d.checkpoint +
      "\n母件料号：" + d.parentItemCode +
      "\n子项数量：" + d.componentCount +
      "\n采集时间：" + d.collectedAt,
      "ok"
    );
  });
});