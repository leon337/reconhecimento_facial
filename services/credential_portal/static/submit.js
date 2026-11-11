/* Nunca transmitir a chave em texto simples nem gravá-la no browser. */
(() => {
  const container = document.querySelector('#key-form');
  const input = document.querySelector('#api-key');
  const button = document.querySelector('#submit-key');
  const status = document.querySelector('#status');
  if (!container || !input || !button || !status) return;

  const setStatus = (message, failed = false) => {
    status.textContent = message;
    status.classList.toggle('error', failed);
  };

  const publicKeyToBytes = (pem) => {
    const base64 = pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, '');
    const raw = atob(base64);
    return Uint8Array.from(raw, (item) => item.charCodeAt(0));
  };

  const toBase64 = (bytes) => {
    let text = '';
    for (let pos = 0; pos < bytes.length; pos += 4096) {
      text += String.fromCharCode(...bytes.slice(pos, pos + 4096));
    }
    return btoa(text);
  };

  button.addEventListener('click', async () => {
    const key = input.value.trim();
    if (key.length < 20 || key.length > 512 || /\s/.test(key)) {
      setStatus('Confira a chave copiada do Google AI Studio.', true);
      return;
    }
    if (!window.isSecureContext || !crypto?.subtle) {
      setStatus('É necessária uma conexão HTTPS para criptografar a chave.', true);
      return;
    }
    button.disabled = true;
    input.disabled = true;
    setStatus('Criptografando a chave antes do envio...');
    try {
      const response = await fetch('/public-key', {
        method: 'GET', credentials: 'omit', cache: 'no-store',
        headers: { 'X-Portal-Ticket': container.dataset.accessTicket },
      });
      if (!response.ok) throw new Error('Sessão de configuração encerrada.');
      const data = await response.json();
      const cryptoKey = await crypto.subtle.importKey(
        'spki', publicKeyToBytes(data.publicKey), { name: 'RSA-OAEP', hash: 'SHA-256' },
        false, ['encrypt'],
      );
      const ciphertext = await crypto.subtle.encrypt(
        { name: 'RSA-OAEP' }, cryptoKey, new TextEncoder().encode(key),
      );
      // Limpar antes mesmo de transmitir: a solicitação leva só ciphertext.
      input.value = '';
      setStatus('Salvando no cofre criptografado...');
      const saved = await fetch('/submit', {
        method: 'POST', cache: 'no-store', credentials: 'omit',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': container.dataset.csrf,
          'X-Portal-Ticket': container.dataset.accessTicket,
        },
        body: JSON.stringify({ encrypted: toBase64(new Uint8Array(ciphertext)) }),
      });
      if (!saved.ok) {
        const info = await saved.json().catch(() => ({}));
        throw new Error(info.error || 'Não foi possível salvar a chave.');
      }
      setStatus('Chave armazenada. Finalizando acesso...');
      window.location.replace('/complete');
    } catch (error) {
      input.value = '';
      setStatus(error.message || 'Erro na configuração. Tente novamente.', true);
    } finally {
      button.disabled = false;
      input.disabled = false;
    }
  });
})();
