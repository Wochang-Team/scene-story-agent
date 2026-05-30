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
    .ops-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(260px, 1fr));
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
      grid-column: 1 / -1;
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
    .status-curl {
      display: none;
      grid-column: 1 / -1;
      min-width: 0;
      margin: -2px 0 0;
      padding: 6px 8px;
      overflow-x: auto;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
      color: #334155;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      line-height: 1.4;
      white-space: pre;
    }
    .status-curl.is-visible {
      display: block;
    }
    .status-detail {
      grid-column: 1 / -1;
      min-width: 0;
      color: #64748b;
      font-size: 12px;
      line-height: 1.4;
      overflow-wrap: anywhere;
    }
    .status-token {
      display: none;
      grid-column: 1 / -1;
      min-width: 0;
      color: #64748b;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.4;
    }
    .status-token.is-visible {
      display: block;
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
    .record-content {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      row-gap: 10px;
      column-gap: 0;
      align-items: start;
      min-width: 0;
    }
    .record-content.has-thumbnail {
      grid-template-columns: 64px minmax(0, 1fr);
      column-gap: 10px;
    }
    .record-copy {
      display: grid;
      gap: 6px;
      min-width: 0;
    }
    .record-thumbnail {
      width: 64px;
      height: 64px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
      object-fit: cover;
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
      grid-template-columns: minmax(0, 1fr);
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
    .record-content > .record-tags {
      grid-column: 1 / -1;
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
      padding: 10px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #ffffff;
      color: #0f172a;
      text-align: left;
      cursor: pointer;
    }
    .related-record-button:hover,
    .related-record-button:focus-visible {
      border-color: #2563eb;
      background: #eff6ff;
    }
    .data-label {
      display: inline-flex;
      gap: 4px;
      align-items: center;
      color: #64748b;
      font-size: 12px;
      font-weight: 700;
    }
    .data-help {
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      line-height: 1;
      cursor: help;
    }
    .data-help::after {
      position: absolute;
      z-index: 20;
      inset-block-end: calc(100% + 6px);
      inset-inline-start: 0;
      width: max-content;
      max-width: 240px;
      box-sizing: border-box;
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      background: #0f172a;
      color: #ffffff;
      content: attr(data-tooltip);
      font-size: 12px;
      font-weight: 500;
      line-height: 1.35;
      opacity: 0;
      pointer-events: none;
      transform: translateY(2px);
      transition: opacity 120ms ease, transform 120ms ease;
      white-space: normal;
      overflow-wrap: break-word;
    }
    .data-help:hover::after,
    .data-help:focus-visible::after {
      opacity: 1;
      transform: translateY(0);
    }
    .data-value {
      overflow-wrap: anywhere;
      color: #0f172a;
      font-size: 14px;
    }
    .data-json {
      display: block;
      max-height: 220px;
      overflow: auto;
      white-space: pre-wrap;
      color: #0f172a;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      line-height: 1.45;
    }
    .detail-menu-list {
      display: grid;
      gap: 4px;
      min-width: 0;
    }
    .detail-pill-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-width: 0;
    }
    .detail-memo-editor {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 6px;
      align-items: center;
      min-width: 0;
    }
    .detail-memo-text {
      overflow-wrap: anywhere;
      line-height: 1.45;
    }
    .detail-memo-text.is-empty {
      color: #94a3b8;
    }
    .detail-memo-edit {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      inline-size: 22px;
      block-size: 22px;
      min-height: 22px;
      padding: 0;
      border: 1px solid #e2e8f0;
      border-radius: 999px;
      background: #f8fafc;
      font-size: 12px;
      line-height: 1;
      cursor: pointer;
    }
    .detail-memo-input {
      width: 100%;
      min-width: 0;
      min-height: 32px;
      box-sizing: border-box;
      padding: 5px 8px;
      border: 1px solid #94a3b8;
      border-radius: 6px;
      font: inherit;
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
      padding: 0;
      border: 0;
      background: transparent;
      color: #475569;
      font-size: 12px;
      text-align: left;
      cursor: pointer;
    }
    .asset-item img {
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
    }
    .asset-item:hover img,
    .asset-item:focus-visible img {
      border-color: #2563eb;
      outline: 2px solid #dbeafe;
      outline-offset: 1px;
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
    .result-card {
      padding: 10px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #f8fafc;
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
    .data-item-title {
      margin: 0;
      color: #0f172a;
      font-size: 13px;
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

      </div>
    </section>

    <section class="workspace-section" aria-labelledby="ops-screens-title">
      <h2 id="ops-screens-title" class="section-heading">처리 데이터 확인 화면</h2>
      <div class="ops-grid">
        <section class="screen" aria-labelledby="status-title">
          <h2 id="status-title">처리 상태 화면</h2>
          <div id="status-board" class="status-board" aria-label="처리 상태">
            <div class="status-item" data-step="record">
              <span class="status-label">원본 기록 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: POST /records</span>
              <span class="status-detail">처리: 기록 생성, 후속 처리 작업 등록</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="assets">
              <span class="status-label">원본 파일 업로드</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: POST /records/{record_id}/assets</span>
              <span class="status-detail">처리: 업로드 파일 저장</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="analysis">
              <span class="status-label">AI 해석 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: POST /records/{record_id}/ai-analysis</span>
              <span class="status-detail">처리: AI 해석 결과 저장</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="thumbnail">
              <span class="status-label">썸네일 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: 별도 API 없음</span>
              <span class="status-detail">처리: AI 해석 요청 중 서버 내부 이미지 처리</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="embedding">
              <span class="status-label">임베딩 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: POST /records/{record_id}/embedding</span>
              <span class="status-detail">처리: 임베딩 벡터 저장</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="relations">
              <span class="status-label">연관 기록 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: 별도 API 없음</span>
              <span class="status-detail">처리: 임베딩 요청 중 연관 후보 계산</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="timeline">
              <span class="status-label">타임라인 후보 저장</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: 별도 API 없음</span>
              <span class="status-detail">처리: 임베딩 요청 중 타임라인 후보 계산</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
            <div class="status-item" data-step="storage">
              <span class="status-label">저장 JSON 조회</span>
              <span class="status-value">대기</span>
              <span class="status-detail">호출: GET /records/{record_id}/storage-json</span>
              <span class="status-detail">처리: 저장 데이터 조회</span>
              <code class="status-curl"></code>
              <span class="status-token"></span>
            </div>
          </div>
        </section>

        <section class="screen" aria-labelledby="analysis-title">
          <h2 id="analysis-title">AI 해석 데이터</h2>
          <div id="analysis-detail"></div>
        </section>

        <section class="screen" aria-labelledby="relation-title">
          <h2 id="relation-title">임베딩/연관 데이터</h2>
          <div id="embedding-meta" class="meta-row"></div>
          <div id="similar-results" class="result-list"></div>
        </section>

        <section class="screen" aria-labelledby="timeline-title">
          <h2 id="timeline-title">타임라인 후보 데이터</h2>
          <div id="timeline-results" class="result-list"></div>
        </section>

        <section class="screen screen-wide" aria-labelledby="json-title">
          <details open>
            <summary id="json-title">저장 JSON 데이터</summary>
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
      assets: new Map(),
      assetUrls: new Map(),
      visitLabels: new Map(),
      selectedRecordId: null
    };

    const form = document.querySelector("#upload-form");
    const result = document.querySelector("#result");
    const submitButton = document.querySelector("#submit-button");
    const filesInput = document.querySelector("#files");
    const primaryPicker = document.querySelector("#primary-picker");
    const statusBoard = document.querySelector("#status-board");
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
      for (const curl of statusBoard.querySelectorAll(".status-curl")) {
        curl.textContent = "";
        curl.classList.remove("is-visible");
      }
      for (const token of statusBoard.querySelectorAll(".status-token")) {
        token.textContent = "";
        token.classList.remove("is-visible");
      }
      result.textContent = "처리 중";
    }

    function shellQuote(value) {
      return `'${String(value).replace(/'/g, "'\\''")}'`;
    }

    function curlCommand(url, options = {}) {
      const method = options.method || "GET";
      const headers = options.headers || authHeaders();
      const parts = ["curl"];
      if (method !== "GET") {
        parts.push("-X", method);
      }
      parts.push(shellQuote(new URL(url, window.location.origin).href));
      for (const [key, value] of Object.entries(headers)) {
        parts.push("-H", shellQuote(`${key}: ${value}`));
      }
      if (options.json !== undefined) {
        parts.push("-d", shellQuote(JSON.stringify(options.json)));
      }
      if (options.fileName) {
        parts.push("-F", shellQuote(`file=@${options.fileName}`));
      }
      return parts.join(" ");
    }

    function tokenNumber(value) {
      const number = Number(value);
      return Number.isFinite(number) ? number.toLocaleString("ko-KR") : "-";
    }

    function tokenUsageText(payload, force = false) {
      const usage = payload?.raw_response_ref?.token_usage || payload?.token_usage || payload?.usage || payload?.usageMetadata;
      if (!usage) {
        return force ? "토큰 사용 - · 남은 토큰 -" : "";
      }
      const used = usage.used_tokens ?? usage.total_tokens ?? usage.totalTokenCount;
      const remaining = usage.remaining_tokens ?? usage.remainingTokens ?? usage.remainingTokenCount;
      const input = usage.input_tokens ?? usage.inputTokens ?? usage.promptTokenCount;
      const output = usage.output_tokens ?? usage.outputTokens ?? usage.candidatesTokenCount;
      const detail = [];
      if (input !== undefined) {
        detail.push(`입력 ${tokenNumber(input)}`);
      }
      if (output !== undefined) {
        detail.push(`출력 ${tokenNumber(output)}`);
      }
      const suffix = detail.length > 0 ? ` (${detail.join(" · ")})` : "";
      return `토큰 사용 ${tokenNumber(used)}${suffix} · 남은 토큰 ${tokenNumber(remaining)}`;
    }

    function updateStep(step, text, stateName = "running", curlText = "", tokenText = "") {
      const item = statusBoard.querySelector(`[data-step="${step}"]`);
      const value = item?.querySelector(".status-value");
      if (!value) {
        return;
      }
      value.textContent = text;
      value.className = `status-value is-${stateName}`;
      const curl = item.querySelector(".status-curl");
      if (curlText && curl) {
        curl.textContent = curlText;
        curl.classList.add("is-visible");
      }
      const token = item.querySelector(".status-token");
      if (tokenText && token) {
        token.textContent = tokenText;
        token.classList.add("is-visible");
      }
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

    function appendPill(parent, text) {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = text;
      parent.appendChild(pill);
    }

    function appendUniquePill(parent, text) {
      const value = String(text || "").trim();
      if (!value) {
        return;
      }
      const exists = Array.from(parent.children).some((child) => child.textContent === value);
      if (!exists) {
        appendPill(parent, value);
      }
    }

    function embeddingModel(storageJson) {
      return storageJson?.data?.record_embeddings?.[0]?.model || "";
    }

    function assetFilePath(asset) {
      return `/records/${asset.record_id}/assets/${asset.asset_id}/file`;
    }

    function representativeAsset(assets) {
      const images = (assets || []).filter((asset) => asset.content_type?.startsWith("image/"));
      return images.find((asset) => asset.asset_type === "thumbnail") || images[0] || null;
    }

    async function assetObjectUrl(asset) {
      if (!asset) {
        return "";
      }
      if (state.assetUrls.has(asset.asset_id)) {
        return state.assetUrls.get(asset.asset_id);
      }
      const response = await fetch(assetFilePath(asset), {headers: authHeaders()});
      if (!response.ok) {
        return "";
      }
      const url = URL.createObjectURL(await response.blob());
      state.assetUrls.set(asset.asset_id, url);
      return url;
    }

    function loadRecordThumbnail(content, asset, alt) {
      if (!asset) {
        return;
      }
      assetObjectUrl(asset).then((url) => {
        if (url) {
          const image = document.createElement("img");
          image.className = "record-thumbnail";
          image.alt = alt;
          image.src = url;
          content.prepend(image);
          content.classList.add("has-thumbnail");
        }
      });
    }

    function uploadAssetItems(assets) {
      const originals = assets.filter((asset) => asset.asset_type !== "thumbnail");
      const thumbnails = assets.filter((asset) => asset.asset_type === "thumbnail");
      return originals.map((asset, index) => ({
        original: asset,
        preview: asset.content_type?.startsWith("image/") ? (thumbnails[index] || asset) : null
      }));
    }

    async function openOriginalAsset(asset) {
      const viewer = window.open("about:blank", "_blank");
      if (!viewer) {
        result.textContent = "새 창을 열 수 없습니다.";
        return;
      }
      const url = await assetObjectUrl(asset);
      if (!url) {
        viewer.close();
        result.textContent = "원본 파일을 불러오지 못했습니다.";
        return;
      }
      viewer.location.href = url;
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

    function userMemoText(record) {
      return String(record?.memo || "").trim();
    }

    function memoDisplayText(record) {
      const memo = userMemoText(record);
      return memo ? `📝 ${memo}` : "";
    }

    function bestActivityText(analysis) {
      return candidateField(bestCandidate(analysis?.activity_candidates), ["name", "activity", "value", "text", "label"]);
    }

    function activityDisplayText(analysis) {
      return bestActivityText(analysis) || analysis?.summary || "";
    }

    function recordListSubtitle(record, analysis) {
      return memoDisplayText(record) || activityDisplayText(analysis) || "요약 없음";
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

    function createRecordListContent(record, analysis, options = {}) {
      const extraTags = options.extraTags || [];
      const titleText = recordListTitle(record, analysis);
      const subtitleText = recordListSubtitle(record, analysis);
      const tags = [...(options.includeRecordTags === false ? [] : recordListTags(record, analysis)), ...extraTags];
      const content = document.createElement("div");
      content.className = "record-content";
      const thumbnailAsset = representativeAsset(state.assets.get(record.record_id));
      const copy = document.createElement("div");
      copy.className = "record-copy";
      const headline = document.createElement("div");
      headline.className = "record-headline";
      const title = document.createElement("div");
      title.className = "record-title";
      title.textContent = titleText;
      const dateTime = document.createElement("time");
      dateTime.className = "record-datetime";
      dateTime.textContent = compactDateTime(recordDateTimeValue(record));
      headline.appendChild(title);
      const memo = document.createElement("div");
      memo.className = "record-memo";
      memo.textContent = subtitleText;
      const tagRow = document.createElement("div");
      tagRow.className = "record-tags";
      for (const tag of tags) {
        appendPill(tagRow, tag);
      }
      copy.append(headline, memo, dateTime);
      content.append(copy, tagRow);
      loadRecordThumbnail(content, thumbnailAsset, titleText);
      return {content, titleText};
    }

    function menuDetailItems(analysis) {
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
      return items;
    }

    function menuDetailText(analysis) {
      return menuDetailItems(analysis).join(", ");
    }

    function menuDetailList(analysis) {
      const items = menuDetailItems(analysis);
      if (items.length === 0) {
        return null;
      }
      const list = document.createElement("div");
      list.className = "detail-menu-list";
      for (const item of items) {
        const line = document.createElement("div");
        line.textContent = item;
        list.appendChild(line);
      }
      return list;
    }

    function tagDetailList(tags) {
      const labels = candidateTexts(tags, ["name", "tag", "value", "text", "label"], 20);
      if (labels.length === 0) {
        return null;
      }
      const list = document.createElement("div");
      list.className = "detail-pill-list";
      for (const label of labels) {
        appendPill(list, label);
      }
      return list;
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

    function relationScore(relation) {
      return Number(relation?.similarity_score || 0);
    }

    function groupedRelatedRelations(relations, limit = 3) {
      const grouped = new Map();
      for (const relation of [...relations].sort((a, b) => relationScore(b) - relationScore(a))) {
        const key = relation.target_record_id;
        if (!key) {
          continue;
        }
        if (!grouped.has(key)) {
          grouped.set(key, {relation, relations: [relation]});
        } else {
          grouped.get(key).relations.push(relation);
        }
      }
      return [...grouped.values()]
        .sort((a, b) => relationScore(b.relation) - relationScore(a.relation))
        .slice(0, limit);
    }

    function relationLabels(relations) {
      const seen = new Set();
      const labels = [];
      for (const relation of relations || []) {
        if (!relation) {
          continue;
        }
        const label = relationTypeLabel(relation.relation_type);
        if (!seen.has(label)) {
          seen.add(label);
          labels.push(label);
        }
      }
      return labels;
    }

    function relationScoreLabel(relation) {
      const score = Number(relation?.similarity_score);
      return Number.isFinite(score) && score > 0 ? `${Math.round(score * 100)}%` : "";
    }

    function relationLabelsWithScores(relations) {
      const labelsByType = new Map();
      for (const relation of relations || []) {
        if (!relation) {
          continue;
        }
        const label = relationTypeLabel(relation.relation_type);
        const score = Number(relation.similarity_score);
        const current = labelsByType.get(label) || 0;
        labelsByType.set(label, Number.isFinite(score) && score > current ? score : current);
      }
      return [...labelsByType.entries()].map(([label, score]) => {
        const scoreLabel = relationScoreLabel({similarity_score: score});
        return scoreLabel ? `${label} ${scoreLabel}` : label;
      });
    }

    function relatedRecordItems(relatedRecords, limit = 3) {
      const grouped = new Map();
      for (const item of relatedRecords
        .filter((item) => item.record)
        .sort((a, b) => relationScore(b.relation) - relationScore(a.relation))) {
        const key = item.record.record_id;
        const relations = item.relations || [item.relation].filter(Boolean);
        if (!grouped.has(key)) {
          grouped.set(key, {...item, relations});
        } else {
          grouped.get(key).relations.push(...relations);
        }
      }
      return [...grouped.values()].slice(0, limit);
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

    const dataHelpText = {
      place_candidates: "AI가 사진과 메모에서 추정한 장소 후보입니다.",
      visit_time_candidates: "AI가 영수증, 화면 정보, 사진 맥락에서 추정한 방문 시간 후보입니다.",
      menu_candidates: "AI가 인식한 메뉴 또는 구매 항목 후보입니다.",
      amount_candidates: "AI가 인식한 가격, 결제금액, 금액 후보입니다.",
      activity_candidates: "AI가 장면에서 추정한 사용자의 활동 후보입니다.",
      similar_record_candidates: "AI가 유사하다고 판단한 기록 후보입니다.",
      revisit_candidates: "AI가 같은 장소 재방문 가능성이 있다고 본 후보입니다.",
      timeline_candidates: "AI가 같은 흐름이나 묶음으로 볼 수 있다고 판단한 후보입니다.",
      tags: "AI가 기록을 설명하기 위해 생성한 키워드입니다.",
      raw_response_ref: "AI 원본 응답이나 참조 정보를 추적하기 위한 값입니다.",
      relation_type: "연관 유형입니다. 유사 기록, 재방문 후보 같은 관계 종류를 뜻합니다.",
      target_record_id: "현재 기록과 연결된 대상 기록의 ID입니다.",
      similarity_score: "두 기록이 얼마나 비슷한지 계산한 점수입니다.",
      decision_status: "이 관계를 화면이나 처리 과정에서 사용할지 판단한 상태입니다.",
      reasons: "이 관계가 만들어진 근거 데이터입니다.",
      timeline_type: "타임라인 후보의 묶음 유형입니다.",
      grouping_key: "타임라인으로 묶을 때 사용하는 기준값입니다.",
      confidence_score: "해당 후보를 신뢰할 수 있는 정도를 나타내는 점수입니다.",
      reason: "타임라인 후보가 만들어진 근거입니다.",
      created_at: "해당 데이터가 생성된 시간입니다."
    };

    function row(label, value) {
      const item = document.createElement("div");
      item.className = "data-row";
      const key = document.createElement("div");
      key.className = "data-label";
      const labelText = document.createElement("span");
      labelText.textContent = label;
      key.appendChild(labelText);
      const helpText = dataHelpText[label];
      if (helpText) {
        const help = document.createElement("span");
        help.className = "data-help";
        help.tabIndex = 0;
        help.textContent = "❓";
        help.dataset.tooltip = helpText;
        help.setAttribute("aria-label", `${label} 설명: ${helpText}`);
        key.appendChild(help);
      }
      const val = document.createElement("div");
      val.className = "data-value";
      if (value instanceof Node) {
        val.appendChild(value);
      } else {
        val.textContent = value || "-";
      }
      item.append(key, val);
      return item;
    }

    function dataJson(value) {
      if (value === undefined || value === null) {
        return "";
      }
      if (Array.isArray(value) && value.length === 0) {
        return "";
      }
      if (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0) {
        return "";
      }
      const code = document.createElement("code");
      code.className = "data-json";
      code.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
      return code;
    }

    function numberText(value, digits = 4) {
      const numeric = Number(value);
      return Number.isFinite(numeric) ? numeric.toFixed(digits) : "";
    }

    function dataItemTitle(prefix, index, summary) {
      const title = document.createElement("p");
      title.className = "data-item-title";
      title.textContent = `${prefix} ${index + 1}${summary ? ` · ${summary}` : ""}`;
      return title;
    }

    function replaceRecord(record) {
      const index = state.records.findIndex((item) => item.record_id === record.record_id);
      if (index >= 0) {
        state.records[index] = record;
      } else {
        state.records.unshift(record);
      }
      computeVisitLabels();
      renderRecordList();
    }

    async function saveRecordMemo(record, value, input) {
      const nextMemo = value.trim();
      if (nextMemo === userMemoText(record)) {
        await selectRecord(record.record_id);
        return;
      }
      input.disabled = true;
      const updated = await requestJson(`/records/${record.record_id}`, {
        method: "PATCH",
        headers: authHeaders({"Content-Type": "application/json"}),
        body: JSON.stringify({memo: nextMemo || null})
      });
      replaceRecord(updated);
      await selectRecord(updated.record_id);
      result.textContent = "메모가 저장되었습니다.";
    }

    function memoDetailEditor(record) {
      const wrapper = document.createElement("div");
      wrapper.className = "detail-memo-editor";
      const text = document.createElement("span");
      text.className = "detail-memo-text";
      const memo = userMemoText(record);
      text.textContent = memo || "메모 없음";
      if (!memo) {
        text.classList.add("is-empty");
      }
      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.className = "detail-memo-edit";
      editButton.textContent = "✏️";
      editButton.title = "메모 수정";
      editButton.setAttribute("aria-label", "메모 수정");
      editButton.addEventListener("click", () => {
        const input = document.createElement("input");
        input.type = "text";
        input.className = "detail-memo-input";
        input.value = memo;
        input.placeholder = "메모 입력";
        let saving = false;
        const save = async () => {
          if (saving) {
            return;
          }
          saving = true;
          try {
            await saveRecordMemo(record, input.value, input);
          } catch (error) {
            result.textContent = error.message;
            input.disabled = false;
            saving = false;
            input.focus();
          }
        };
        input.addEventListener("blur", save);
        input.addEventListener("keydown", (event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            input.blur();
          }
        });
        wrapper.replaceChildren(input);
        input.focus();
        input.select();
      });
      wrapper.append(text, editButton);
      return wrapper;
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

        const relatedRelations = item.relations || [relation];
        const {content, titleText} = createRecordListContent(relatedRecord, relatedAnalysis, {
          extraTags: relationLabelsWithScores(relatedRelations),
          includeRecordTags: false
        });
        button.setAttribute("aria-label", `연관 기록 선택: ${titleText}`);
        button.appendChild(content);
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
      const tags = document.createElement("div");
      tags.className = "detail-tags";
      for (const tag of recordListTags(record, analysis)) {
        appendPill(tags, tag);
      }
      hero.append(title, tags);
      return hero;
    }

    function clearSelectedRecordViews() {
      recordDetail.replaceChildren();
      assetList.replaceChildren();
      analysisDetail.replaceChildren();
      embeddingMeta.replaceChildren();
      similarResults.replaceChildren();
      timelineResults.replaceChildren();
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
        const {content, titleText} = createRecordListContent(record, analysis);
        button.setAttribute("aria-label", `기록 선택: ${titleText}`);

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
        button.append(deleteButton, content);
        recordList.appendChild(button);
      }
    }

    function renderRecordDetail(record, assets, analysis, relations, timelineCandidates, relatedRecords) {
      const sections = [
        renderDetailHero(record, analysis),
        detailSection("상세 정보", [
          {label: "메모", value: memoDetailEditor(record)},
          {label: "시간", value: detailDateTime(recordDateTimeValue(record))},
          {label: "메뉴", value: menuDetailList(analysis)},
          {label: "태그", value: tagDetailList(analysis?.tags)},
          {label: "활동내역", value: bestActivityText(analysis)},
          {label: "AI 요약", value: analysis?.summary}
        ]),
        connectionSection(relatedRecords || [])
      ].filter(Boolean);
      recordDetail.replaceChildren(...sections);

      assetList.replaceChildren();
      const uploadItems = uploadAssetItems(assets);
      if (uploadItems.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "업로드된 파일이 없습니다.";
        assetList.appendChild(empty);
        return;
      }
      for (const itemAssets of uploadItems) {
        const asset = itemAssets.original;
        const item = document.createElement("button");
        item.type = "button";
        item.className = "asset-item";
        item.title = "원본 파일 열기";
        item.addEventListener("click", () => openOriginalAsset(asset));
        if (itemAssets.preview) {
          const img = document.createElement("img");
          img.alt = asset.content_type;
          item.appendChild(img);
          assetObjectUrl(itemAssets.preview).then((url) => {
            if (url) {
              img.src = url;
            }
          });
        }
        const caption = document.createElement("span");
        caption.textContent = `원본 / ${Math.round((asset.byte_size || 0) / 1024)}KB`;
        item.appendChild(caption);
        assetList.appendChild(item);
      }
    }

    function renderAnalysis(analysis) {
      analysisDetail.replaceChildren();
      if (!analysis) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "AI 해석 데이터가 없습니다.";
        analysisDetail.appendChild(empty);
        return;
      }

      const meta = document.createElement("div");
      meta.className = "meta-row";
      appendUniquePill(meta, analysis.model);
      if (analysis.scene_type) {
        appendUniquePill(meta, `장면 ${analysis.scene_type}`);
      }

      const rows = [
        row("place_candidates", dataJson(analysis.place_candidates)),
        row("visit_time_candidates", dataJson(analysis.visit_time_candidates)),
        row("menu_candidates", dataJson(analysis.menu_candidates)),
        row("amount_candidates", dataJson(analysis.amount_candidates)),
        row("activity_candidates", dataJson(analysis.activity_candidates)),
        row("similar_record_candidates", dataJson(analysis.similar_record_candidates)),
        row("revisit_candidates", dataJson(analysis.revisit_candidates)),
        row("timeline_candidates", dataJson(analysis.timeline_candidates)),
        row("tags", dataJson(analysis.tags)),
        row("raw_response_ref", dataJson(analysis.raw_response_ref))
      ];
      analysisDetail.replaceChildren(...(meta.children.length > 0 ? [meta, ...rows] : rows));
    }

    async function fetchRelatedRecords(relations, limit = 3) {
      const relatedItems = groupedRelatedRelations(relations, limit);
      return Promise.all(relatedItems.map(async (item) => {
        const record = await optionalJson(`/records/${item.relation.target_record_id}`, {
          headers: authHeaders()
        });
        return {...item, record};
      }));
    }

    function renderSimilarResults(relations, relatedRecords, storageJson) {
      similarResults.replaceChildren();
      embeddingMeta.replaceChildren();
      const embedding = storageJson?.data?.record_embeddings?.[0];
      if (embedding) {
        appendUniquePill(embeddingMeta, embedding.model);
        appendUniquePill(embeddingMeta, `${embedding.dimension}차원`);
      } else {
        appendUniquePill(embeddingMeta, "임베딩 없음");
      }
      appendUniquePill(embeddingMeta, `연관 ${relations.length}건`);

      if (relations.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "연관 데이터가 없습니다.";
        similarResults.appendChild(empty);
        return;
      }

      for (const [index, relation] of relations.entries()) {
        const article = document.createElement("article");
        article.className = "result-row result-card";
        article.append(
          dataItemTitle("연관", index, relation.relation_type),
          row("relation_type", relation.relation_type),
          row("target_record_id", relation.target_record_id),
          row("similarity_score", numberText(relation.similarity_score)),
          row("decision_status", relation.decision_status),
          row("created_at", relation.created_at),
          row("reasons", dataJson(relation.reasons))
        );
        similarResults.appendChild(article);
      }
    }

    function renderTimeline(candidates, storageJson) {
      timelineResults.replaceChildren();
      const meta = document.createElement("div");
      meta.className = "meta-row";
      appendUniquePill(meta, embeddingModel(storageJson));
      if (meta.children.length > 0) {
        timelineResults.appendChild(meta);
      }
      if (candidates.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "타임라인 후보 데이터가 없습니다.";
        timelineResults.appendChild(empty);
        return;
      }

      for (const [index, candidate] of candidates.entries()) {
        const article = document.createElement("article");
        article.className = "result-row result-card";
        article.append(
          dataItemTitle("타임라인", index, candidate.timeline_type),
          row("timeline_type", candidate.timeline_type),
          row("grouping_key", candidate.grouping_key),
          row("confidence_score", numberText(candidate.confidence_score)),
          row("reason", dataJson(candidate.reason || candidate.reasons)),
          row("created_at", candidate.created_at)
        );
        timelineResults.appendChild(article);
      }
    }

    async function loadRecords() {
      const payload = await requestJson("/records", {headers: authHeaders()});
      state.records = payload.records;
      state.analyses.clear();
      state.assets.clear();
      await Promise.all(state.records.map(async (record) => {
        const [analysis, assetsPayload] = await Promise.all([
          optionalJson(`/records/${record.record_id}/ai-analysis`, {
            headers: authHeaders()
          }),
          optionalJson(`/records/${record.record_id}/assets`, {
            headers: authHeaders()
          })
        ]);
        if (analysis) {
          state.analyses.set(record.record_id, analysis);
        }
        if (assetsPayload) {
          state.assets.set(record.record_id, assetsPayload.assets);
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
      state.assets.set(recordId, assetsPayload.assets);
      if (analysis) {
        state.analyses.set(recordId, analysis);
        computeVisitLabels();
      }
      renderRecordList();
      const relatedRecords = await fetchRelatedRecords(relationsPayload.relations);
      renderRecordDetail(record, assetsPayload.assets, analysis, relationsPayload.relations, timelinePayload.timeline_candidates, relatedRecords);
      renderAnalysis(analysis);
      renderSimilarResults(relationsPayload.relations, relatedRecords, storageJson);
      renderTimeline(timelinePayload.timeline_candidates, storageJson);
      result.textContent = JSON.stringify(storageJson || {detail: "storage-json 없음"}, null, 2);
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
        const recordCurl = curlCommand("/records", {
          method: "POST",
          headers: authHeaders({"Content-Type": "application/json"}),
          json: recordPayload
        });
        updateStep("record", "저장 중", "running", recordCurl);
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
        const assetCurl = files
          .map((file) => curlCommand(`/records/${record.record_id}/assets`, {
            method: "POST",
            headers: authHeaders(),
            fileName: file.name
          }))
          .join("\\n");
        updateStep("assets", `원본 ${files.length}개 저장 중`, "running", assetCurl);
        for (const file of files) {
          const formData = new FormData();
          formData.append("file", file);
          await requestJson(`/records/${record.record_id}/assets`, {
            method: "POST",
            headers: authHeaders(),
            body: formData
          });
        }
        updateStep("assets", `원본 ${files.length}개 저장 완료`, "done");

        const analysisCurl = curlCommand(`/records/${record.record_id}/ai-analysis`, {
          method: "POST",
          headers: authHeaders()
        });
        updateStep("analysis", "해석 저장 중", "running", analysisCurl);
        updateStep("thumbnail", "대기", "running", "별도 API 호출 없음");
        const analysis = await requestJson(`/records/${record.record_id}/ai-analysis`, {
          method: "POST",
          headers: authHeaders()
        });
        state.analyses.set(record.record_id, analysis);
        const analysisTokens = tokenUsageText(analysis, true);
        updateStep("analysis", "해석 저장 완료", "done", analysisCurl, analysisTokens);
        updateStep("thumbnail", "썸네일 저장 완료", "done", "별도 API 호출 없음");

        const embeddingCurl = curlCommand(`/records/${record.record_id}/embedding`, {
          method: "POST",
          headers: authHeaders()
        });
        updateStep("embedding", "임베딩 저장 중", "running", embeddingCurl);
        const embeddingResult = await requestJson(`/records/${record.record_id}/embedding`, {
          method: "POST",
          headers: authHeaders()
        });
        const embeddingTokens = tokenUsageText(embeddingResult, true);
        updateStep("embedding", `${embeddingResult.embedding.dimension}차원 저장 완료`, "done", embeddingCurl, embeddingTokens);

        updateStep("relations", "연관 기록 저장 중", "running", "별도 API 호출 없음");
        const relationCount = (embeddingResult.relations || []).length;
        updateStep("relations", `${relationCount}건 저장 완료`, "done", "별도 API 호출 없음");
        updateStep("timeline", "타임라인 후보 저장 중", "running", "별도 API 호출 없음");
        const timelineCount = (embeddingResult.timeline_candidates || []).length;
        updateStep("timeline", `${timelineCount}건 저장 완료`, "done", "별도 API 호출 없음");

        const storageCurl = curlCommand(`/records/${record.record_id}/storage-json`, {
          headers: authHeaders()
        });
        updateStep("storage", "저장 JSON 조회 중", "running", storageCurl);
        await refreshAfterUpload(record.record_id);
        updateStep("storage", "조회 완료 · 추가 저장 없음", "done");
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

    loadRecords().catch((error) => {
      recordList.textContent = error.message;
    });
  </script>
</body>
</html>
"""
