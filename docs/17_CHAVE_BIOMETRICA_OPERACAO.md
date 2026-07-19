# Operação da chave biométrica

- Armazene `BIOMETRIC_ENCRYPTION_KEY` no gerenciador de segredos do ambiente.
- Não reutilize `SECRET_KEY` como chave biométrica.
- Não exponha a chave em logs, commits, tickets ou arquivos `.env` versionados.
- Backup da chave deve ser criptografado e ter acesso restrito.
- A perda da chave impede a recuperação dos templates protegidos.
- Rotação de chave exigirá rotina própria de descriptografia e recriptografia, prevista para o hardening operacional.
