from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/ui/upload", response_class=HTMLResponse)
def upload_page() -> str:
    return """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scene Story Agent MVP</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%232563eb'/%3E%3Cpath d='M4 11h8M4 8h8M4 5h5' stroke='white' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E">
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f9;
      color: #1f2937;
    }
    body {
      margin: 0;
      padding: 24px;
    }
    main {
      max-width: 1440px;
      margin: 0 auto;
    }
    h1 {
      margin: 0 0 18px;
      font-size: 24px;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 17px;
      letter-spacing: 0;
    }
    h3 {
      margin: 16px 0 8px;
      font-size: 14px;
      letter-spacing: 0;
    }
    .workspace-section {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }
    .workspace-section:first-of-type {
      margin-top: 0;
    }
    .section-heading {
      margin: 0;
      color: #334155;
      font-size: 15px;
      letter-spacing: 0;
    }
    .user-flow-grid {
      display: grid;
      gap: 16px;
    }
    .user-flow-row {
      display: grid;
      gap: 16px;
      align-items: start;
      justify-content: start;
    }
    .user-flow-primary {
      grid-template-columns: repeat(3, minmax(300px, 390px));
    }
    .user-flow-secondary {
      grid-template-columns: repeat(3, minmax(300px, 390px));
    }
    .ops-grid {
      display: grid;
      grid-template-columns: minmax(280px, 0.8fr) minmax(0, 1.2fr);
      gap: 16px;
      align-items: start;
    }
    .screen {
      box-sizing: border-box;
      min-width: 0;
      min-height: 220px;
      padding: 16px;
      border: 1px solid #d7dce2;
      border-radius: 8px;
      background: #ffffff;
    }
    .screen-wide {
      grid-column: span 2;
    }
    .user-flow-grid .screen {
      width: 100%;
      max-width: 390px;
      justify-self: start;
    }
    form {
      display: grid;
      gap: 12px;
    }
    label, legend {
      display: grid;
      gap: 6px;
      font-size: 14px;
      font-weight: 700;
    }
    fieldset {
      display: grid;
      gap: 8px;
      min-width: 0;
      margin: 0;
      padding: 0;
      border: 0;
    }
    input, textarea, button {
      font: inherit;
    }
    input, textarea {
      min-width: 0;
      padding: 10px 12px;
      border: 1px solid #c8d0d9;
      border-radius: 6px;
      background: #ffffff;
    }
    textarea {
      resize: vertical;
    }
    button {
      width: fit-content;
      min-height: 38px;
      padding: 8px 12px;
      border: 0;
      border-radius: 6px;
      color: #ffffff;
      background: #2563eb;
      cursor: pointer;
      font-weight: 700;
    }
    button:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }
    .choice-row {
      display: flex;
      flex-wrap: nowrap;
      gap: 6px;
    }
    .choice-row input {
      position: absolute;
      inline-size: 1px;
      block-size: 1px;
      opacity: 0;
      pointer-events: none;
    }
    .choice {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      inline-size: 40px;
      block-size: 36px;
      padding: 0;
      border: 1px solid #c8d0d9;
      border-radius: 6px;
      background: #ffffff;
      cursor: pointer;
      font-size: 16px;
      font-weight: 700;
    }
    .choice-row input:checked + .choice {
      color: #ffffff;
      border-color: #2563eb;
      background: #2563eb;
    }
    .choice-row input:focus-visible + .choice {
      outline: 3px solid #93c5fd;
      outline-offset: 2px;
    }
    .status-board {
      display: grid;
      gap: 8px;
    }
    .status-item {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 9px 0;
      border-top: 1px solid #e2e8f0;
      font-size: 14px;
    }
    .status-item:first-child {
      border-top: 0;
    }
    .status-label {
      color: #334155;
      font-weight: 700;
    }
    .status-value,
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      background: #f1f5f9;
      color: #475569;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .status-value.is-running {
      background: #dbeafe;
      color: #1d4ed8;
    }
    .status-value.is-done {
      background: #dcfce7;
      color: #166534;
    }
    .status-value.is-failed {
      background: #fee2e2;
      color: #991b1b;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }
    .metric {
      min-width: 0;
      padding: 10px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
    }
    .metric b {
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      color: #64748b;
    }
    .metric span {
      overflow-wrap: anywhere;
      color: #0f172a;
      font-size: 14px;
    }
    .list {
      display: grid;
      gap: 8px;
      min-width: 0;
    }
    .record-button {
      position: relative;
      display: grid;
      gap: 6px;
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      min-width: 0;
      padding: 10px 42px 10px 10px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #ffffff;
      color: #0f172a;
      text-align: left;
      cursor: pointer;
    }
    .record-button.is-selected {
      border-color: #2563eb;
      background: #eff6ff;
    }
    .record-delete {
      position: absolute;
      inset-block-start: 8px;
      inset-inline-end: 8px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      inline-size: 26px;
      block-size: 26px;
      min-height: 26px;
      padding: 0;
      border: 1px solid transparent;
      border-radius: 999px;
      background: transparent;
      color: #64748b;
      font-size: 14px;
      line-height: 1;
    }
    .record-delete:hover,
    .record-delete:focus-visible {
      border-color: #fecaca;
      background: #fee2e2;
      color: #991b1b;
    }
    .record-title {
      display: -webkit-box;
      min-width: 0;
      overflow: hidden;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      text-overflow: ellipsis;
      overflow-wrap: anywhere;
      font-weight: 800;
    }
    .record-headline {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: start;
      min-width: 0;
    }
    .record-datetime {
      color: #64748b;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.5;
      white-space: nowrap;
    }
    .record-memo {
      display: -webkit-box;
      min-width: 0;
      overflow: hidden;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      text-overflow: ellipsis;
      overflow-wrap: anywhere;
      color: #475569;
      font-size: 13px;
      line-height: 1.4;
    }
    .record-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-width: 0;
      overflow: hidden;
    }
    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      color: #64748b;
      font-size: 12px;
    }
    .data-row {
      display: grid;
      gap: 4px;
      padding: 9px 0;
      border-top: 1px solid #e2e8f0;
    }
    .data-row:first-child {
      border-top: 0;
    }
    .detail-hero,
    .detail-section {
      display: grid;
      gap: 8px;
      padding: 10px 0;
      border-top: 1px solid #e2e8f0;
    }
    .detail-hero:first-child,
    .detail-section:first-child {
      border-top: 0;
      padding-top: 0;
    }
    .detail-title {
      overflow-wrap: anywhere;
      color: #0f172a;
      font-size: 16px;
      font-weight: 800;
    }
    .detail-subtitle {
      overflow-wrap: anywhere;
      color: #334155;
      font-size: 14px;
      line-height: 1.4;
    }
    .detail-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-width: 0;
    }
    .detail-section .data-row {
      grid-template-columns: 68px minmax(0, 1fr);
      gap: 10px;
      align-items: start;
      padding: 7px 0;
    }
    .related-record-list {
      display: grid;
      gap: 6px;
      padding-top: 7px;
    }
    .related-record-button {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      padding: 8px 10px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
      color: #0f172a;
      text-align: left;
    }
    .related-record-button:hover,
    .related-record-button:focus-visible {
      border-color: #2563eb;
      background: #eff6ff;
    }
    .related-record-title {
      overflow-wrap: anywhere;
      font-size: 13px;
      font-weight: 800;
    }
    .related-record-subtitle {
      overflow-wrap: anywhere;
      color: #475569;
      font-size: 12px;
      line-height: 1.4;
    }
    .data-label {
      color: #64748b;
      font-size: 12px;
      font-weight: 700;
    }
    .data-value {
      overflow-wrap: anywhere;
      color: #0f172a;
      font-size: 14px;
    }
    .primary-picker {
      display: none;
      gap: 8px;
    }
    .primary-picker.is-visible {
      display: grid;
    }
    .primary-picker-title {
      color: #334155;
      font-size: 13px;
      font-weight: 800;
    }
    .primary-preview-list {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
      min-width: 0;
    }
    .primary-preview-button {
      position: relative;
      width: 100%;
      min-height: 0;
      padding: 0;
      overflow: hidden;
      border: 2px solid transparent;
      border-radius: 6px;
      background: #f8fafc;
    }
    .primary-preview-button.is-selected {
      border-color: #2563eb;
    }
    .primary-preview-button img {
      display: block;
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
    }
    .primary-preview-badge {
      position: absolute;
      inset-block-start: 4px;
      inset-inline-start: 4px;
      padding: 2px 6px;
      border-radius: 999px;
      background: #2563eb;
      color: #ffffff;
      font-size: 11px;
      font-weight: 800;
    }
    .asset-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
      gap: 8px;
    }
    .asset-item {
      display: grid;
      gap: 6px;
      min-width: 0;
      color: #475569;
      font-size: 12px;
    }
    .asset-item img {
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
    }
    .empty {
      padding: 10px 0;
      color: #64748b;
      font-size: 14px;
    }
    .result-list {
      display: grid;
      gap: 8px;
    }
    .result-row {
      display: grid;
      gap: 8px;
      padding: 10px 0;
      border-top: 1px solid #e2e8f0;
    }
    .result-row:first-child {
      border-top: 0;
    }
    .result-title {
      margin: 0;
      overflow-wrap: anywhere;
      color: #0f172a;
      font-weight: 800;
    }
    details {
      margin-top: 0;
    }
    summary {
      cursor: pointer;
      font-weight: 800;
    }
    pre {
      max-height: 520px;
      margin-top: 12px;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      border: 1px solid #d7dce2;
      border-radius: 8px;
      background: #111827;
      color: #e5e7eb;
      font-size: 12px;
    }
    @media (max-width: 760px) {
      body {
        padding: 12px;
      }
      main {
        max-width: 430px;
      }
      .user-flow-grid,
      .user-flow-row,
      .ops-grid {
        grid-template-columns: 1fr;
      }
      .screen-wide {
        grid-column: span 1;
      }
      .summary-grid {
        grid-template-columns: 1fr;
      }
      .screen,
      .user-flow-grid .screen {
        max-width: 100%;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1>로컬 MVP 화면 그리드</h1>
    <section class="workspace-section" aria-labelledby="user-screens-title">
      <h2 id="user-screens-title" class="section-heading">사용자 화면</h2>
      <div class="user-flow-grid">
        <div class="user-flow-row user-flow-primary">
          <section class="screen" aria-labelledby="upload-title">
            <h2 id="upload-title">업로드 화면</h2>
            <form id="upload-form">
              <label>
                로컬 사용자
                <input id="local-user" name="localUser" value="local-mvp" autocomplete="off">
              </label>
              <label>
                메모
                <textarea id="memo" name="memo" rows="4"></textarea>
              </label>
              <fieldset>
                <legend>감정</legend>
                <div class="choice-row" aria-label="감정 선택">
                <input id="emotion-joy" name="emotion" type="radio" value="joy" checked>
                <label class="choice" for="emotion-joy" title="기쁨">😊</label>
                <input id="emotion-calm" name="emotion" type="radio" value="calm">
                  <label class="choice" for="emotion-calm" title="평온">😐</label>
                  <input id="emotion-sad" name="emotion" type="radio" value="sad">
                  <label class="choice" for="emotion-sad" title="슬픔">😢</label>
                  <input id="emotion-angry" name="emotion" type="radio" value="angry">
                  <label class="choice" for="emotion-angry" title="화남">😠</label>
                  <input id="emotion-tired" name="emotion" type="radio" value="tired">
                  <label class="choice" for="emotion-tired" title="피곤">😴</label>
                </div>
              </fieldset>
              <fieldset>
              <legend>만족도</legend>
              <div class="choice-row" aria-label="만족도 선택">
                <input id="satisfaction-5" name="satisfaction" type="radio" value="5" checked>
                <label class="choice" for="satisfaction-5">5</label>
                <input id="satisfaction-4" name="satisfaction" type="radio" value="4">
                <label class="choice" for="satisfaction-4">4</label>
                <input id="satisfaction-3" name="satisfaction" type="radio" value="3">
                <label class="choice" for="satisfaction-3">3</label>
                <input id="satisfaction-2" name="satisfaction" type="radio" value="2">
                <label class="choice" for="satisfaction-2">2</label>
                <input id="satisfaction-1" name="satisfaction" type="radio" value="1">
                <label class="choice" for="satisfaction-1">1</label>
              </div>
            </fieldset>
              <label>
                방문 사진
                <input id="files" name="files" type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime" multiple required>
              </label>
              <div id="primary-picker" class="primary-picker" aria-live="polite"></div>
              <button id="submit-button" type="submit">업로드</button>
            </form>
          </section>

          <section class="screen" aria-labelledby="list-title">
            <h2 id="list-title">목록</h2>
            <div id="record-list" class="list"></div>
          </section>

          <section class="screen" aria-labelledby="detail-title">
            <h2 id="detail-title">상세</h2>
            <div id="record-detail"></div>
            <h3>업로드 파일</h3>
            <div id="asset-list" class="asset-grid"></div>
          </section>
        </div>

        <div class="user-flow-row user-flow-secondary">
          <section class="screen" aria-labelledby="analysis-title">
            <h2 id="analysis-title">AI 해석 화면</h2>
            <div id="analysis-detail"></div>
          </section>

          <section class="screen" aria-labelledby="relation-title">
            <h2 id="relation-title">유사 기록/재방문 화면</h2>
            <h3>임베딩 검색 결과</h3>
            <div id="embedding-meta" class="meta-row"></div>
            <div id="similar-results" class="result-list"></div>
          </section>

          <section class="screen" aria-labelledby="timeline-title">
            <h2 id="timeline-title">타임라인 후보 화면</h2>
            <div id="timeline-results" class="result-list"></div>
          </section>
        </div>
      </div>
    </section>

    <section class="workspace-section" aria-labelledby="ops-screens-title">
      <h2 id="ops-screens-title" class="section-heading">처리 데이터 확인 화면</h2>
      <div class="ops-grid">
        <section class="screen" aria-labelledby="status-title">
          <h2 id="status-title">처리 상태 화면</h2>
          <div id="status-board" class="status-board" aria-label="처리 상태">
            <div class="status-item" data-step="record">
              <span class="status-label">원본 기록</span>
              <span class="status-value">대기</span>
            </div>
            <div class="status-item" data-step="assets">
              <span class="status-label">사진 업로드</span>
              <span class="status-value">대기</span>
            </div>
            <div class="status-item" data-step="analysis">
              <span class="status-label">AI 해석</span>
              <span class="status-value">대기</span>
            </div>
            <div class="status-item" data-step="embedding">
              <span class="status-label">임베딩 검색</span>
              <span class="status-value">대기</span>
            </div>
            <div class="status-item" data-step="relations">
              <span class="status-label">유사 기록</span>
              <span class="status-value">대기</span>
            </div>
            <div class="status-item" data-step="storage">
              <span class="status-label">저장 JSON</span>
              <span class="status-value">대기</span>
            </div>
          </div>
          <div id="summary-grid" class="summary-grid" aria-label="저장 요약"></div>
        </section>

        <section class="screen" aria-labelledby="json-title">
          <details open>
            <summary id="json-title">저장 JSON 화면</summary>
            <pre id="result">대기 중</pre>
          </details>
        </section>
      </div>
    </section>
  </main>
  <script>
    const state = {
      records: [],
      analyses: new Map(),
      visitLabels: new Map(),
      selectedRecordId: null
    };

    const form = document.querySelector("#upload-form");
    const result = document.querySelector("#result");
    const submitButton = document.querySelector("#submit-button");
    const filesInput = document.querySelector("#files");
    const primaryPicker = document.querySelector("#primary-picker");
    const statusBoard = document.querySelector("#status-board");
    const summaryGrid = document.querySelector("#summary-grid");
    const recordList = document.querySelector("#record-list");
    const recordDetail = document.querySelector("#record-detail");
    const assetList = document.querySelector("#asset-list");
    const analysisDetail = document.querySelector("#analysis-detail");
    const embeddingMeta = document.querySelector("#embedding-meta");
    const similarResults = document.querySelector("#similar-results");
    const timelineResults = document.querySelector("#timeline-results");
    let selectedPrimaryFileIndex = null;
    let primaryPreviewUrls = [];

    function localUser() {
      return document.querySelector("#local-user").value || "local-mvp";
    }

    function resetStatus() {
      for (const value of statusBoard.querySelectorAll(".status-value")) {
        value.textContent = "대기";
        value.className = "status-value";
      }
      renderDefaultSummary();
      result.textContent = "처리 중";
    }

    function updateStep(step, text, stateName = "running") {
      const value = statusBoard.querySelector(`[data-step="${step}"] .status-value`);
      if (!value) {
        return;
      }
      value.textContent = text;
      value.className = `status-value is-${stateName}`;
    }

    function clearPrimaryPicker() {
      for (const url of primaryPreviewUrls) {
        URL.revokeObjectURL(url);
      }
      primaryPreviewUrls = [];
      selectedPrimaryFileIndex = null;
      primaryPicker.replaceChildren();
      primaryPicker.classList.remove("is-visible");
    }

    function imageFileEntries(files) {
      return files
        .map((file, index) => ({file, index}))
        .filter((item) => item.file.type.startsWith("image/"));
    }

    function renderPrimaryPicker(files, preferredIndex = null) {
      clearPrimaryPicker();
      const images = imageFileEntries(files);
      if (images.length === 0) {
        return;
      }

      const preferred = images.find((item) => item.index === preferredIndex);
      selectedPrimaryFileIndex = preferred ? preferred.index : images[0].index;
      primaryPicker.classList.add("is-visible");

      const title = document.createElement("div");
      title.className = "primary-picker-title";
      title.textContent = "대표사진 선택";
      const list = document.createElement("div");
      list.className = "primary-preview-list";

      for (const item of images) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "primary-preview-button";
        if (item.index === selectedPrimaryFileIndex) {
          button.classList.add("is-selected");
        }
        button.setAttribute("aria-label", `${item.file.name} 대표사진 선택`);
        button.addEventListener("click", () => renderPrimaryPicker(Array.from(filesInput.files), item.index));

        const image = document.createElement("img");
        const url = URL.createObjectURL(item.file);
        primaryPreviewUrls.push(url);
        image.src = url;
        image.alt = item.file.name;
        button.appendChild(image);

        if (item.index === selectedPrimaryFileIndex) {
          const badge = document.createElement("span");
          badge.className = "primary-preview-badge";
          badge.textContent = "대표";
          button.appendChild(badge);
        }
        list.appendChild(button);
      }
      primaryPicker.append(title, list);
    }

    function orderedUploadFiles(files) {
      if (selectedPrimaryFileIndex === null) {
        return files;
      }
      const primaryFile = files[selectedPrimaryFileIndex];
      if (!primaryFile || !primaryFile.type.startsWith("image/")) {
        return files;
      }
      return [primaryFile, ...files.filter((_, index) => index !== selectedPrimaryFileIndex)];
    }

    async function requestJson(url, options = {}) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const error = new Error(await response.text());
        error.status = response.status;
        throw error;
      }
      return response.json();
    }

    async function requestNoContent(url, options = {}) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const error = new Error(await response.text());
        error.status = response.status;
        throw error;
      }
    }

    async function optionalJson(url, options = {}) {
      try {
        return await requestJson(url, options);
      } catch (error) {
        if (error.status === 404) {
          return null;
        }
        throw error;
      }
    }

    function authHeaders(extra = {}) {
      return {"X-Local-User": localUser(), ...extra};
    }

    function metric(label, value) {
      const item = document.createElement("div");
      item.className = "metric";
      const title = document.createElement("b");
      title.textContent = label;
      const content = document.createElement("span");
      content.textContent = value || "-";
      item.append(title, content);
      return item;
    }

    function renderDefaultSummary() {
      summaryGrid.replaceChildren(
        metric("기록 ID", "-"),
        metric("AI 장면", "-"),
        metric("AI 요약", "-"),
        metric("방문 차수", "-")
      );
    }

    function renderSummary(record, analysis, embeddingResult) {
      summaryGrid.replaceChildren(
        metric("기록 ID", record.record_id),
        metric("AI 장면", analysis?.scene_type || "-"),
        metric("AI 요약", analysis?.summary || "-"),
        metric("방문 차수", state.visitLabels.get(record.record_id) || "-"),
        metric("임베딩", embeddingResult ? `${embeddingResult.embedding.provider} / ${embeddingResult.embedding.dimension}차원` : "-")
      );
    }

    function appendPill(parent, text) {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = text;
      parent.appendChild(pill);
    }

    function formatDate(value) {
      if (!value) {
        return "시간 없음";
      }
      return new Date(value).toLocaleString("ko-KR");
    }

    function candidateText(value) {
      if (!value) {
        return "";
      }
      if (Array.isArray(value)) {
        return value.map(candidateText).filter(Boolean).join(", ");
      }
      if (typeof value === "object") {
        return value.name || value.place || value.value || value.text || value.label || Object.values(value).map(candidateText).filter(Boolean).join(" ");
      }
      return String(value);
    }

    function analysisPlace(analysis) {
      const first = analysis?.place_candidates?.[0];
      return candidateText(first) || "";
    }

    function candidateField(value, keys) {
      if (!value) {
        return "";
      }
      if (Array.isArray(value)) {
        for (const item of value) {
          const text = candidateField(item, keys);
          if (text) {
            return text;
          }
        }
        return "";
      }
      if (typeof value === "object") {
        for (const key of keys) {
          if (value[key]) {
            return candidateText(value[key]);
          }
        }
        return candidateText(value);
      }
      return String(value);
    }

    function candidateScore(value) {
      if (!value || typeof value !== "object") {
        return 0;
      }
      for (const key of ["score", "confidence", "confidence_score", "probability"]) {
        const score = Number(value[key]);
        if (Number.isFinite(score)) {
          return score;
        }
      }
      return 0;
    }

    function stripMenuMeta(text) {
      return String(text || "")
        .replace(/(?:₩[ \t]*)?[0-9]{1,3}(?:,[0-9]{3})+원?/g, "")
        .replace(/[0-9]+[ \t]*(?:원|KRW|달러|USD)/gi, "")
        .replace(/[0-9]+[ \t]*(?:개|잔|병|캔|팩|세트|인분)/g, "")
        .replace(/^(?:[0-9]+(?:[.,][0-9]+)?[ \t]*)+/, "")
        .replace(/[ \t]{2,}/g, " ")
        .trim();
    }

    function extractAmountText(text) {
      const value = String(text || "");
      const match = value.match(/(?:₩[ \t]*)?[0-9]{1,3}(?:,[0-9]{3})+원?|[0-9]+[ \t]*(?:원|KRW|달러|USD)/i);
      return match ? match[0].replace(/[ \t]+/g, "") : "";
    }

    function formatAmountValue(amount, currency) {
      const numeric = Number(amount);
      if (Number.isFinite(numeric)) {
        if (!currency || String(currency).toUpperCase() === "KRW") {
          return `${numeric.toLocaleString("ko-KR")}원`;
        }
        return `${numeric.toLocaleString("ko-KR")} ${currency}`;
      }
      return candidateText(amount);
    }

    function amountText(value) {
      if (!value) {
        return "";
      }
      if (typeof value === "object") {
        if (value.amount !== undefined) {
          return formatAmountValue(value.amount, value.currency);
        }
        if (value.price !== undefined) {
          return formatAmountValue(value.price, value.currency);
        }
      }
      return extractAmountText(candidateText(value)) || candidateText(value);
    }

    function isMenuNameText(text) {
      const value = stripMenuMeta(text);
      return Boolean(value) && !/^[0-9.,]+$/.test(value);
    }

    function menuNameText(value) {
      if (!value) {
        return "";
      }
      if (typeof value === "object" && !Array.isArray(value)) {
        for (const key of ["menu", "item", "title", "name", "value", "text", "label"]) {
          if (value[key] !== undefined) {
            const text = stripMenuMeta(candidateText(value[key]));
            if (isMenuNameText(text)) {
              return text;
            }
          }
        }
      }
      const text = stripMenuMeta(candidateField(value, ["menu", "item", "title", "name", "value", "text", "label"]));
      return isMenuNameText(text) ? text : "";
    }

    function bestCandidate(value) {
      if (!Array.isArray(value) || value.length === 0) {
        return null;
      }
      return [...value].sort((a, b) => candidateScore(b) - candidateScore(a))[0];
    }

    function recordDateTimeValue(record) {
      return record.happened_at || record.created_at || "";
    }

    function compactDateTime(value) {
      if (!value) {
        return "";
      }
      const date = new Date(value);
      const dateText = date.toLocaleDateString("ko-KR", {
        month: "2-digit",
        day: "2-digit"
      });
      const timeText = date.toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
      });
      return `${dateText} ${timeText}`;
    }

    function detailDateTime(value) {
      if (!value) {
        return "";
      }
      const date = new Date(value);
      const dateText = date.toLocaleDateString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
      });
      const timeText = date.toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
      });
      return `${dateText} ${timeText}`;
    }

    function recordListTitle(record, analysis) {
      const placeName = candidateField(analysis?.place_candidates, ["name", "place_name", "title", "place", "value", "text", "label"]);
      const visitLabel = state.visitLabels.get(record.record_id);
      const visitCount = visitLabel && placeName && visitLabel.startsWith(placeName) ? visitLabel.replace(placeName, "").trim() : "";
      if (placeName && visitCount) {
        return `${placeName} · ${visitCount}`;
      }
      if (placeName) {
        return placeName;
      }

      const sceneType = analysis?.scene_type || "";
      if (sceneType) {
        return sceneType;
      }

      const activity = candidateField(analysis?.activity_candidates, ["name", "activity", "value", "text", "label"]);
      if (activity) {
        return activity;
      }

      return record.memo || "새 기록";
    }

    function recordListSubtitle(record, analysis) {
      const activity = candidateField(bestCandidate(analysis?.activity_candidates), ["name", "activity", "value", "text", "label"]);
      return activity || analysis?.summary || record.memo || "요약 없음";
    }

    function recordListTags(record, analysis) {
      const tags = [];
      const emotion = emotionIcon(record.emotion);
      if (emotion) {
        tags.push(emotion);
      }
      if (record.satisfaction_score) {
        tags.push(`${record.satisfaction_score}점`);
      }
      const menu = menuNameText(bestCandidate(analysis?.menu_candidates));
      if (menu) {
        tags.push(menu);
      }
      return tags;
    }

    function menuDetailText(analysis) {
      const menus = Array.isArray(analysis?.menu_candidates)
        ? [...analysis.menu_candidates].sort((a, b) => candidateScore(b) - candidateScore(a))
        : [];
      const amounts = Array.isArray(analysis?.amount_candidates)
        ? [...analysis.amount_candidates].sort((a, b) => candidateScore(b) - candidateScore(a))
        : [];
      const size = Math.max(menus.length, amounts.length);
      const items = [];
      for (let index = 0; index < size; index += 1) {
        const menu = menuNameText(menus[index]);
        const amount = amountText(menus[index]) || amountText(amounts[index]);
        const text = [menu, amount].filter(Boolean).join(" ");
        if (text) {
          items.push(text);
        }
      }
      return items.join(", ");
    }

    function candidateTexts(value, keys, limit = 3) {
      if (!Array.isArray(value)) {
        const text = candidateField(value, keys);
        return text ? [text] : [];
      }
      return [...value]
        .sort((a, b) => candidateScore(b) - candidateScore(a))
        .map((item) => candidateField(item, keys))
        .filter(Boolean)
        .slice(0, limit);
    }

    function joinedCandidates(value, keys, limit = 3) {
      return candidateTexts(value, keys, limit).join(", ");
    }

    function relationTypeLabel(value) {
      const labels = {
        similar_scene: "유사한 기록",
        same_place_candidate: "같은 장소 후보",
        similar_topic: "비슷한 주제",
        revisit_candidate: "다시 방문한 기록",
        timeline_candidate: "같은 흐름의 기록"
      };
      return labels[value] || value || "-";
    }

    function relatedRecordItems(relatedRecords, limit = 3) {
      return relatedRecords
        .filter((item) => item.record)
        .sort((a, b) => Number(b.relation?.similarity_score || 0) - Number(a.relation?.similarity_score || 0))
        .slice(0, limit);
    }

    function emotionIcon(value) {
      const icons = {
        joy: "😊",
        calm: "😐",
        sad: "😢",
        angry: "😠",
        tired: "😴"
      };
      return icons[value] || "";
    }

    function computeVisitLabels() {
      const counters = new Map();
      const sorted = [...state.records].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      state.visitLabels.clear();
      for (const record of sorted) {
        const place = analysisPlace(state.analyses.get(record.record_id));
        if (!place) {
          state.visitLabels.set(record.record_id, "장소 미확정");
          continue;
        }
        const count = (counters.get(place) || 0) + 1;
        counters.set(place, count);
        state.visitLabels.set(record.record_id, `${place} ${count}번째 방문`);
      }
    }

    function row(label, value) {
      const item = document.createElement("div");
      item.className = "data-row";
      const key = document.createElement("div");
      key.className = "data-label";
      key.textContent = label;
      const val = document.createElement("div");
      val.className = "data-value";
      val.textContent = value || "-";
      item.append(key, val);
      return item;
    }

    function detailSection(title, rows) {
      const visibleRows = rows.filter((item) => item.value);
      if (visibleRows.length === 0) {
        return null;
      }
      const section = document.createElement("section");
      section.className = "detail-section";
      section.setAttribute("aria-label", title);
      for (const item of visibleRows) {
        section.appendChild(row(item.label, item.value));
      }
      return section;
    }

    function detailRelatedRecords(items) {
      if (items.length === 0) {
        return null;
      }
      const list = document.createElement("div");
      list.className = "related-record-list";
      for (const item of items) {
        const relation = item.relation;
        const relatedRecord = item.record;
        const relatedAnalysis = state.analyses.get(relatedRecord.record_id);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "related-record-button";
        button.addEventListener("click", () => selectRecord(relatedRecord.record_id));

        const title = document.createElement("div");
        title.className = "related-record-title";
        title.textContent = recordListTitle(relatedRecord, relatedAnalysis);
        const subtitle = document.createElement("div");
        subtitle.className = "related-record-subtitle";
        subtitle.textContent = recordListSubtitle(relatedRecord, relatedAnalysis);
        const meta = document.createElement("div");
        meta.className = "meta-row";
        appendPill(meta, relationTypeLabel(relation.relation_type));
        button.append(title, subtitle, meta);
        list.appendChild(button);
      }
      return list;
    }

    function connectionSection(relatedRecords) {
      const items = relatedRecordItems(relatedRecords, 3);
      const section = detailSection("연관 기록", [
        {label: "연관 기록", value: `${items.length}건`}
      ]);
      const relatedList = detailRelatedRecords(items);
      if (section && relatedList) {
        section.appendChild(relatedList);
      }
      return section;
    }

    function renderDetailHero(record, analysis) {
      const hero = document.createElement("section");
      hero.className = "detail-hero";
      const title = document.createElement("div");
      title.className = "detail-title";
      title.textContent = recordListTitle(record, analysis);
      const subtitle = document.createElement("div");
      subtitle.className = "detail-subtitle";
      subtitle.textContent = recordListSubtitle(record, analysis);
      const tags = document.createElement("div");
      tags.className = "detail-tags";
      for (const tag of recordListTags(record, analysis)) {
        appendPill(tags, tag);
      }
      hero.append(title, subtitle, tags);
      return hero;
    }

    function clearSelectedRecordViews() {
      recordDetail.replaceChildren();
      assetList.replaceChildren();
      analysisDetail.replaceChildren();
      embeddingMeta.replaceChildren();
      similarResults.replaceChildren();
      timelineResults.replaceChildren();
      renderDefaultSummary();
      result.textContent = "기록이 삭제되었습니다.";
    }

    async function deleteRecord(recordId) {
      if (!window.confirm("이 기록을 삭제할까요?")) {
        return;
      }
      await requestNoContent(`/records/${recordId}`, {
        method: "DELETE",
        headers: authHeaders()
      });
      state.records = state.records.filter((record) => record.record_id !== recordId);
      state.analyses.delete(recordId);
      state.visitLabels.delete(recordId);
      if (state.selectedRecordId === recordId) {
        state.selectedRecordId = null;
        clearSelectedRecordViews();
      }
      computeVisitLabels();
      renderRecordList();
    }

    function renderRecordList() {
      recordList.replaceChildren();
      if (state.records.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "아직 기록이 없습니다.";
        recordList.appendChild(empty);
        return;
      }

      for (const record of state.records) {
        const button = document.createElement("article");
        button.className = "record-button";
        button.tabIndex = 0;
        button.setAttribute("role", "button");
        if (record.record_id === state.selectedRecordId) {
          button.classList.add("is-selected");
        }
        button.addEventListener("click", () => selectRecord(record.record_id));
        button.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            selectRecord(record.record_id);
          }
        });

        const analysis = state.analyses.get(record.record_id);
        const titleText = recordListTitle(record, analysis);
        const subtitleText = recordListSubtitle(record, analysis);
        const tags = recordListTags(record, analysis);
        button.setAttribute("aria-label", `기록 선택: ${titleText}`);

        const headline = document.createElement("div");
        headline.className = "record-headline";
        const title = document.createElement("div");
        title.className = "record-title";
        title.textContent = titleText;
        const dateTime = document.createElement("time");
        dateTime.className = "record-datetime";
        dateTime.textContent = compactDateTime(recordDateTimeValue(record));
        headline.append(title, dateTime);
        const memo = document.createElement("div");
        memo.className = "record-memo";
        memo.textContent = subtitleText;
        const tagRow = document.createElement("div");
        tagRow.className = "record-tags";
        for (const tag of tags) {
          appendPill(tagRow, tag);
        }
        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "record-delete";
        deleteButton.textContent = "X";
        deleteButton.title = "기록 삭제";
        deleteButton.setAttribute("aria-label", `${titleText} 삭제`);
        deleteButton.addEventListener("click", async (event) => {
          event.stopPropagation();
          try {
            await deleteRecord(record.record_id);
          } catch (error) {
            result.textContent = error.message;
          }
        });
        button.append(deleteButton, headline, memo, tagRow);
        recordList.appendChild(button);
      }
    }

    function renderRecordDetail(record, assets, analysis, relations, timelineCandidates, relatedRecords) {
      const sections = [
        renderDetailHero(record, analysis),
        detailSection("상세 정보", [
          {label: "메모", value: record.memo},
          {label: "시간", value: detailDateTime(recordDateTimeValue(record))},
          {label: "메뉴", value: menuDetailText(analysis)},
          {label: "태그", value: candidateText(analysis?.tags)}
        ]),
        connectionSection(relatedRecords || [])
      ].filter(Boolean);
      recordDetail.replaceChildren(...sections);

      assetList.replaceChildren();
      if (assets.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "업로드된 파일이 없습니다.";
        assetList.appendChild(empty);
        return;
      }
      for (const asset of assets) {
        const item = document.createElement("a");
        item.className = "asset-item";
        item.href = `/records/${asset.record_id}/assets/${asset.asset_id}/file`;
        item.target = "_blank";
        if (asset.content_type.startsWith("image/")) {
          const img = document.createElement("img");
          img.src = item.href;
          img.alt = asset.content_type;
          item.appendChild(img);
        }
        const caption = document.createElement("span");
        caption.textContent = `${asset.asset_type} / ${Math.round((asset.byte_size || 0) / 1024)}KB`;
        item.appendChild(caption);
        assetList.appendChild(item);
      }
    }

    function renderAnalysis(analysis) {
      analysisDetail.replaceChildren();
      if (!analysis) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "AI 해석 결과가 없습니다.";
        analysisDetail.appendChild(empty);
        return;
      }

      analysisDetail.replaceChildren(
        row("장면 유형", analysis.scene_type),
        row("요약", analysis.summary),
        row("장소 후보", candidateText(analysis.place_candidates)),
        row("방문 시간 후보", candidateText(analysis.visit_time_candidates)),
        row("메뉴 후보", candidateText(analysis.menu_candidates)),
        row("활동 후보", candidateText(analysis.activity_candidates)),
        row("금액 후보", candidateText(analysis.amount_candidates)),
        row("태그", candidateText(analysis.tags))
      );
    }

    async function fetchRelatedRecords(relations, limit = 3) {
      const topRelations = [...relations]
        .sort((a, b) => Number(b.similarity_score || 0) - Number(a.similarity_score || 0))
        .slice(0, limit);
      return Promise.all(topRelations.map(async (relation) => {
        const record = await optionalJson(`/records/${relation.target_record_id}`, {
          headers: authHeaders()
        });
        return {relation, record};
      }));
    }

    function renderSimilarResults(relations, relatedRecords, storageJson) {
      similarResults.replaceChildren();
      embeddingMeta.replaceChildren();
      const embedding = storageJson?.data?.record_embeddings?.[0];
      if (embedding) {
        appendPill(embeddingMeta, `provider ${embedding.provider}`);
        appendPill(embeddingMeta, `model ${embedding.model}`);
        appendPill(embeddingMeta, `${embedding.dimension}차원`);
      } else {
        appendPill(embeddingMeta, "임베딩 없음");
      }
      appendPill(embeddingMeta, `유사 기록 ${relations.length}건`);

      if (relations.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "아직 비교할 이전 기록이 없습니다.";
        similarResults.appendChild(empty);
        return;
      }

      for (const item of relatedRecords) {
        const relation = item.relation;
        const relatedRecord = item.record;
        const relatedAnalysis = relatedRecord ? state.analyses.get(relatedRecord.record_id) : null;
        const article = document.createElement("article");
        article.className = "result-row";
        const title = document.createElement("p");
        title.className = "result-title";
        title.textContent = relatedRecord ? recordListTitle(relatedRecord, relatedAnalysis) : relation.target_record_id;
        const subtitle = document.createElement("div");
        subtitle.className = "related-record-subtitle";
        subtitle.textContent = relatedRecord ? recordListSubtitle(relatedRecord, relatedAnalysis) : "";
        const meta = document.createElement("div");
        meta.className = "meta-row";
        appendPill(meta, relationTypeLabel(relation.relation_type));
        article.append(title, subtitle, meta);
        similarResults.appendChild(article);
      }
    }

    function renderTimeline(candidates) {
      timelineResults.replaceChildren();
      if (candidates.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "생성된 타임라인 후보가 없습니다.";
        timelineResults.appendChild(empty);
        return;
      }

      for (const candidate of candidates) {
        const article = document.createElement("article");
        article.className = "result-row";
        const title = document.createElement("p");
        title.className = "result-title";
        title.textContent = candidate.grouping_key;
        const meta = document.createElement("div");
        meta.className = "meta-row";
        appendPill(meta, candidate.timeline_type);
        appendPill(meta, `신뢰도 ${Number(candidate.confidence_score).toFixed(2)}`);
        article.append(title, meta);
        timelineResults.appendChild(article);
      }
    }

    async function loadRecords() {
      const payload = await requestJson("/records", {headers: authHeaders()});
      state.records = payload.records;
      state.analyses.clear();
      await Promise.all(state.records.map(async (record) => {
        const analysis = await optionalJson(`/records/${record.record_id}/ai-analysis`, {
          headers: authHeaders()
        });
        if (analysis) {
          state.analyses.set(record.record_id, analysis);
        }
      }));
      computeVisitLabels();
      renderRecordList();
    }

    async function selectRecord(recordId) {
      state.selectedRecordId = recordId;
      renderRecordList();
      const [record, assetsPayload, analysis, relationsPayload, timelinePayload, storageJson] = await Promise.all([
        requestJson(`/records/${recordId}`, {headers: authHeaders()}),
        requestJson(`/records/${recordId}/assets`, {headers: authHeaders()}),
        optionalJson(`/records/${recordId}/ai-analysis`, {headers: authHeaders()}),
        requestJson(`/records/${recordId}/relations`, {headers: authHeaders()}),
        requestJson(`/records/${recordId}/timeline-candidates`, {headers: authHeaders()}),
        optionalJson(`/records/${recordId}/storage-json`, {headers: authHeaders()})
      ]);
      if (analysis) {
        state.analyses.set(recordId, analysis);
        computeVisitLabels();
      }
      renderRecordList();
      const relatedRecords = await fetchRelatedRecords(relationsPayload.relations);
      renderRecordDetail(record, assetsPayload.assets, analysis, relationsPayload.relations, timelinePayload.timeline_candidates, relatedRecords);
      renderAnalysis(analysis);
      renderSimilarResults(relationsPayload.relations, relatedRecords, storageJson);
      renderTimeline(timelinePayload.timeline_candidates);
      result.textContent = JSON.stringify(storageJson || {detail: "storage-json 없음"}, null, 2);
      const latestEmbedding = storageJson?.data?.record_embeddings?.[0];
      renderSummary(record, analysis, latestEmbedding ? {embedding: latestEmbedding} : null);
    }

    async function refreshAfterUpload(recordId) {
      await loadRecords();
      await selectRecord(recordId);
    }

    filesInput.addEventListener("change", () => {
      renderPrimaryPicker(Array.from(filesInput.files));
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      resetStatus();
      submitButton.disabled = true;

      const emotionInput = document.querySelector("input[name='emotion']:checked");
      const satisfactionInput = document.querySelector("input[name='satisfaction']:checked");
      const recordPayload = {
        memo: document.querySelector("#memo").value || null,
        emotion: emotionInput ? emotionInput.value : null,
        satisfaction_score: satisfactionInput ? Number(satisfactionInput.value) : null
      };

      try {
        updateStep("record", "저장 중");
        const record = await requestJson("/records", {
          method: "POST",
          headers: authHeaders({"Content-Type": "application/json"}),
          body: JSON.stringify(recordPayload)
        });
        updateStep("record", "저장 완료", "done");

        const selectedFiles = Array.from(filesInput.files);
        if (selectedFiles.length === 0) {
          throw new Error("업로드할 파일을 선택하세요.");
        }
        const files = orderedUploadFiles(selectedFiles);
        updateStep("assets", `${files.length}개 저장 중`);
        for (const file of files) {
          const formData = new FormData();
          formData.append("file", file);
          await requestJson(`/records/${record.record_id}/assets`, {
            method: "POST",
            headers: authHeaders(),
            body: formData
          });
        }
        updateStep("assets", `${files.length}개 저장 완료`, "done");

        updateStep("analysis", "해석 중");
        const analysis = await requestJson(`/records/${record.record_id}/ai-analysis`, {
          method: "POST",
          headers: authHeaders()
        });
        state.analyses.set(record.record_id, analysis);
        updateStep("analysis", "해석 완료", "done");

        updateStep("embedding", "검색 중");
        const embeddingResult = await requestJson(`/records/${record.record_id}/embedding`, {
          method: "POST",
          headers: authHeaders()
        });
        updateStep("embedding", `${embeddingResult.embedding.dimension}차원 생성`, "done");

        updateStep("relations", "구성 중");
        updateStep("relations", `${embeddingResult.relations.length}건`, "done");

        updateStep("storage", "조회 중");
        await refreshAfterUpload(record.record_id);
        updateStep("storage", "조회 완료", "done");
      } catch (error) {
        for (const value of statusBoard.querySelectorAll(".status-value.is-running")) {
          value.textContent = "실패";
          value.className = "status-value is-failed";
        }
        result.textContent = error.message;
      } finally {
        submitButton.disabled = false;
      }
    });

    renderDefaultSummary();
    loadRecords().catch((error) => {
      recordList.textContent = error.message;
    });
  </script>
</body>
</html>
"""
