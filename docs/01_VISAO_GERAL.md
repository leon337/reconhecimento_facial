# Visão Geral — Controle de Ponto Potiguar

## 1. Objetivo

O Controle de Ponto Potiguar é uma aplicação web em Flask para cadastro de colaboradores, autenticação administrativa, reconhecimento facial e registro de ponto. O projeto também contém regras de jornada, tolerâncias, banco de horas e fechamento mensal.

## 2. Escopo atual

A versão atual cobre:

- cadastro e administração de usuários;
- autenticação da área administrativa;
- cadastro e comparação facial;
- registro de ponto;
- bloqueio de batidas duplicadas;
- cálculo diário de jornada;
- tolerâncias configuráveis;
- consolidação de banco de horas;
- fechamento mensal;
- testes automatizados e CI;
- execução local, por Gunicorn e por Docker.

Não fazem parte do escopo concluído desta fase:

- folha de pagamento;
- aplicativo móvel nativo;
- multiempresa e múltiplas obras;
- geolocalização;
- persistência definitiva do fechamento mensal;
- deploy de produção já autorizado.

## 3. Público-alvo

- administradores e responsáveis pelo ponto;
- setor de recursos humanos;
- colaboradores que registram a jornada;
- desenvolvedores e operadores responsáveis pela manutenção.

## 4. Tecnologias principais

- Python e Flask;
- Flask-SQLAlchemy e SQLAlchemy;
- Flask-WTF e proteção CSRF;
- `face-recognition`, `dlib`, NumPy e Pillow;
- SQLite como padrão local;
- Gunicorn para execução do servidor;
- Docker para empacotamento;
- Pytest e GitHub Actions para validação.

## 5. Fluxo geral

```text
Administrador cadastra colaborador
              │
              ▼
      Biometria é cadastrada
              │
              ▼
Colaborador apresenta o rosto
              │
              ▼
 Sistema compara a representação facial
              │
              ▼
   Regras de ponto validam a batida
              │
              ▼
 Jornada e banco de horas são calculados
```

O pipeline funciona como uma linha de montagem: cada etapa recebe um resultado validado da etapa anterior. Uma falha no reconhecimento ou nas regras de ponto deve interromper o fluxo antes da persistência.

## 6. Segurança e privacidade

Dados biométricos são dados pessoais sensíveis. O desenvolvimento e os testes devem usar apenas dados sintéticos ou fictícios. Produção depende de revisão jurídica, criptografia adequada, política de retenção, controle de acesso, auditoria e plano de resposta a incidentes.

Consulte `docs/07_SEGURANCA_E_LGPD.md`.

## 7. Testes

O projeto deve manter:

- testes unitários para regras de jornada, tolerâncias e banco de horas;
- testes de integração para rotas, autenticação e registro de ponto;
- validação de sintaxe;
- build Docker no CI.

## 8. Limitações conhecidas

- SQLite é adequado ao desenvolvimento, mas não é a escolha recomendada para produção concorrente;
- o reconhecimento depende da qualidade da imagem e do ambiente;
- biometria real não deve ser usada em desenvolvimento;
- o fechamento mensal ainda precisa de estratégia definitiva de persistência e governança operacional.

## 9. Evoluções futuras

- múltiplas empresas e obras;
- geolocalização;
- justificativas e correções com aprovação;
- relatórios avançados;
- integração com folha de pagamento;
- aplicativo móvel;
- reconhecimento offline e sincronização posterior.
