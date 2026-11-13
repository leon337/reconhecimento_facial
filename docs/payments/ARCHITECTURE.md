# Potiguar — arquitetura do módulo de conferência de pagamentos (fase 01)

## Objetivo e recorte
Substituir, gradualmente, a operação da planilha por um fluxo web integrado à aplicação existente `leon337/reconhecimento_facial`. **O recorte implementado é exclusivamente temporal:** períodos semanais e jornadas de funcionários já cadastrados. Sem folha monetária, chave PIX, aprovações ou envio bancário.

## Componentes implementados
- **Banco:** `PaymentPeriod` e `PaymentWorkEntry` em `app/payment_models.py`. Isolamento por `company_id` e `worksite_id`; chave composta estável `scope_key` para período sem duplicidade; unique por pessoa/data/período.
- **Migração:** `20261113_10` sobre `20261112_09`, sem alterar tabelas antigas.
- **API Flask:** `GET /admin/pagamentos`, `POST /admin/pagamentos/periodos`, `GET /admin/pagamentos/periodos/<id>`, `POST /admin/pagamentos/periodos/<id>/jornadas`.
- **Cálculo puro:** `app/payment_time.py` opera apenas com entrada, intervalo e saída; horários locais ordenados, precisão de minuto, sem turno noturno/múltiplos intervalos.
- **UI responsiva:** `templates/admin/payments*.html`; menu do painel existente.
- **Segurança:** `PAYMENTS_VIEW` e `PAYMENTS_EDIT` por RBAC; empresa obrigatória; permissões em cada rota; ownership da obra e do funcionário verificado no servidor; POST com CSRF da aplicação; cache HTTP privado; auditoria imutável dos lançamentos. Nenhum campo de remuneração ou PIX é persistido.
- **Testes:** dados totalmente fictícios, verificações de duplicidade, proteção CSRF, isolamento entre empresas e obras, períodos e jornadas inválidas, registro e auditoria.

## Fluxo de domínio
```
Usuário autenticado (empresa definida)
  → período de 7 dias (rascunho)
  → seleção de funcionário EXISTENTE do escopo
  → horário validado (4 marcos no mesmo dia)
  → minutos calculados no servidor
  → registro único e evento de auditoria
  → painel de conferência de horas
  → [SEM TOTAL MONETÁRIO / SEM PAGAMENTO]
```

## Regras preservadas e decisões não tomadas
- Tempo trabalhado = (início intervalo - entrada) + (saída - fim intervalo), com horários estritamente crescentes.
- Não se estima tarifa com base em nomes de colunas da planilha.
- Não se aplica automaticamente adicional noturno, domingo, feriado, desconto, banco de horas ou direitos trabalhistas; decisões dependem do tipo de vínculo, contratos e validação legal/contábil.
- Escopo por `Employee` existente, para evitar base paralela de pessoas.
- Não há operação destrutiva de exclusão/alteração de jornadas nesta fase; correções requerem desenho de retificação auditável posterior.

## Próximas fases
1. Reconciliação da semântica de cada coluna e fórmulas de todas as cinco fontes com casos revisados.
2. Cadastro de regras/tarifas por vínculo e vigência, sem hardcode de valores.
3. Motor de cálculo financeiro determinístico com `Decimal`, evidência de origem, tolerâncias e cenários extremos.
4. Aprovação segregada, comprovantes e conciliação, com gates explícitos. Nenhuma transferência automática antes de autorização específica.
5. Importação progressiva auditada e UX de operadores; revisão visual em celular.
