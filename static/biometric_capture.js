(() => {
  "use strict";

  const form = document.getElementById("biometric-form");
  const video = document.getElementById("camera-preview");
  const canvas = document.getElementById("camera-canvas");
  const preview = document.getElementById("captured-preview");
  const fileInput = document.getElementById("biometric-file");
  const startButton = document.getElementById("start-camera");
  const captureButton = document.getElementById("capture-photo");
  const retakeButton = document.getElementById("retake-photo");
  const status = document.getElementById("camera-status");

  if (!form || !video || !canvas || !preview || !fileInput) {
    return;
  }

  let stream = null;
  let previewUrl = null;

  const setStatus = (message, isError = false) => {
    status.textContent = message;
    status.classList.toggle("text-red-700", isError);
    status.classList.toggle("text-gray-600", !isError);
  };

  const revokePreviewUrl = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    video.srcObject = null;
  };

  const showCapturedFile = (file) => {
    revokePreviewUrl();
    previewUrl = URL.createObjectURL(file);
    preview.src = previewUrl;
    preview.classList.remove("hidden");
    video.classList.add("hidden");
    captureButton.classList.add("hidden");
    retakeButton.classList.remove("hidden");
    startButton.classList.add("hidden");
    setStatus("Foto pronta. Confirme o cadastro ou tire outra foto.");
  };

  const assignCapturedBlob = (blob) => {
    const capturedFile = new File([blob], "biometria-camera.jpg", {
      type: "image/jpeg",
      lastModified: Date.now(),
    });
    const transfer = new DataTransfer();
    transfer.items.add(capturedFile);
    fileInput.files = transfer.files;
    showCapturedFile(capturedFile);
  };

  startButton.addEventListener("click", async () => {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setStatus(
        "A câmera ao vivo exige localhost ou HTTPS. No celular, use o campo abaixo para abrir a câmera frontal.",
        true,
      );
      fileInput.focus();
      return;
    }

    try {
      stopCamera();
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });
      video.srcObject = stream;
      await video.play();
      preview.classList.add("hidden");
      video.classList.remove("hidden");
      captureButton.classList.remove("hidden");
      retakeButton.classList.add("hidden");
      startButton.classList.add("hidden");
      setStatus("Câmera ativa. Centralize o rosto e pressione Capturar foto.");
    } catch (error) {
      console.error("camera_access_failed", error);
      setStatus(
        "Não foi possível acessar a câmera. Verifique a permissão do navegador ou use a câmera do celular abaixo.",
        true,
      );
    }
  });

  captureButton.addEventListener("click", () => {
    if (!stream || video.videoWidth === 0 || video.videoHeight === 0) {
      setStatus("A câmera ainda não está pronta. Aguarde e tente novamente.", true);
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setStatus("Não foi possível gerar a foto. Tente novamente.", true);
          return;
        }
        stopCamera();
        assignCapturedBlob(blob);
      },
      "image/jpeg",
      0.92,
    );
  });

  retakeButton.addEventListener("click", async () => {
    fileInput.value = "";
    preview.classList.add("hidden");
    retakeButton.classList.add("hidden");
    startButton.classList.remove("hidden");
    setStatus("Foto descartada. Abra a câmera para realizar uma nova captura.");
  });

  fileInput.addEventListener("change", () => {
    const [file] = fileInput.files;
    if (!file) {
      return;
    }
    stopCamera();
    showCapturedFile(file);
  });

  form.addEventListener("submit", (event) => {
    if (!fileInput.files.length) {
      event.preventDefault();
      setStatus("Capture ou selecione uma foto antes de confirmar.", true);
    }
  });

  window.addEventListener("beforeunload", () => {
    stopCamera();
    revokePreviewUrl();
  });
})();
