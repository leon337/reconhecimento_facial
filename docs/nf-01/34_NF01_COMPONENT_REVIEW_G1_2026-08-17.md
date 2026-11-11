# NF-01 — Component Review G1 — CameraPanel

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
G1_CAMERA_PANEL=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_G_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=G2_PUNCH_RESULT_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `CameraPanel` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`CameraPanel` controla a experiência visual e operacional de captura por câmera. Ele não é o mecanismo de reconhecimento facial, liveness, identidade ou persistência biométrica.

```text
CÂMERA
  ↓
CameraPanel
  ↓
FRAME / CAPTURE
  ↓
quality / liveness / recognition
  ↓
domain result
```

```text
CAMERA_PANEL != FACE_RECOGNITION_ENGINE
CAMERA_PANEL != LIVENESS_ENGINE
CAMERA_PANEL != IDENTITY_ENGINE
CAMERA_PANEL != BIOMETRIC_STORAGE_ENGINE
CAMERA_PANEL != QUALITY_ENGINE
```

## Contextos suportados

```text
ENROLLMENT................................. SUPPORTED
PUNCH...................................... SUPPORTED
ENROLLMENT != IDENTIFICATION
```

No enrollment, a identidade alvo já é conhecida e autorizada; no punch, a captura alimenta identificação e posterior persistência do evento de ponto.

## Estados canônicos

```text
REQUESTING_PERMISSION
PERMISSION_DENIED
CAMERA_UNAVAILABLE
INITIALIZING
READY
CAPTURING
QUALITY_CHECK
LIVENESS_CHECK
PROCESSING
RECOVERABLE_FAILURE
BLOCKING_FAILURE
```

Sucesso de captura não equivale a sucesso de registro de ponto.

```text
CAMERA_CAPTURE_SUCCESS != PUNCH_SUCCESS
FACE_MATCH_SUCCESS != PUNCH_PERSISTENCE_SUCCESS
```

## Permissão e disponibilidade

```text
PERMISSION_DENIED != CAMERA_UNAVAILABLE
USER_DENIED_PERMISSION != DEVICE_NOT_FOUND
DEVICE_BUSY != USER_DENIED_PERMISSION
BROWSER_BLOCKED != CAMERA_BROKEN
```

A UI deve distinguir os estados semanticamente sem expor exceções técnicas brutas.

## Preview e stream real

```text
LIVE_PREVIEW => ACTUAL_ACTIVE_STREAM
FROZEN_FRAME != LIVE_CAMERA
STREAM_STOPPED => UPDATE_CAMERA_STATE
CAMERA_ACTIVE_LABEL => SOURCE_ACTUAL_STREAM_STATE
```

Um último frame congelado nunca pode continuar sendo apresentado como câmera ativa.

## Estado textual e orientação

O preview visual deve sempre ser acompanhado por estado textual e instrução contextual, como inicialização, câmera pronta, posicionamento, qualidade, processamento e falha recuperável.

```text
GUIDE_OVERLAY != FACE_DETECTION_RESULT
CAMERA_PANEL != FACE_DETECTION_ENGINE
```

Molduras e overlays são orientação visual; não representam detecção real sem sinal canônico do engine.

## Qualidade e liveness

```text
QUALITY_ENGINE
      ↓
CANONICAL_QUALITY_STATE
      ↓
CameraPanel

LIVENESS_ENGINE
      ↓
CANONICAL_LIVENESS_STATE
      ↓
CameraPanel
```

```text
CAMERA_PANEL != QUALITY_DECISION
CAMERA_PANEL != LIVENESS_DECISION
NO_LIVENESS_RESULT != LIVENESS_PASSED
```

A UI pode orientar sobre rosto distante, iluminação, enquadramento, múltiplas faces ou movimento apenas quando esses estados forem fornecidos pelo pipeline apropriado.

## Captura automática, manual e progresso

```text
AUTO_CAPTURE................................. SUPPORTED_WHEN_CANONICAL_CONDITIONS_MET
MANUAL_CAPTURE............................... SUPPORTED_WHEN_FLOW_WARRANTS
MULTI_CAPTURE_ENROLLMENT..................... SUPPORTED
CAPTURE_PROGRESS............................. REAL_ONLY
FABRICATED_PROGRESS......................... PROHIBITED
```

Captura automática não deve disparar por timer visual sem condição canônica válida.

## Privacidade e persistência

