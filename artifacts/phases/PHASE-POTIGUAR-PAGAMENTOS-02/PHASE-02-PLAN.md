# Plano — Potiguar Pagamentos Fase 02

Missão MCF-POTIGUAR-PAGAMENTOS-20261113 (Issue #522). Orquestração MESTRE; autoridade final LEANDRO; risco Classe C.

Objetivo: oferecer diagnóstico técnico não persistente das planilhas Excel e acelerar a validação de grandes massas sintéticas de jornadas usando GPU local.

Escopo: parser ZIP/XML com limites, rota Flask protegida por RBAC e CSRF, UI responsiva, testes HTTP, teste GPU independente e documentação auditável. Arquivo original do Drive é insumo de leitura, não base confiável de cálculo.

Fora do escopo: importar células reais, associar funcionários automaticamente, inferir salários, efetuar transferências ou implantar em produção.

Aceite: arquivos .xlsx válidos suportados até 12 MiB, resposta agregada sem PII, rejeição de anexos suspeitos, 100% dos testes selecionados, cenário GPU sem divergências, PRF com manifesto e branch isolada. Gate contábil e humano para fases posteriores.