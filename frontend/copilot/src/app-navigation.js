/** Ferramentas de navegação da área administrativa, limitadas às telas autorizadas. */
export const APP_NAVIGATION_NAME = 'navigate_potiguar';
export const appNavigationTool = {
  functionDeclarations: [{
    name: APP_NAVIGATION_NAME,
    description: 'Navegue de fato até uma tela oficial solicitada pelo usuário: dashboard, histórico de ponto, relatórios, funcionários, rascunhos ou novo cadastro. Somente telas permitidas pelo backend. Não use URLs arbitrárias, não altere registros.',
    parametersJsonSchema: {
      type: 'object',
      properties: {
        destination: {type: 'string', enum: ['dashboard', 'attendance', 'reports', 'employees', 'drafts', 'new_employee'],
          description: 'dashboard: painel; attendance: histórico de ponto; reports: relatórios; employees: funcionários; drafts: rascunhos; new_employee: iniciar formulário V2'},
      },
      required: ['destination'],
    },
  }],
};
export function sanitizeAppNavigation(raw, canCreate = false) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  if (['dashboard','attendance','reports','employees'].includes(raw.destination)) return {destination: raw.destination};
  if (['drafts','new_employee'].includes(raw.destination) && canCreate) return {destination: raw.destination};
  return null;
}
/** Só caminhos internos canônicos, sem origem remota, query ou fragmento. */
export function safeAppPath(path) {
  return typeof path === 'string' && /^\/admin\/[a-z0-9/_-]+$/i.test(path)
    && !path.includes('//') && !path.includes('..');
}
