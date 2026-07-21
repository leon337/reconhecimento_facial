(() => {
  "use strict";

  const app = document.getElementById("punch-app");
  const video = document.getElementById("video");
  const startButton = document.getElementById("start-camera");
  const captureButton = document.getElementById("capture");
  const mobileInput = document.getElementById("mobile-image");
  const mobileSubmitButton = document.getElementById("submit-mobile-image");
  const statusElement = document.getElementById("status");
  const typeSelect = document.getElementById("tipo");

  if (
    !app ||
    !video ||
    !startButton ||
    !captureButton ||
    !mobileInput ||
    !mobileSubmitButton ||
    !statusElement ||
    !typeSelect
  ) {
    return;
  }

  const submitUrl = app.dataset.submitUrl;
  const csrfToken = app.dataset.csrfToken;
  let stream = null;
  let busy = false;
  let progressTimer = null;
  let elapsedSeconds = 0;

  const setStatus = (message, kind = "info") => {
    statusElement.textContent = message;
    statusElement.classList.toggle("text-red-700", kind === "error");
    statusElement.classList.toggle("text-green-700", kind === "success");
    statusElement.classList.toggle("text-gray-700", kind === "info");
  };

  const stopProgress = () => {
    if (progressTimer) {
      window.clearInterval(progressTimer);
      progressTimer = null;
    }
  };

  const startProgress = () => {
    stopProgress();
    elapsedSeconds = 0;
    setStatus("Processando reconhecimento...");
    progressTimer = window.setInterval(() => {
      elapsedSeconds += 1;
      if (elapsedSeconds >= 5) {
        setStatus(`Reconhecimento em andamento (${elapsedSeconds}s). Aguarde...`);
      }
    }, 1000);
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    video.srcObject = null;
  };

  const resetLiveCameraControls = () => {
    stopCamera();
    video.classList.add("hidden");
    captureButton.classList.add("hidden");
    captureButton.disabled = true;
    if (window.isSecureContext && navigator.mediaDevices?.getUserMedia) {
      startButton.classList.remove("hidden");
      startButton.disabled = busy;
    }
  };

  const setBusy = (value) => {
    busy = value;
    captureButton.disabled = value || !stream;
    mobileInput.disabled = value;
    mobileSubmitButton.disabled = value || !mobileInput.files.length;
    startButton.disabled = value;
  };

  const startCamera = async () => {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setStatus(
        "Neste endereço HTTP a câmera ao vivo é bloqueada. Use o campo de câmera do celular abaixo.",
        "info",
      );
      return;
    }

    try {
      stopCamera();
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });
      video.srcObject = stream;
      await video.play();
      video.classList.remove("hidden");
      captureButton.classList.remove("hidden");
      captureButton.disabled = false;
      startButton.classList.add("hidden");
      setStatus("Câmera ativa. Centralize o rosto e pressione Capturar e registrar.");
    } catch (error) {
      console.error("punch_camera_access_failed", error);
      resetLiveCameraControls();
      setStatus(
        "Não foi possível acessar a câmera ao vivo. Verifique a permissão ou use a câmera do celular abaixo.",
        "error",
      );
    }
  };

  const readAsDataUrl = (source) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("image_read_failed"));
      reader.readAsDataURL(source);
    });

  const loadImage = (dataUrl) =>
    new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("image_decode_failed"));
      image.src = dataUrl;
    });

  const normalizeImage = async (source) => {
    const dataUrl = await readAsDataUrl(source);
    const image = await loadImage(dataUrl);
    const maxDimension = 640;
    const scale = Math.min(1, maxDimension / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    canvas.getContext("2d").drawImage(image, 0, 0, width, height);

    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error("image_encode_failed"))),
        "image/jpeg",
        0.86,
      );
    });
  };

  const parseResponse = async (response) => {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    const text = await response.text();
    return { message: text || "Resposta inválida do servidor." };
  };

  const submitImage = async (source) => {
    if (busy || !source) {
      return;
    }

    setBusy(true);
    startProgress();

    try {
      const normalizedBlob = await normalizeImage(source);
      const formData = new FormData();
      formData.append("image", normalizedBlob, "captura.jpg");
      formData.append("tipo", typeSelect.value);
      formData.append("csrf_token", csrfToken);

      const response = await fetch(submitUrl, {
        method: "POST",
        body: formData,
        headers: { Accept: "application/json" },
      });
      const data = await parseResponse(response);
      const message = data.message || "Resposta inválida do servidor.";

      if (response.ok) {
        setStatus(message, "success");
        mobileInput.value = "";
      } else if (data.code === "duplicate_punch" && data.retry_after_seconds) {
        setStatus(`${message} Tente novamente em ${data.retry_after_seconds}s.`, "error");
      } else {
        setStatus(message, "error");
      }
    } catch (error) {
      console.error("punch_submit_failed", error);
      setStatus("Falha ao processar ou comunicar com o servidor.", "error");
    } finally {
      stopProgress();
      setBusy(false);
      resetLiveCameraControls();
    }
  };

  startButton.addEventListener("click", startCamera);

  captureButton.addEventListener("click", () => {
    if (!stream || !video.videoWidth || !video.videoHeight) {
      setStatus("A câmera ainda não está pronta.", "error");
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setStatus("Falha ao capturar a imagem.", "error");
          return;
        }
        stopCamera();
        submitImage(blob);
      },
      "image/jpeg",
      0.9,
    );
  });

  mobileInput.addEventListener("change", () => {
    mobileSubmitButton.disabled = busy || !mobileInput.files.length;
    if (mobileInput.files.length) {
      setStatus("Foto pronta. Selecione Entrada ou Saída e confirme o registro.");
    }
  });

  mobileSubmitButton.addEventListener("click", () => {
    const [file] = mobileInput.files;
    if (!file) {
      setStatus("Capture uma foto antes de registrar.", "error");
      return;
    }
    submitImage(file);
  });

  window.addEventListener("pagehide", () => {
    stopCamera();
    stopProgress();
  });

  if (window.isSecureContext && navigator.mediaDevices?.getUserMedia) {
    startCamera();
  } else {
    setStatus("No celular, use o campo abaixo para abrir a câmera frontal.");
  }
})();
