const state = {
  currentTraceId: "",
  pendingInterrupt: null,
  currentResult: "",
  tokenCount: 0,
  eventCount: 0,
  sourceCount: 0,
  interruptCount: 0,
};

const elements = {
  form: document.getElementById("research-form"),
  questionInput: document.getElementById("question-input"),
  userIdInput: document.getElementById("user-id"),
  threadIdInput: document.getElementById("thread-id"),
  refreshThreadButton: document.getElementById("refresh-thread"),
  clearButton: document.getElementById("clear-button"),
  statusBadge: document.getElementById("status-badge"),
  traceId: document.getElementById("trace-id"),
  resultMeta: document.getElementById("result-meta"),
  resultOutput: document.getElementById("result-output"),
  eventLog: document.getElementById("event-log"),
  sourcesList: document.getElementById("sources-list"),
  interruptPanel: document.getElementById("interrupt-panel"),
  interruptForm: document.getElementById("interrupt-form"),
  actionRequests: document.getElementById("action-requests"),
  submitButton: document.getElementById("submit-button"),
  resumeButton: document.getElementById("resume-button"),
  chips: Array.from(document.querySelectorAll(".chip")),
  heroStage: document.getElementById("hero-stage"),
  heroStageCopy: document.getElementById("hero-stage-copy"),
  metricTokenCount: document.getElementById("metric-token-count"),
  metricEventCount: document.getElementById("metric-event-count"),
  metricSourceCount: document.getElementById("metric-source-count"),
  metricInterruptCount: document.getElementById("metric-interrupt-count"),
};

function createThreadId() {
  return `thread_${Date.now()}`;
}

function restoreSession() {
  const savedUserId = window.localStorage.getItem("rf_user_id");
  const savedThreadId = window.localStorage.getItem("rf_thread_id");

  if (savedUserId) {
    elements.userIdInput.value = savedUserId;
  }

  elements.threadIdInput.value = savedThreadId || createThreadId();
}

function persistSession() {
  window.localStorage.setItem("rf_user_id", elements.userIdInput.value.trim() || "user_001");
  window.localStorage.setItem("rf_thread_id", elements.threadIdInput.value.trim() || createThreadId());
}

function setStatus(text, tone = "idle") {
  elements.statusBadge.textContent = text;
  elements.statusBadge.className = `status-badge status-${tone}`;
}

function setTraceId(traceId) {
  state.currentTraceId = traceId || "";
  elements.traceId.textContent = traceId || "尚未开始";
}

function setResultMeta(text) {
  elements.resultMeta.textContent = text;
}

function setStageLabel(title, copy) {
  elements.heroStage.textContent = title;
  elements.heroStageCopy.textContent = copy;
}

function syncMetricView() {
  elements.metricTokenCount.textContent = String(state.tokenCount);
  elements.metricEventCount.textContent = String(state.eventCount);
  elements.metricSourceCount.textContent = String(state.sourceCount);
  elements.metricInterruptCount.textContent = String(state.interruptCount);
}

function resetMetrics() {
  state.tokenCount = 0;
  state.eventCount = 0;
  state.sourceCount = 0;
  state.interruptCount = 0;
  syncMetricView();
}

function setBusy(isBusy) {
  elements.submitButton.disabled = isBusy;
  elements.resumeButton.disabled = isBusy;
  elements.refreshThreadButton.disabled = isBusy;
}

function resetOutput() {
  state.currentResult = "";
  elements.resultOutput.textContent = "";
  elements.eventLog.innerHTML = "";
  elements.eventLog.classList.add("empty-state");
  elements.eventLog.textContent = "等待执行事件";
  elements.sourcesList.innerHTML = "";
  elements.sourcesList.classList.add("empty-state");
  elements.sourcesList.textContent = "当前还没有来源数据";
  setTraceId("");
  setResultMeta("等待任务开始");
  setStageLabel(
    "Ready For Research Brief",
    "提交任务后，这里会实时展示规划、检索、审批和完成阶段。",
  );
  resetMetrics();
  hideInterruptPanel();
}

function appendEvent(title, content, tone = "neutral") {
  state.eventCount += 1;
  syncMetricView();

  if (elements.eventLog.classList.contains("empty-state")) {
    elements.eventLog.classList.remove("empty-state");
    elements.eventLog.innerHTML = "";
  }

  const item = document.createElement("article");
  item.className = `event-item event-${tone}`;

  const titleNode = document.createElement("div");
  titleNode.className = "event-title";
  titleNode.textContent = title;

  const contentNode = document.createElement("div");
  contentNode.className = "event-content";
  contentNode.textContent = content;

  item.append(titleNode, contentNode);
  elements.eventLog.prepend(item);
}

