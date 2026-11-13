/** Propostas por IA, sem permissão de escrita ou leitura de dados confidenciais. */
export const ONBOARDING_FUNCTION_NAME = 'suggest_onboarding_fields';
export const ALLOWED_ONBOARDING_FIELDS = Object.freeze({
  0: ['relation_type', 'other_relation'],
  1: ['full_name', 'social_name', 'nationality', 'education'],
  2: ['country', 'address_type', 'city', 'state'],
  3: ['department', 'job_role', 'manager', 'schedule', 'contract_type', 'transport_benefit', 'benefit_policy'],
  4: [], 5: [], 6: [], 7: [],
});
export const onboardingSuggestionTool = {
  functionDeclarations: [{
    name: ONBOARDING_FUNCTION_NAME,
    description: [
      'Somente quando o administrador solicitar sugerir o preenchimento de campos da etapa ATUAL',
      'retorne valores explicitamente informados pela pessoa; nunca grave nada.',
      'Não invente nenhum dado. Nunca inclua CPF, RG, documentos, raça/cor, PCD, dependentes,',
      'telefones, e-mails, logradouro completo, dados bancários, PIX, credenciais, perfis,',
      'permissões, consentimento ou biometria.',
      'Na etapa Pagamento, Acesso, Biometria e Revisão, apenas explique; não ofereça sugestões estruturadas.',
    ].join(' '),
    parametersJsonSchema: {
      type: 'object',
      properties: {
        step: {type: 'integer', description: 'Índice de 0 a 7 da etapa atual'},
        suggestions: {type: 'array', maxItems: 5, items: {type: 'object', properties: {
          field: {type: 'string'}, value: {type: 'string'},
        }, required: ['field', 'value']}},
      },
      required: ['step', 'suggestions'],
    },
  }],
};
export function sanitizeOnboardingSuggestions(raw, step) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return [];
  if (!Number.isInteger(step) || step < 0 || step > 7) return [];
  if (raw.step !== step || !Array.isArray(raw.suggestions) || raw.suggestions.length > 5) return [];
  const result = [], seen = new Set();
  for (const item of raw.suggestions) {
    if (!item || typeof item.field !== 'string' || typeof item.value !== 'string') continue;
    if (!ALLOWED_ONBOARDING_FIELDS[step].includes(item.field) || seen.has(item.field)) continue;
    const value = item.value.trim();
    if (!value || value.length > 120 || /[<>\x00-\x1f]/.test(value)) continue;
    seen.add(item.field);
    result.push({field: item.field, value});
  }
  return result;
}