```text
PREVIEW != CAPTURE
CAPTURE != BIOMETRIC_TEMPLATE
BIOMETRIC_TEMPLATE != ENROLLMENT_CONFIRMED
NO_UNAUTHORIZED_FRAME_PERSISTENCE
NO_FRAME_IN_LOCALSTORAGE
NO_FRAME_IN_SESSIONSTORAGE
NO_RAW_FRAME_IN_LOGS_OR_ANALYTICS
PREVIOUS_USER_FRAME_RESIDUE => PROHIBITED
NEXT_USER => CLEAR_PERSON_SPECIFIC_TRANSIENT_STATE
```

O componente não persiste imagens por conveniência e não deixa resíduos de uma sessão para a próxima em dispositivos compartilhados.

## Fluxo biométrico normal

```text
NORMAL_BIOMETRIC_FLOW => LIVE_CAMERA
GALLERY_UPLOAD => OUTSIDE_NORMAL_BIOMETRIC_FLOW
```

Upload/galeria não entram como alternativa automática ao fluxo biométrico ao vivo.

## Seleção e troca de câmera

```text
CAMERA_SWITCH............................... SUPPORTED_WHEN_SAFE
ASSUME_DEVICE_0_IS_FRONT_CAMERA............. PROHIBITED
SWITCH_DURING_CAPTURING_PROCESSING.......... PROHIBITED
```

A escolha do dispositivo deve considerar câmeras disponíveis e contexto real do dispositivo.

## Ciclo de vida

```text
PANEL_CLOSED => STOP_MEDIA_TRACKS
PANEL_CLOSED => RELEASE_CAMERA_STREAM
DEVICE_DISCONNECT => REVALIDATE_STATE
TAB_RESUME => REVALIDATE_WHEN_NEEDED
```

A câmera não deve permanecer ativa após a superfície deixar de utilizá-la.

## Processamento e duplicidade

```text
CAPTURING_OR_PROCESSING => DUPLICATE_CAPTURE_BLOCKED
CAPTURED_FRAME != LIVE_PREVIEW
REQUEST_FAILED != RECOGNITION_FAILED
REQUEST_FAILED != OPERATION_FAILED
```

Timeout de processamento não autoriza declarar reconhecimento ou registro de ponto como falho sem classificação canônica.

## Reconhecimento e punch

```text
CAMERA_FAILURE != QUALITY_FAILURE
QUALITY_FAILURE != LIVENESS_FAILURE
LIVENESS_FAILURE != IDENTITY_NO_MATCH
IDENTITY_NO_MATCH != PUNCH_OPERATION_FAILURE
FACE_MATCH_SUCCESS != PUNCH_PERSISTENCE_SUCCESS
```

Para punch:

```text
capture
  ↓
recognition confirmed
  ↓
identity confirmed
  ↓
punch persisted
  ↓
PunchResult
```

Somente `PunchResult` deve representar o resultado final do registro de ponto.

## No-match e múltiplos rostos

```text
NO_MATCH => NO_IDENTITY_GUESS
NO_MATCH => NO_CANDIDATE_NAME_LEAK
MULTIPLE_FACES => NO_SILENT_PERSON_SELECTION
```

O componente não adivinha identidade nem escolhe silenciosamente um rosto entre vários.

## RBAC e escopo

```text
ADMIN_ENROLLMENT_CONTEXT != EMPLOYEE_PUNCH_CONTEXT
RBAC_TENANT_EMPLOYEE_SCOPE => BEFORE_ENROLLMENT_OPERATION
BACKEND_REVALIDATION => REQUIRED
```

O `CameraPanel` não substitui autorização. Enrollment administrativo e punch possuem contextos de autorização diferentes.

## Mensagens e diagnóstico

```text
USER_MESSAGE != INTERNAL_CAMERA_DIAGNOSTIC
RAW_BROWSER_EXCEPTION_TO_USER............... PROHIBITED
RAW_LIVENESS_SCORE_TO_USER.................. PROHIBITED
RAW_EMBEDDING_OR_TEMPLATE_TO_USER........... PROHIBITED
```

Detalhes técnicos podem existir em logs seguros e minimizados, nunca como mensagem operacional bruta.

## Acessibilidade e responsividade

```text
TEXTUAL_STATE............................... REQUIRED
TEXTUAL_INSTRUCTIONS........................ REQUIRED
KEYBOARD_ACTIONS............................ REQUIRED
FOCUS_VISIBLE............................... REQUIRED
COLOR_ONLY_STATUS........................... PROHIBITED
FRAME_BY_FRAME_ANNOUNCEMENT................. PROHIBITED
MATERIAL_STATE_CHANGE_ANNOUNCEMENT.......... CONTEXTUAL
REDUCED_MOTION.............................. REQUIRED
RESPONSIVE_PREVIEW.......................... REQUIRED
VIDEO_ASPECT_RATIO.......................... PRESERVE
```

