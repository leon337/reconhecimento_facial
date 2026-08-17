# NF-01 — Design Lab

Laboratório visual isolado da NF-01.

```text
CANONICAL_APPSHELL=ONE
CURRENT_APPSHELL_OWNER=assets/app-shell.css+app-shell.js
CURRENT_APPSHELL_VERSION=i8
LEGACY_SHELL_OWNER=assets/legacy-shell.css+legacy-shell.js
DASHBOARD_SHARED_APPSHELL=YES
EMPLOYEES_SHARED_APPSHELL=YES
ONBOARDING_SHARED_APPSHELL=YES
I7_LEGACY_SHELL_QUARANTINE=COMPLETE
I8_APPSHELL_STRUCTURAL_ACCEPTANCE=COMPLETE
I8_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_HARDENING
ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
HISTORICAL_V1=screens/03.03-novo-funcionario.html
HISTORICAL_V1_PRESERVED=YES
HISTORICAL_V1_MIGRATED=NO
NEXT_OFFICIAL_ITEM=I9_PHASE_I_CLOSEOUT_GATE
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR_MERGE=NOT_AUTHORIZED
```

I8 endureceu o bootstrap para exigir exatamente um `<main data-app-shell-content>` e corrigiu o conjunto de foco do overlay mobile, excluindo controles ocultos e preservando corretamente o gatilho antes de aplicar `inert` ao conteúdo.

A aceitação I8 é source-level. Matriz visual 360/768/1024/1440+, larguras intermediárias, zoom 200%, screen reader, a11y automatizada, novos testes unitários/integrados e production E2E continuam não executados.
