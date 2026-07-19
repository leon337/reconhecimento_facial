"use strict";

const app = document.getElementById("punch-app");
const video = document.getElementById("video");
const captureButton = document.getElementById("capture");
const statusElement = document.getElementById("status");
const submitUrl = app.dataset.submitUrl;
const csrfToken = app.dataset.csrfToken;

navigator.mediaDevices
  .getUserMedia({ video: { facingMode: "user" }, audio: false })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch(() => {
    statusElement.textContent = "Não foi possível acessar a câmera.";
  });

captureButton.addEventListener("click", () => {
  if (!video.videoWidth || !video.videoHeight) {
    statusElement.textContent = "A câmera ainda não está pronta.";
    return;
  }

  captureButton.disabled = true;
  statusElement.textContent = "Processando...";

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  canvas.toBlob(async (blob) => {
    if (!blob) {
      statusElement.textContent = "Falha ao capturar a imagem.";
      captureButton.disabled = false;
      return;
    }

    const formData = new FormData();
    formData.append("image", blob, "captura.jpg");
    formData.append("tipo", document.getElementById("tipo").value);
    formData.append("csrf_token", csrfToken);

    try {
      const response = await fetch(submitUrl, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      statusElement.textContent = data.message || "Resposta inválida do servidor.";
    } catch {
      statusElement.textContent = "Falha de comunicação com o servidor.";
    } finally {
      captureButton.disabled = false;
    }
  }, "image/jpeg", 0.9);
});