function appendResultChunk(content) {
  state.currentResult += content;
  elements.resultOutput.textContent = state.currentResult;
}

function setFinalResult(result) {
  state.currentResult = result || "";
  elements.resultOutput.textContent = state.currentResult;
}

function renderSources(sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    state.sourceCount = 0;
    syncMetricView();
    elements.sourcesList.innerHTML = "当前还没有来源数据";
    elements.sourcesList.classList.add("empty-state");
    return;
  }

  state.sourceCount = sources.length;
  syncMetricView();
  elements.sourcesList.classList.remove("empty-state");
  elements.sourcesList.innerHTML = "";

  sources.forEach((source) => {
    const card = document.createElement("article");
    card.className = "source-card";

    const title = document.createElement("h3");
    title.textContent = source.title || "未命名来源";

    const link = document.createElement("a");
    link.href = safeUrl(source.url);
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "查看原文";

    const note = document.createElement("p");
    note.textContent = source.note || "无附加说明";

    card.append(title, link, note);
    elements.sourcesList.appendChild(card);
  });
}

function showInterruptPanel(interruptDetails) {
  state.pendingInterrupt = interruptDetails;
  state.interruptCount += (interruptDetails?.action_requests || []).length || 1;
  syncMetricView();
  elements.interruptPanel.classList.remove("hidden");
  elements.actionRequests.innerHTML = "";

  const actions = interruptDetails?.action_requests || [];

  actions.forEach((action, index) => {
    const args = action.args || action.arguments || {};
    const wrapper = document.createElement("article");
    wrapper.className = "action-card";
    wrapper.innerHTML = `
      <div class="action-head">
        <h3>${escapeHtml(action.name || `action_${index + 1}`)}</h3>
        <label class="field inline-field">
          <span>决策</span>
          <select class="decision-select" data-index="${index}">
            <option value="approve">approve</option>
            <option value="edit">edit</option>
            <option value="reject">reject</option>
          </select>
        </label>
      </div>
      <label class="field">
        <span>参数 JSON</span>
        <textarea class="action-args" data-index="${index}" rows="8">${escapeHtml(JSON.stringify(args, null, 2))}</textarea>
      </label>
    `;
    elements.actionRequests.appendChild(wrapper);
  });
}

function hideInterruptPanel() {
  state.pendingInterrupt = null;
  elements.interruptPanel.classList.add("hidden");
  elements.actionRequests.innerHTML = "";
}

function collectDecisions() {
  const actions = state.pendingInterrupt?.action_requests || [];

  return actions.map((action, index) => {
    const decision = elements.actionRequests.querySelector(`.decision-select[data-index="${index}"]`).value;
    const rawArgs = elements.actionRequests.querySelector(`.action-args[data-index="${index}"]`).value;

    if (decision === "approve") {
      return { type: "approve" };
    }

    if (decision === "reject") {
      return { type: "reject" };
    }

    return {
      type: "edit",
      edited_action: {
        name: action.name,
        args: JSON.parse(rawArgs),
      },
    };
  });
}

async function streamJsonEvents(url, payload, onEvent) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }

  if (!response.body) {
    throw new Error("浏览器未返回可读流");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary).trim();
      buffer = buffer.slice(boundary + 2);

      rawEvent
        .split("\n")
        .filter((line) => line.startsWith("data:"))
        .forEach((line) => {
          const payloadText = line.slice(5).trim();
          if (payloadText) {
            onEvent(JSON.parse(payloadText));
          }
        });

      boundary = buffer.indexOf("\n\n");
    }

    if (done) {
      break;
    }
  }
}