O fluxo não pode depender apenas da imagem. Mudanças de estado materiais podem ser anunciadas, mas não cada frame ou microvariação de qualidade.

## Conectividade e degradação

```text
CAMERA_AVAILABLE != RECOGNITION_SERVICE_AVAILABLE
CAMERA_READY != SYSTEM_READY
```

A câmera local pode estar pronta enquanto serviços de reconhecimento estão degradados. A UI deve refletir essas dimensões separadamente e usar `DegradationBanner`/estado bloqueante conforme fallback real.

## Observabilidade e segurança

```text
OBSERVABILITY => METADATA_MINIMIZATION
RAW_BIOMETRIC_IMAGE_IN_TELEMETRY............ PROHIBITED
BIOMETRIC_TEMPLATE_IN_TELEMETRY............. PROHIBITED
```

Métricas operacionais agregadas podem existir futuramente sem capturar conteúdo biométrico bruto.

## Contrato congelado

```text
G1_CAMERA_PANEL

live camera experience....................... YES
face recognition engine...................... NO
liveness engine.............................. NO
identity engine.............................. NO
biometric storage engine..................... NO
ENROLLMENT................................... YES
PUNCH........................................ YES
ENROLLMENT = IDENTIFICATION.................. NO
permission states............................ YES
PERMISSION_DENIED = CAMERA_UNAVAILABLE....... NO
actual live preview.......................... YES
frozen frame presented as live............... NO
textual camera state......................... YES
guide overlay................................ YES
guide = real detection....................... NO
quality feedback............................. YES from engine
CameraPanel decides quality.................. NO
liveness feedback............................ YES from engine
CameraPanel decides liveness................. NO
NO_LIVENESS_RESULT = PASSED.................. NO
auto capture................................. YES when canonical conditions met
manual capture............................... YES when flow warrants
multi-capture enrollment..................... YES
fake progress................................ NO
unauthorized frame persistence............... NO
localStorage/sessionStorage image............ NO
previous-user frame residue.................. NO
live camera normal biometric flow............ YES
gallery/upload normal flow................... NO
camera switch................................ YES when safe
switch during unsafe processing.............. NO
panel close → release stream................. YES
device disconnect revalidation............... YES
PROCESSING duplicate capture................. NO
REQUEST_FAILED = RECOGNITION_FAILED.......... NO
FACE_MATCH_SUCCESS = PUNCH_SUCCESS............ NO
NO_MATCH → identity guessing................. NO
MULTIPLE_FACES → silent selection............ NO
Camera ready = system ready.................. NO
camera available = recognition available..... NO
RBAC before enrollment....................... YES
backend revalidation......................... YES
raw biometric diagnostics to user............ NO
raw image in logs/analytics.................. NO
textual accessibility........................ YES
frame-by-frame screen-reader announcement.... NO
reduced motion............................... YES
responsive preview........................... YES
preserve video aspect ratio.................. YES
```

## Testes futuros obrigatórios

### Unitários

- estados de permissão e disponibilidade;
- inicialização, ready, captura e processamento;
- quality/liveness feedback;
- troca de câmera;
- stream encerrado e cleanup;
- bloqueio de captura duplicada.

### Integração

- `CameraPanel + browser permissions`;
- `CameraPanel + quality engine`;
- `CameraPanel + liveness`;
- `CameraPanel + recognition`;
- enrollment;
- `CameraPanel + PunchResult`;
- `CameraPanel + ErrorState`;
- `CameraPanel + DegradationBanner`.

### Segurança e privacidade

- nenhum frame em logs, analytics, localStorage ou sessionStorage;
- ausência de resíduos do usuário anterior;
- RBAC do enrollment;
- isolamento por tenant;
- transporte seguro quando remoto;
- ausência de diagnóstico biométrico bruto na UI.

### Dispositivos

- webcam desktop/notebook;
- navegador mobile;
- câmera frontal/traseira;
- desconexão do dispositivo;
- mudança de orientação;
- background/resume.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- reduced motion;
- estados textuais;
- ausência de anúncios frame a frame.

## Invariantes preservados

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend/routes=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
NF02=NOT_STARTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PR32_MERGE=NOT_AUTHORIZED
```

## Continuidade

```text
PHASE_F_COMPONENT_REVIEW=COMPLETE
G1_CAMERA_PANEL=FROZEN_INDIVIDUALLY
PHASE_G_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=G2_PUNCH_RESULT_COMPONENT_REVIEW
```
