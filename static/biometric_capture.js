(() => {
  "use strict";

  const app = document.getElementById("biometric-app");
  const video = document.getElementById("camera-preview");
  const startCameraButton = document.getElementById("start-camera");
  const startEnrollmentButton = document.getElementById("start-enrollment");
  const challengePanel = document.getElementById("challenge-panel");
  const challengeText = document.getElementById("challenge-text");
  const challengeProgress = document.getElementById("challenge-progress");
  const status = document.getElementById("camera-status");

  if (
    !app ||
    !video ||
    !startCameraButton ||
    !startEnrollmentButton ||
    !challengePanel ||
    !challengeText ||
    !challengeProgress ||
    !status
  ) {
    return;
  }

  const submitUrl = app.dataset.submitUrl;
  const challengeUrl = app.dataset.challengeUrl;
  const csrfToken = app.dataset.csrfToken;
  let stream = null;
  let busy = false;

  const sleep = (milliseconds) =>
    new Promise((resolve) => window.setTimeout(resolve, milliseconds));

  const setStatus = (message, isError = false) => {
    status.textContent = message;
    status.classList.toggle("text-red-700", isError);
    status.classList.toggle("text-gray-600", !isError);
  };

  const secureCameraAvailable = () =>
    window.isSecureContext && Boolean(navigator.mediaDevices?.getUserMedia);

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    video.srcObject = null;
  };

  const setBusy = (value) => {
    busy = value;
    startCameraButton.disabled = value;
    startEnrollmentButton.disabled = value || !stream;
  };

  const startCamera = async () => {
    if (!secureCameraAvailable()) {
      setStatus(
        "A câmera ao vivo exige HTTPS no celular. Use o endereço seguro exibido pelo instalador.",
        true,
      );
      return;
    }

    try {
      stopCamera();
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: "user",
          width: { ideal: 640, max: 640 },
          height: { ideal: 480, max: 480 },
          frameRate: { ideal: 24, max: 30 },
        },
      });
      video.srcObject = stream;
      await video.play();
      video.classList.remove("hidden");
      startCameraButton.classList.add("hidden");
      startEnrollmentButton.classList.remove("hidden");
      startEnrollmentButton.disabled = false;
      setStatus("Câmera pronta. Mantenha apenas o funcionário no enquadramento.");
    } catch (error) {
      console.error("biometric_secure_camera_failed", error);
      stopCamera();
      setStatus("Não foi possível abrir a câmera. Verifique a permissão do navegador.", true);
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
        0.84,
      );
    });

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

  const captureBurst = async (count, intervalMs) => {
    const frames = [];
    for (let index = 0; index < count; index += 1) {
      frames.push(await captureFrame());
      challengeProgress.textContent = `Capturando ${index + 1}/${count}`;
      if (index + 1 < count) {
        await sleep(intervalMs);
      }
    }
    return frames;
  };

  const enroll = async () => {
    if (busy || !stream) {
      return;
    }

    setBusy(true);
    challengePanel.classList.remove("hidden");
    setStatus("Preparando prova de vida...");

    try {
      const challenge = await requestChallenge();
      challengeText.textContent = challenge.prompt;
      challengeProgress.textContent = "Prepare-se";
      await sleep(650);
      const frames = await captureBurst(
        Number(challenge.frame_count || 6),
        Number(challenge.capture_interval_ms || 240),
      );
      challengeProgress.textContent = "Validando biometria...";
      setStatus("Verificando prova de vida e duplicidade facial...");

      const formData = new FormData();
      frames.forEach((frame, index) => {
        formData.append("frames", frame, `cadastro-${index + 1}.jpg`);
      });
      formData.append("challenge_id", challenge.challenge_id);
      formData.append("csrf_token", csrfToken);

      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 15000);
      let response;
      try {
        response = await fetch(submitUrl, {
          method: "POST",
          body: formData,
          credentials: "same-origin",
          signal: controller.signal,
        });
      } finally {
        window.clearTimeout(timeoutId);
      }

      if (response.redirected) {
        window.location.assign(response.url);
        return;
      }
      if (!response.ok) {
        throw new Error("enrollment_rejected");
      }
      window.location.assign(submitUrl.replace(/\/biometric$/, ""));
    } catch (error) {
      console.error("live_biometric_enrollment_failed", error);
      if (error.name === "AbortError") {
        setStatus("A validação excedeu 15 segundos. Tente novamente.", true);
      } else {
        setStatus("Não foi possível concluir o cadastro ao vivo. Tente novamente.", true);
      }
      challengeProgress.textContent = "Verificação interrompida";
      setBusy(false);
      window.setTimeout(() => challengePanel.classList.add("hidden"), 1800);
    }
  };

  startCameraButton.addEventListener("click", startCamera);
  startEnrollmentButton.addEventListener("click", enroll);
  window.addEventListener("pagehide", stopCamera);

  if (secureCameraAvailable()) {
    startCamera();
  } else {
    setStatus(
      "Câmera bloqueada neste endereço. No celular, abra o endereço HTTPS e confie no certificado local.",
      true,
    );
  }
})();
