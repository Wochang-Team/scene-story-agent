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
  <title>Scene Story Agent Upload</title>
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
      padding: 32px;
    }
    main {
      max-width: 760px;
      margin: 0 auto;
    }
    h1 {
      font-size: 24px;
      margin: 0 0 20px;
    }
    form {
      display: grid;
      gap: 14px;
      padding: 20px;
      background: #ffffff;
      border: 1px solid #d7dce2;
      border-radius: 8px;
    }
    label, legend {
      display: grid;
      gap: 6px;
      font-size: 14px;
      font-weight: 600;
    }
    fieldset {
      display: grid;
      gap: 8px;
      min-width: 0;
      margin: 0;
      padding: 0;
      border: 0;
    }
    legend {
      margin-bottom: 2px;
    }
    .choice-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
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
      min-width: 44px;
      min-height: 40px;
      padding: 8px 12px;
      border: 1px solid #c8d0d9;
      border-radius: 6px;
      background: #ffffff;
      cursor: pointer;
      font-size: 18px;
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
    input, textarea, button {
      font: inherit;
    }
    input, textarea {
      padding: 10px 12px;
      border: 1px solid #c8d0d9;
      border-radius: 6px;
      background: #ffffff;
    }
    button {
      width: fit-content;
      padding: 10px 14px;
      border: 0;
      border-radius: 6px;
      color: #ffffff;
      background: #2563eb;
      cursor: pointer;
    }
    pre {
      white-space: pre-wrap;
      margin-top: 16px;
      padding: 16px;
      border: 1px solid #d7dce2;
      border-radius: 8px;
      background: #111827;
      color: #e5e7eb;
    }
  </style>
</head>
<body>
  <main>
    <h1>로컬 기록 업로드</h1>
    <form id="upload-form">
      <label>
        로컬 사용자
        <input id="local-user" name="localUser" value="local-user" autocomplete="off">
      </label>
      <label>
        메모
        <textarea id="memo" name="memo" rows="4"></textarea>
      </label>
      <fieldset>
        <legend>감정</legend>
        <div class="choice-row" aria-label="감정 선택">
          <input id="emotion-joy" name="emotion" type="radio" value="joy">
          <label class="choice" for="emotion-joy" title="기쁨">😊</label>
          <input id="emotion-calm" name="emotion" type="radio" value="calm" checked>
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
          <input id="satisfaction-1" name="satisfaction" type="radio" value="1">
          <label class="choice" for="satisfaction-1">1</label>
          <input id="satisfaction-2" name="satisfaction" type="radio" value="2">
          <label class="choice" for="satisfaction-2">2</label>
          <input id="satisfaction-3" name="satisfaction" type="radio" value="3" checked>
          <label class="choice" for="satisfaction-3">3</label>
          <input id="satisfaction-4" name="satisfaction" type="radio" value="4">
          <label class="choice" for="satisfaction-4">4</label>
          <input id="satisfaction-5" name="satisfaction" type="radio" value="5">
          <label class="choice" for="satisfaction-5">5</label>
        </div>
      </fieldset>
      <label>
        파일
        <input id="file" name="file" type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime" required>
      </label>
      <button type="submit">업로드</button>
    </form>
    <pre id="result">대기 중</pre>
  </main>
  <script>
    const form = document.querySelector("#upload-form");
    const result = document.querySelector("#result");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      result.textContent = "업로드 중";

      const localUser = document.querySelector("#local-user").value || "local-user";
      const emotionInput = document.querySelector("input[name='emotion']:checked");
      const satisfactionInput = document.querySelector("input[name='satisfaction']:checked");
      const recordPayload = {
        memo: document.querySelector("#memo").value || null,
        emotion: emotionInput ? emotionInput.value : null,
        satisfaction_score: satisfactionInput ? Number(satisfactionInput.value) : null
      };

      const recordResponse = await fetch("/records", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Local-User": localUser
        },
        body: JSON.stringify(recordPayload)
      });
      if (!recordResponse.ok) {
        result.textContent = await recordResponse.text();
        return;
      }
      const record = await recordResponse.json();

      const formData = new FormData();
      formData.append("file", document.querySelector("#file").files[0]);
      const assetResponse = await fetch(`/records/${record.record_id}/assets`, {
        method: "POST",
        headers: {"X-Local-User": localUser},
        body: formData
      });
      if (!assetResponse.ok) {
        result.textContent = await assetResponse.text();
        return;
      }
      await assetResponse.json();

      const analysisResponse = await fetch(`/records/${record.record_id}/ai-analysis`, {
        method: "POST",
        headers: {"X-Local-User": localUser}
      });
      if (!analysisResponse.ok) {
        result.textContent = await analysisResponse.text();
        return;
      }

      const embeddingResponse = await fetch(`/records/${record.record_id}/embedding`, {
        method: "POST",
        headers: {"X-Local-User": localUser}
      });
      if (!embeddingResponse.ok) {
        result.textContent = await embeddingResponse.text();
        return;
      }

      const finalStorageResponse = await fetch(`/records/${record.record_id}/storage-json`, {
        headers: {"X-Local-User": localUser}
      });
      if (!finalStorageResponse.ok) {
        result.textContent = await finalStorageResponse.text();
        return;
      }
      result.textContent = JSON.stringify(await finalStorageResponse.json(), null, 2);
    });
  </script>
</body>
</html>
"""
