
const resultArea = document.getElementById("result-area");
const allButtons = document.querySelectorAll(".action-btn");

allButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    if (btn.id === "clear-btn") {
      clearResult();
      return;
    }

    const action = btn.dataset.action;

    if (action === "stat") {
      loadStat(btn.dataset.metric);
    } else if (action === "chart") {
      loadChart(btn.dataset.kind);
    }
  });
});

async function loadStat(metric) {
  showLoading("Считаю статистику...");

  try {
    const response = await fetch(`/api/stat/${metric}`);

    if (!response.ok) {
      throw new Error(`Сервер ответил ${response.status}`);
    }

    const data = await response.json();

    resultArea.innerHTML = `
      <div class="stat-card">
        <div class="label">${data.label}</div>
        <div class="value">${data.value}</div>
      </div>
    `;
  } catch (err) {
    showError("Не удалось загрузить статистику: " + err.message);
  }
}

async function loadChart(kind) {
  showLoading("Строю график...");

  try {
    const response = await fetch(`/api/chart/${kind}`);

    if (!response.ok) {
      throw new Error(`Сервер ответил ${response.status}`);
    }

    const blob = await response.blob();
    const imgUrl = URL.createObjectURL(blob);

    resultArea.innerHTML = `
      <div class="chart-container">
        <img src="${imgUrl}" alt="График ${kind}">
      </div>
    `;
  } catch (err) {
    showError("Не удалось построить график: " + err.message);
  }
}

function showLoading(text) {
  resultArea.innerHTML = `<p class="loading">⏳ ${text}</p>`;
}

function showError(message) {
  resultArea.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function clearResult() {
  resultArea.innerHTML = `
    <p class="placeholder">
      ← Нажмите кнопку слева, чтобы увидеть результат
    </p>
  `;
}

