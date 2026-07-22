# LEA-125 — Relatório Final de Análise Crítica e Escopo Implementável

**Projeto:** Controle de Ponto Potiguar  
**Repositório:** `leon337/reconhecimento_facial`  
**Issue principal:** LEA-125  
**Subtarefas cobertas:** LEA-126 a LEA-132  
**Modo:** `ANÁLISE_CRÍTICA / SOMENTE LEITURA`  
**Implementação:** `PROIBIDA`  
**GitHub alterado:** `NO`  
**Linear alterado:** `NO`  
**Roadmap aprovado:** `NO — PROPOSTA APENAS`  

> Este documento não é parecer jurídico e não declara conformidade do produto ou de concorrentes.

## Fontes e método

- Fonte principal: **Resumo Executivo.pdf**, 31 páginas, especialmente p. 2–17, 25–26 e 27–30.
- Fonte técnica oficial: `CHECKPOINT.md`, `PROJECT_STATE.md`, código da `main`, modelos, rotas, documentação de fases e PRs do repositório.
- Fonte de governança: LEA-125, LEA-126–132 e LEA-85 no Linear.
- Verificação normativa: Portaria MTP nº 671/2021 e perguntas e respostas do MTE; LGPD art. 11; orientações da ANPD; Lei nº 14.063/2020.
- Regra de evidência: o relatório de mercado sugere candidatos; GitHub/Linear definem o estado real do CPP; itens jurídicos ficam como `EXIGE_VALIDAÇÃO_JURÍDICA`.

## 1. Resumo executivo

Foram consolidadas **84 funcionalidades candidatas**. O relatório é útil como inventário de mercado, porém não é confiável como fonte única de estado técnico, conformidade ou prioridade.

### Conclusões centrais

1. O CPP está mais avançado do que o PDF afirma em segurança e biometria: possui Flask/Gunicorn, PostgreSQL/Alembic, isolamento por empresa/obra, RBAC, template biométrico cifrado, liveness passivo multiquadro, auditoria, backup/restore e HTTPS local.
2. O CPP está menos avançado do que a matriz afirma em operação de RH: não há fluxo completo de intervalos, correções/aprovações, relatórios, comprovantes persistentes, fechamento por interface, offline, GPS/geofence, API ou integrações.
3. Existe uma separação crítica entre **modelo entregue** e **funcionalidade operacional**: `AttendanceEvent`, `AttendanceAdjustment` e `AttendanceClosure` existem, mas a rota viva ainda grava a tabela legada `Ponto` e não expõe o workflow completo.
4. A FASE 10.1.1 tem validação funcional aprovada, mas a homologação estatística continua adiada. A ampliação deve preservar esse bloqueio.
5. O primeiro passo recomendado não é copiar o roadmap do PDF. É fechar a dívida da FASE 10.1.1, decidir o papel regulatório do produto e convergir o registro vivo para o domínio imutável.
6. PAdES, REP-P, AFD, AEJ, retenção e base legal não podem ser tratados como checklist genérico. Dependem da arquitetura e de validação especializada.

### Distribuição pelo estado real

| Estado | Quantidade | Interpretação |
|---|---:|---|
| ENTREGUE | 15 | evidência técnica suficiente na `main`/piloto |
| PARCIAL | 22 | há modelo, componente ou fluxo incompleto |
| NÃO IMPLEMENTADO | 34 | não foi localizado no estado oficial |
| NÃO VERIFICADO | 0 | evidência insuficiente para classificar |
| NÃO RECOMENDADO | 5 | fora do núcleo ou risco desproporcional |
| EXIGE_VALIDAÇÃO_JURÍDICA | 8 | não pode ser decidido apenas por engenharia |
