(() => {
  "use strict";

  const app = document.getElementById("punch-app");
  const video = document.getElementById("video");
  const startCameraButton = document.getElementById("start-camera");
  const startVerificationButton = document.getElementById("start-verification");
  const challengePanel = document.getElementById("challenge-panel");
  const challengeText = document.getElementById("challenge-text");
  const challengeCountdown = document.getElementById("challenge-countdown");
  const statusElement = document.getElementById("status");
  const elapsedElement = document.getElementById("elapsed-time");
  const typeSelect = document.getElementById("tipo");

  if (
    !app ||
    !video ||
    !startCameraButton ||
    !startVerificationButton ||
    !challengePanel ||
    !challengeText ||
    !challengeCountdown ||
    !statusElement ||
    !elapsedElement ||
    !typeSelect
  ) {
    return;
  }

  const submitUrl = app.dataset.submitUrl;
  const challengeUrl = app.dataset.challengeUrl;
  const csrfToken = app.dataset.csrfToken;
  let stream = null;
  let busy = false;
  let elapsedTimer = null;
  let operationStarted = 0;

  const sleep = (milliseconds) =>
    new Promise((resolve) => window.setTimeout(resolve, milliseconds));

  const setStatus = (message, kind = "info") => {
    statusElement.textContent = message;
    statusElement.classList.toggle("text-red-700", kind === "error");
    statusElement.classList.toggle("text-green-700", kind === "success");
    statusElement.classList.toggle("text-gray-700", kind === "info");
  };

  const startTimer = () => {
    operationStarted = performance.now();
    window.clearInterval(elapsedTimer);
    elapsedTimer = window.setInterval(() => {
      elapsedElement.textContent = `${((performance.now() - operationStarted) / 1000).toFixed(1).replace(".", ",")}s`;
    }, 100);
  };

  const stopTimer = () => {
    window.clearInterval(elapsedTimer);
    elapsedTimer = null;
    if (operationStarted) {
      elapsedElement.textContent = `${((performance.now() - operationStarted) / 1000).toFixed(1).replace(".", ",")}s`;
    }
  };

  const setBusy = (value) => {
    busy = value;
    startCameraButton.disabled = value;
    startVerificationButton.disabled = value || !stream;
    typeSelect.disabled = value;
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    video.srcObject = null;
  };

  const secureCameraAvailable = () =>
    window.isSecureContext && Boolean(navigator.mediaDevices?.getUserMedia);

  const startCamera = async () => {
    if (!secureCameraAvailable()) {
      setStatus(
        "A câmera exige HTTPS no celular. Acesse o endereço https exibido pelo instalador e instale o certificado local.",
        "error",
      );
      return;
    }

    try {
      stopCamera();
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640, max: 640 },
          height: { ideal: 480, max: 480 },
          frameRate: { ideal: 24, max: 30 },
        },
        audio: false,
      });
      video.srcObject = stream;
      await video.play();
      video.classList.remove("hidden");
      startCameraButton.classList.add("hidden");
      startVerificationButton.classList.remove("hidden");
      startVerificationButton.disabled = false;
      setStatus("Câmera pronta. Uma pessoa por vez diante do equipamento.");
    } catch (error) {
      console.error("secure_camera_failed", error);
      stopCamera();
      setStatus("Não foi possível abrir a câmera. Verifique a permissão do navegador.", "error");
    }
  };

  const captureFrame = () =>
    new Promise((resolve, reject) => {
      if (!stream || !video.videoWidth || !video.videoHeight) {
        reject(new Error("camera_not_ready"));
        return;
      }
      const maxDimension = 480;
      const scale = Math.min(
        1,
        maxDimension / Math.max(video.videoWidth, video.videoHeight),
      );
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
      canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
      canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error("frame_encode_failed"))),
        "image/jpeg",
        0.82,
      );
    });

  const parseResponse = async (response) => {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    const text = await response.text();
    return { message: text || "Resposta inválida do servidor." };
  };

  const requestChallenge = async () => {
    const response = await fetch(challengeUrl, {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    if (!response.ok) {
      throw new Error("challenge_request_failed");
    }
    return response.json();
  };

  const captureBurst = async (frameCount, intervalMs) => {
    const frames = [];
    for (let index = 0; index < frameCount; index += 1) {
      frames.push(await captureFrame());
      challengeCountdown.textContent = `Capturando ${index + 1}/${frameCount}`;
      if (index + 1 < frameCount) {
        await sleep(intervalMs);
      }
    }
    return frames;
  };

  const verifyAndPunch = async () => {
    if (busy || !stream) {
      return;
    }

    setBusy(true);
    startTimer();
    challengePanel.classList.remove("hidden");
    setStatus("Preparando prova de vida...");

    try {
      const challenge = await requestChallenge();
      challengeText.textContent = challenge.prompt;
      challengeCountdown.textContent = "Prepare-se";
      await sleep(650);

      const frames = await captureBurst(
        Number(challenge.frame_count || 6),
        Number(challenge.capture_interval_ms || 240),
      );
      challengeCountdown.textContent = "Identificando funcionário...";
      setStatus("Prova de vida capturada. Identificando funcionário...");

      const formData = new FormData();
      frames.forEach((frame, index) => {
        formData.append("frames", frame, `quadro-${index + 1}.jpg`);
      });
      formData.append("challenge_id", challenge.challenge_id);
      formData.append("tipo", typeSelect.value);
      formData.append("csrf_token", csrfToken);

      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 12000);
      let response;
      try {
        response = await fetch(submitUrl, {
          method: "POST",
          body: formData,
          headers: { Accept: "application/json" },
          credentials: "same-origin",
          signal: controller.signal,
        });
      } finally {
        window.clearTimeout(timeoutId);
      }

      const data = await parseResponse(response);
      if (response.ok) {
        const seconds = Number(data.processing_ms || 0) / 1000;
        setStatus(`${data.message} Processamento: ${seconds.toFixed(1).replace(".", ",")}s.`, "success");
        challengeCountdown.textContent = data.target_met
          ? "Meta de desempenho atingida"
          : "Registro concluído; desempenho acima da meta";
      } else if (data.code === "duplicate_punch" && data.retry_after_seconds) {
        setStatus(`${data.message} Aguarde ${data.retry_after_seconds}s.`, "error");
        challengeCountdown.textContent = "Registro não duplicado";
      } else {
        setStatus(data.message || "Verificação não concluída.", "error");
        challengeCountdown.textContent = "Tente novamente";
      }
    } catch (error) {
      console.error("live_punch_failed", error);
      if (error.name === "AbortError") {
        setStatus("O processamento excedeu 12 segundos. Tente novamente.", "error");
      } else {
        setStatus("Falha na prova de vida ou comunicação com o servidor.", "error");
      }
      challengeCountdown.textContent = "Verificação interrompida";
    } finally {
      stopTimer();
      setBusy(false);
      window.setTimeout(() => challengePanel.classList.add("hidden"), 1800);
    }
  };

  startCameraButton.addEventListener("click", startCamera);
  startVerificationButton.addEventListener("click", verifyAndPunch);
  window.addEventListener("pagehide", () => {
    stopCamera();
    window.clearInterval(elapsedTimer);
  });

  if (secureCameraAvailable()) {
    startCamera();
  } else {
    setStatus(
      "Câmera bloqueada neste endereço. No celular, use o endereço HTTPS e confie no certificado local.",
      "error",
    );
  }
})();
