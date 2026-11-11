/* Formulário único: autenticação e depósito cifrado sem cookies e sem redirects. */
(() => {
  const form = document.querySelector('#key-form');
  const access = document.querySelector('#access-code');
  const keyInput = document.querySelector('#api-key');
  const status = document.querySelector('#status');
  const submit = document.querySelector('#submit-key');
  if (!form || !access || !keyInput || !status || !submit) return;

  const setStatus = (message, failed = false) => {
    status.textContent = message;
    status.classList.toggle('error', failed);
  };

  const toBytes = (pem) => {
    const compact = pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, '');
    return Uint8Array.from(atob(compact), (character) => character.charCodeAt(0));
  };

  const toBase64 = (bytes) => {
    let result = '';
    for (let pos = 0; pos < bytes.length; pos += 4096) {
      result += String.fromCharCode(...bytes.subarray(pos, pos + 4096));
    }
    return btoa(result);
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const code = access.value.trim();
    const apiKey = keyInput.value.trim();

    if (code.length < 10 || code.length > 256) {
      setStatus('Confira o código temporário fornecido pelo MESTRE.', true);
      access.focus();
      return;
    }
    if (apiKey.length < 20 || apiKey.length > 512 || /\s/.test(apiKey)) {
      setStatus('Confira a chave copiada do Google AI Studio.', true);
      keyInput.focus();
      return;
    }
    if (!window.isSecureContext || !window.crypto?.subtle) {
      setStatus('Abra o endereço HTTPS do portal para criptografar a chave.', true);
      return;
    }

    submit.disabled = true;
    setStatus('Criptografando e validando seu acesso...');
    try {
      const publicResponse = await fetch('/public-key', {
        method: 'GET', cache: 'no-store', credentials: 'omit',
      });
      if (!publicResponse.ok) throw new Error('O portal expirou. Solicite uma nova sessão.');
      const { publicKey } = await publicResponse.json();
      const key = await crypto.subtle.importKey(
        'spki', toBytes(publicKey), { name: 'RSA-OAEP', hash: 'SHA-256' },
        false, ['encrypt'],
      );
      const encrypted = await crypto.subtle.encrypt(
        { name: 'RSA-OAEP' }, key, new TextEncoder().encode(apiKey),
      );
      // O valor digitado não deve permanecer na página após a tentativa.
      keyInput.value = '';
      const response = await fetch('/submit-once', {
        method: 'POST', cache: 'no-store', credentials: 'omit',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge: form.dataset.challenge,
          code,
          encrypted: toBase64(new Uint8Array(encrypted)),
        }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.error || 'Não foi possível salvar. Tente novamente.');
      }
      access.value = '';
      form.replaceChildren();
      const result = document.createElement('p');
      result.setAttribute('role', 'status');
      result.style.fontSize = '18px';
      result.style.lineHeight = '1.6';
      result.textContent = '✅ Chave recebida com segurança. O acesso foi encerrado. Volte à conversa e informe apenas que concluiu.';
      form.appendChild(result);
    } catch (error) {
      setStatus(error.message || 'Erro na configuração. Tente novamente.', true);
    } finally {
      submit.disabled = false;
    }
  });
})();
