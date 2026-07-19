# FASE 9.4 — Biometria segregada e criptografada

## Objetivo

Retirar o template facial do fluxo comum de cadastro, armazená-lo em entidade própria e protegê-lo com criptografia autenticada.

## Controles implementados

- `BiometricProfile` separado de `User`;
- template facial criptografado com Fernet;
- chave externa em `BIOMETRIC_ENCRYPTION_KEY`;
- falha fechada quando a chave está ausente ou inválida;
- imagem salva em diretório privado configurado por `BIOMETRIC_STORAGE_FOLDER`;
- nenhuma URL pública gerada para a imagem;
- perfil único por usuário;
- versionamento do algoritmo biométrico;
- substituição segura do arquivo anterior;
- reconhecimento com leitura do perfil protegido;
- fallback temporário para `User.face_encoding` legado;
- migration Alembic reversível;
- testes somente com dados sintéticos.

## Operação

Gere uma chave Fernet fora do repositório e configure-a como segredo:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
export BIOMETRIC_ENCRYPTION_KEY='chave-gerada'
```

A chave não deve ser gravada no Git, banco de dados, logs ou imagens de container.

## Limites desta fase

Os campos legados `face_encoding` e `photo_url` permanecem temporariamente no modelo para compatibilidade. A remoção definitiva dependerá de migração controlada dos registros existentes e validação de produção.
