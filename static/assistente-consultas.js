(() => {
  "use strict";
  const root = document.querySelector(".shell");
  const form = document.getElementById("ask-form");
  const input = document.getElementById("question");
  const send = document.getElementById("send");
  const messages = document.getElementById("messages");
  const append = (who, message, data) => {
    const bubble = document.createElement("article");
    bubble.className = "bubble " + (who === "Você" ? "human" : "bot");
    const speaker = document.createElement("span");
    speaker.className = "speaker";
    speaker.textContent = who;
    const p = document.createElement("p");
    p.textContent = message;
    bubble.append(speaker, p);
    if (data && Array.isArray(data.rows) && data.rows.length) {
      const list = document.createElement("div");
      list.className = "result-list";
      data.rows.forEach((row) => {
        const item = document.createElement("div");
        item.className = "result-item";
        const keys = Object.keys(row);
        const title = document.createElement("strong");
        title.textContent = String(row[keys[0]] ?? "");
        item.append(title);
        keys.slice(1).forEach((key) => {
          const line = document.createElement("span");
          line.textContent = key.replaceAll("_", " ") + ": " + String(row[key] ?? "");
          item.append(line);
        });
        list.append(item);
      });
      bubble.append(list);
    }
    if (data?.source) {
      const source = document.createElement("div");
      source.className = "source";
      source.textContent = "Fonte: " + data.source;
      bubble.append(source);
    }
    messages.append(bubble);
    messages.scrollTop = messages.scrollHeight;
  };
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question || send.disabled) return;
    append("Você", question);
    input.value = "";
    send.disabled = true;
    try {
      const response = await fetch(root.dataset.api, {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json", "X-CSRFToken": root.dataset.csrf},
        body: JSON.stringify({question})
      });
      if (response.redirected) {
        append("Assistente Potiguar", "Sua sessão expirou. Faça login novamente.");
        return;
      }
      const data = await response.json();
      if (!response.ok) {
        append("Assistente Potiguar", data.error || "Não foi possível concluir a consulta.");
        return;
      }
      append("Assistente Potiguar", data.answer, data);
    } catch {
      append("Assistente Potiguar", "Falha de conexão. Tente novamente.");
    } finally {
      send.disabled = false;
      input.focus();
    }
  });
  document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => {
      input.value = button.dataset.question;
      form.requestSubmit();
    });
  });
})();