function handleStreamEvent(event) {
  if (event.trace_id) {
    setTraceId(event.trace_id);
  }

  if (event.type === "token") {
    const tokenText = event.content || "";
    state.tokenCount += tokenText.length;
    syncMetricView();
    setStatus("生成中", "running");
    setStageLabel("Drafting Live Analysis", "模型正在实时生成研究内容，浏览器正在持续接收 SSE 输出。");
    setResultMeta(`实时生成中 · ${event.elapsed_ms}ms`);
    appendResultChunk(tokenText);
    appendEvent("Token", tokenText, "running");
    return;
  }

  if (event.type === "tool_output") {
    setStageLabel("Consulting Retrieval Tools", "系统已切入工具阶段，正在处理检索或外部能力返回结果。");
    appendEvent("工具输出", event.content || "收到工具结果", "tool");
    return;
  }

  if (event.type === "interrupted") {
    setStatus("等待审批", "warning");
    setStageLabel("Waiting For Human Review", "已命中人工审批节点，需要你确认检索工具参数后才能继续执行。");
    setResultMeta("检测到需要人工审批的工具调用");
    appendEvent("需要审批", "请在右侧审批面板确认后继续执行。", "warning");
    showInterruptPanel(event.interrupt_details);
    return;
  }

  if (event.type === "completed") {
    setStatus("已完成", "success");
    setStageLabel("Research Report Delivered", "研究报告已经生成，来源与建议也已整理完成。");
    setResultMeta(`执行完成 · ${event.elapsed_ms}ms`);
    setFinalResult(event.result || state.currentResult);
    renderSources(event.sources || []);
    appendEvent("执行完成", "研究报告已生成。", "success");
    hideInterruptPanel();
  }
}

async function startResearch(payload) {
  resetOutput();
  setBusy(true);
  setStatus("执行中", "running");
  setStageLabel("Planning Research Flow", "系统正在拆解问题、组织研究提纲并准备进入检索阶段。");
  setResultMeta("正在调用 /ask/stream");
  appendEvent("任务开始", payload.question, "neutral");

  try {
    await streamJsonEvents("/ask/stream", payload, handleStreamEvent);
  } catch (error) {
    setStatus("执行失败", "error");
    setStageLabel("Execution Failed", "本次请求未正常完成，请检查接口状态或环境配置。");
    setResultMeta("请求出现异常");
    appendEvent("错误", error.message, "error");
  } finally {
    setBusy(false);
  }
}

async function resumeResearch(decisions) {
  const payload = {
    user_id: elements.userIdInput.value.trim() || "user_001",
    thread_id: elements.threadIdInput.value.trim(),
    decisions,
  };

  setBusy(true);
  setStatus("继续执行中", "running");
  setStageLabel("Resuming After Review", "系统正在从审批中断点恢复执行，并继续完成研究结果生成。");
  setResultMeta("正在调用 /intervene/stream");
  appendEvent("提交审批", JSON.stringify(decisions, null, 2), "neutral");

  try {
    await streamJsonEvents("/intervene/stream", payload, handleStreamEvent);
  } catch (error) {
    setStatus("审批失败", "error");
    setStageLabel("Review Resume Failed", "审批已提交，但恢复执行过程出现异常。");
    appendEvent("错误", error.message, "error");
  } finally {
    setBusy(false);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeUrl(value) {
  try {
    const url = new URL(value, window.location.origin);
    if (url.protocol === "http:" || url.protocol === "https:") {
      return url.toString();
    }
  } catch (_error) {
    return "#";
  }

  return "#";
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = elements.questionInput.value.trim();
  const userId = elements.userIdInput.value.trim() || "user_001";
  const threadId = elements.threadIdInput.value.trim() || createThreadId();

  if (!question) {
    setStatus("请先输入研究问题", "warning");
    setStageLabel("Waiting For A Brief", "先输入一个值得展示的研究问题，再启动完整工作流。");
    return;
  }

  elements.threadIdInput.value = threadId;
  persistSession();

  await startResearch({
    user_id: userId,
    thread_id: threadId,
    question,
  });
});

elements.interruptForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    const decisions = collectDecisions();
    await resumeResearch(decisions);
  } catch (error) {
    setStatus("审批参数错误", "error");
    setStageLabel("Approval Payload Error", "当前审批参数不是合法 JSON，请修正后再继续。");
    appendEvent("错误", error.message, "error");
  }
});

elements.refreshThreadButton.addEventListener("click", () => {
  elements.threadIdInput.value = createThreadId();
  persistSession();
  setStatus("线程已重置", "idle");
  setStageLabel("Fresh Thread Prepared", "新的线程已就绪，可以开始下一次研究任务。");
});

elements.clearButton.addEventListener("click", () => {
  resetOutput();
  setStatus("待命中", "idle");
});

elements.userIdInput.addEventListener("change", persistSession);
elements.threadIdInput.addEventListener("change", persistSession);

elements.chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    elements.questionInput.value = chip.dataset.question || "";
    elements.questionInput.focus();
  });
});

restoreSession();
persistSession();
resetOutput();
setStatus("待命中", "idle");
