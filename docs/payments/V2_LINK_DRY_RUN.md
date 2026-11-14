# Potiguar — Fase 04: associação simulada ao cadastro de funcionários V2

## Integração real do código e pontos de entrada

A função de prévia consulta **os modelos existentes da Potiguar V2**, não uma base paralela:

- `Employee` (`employees`): ID interno, nome funcional, empresa, obra, ativo.
- `EmployeeOnboarding` (`employee_onboarding`): **somente existência da ficha por employee_id e company_id**, sem ler nem descriptografar `encrypted_payload`.
- Endpoint integrado `/admin/pagamentos/importacoes/analisar` no mesmo blueprint administrativo da V2.
- Novo comando **Conferir com cadastro V2** no formulário de importação da área de pagamentos.
- Novo link na tela `/admin/users` (lista dos funcionários V2) para usuários autorizados.
- Nenhuma nova tabela, migração, credencial, usuário ou repositório de funcionários criado.

## Fluxo da simulação

```
Usuário com PAYMENTS_EDIT e company_id
  → upload XLSX (12 MiB + proteção ZIP/XML já existente)
  → preflight seguro e mapeamento de cabeçalhos
  → escolher escopo empresa/obra autorizado
  → ler SOMENTE coluna textual de funcionários da aba de resumo
     - caso cabeçalho mesclado A3:B3, localizar nomes em B
     - não interpretar fórmulas, valores, CPF ou PIX
  → consultar Employee + existência de EmployeeOnboarding do mesmo tenant
  → normalizar nomes em memória e comparar por igualdade estrita
  → classificar inconsistências, exibir contagens e números de linhas
  → descartar nomes em memória ao fim da requisição, sem commit em banco
```

## Categorias de resposta
- `v2_match`: nome normalizado único, funcionário ativo, ficha V2 presente. **Hipótese de correspondência, não identidade comprovada ou vínculo persistido.**
- `unmatched`: nome não encontrado no escopo autorizado.
- `legacy_only`: nome único pertence a funcionário sem ficha V2.
- `inactive`: funcionário encontrado, mas inativo.
- `ambiguous`: mais de um funcionário com mesmo nome normalizado.
- `duplicate_source`: identificação repetida dentro do resumo da planilha (indício de duplicidade, não veredito sobre cadastro).
- `invalid_source`: campo do nome não confiável, numérico, em fórmula ou normalização rejeitada.

## Segurança

1. A rota exige `PAYMENTS_EDIT` e empresa vinculada. Obra selecionada pertence à mesma empresa; usuário preso a uma obra não pode escolher outra.
2. Query V2 faz `Employee.company_id == user.company_id`, e `EmployeeOnboarding.company_id == Employee.company_id`; `worksite_id` limita empregados quando selecionado.
3. Leitura no banco é apenas de `id`, `name`, `active` e existência da ficha; nenhum `CPF`, `pix_key`, `salary`, `hour_value` nem campo criptografado é acessado.
4. Resultado em HTML contém somente status e número da linha (até 75 linhas visíveis), jamais nomes de funcionários ou dados PIX da planilha.
5. Limites: 1.600 linhas do resumo, 1.000 identidades por arquivo, 10.000 funcionários da empresa/obra e único cabeçalho confiável.
6. Conteúdo da planilha não é armazenado em banco ou logs operacionais; resposta HTTP `Cache-Control: private, no-store`; POST com CSRF.
7. `can_commit=False` por contrato; **não há endpoint de confirmar importação**.
8. Suítes de regressão de onboarding V2 foram executadas junto das suites do módulo de pagamentos.

## Observações da fonte real (Ajudantes)
Na planilha real, o cabeçalho “FUNCIONÁRIOS” ocupa o intervalo mesclado `A3:B3`. Os dados textuais de trabalhadores aparecem em `B`, não em `A`. A correção foi comprovada por inspeção estrutural sem imprimir valores pessoais.

Um smoke sem conectar ao banco real indicou **156 células identificadoras candidatas**, sendo 45 ocorrências em grupos repetidos, 8 inválidas e 103 sem correspondência porque o cadastro fornecido à simulação estava **vazio**. Esses números não são resultado de associação à V2 real e não constituem um parecer sobre pagamentos.

## Pendências explícitas
- Revisão da política de identidade com responsáveis de RH/contabilidade, inclusive homônimos e registros de terceiros.
- Eventual importação efetiva exigirá contrato de autorização, verificação adicional e rastreabilidade por fonte + versão.
- Reconciliação financeira, regras de diária/hora, adicionais, descontos, jornadas e PIX permanecem fora de escopo.
- Como as PRs de fases 02/03 são drafts empilhadas, esse código só estará navegável em V2 hospedada após integração governada, CI e homologação. **Não afirmar deploy**.
