/** Apenas preparação do rascunho. Não grava funcionário nem senha. */
export const REGISTRATION_FUNCTION_NAME = 'prepare_employee_registration';

export const registrationTool = {
  functionDeclarations: [{
    name: REGISTRATION_FUNCTION_NAME,
    description: [
      'Quando o administrador pedir explicitamente cadastrar ou criar um funcionário,',
      'extraia os dados ditados para um RASCUNHO que o humano deverá revisar.',
      'Esta função NÃO cadastra. Nunca invente dados, senha, CPF, biometria, matrícula ou usuário.',
      'Campos ausentes permanecem vazios e o usuário poderá completar o cartão de revisão.',
    ].join(' '),
    parametersJsonSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Nome completo mencionado pelo usuário (ou vazio).' },
        username: { type: 'string', description: 'Usuário de acesso mencionado (ou vazio).' },
        registration: { type: 'string', description: 'Matrícula mencionada (ou vazio).' },
        job_title: { type: 'string', description: 'Função profissional mencionada (ou vazio).' },
        schedule: { type: 'string', description: 'Horário mencionado (ou vazio).' },
      },
    },
  }],
};

const fieldNames = ['name','username','registration','job_title','schedule'];

export function sanitizeRegistrationDraft(args) {
  const source = args && typeof args === 'object' && !Array.isArray(args) ? args : {};
  const result = {};
  for (const key of fieldNames) {
    const value = source[key];
    result[key] = typeof value === 'string' ? value.trim().slice(0,180) : '';
  }
  return result;
}

export function validRegistrationDraft(draft) {
  const errors = [];
  if (!draft.name || draft.name.trim().length < 3 || draft.name.trim().length > 120) {
    errors.push('Informe o nome completo.');
  }
  if (!/^[a-z][a-z0-9._-]{2,63}$/.test((draft.username || '').trim().toLowerCase())) {
    errors.push('Usuário deve ter 3 a 64 caracteres, começar com letra e usar apenas letras, números, ponto, hífen ou sublinhado.');
  }
  for (const [field, max] of [['registration',50],['job_title',80],['schedule',120]]) {
    if ((draft[field] || '').length > max) errors.push(`Campo ${field} excedeu o tamanho permitido.`);
  }
  return errors;
}
