# Segurança e LGPD

## Objetivo

Definir a base de conformidade, segurança e governança para o tratamento de dados pessoais no sistema Controle de Ponto Potiguar.

> Este documento é uma referência técnica inicial e não substitui validação jurídica antes da produção.

## Escopo atual

Durante desenvolvimento e homologação devem ser usados somente nomes fictícios, rostos genéricos, dados sintéticos e bancos descartáveis.

Dados biométricos reais permanecem proibidos até a conclusão da revisão jurídica, das medidas técnicas de proteção e do checklist de produção.

## Matriz de dados

| Dado | Classificação | Finalidade | Proteção mínima | Retenção | Acesso |
|---|---|---|---|---|---|
| Nome | Dado pessoal | Identificação do trabalhador | HTTPS, controle de acesso e banco protegido | Conforme necessidade trabalhista e política aprovada | RH e administradores autorizados |
| Matrícula | Dado pessoal | Identificação interna | HTTPS, controle de acesso e banco protegido | Conforme necessidade trabalhista | RH e administradores autorizados |
| Cargo/função | Dado pessoal | Gestão e relatórios | Controle de acesso | Durante o vínculo e prazo aprovado | RH e administradores autorizados |
| Foto facial | Dado pessoal sensível/biométrico | Cadastro biométrico | Criptografia em trânsito e em repouso, acesso restrito | Somente enquanto necessária e autorizada | Administradores biométricos autorizados |
| Encoding facial | Dado pessoal sensível/biométrico | Comparação facial | Criptografia forte, segregação e acesso restrito | Somente enquanto necessário e autorizado | Serviço de reconhecimento e administradores autorizados |
| Registros de entrada e saída | Dado pessoal | Controle de jornada | Integridade, auditoria e controle de acesso | Conforme obrigação legal e política aprovada | RH e administradores autorizados |
| Banco de horas | Dado pessoal | Gestão da jornada | Integridade, auditoria e controle de acesso | Conforme obrigação legal | RH e administradores autorizados |
| Logs de autenticação e operação | Dado pessoal/operacional | Segurança e auditoria | Proteção contra alteração e acesso restrito | Prazo mínimo necessário definido em política | Administradores de segurança |
| IP, navegador e dispositivo | Dado pessoal/técnico | Segurança e diagnóstico | Minimização e acesso restrito | Prazo mínimo necessário | Administradores de segurança |

## Princípios obrigatórios

- finalidade específica e documentada;
- minimização da coleta;
- separação entre desenvolvimento, homologação e produção;
- acesso por menor privilégio;
- rastreabilidade das operações administrativas;
- retenção limitada e descarte seguro;
- resposta documentada a incidentes;
- proibição de segredos, bancos e biometrias reais no Git.

## Requisitos antes da produção

- [ ] base legal e documentos aplicáveis validados juridicamente;
- [ ] responsáveis pelo tratamento e atendimento aos titulares definidos;
- [ ] HTTPS obrigatório;
- [ ] criptografia dos dados biométricos em repouso;
- [ ] chaves fora do repositório e com rotação definida;
- [ ] PostgreSQL ou banco de produção protegido e separado;
- [ ] logs de auditoria para operações administrativas;
- [ ] política de retenção e exclusão aprovada;
- [ ] backup criptografado e restauração testada;
- [ ] processo de incidente e comunicação aprovado;
- [ ] dados sintéticos removidos do ambiente de produção;
- [ ] revisão do histórico Git ou criação de repositório limpo;
- [ ] testes de segurança, integração e recuperação aprovados.

## Operações proibidas

- armazenar dados biométricos reais sem proteção adequada;
- versionar banco de dados, fotos ou encodings reais;
- reutilizar dados de produção em testes;
- compartilhar backups sem criptografia;
- permitir acesso administrativo sem autenticação e autorização;
- realizar deploy de produção enquanto os requisitos deste documento estiverem pendentes.

## Estado

```text
LGPD_MATRIX=BASELINE_DOCUMENTED
REAL_BIOMETRIC_DATA=PROHIBITED
PRODUCTION_DEPLOY=BLOCKED_PENDING_COMPLIANCE
LEGAL_REVIEW=PENDING
HISTORICAL_DATA_REVIEW=PENDING
```
