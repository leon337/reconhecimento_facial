/* Filtro de precaução: o navegador pode identificar padrões óbvios, não substituir revisão LGPD. */
const EMAIL=/\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b/i;
const TERMS=/\b(?:cpf|cnpj|rg|pix|senha|telefone|celular|conta bancária|salário|chave de acesso|rua|avenida|travessa)\b/i;
export function isProtectedInput(value){
  if(typeof value!=='string')return false;
  return value.replace(/\D/g,'').length>=8 || EMAIL.test(value) || TERMS.test(value) || /R\$\s*\d/i.test(value);
}
