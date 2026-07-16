# 10 — Manual do Administrador

## 1. Objetivo

Orientar o administrador no acesso ao painel, cadastro de funcionários e registro biométrico. Este manual descreve somente funções existentes ou claramente previstas no estado atual do sistema.

## 2. Pré-requisitos

- aplicação em execução;
- usuário com papel `admin` criado;
- acesso autorizado ao painel;
- navegador atualizado;
- HTTPS obrigatório em produção;
- autorização interna para tratamento de dados pessoais e biométricos.

## 3. Acesso ao painel

Abra:

```text
/admin/login
```

Informe usuário e senha administrativos.

Somente contas com papel `admin` podem entrar. Credenciais inválidas retornam mensagem de erro e não criam sessão.

Após a autenticação, o sistema direciona para a lista de usuários.

## 4. Encerrar sessão

Use a ação de logout do painel.

O logout:

- limpa a sessão administrativa;
- encerra o acesso atual;
- redireciona para a página de login.

Não compartilhe sessões ou credenciais.

## 5. Consultar usuários

A lista administrativa fica em:

```text
/admin/users
```

A tela apresenta os usuários cadastrados e permite acessar o fluxo de biometria de cada colaborador.

## 6. Cadastrar funcionário

Acesse:

```text
/admin/users/new
```

Preencha os campos disponíveis:

- nome de usuário;
- senha inicial;
- nome completo;
- matrícula;
- função;
- jornada;
- endereço;
- tipo de passagem.

Confirme o cadastro.

O sistema armazena a senha como hash. A senha original não deve ser registrada em planilhas, mensagens ou documentos.

### Boas práticas

- use matrícula única;
- não reutilize contas;
- cadastre uma pessoa por usuário;
- revise a jornada antes de salvar;
- use dados fictícios em desenvolvimento e homologação.

## 7. Formato da jornada

Formatos aceitos pela regra atual:

```text
08:00-17:00
```

ou com intervalo:

```text
08:00-12:00,13:00-17:00
```

Registros fora do formato esperado podem impedir cálculos corretos.

## 8. Cadastrar biometria

Na lista de usuários, abra o cadastro biométrico do funcionário.

O endpoint administrativo correspondente segue o formato:

```text
/admin/users/<id>/biometric
```

Envie uma imagem JPEG ou PNG válida.

O sistema:

```text
recebe arquivo
→ valida extensão
→ valida conteúdo real da imagem
→ gera nome aleatório
→ detecta o rosto
→ gera encoding facial
→ vincula biometria ao usuário
```

### Requisitos da imagem

- apenas uma pessoa;
- rosto visível;
- boa iluminação;
- sem desfoque forte;
- sem obstrução relevante;
- enquadramento frontal sempre que possível.

### Mensagens possíveis

| Mensagem | Significado |
|---|---|
| Arquivo inválido | Arquivo ausente ou extensão não permitida |
| O conteúdo enviado não é uma imagem JPEG ou PNG válida | O arquivo não corresponde ao formato declarado |
| Não foi possível processar a imagem | Falha de leitura ou processamento |
| Nenhum rosto detectado | A imagem não gerou encoding facial |
| Biometria cadastrada com sucesso | Cadastro concluído |

## 9. Proteção dos dados biométricos

A biometria é dado pessoal sensível.

O administrador deve:

- limitar acesso ao painel;
- evitar cópias locais desnecessárias;
- não enviar fotos por aplicativos de mensagem;
- não usar dados reais em testes;
- respeitar a política de retenção;
- registrar exclusão quando o tratamento deixar de ser necessário;
- comunicar incidentes ao responsável definido pela empresa.

## 10. Registro de ponto do funcionário

O painel administrativo não deve registrar o ponto em nome do colaborador como procedimento normal.

O fluxo operacional ocorre em:

```text
/punch
```

O sistema aceita somente:

```text
ENTRADA
SAIDA
```

Uma batida dentro da janela configurada é bloqueada para evitar duplicidade.

## 11. Jornada e banco de horas

A lógica atual permite calcular:

- duração prevista;
- duração trabalhada;
- atraso;
- saída antecipada;
- saldo diário;
- crédito;
- débito;
- saldo acumulado;
- dias incompletos.

Tolerâncias padrão:

```text
ATRASO=5 minutos
HORA_EXTRA=10 minutos
SALDO=5 minutos
```

Dias com número ímpar de registros são considerados incompletos e impedem o fechamento mensal.

## 12. Fechamento mensal

O fechamento mensal somente pode ocorrer quando:

- todos os resultados pertencem ao mês informado;
- não há registros incompletos;
- créditos e débitos foram consolidados;
- saldo anterior foi informado corretamente.

No estado atual, a persistência definitiva do fechamento e a interface administrativa correspondente ainda não estão concluídas. Não trate um cálculo isolado como fechamento jurídico definitivo.

## 13. Funções ainda não disponíveis no painel

- edição completa de usuário;
- exclusão administrativa completa;
- correção manual auditável de ponto;
- justificativa de ausência;
- exportação de relatórios;
- fechamento mensal pela interface;
- restauração de backup pela interface;
- gestão granular de permissões.

Essas funções devem ser documentadas novamente quando forem implementadas.

## 14. Procedimento em caso de erro

```text
1. Não repetir ações várias vezes.
2. Registrar data, horário e mensagem exibida.
3. Confirmar usuário e ambiente.
4. Verificar logs sem expor dados pessoais.
5. Abrir ocorrência técnica.
6. Não editar diretamente o banco de produção.
```

## 15. Checklist diário do administrador

```text
□ aplicação acessível
□ login administrativo funcional
□ câmera operacional
□ relógio do servidor correto
□ armazenamento disponível
□ logs sem erro crítico
□ backups recentes confirmados
□ nenhum dado real em ambiente de teste
```

## 16. Segurança

- não use senha padrão em produção;
- não compartilhe conta administrativa;
- não desative CSRF;
- não exponha a aplicação sem HTTPS;
- não versione `.env`, banco ou uploads reais;
- não altere registros diretamente no SQLite ou PostgreSQL;
- mantenha backup criptografado e restauração testada.
