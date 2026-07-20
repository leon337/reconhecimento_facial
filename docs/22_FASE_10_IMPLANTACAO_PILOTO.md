# FASE 10 — Implantação piloto

## Objetivo
Disponibilizar o Controle de Ponto Potiguar em ambiente piloto controlado, com endereço HTTPS, PostgreSQL persistente, armazenamento biométrico privado, backups e administrador inicial.

## Decisão de arquitetura
O piloto será implantado em servidor Linux com Docker Compose. Esta opção preserva compatibilidade com `face_recognition`, PostgreSQL, volumes persistentes, scripts de backup e armazenamento biométrico privado. Plataformas serverless sem disco persistente não são o alvo principal desta fase.

## Fluxo de implantação
1. Provisionar servidor Linux.
2. Instalar Docker Engine e Docker Compose.
3. Configurar DNS e HTTPS.
4. Criar segredos fora do repositório.
5. Subir PostgreSQL e aplicação com volumes persistentes.
6. Executar migrations Alembic.
7. Criar administrador inicial.
8. Cadastrar empresa e obra piloto.
9. Validar câmera, login, RBAC e registro de ponto.
10. Configurar backup recorrente e cópia externa.
11. Executar checklist operacional e emitir aceite do piloto.

## Segredos obrigatórios
- `SECRET_KEY`
- `BIOMETRIC_ENCRYPTION_KEY`
- `DATABASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

Nenhum segredo deve ser versionado no GitHub.

## Critérios de aceite
- URL HTTPS acessível;
- migrations aplicadas;
- `/health` com aplicação e banco em estado saudável;
- administrador consegue autenticar;
- empresa e obra piloto cadastradas;
- registro de ponto validado no celular;
- arquivos biométricos fora de diretório público;
- backup criado e restauração testada;
- logs sem senhas, chaves ou templates biométricos;
- checklist manual aprovado.

## Estado inicial
- `BRANCH=fase-10-implantacao-piloto`
- `PRODUCTION_PUBLIC_REAL_DATA=BLOCKED`
- `PILOT_DEPLOYMENT=IN_PROGRESS`
