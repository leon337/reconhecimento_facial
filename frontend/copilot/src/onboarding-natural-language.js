/**
 * Reconhecimento conservador de escolhas já expostas no formulário Potiguar.
 * Não interpreta campos livres, financeiros, biométricos ou qualquer dado pessoal.
 * Não substitui o LLM: elimina falhas triviais de sinônimos em selects seguros.
 */
const ALIASES = Object.freeze({
  relation_type: Object.freeze({
    'CLT comum': ['clt comum','clt normal','clt padrao','clt tradicional','clt regular',
      'contrato comum','contrato clt comum','carteira assinada comum','registro comum'],
    'CLT intermitente': ['clt intermitente','contrato intermitente','regime intermitente',
      'trabalho intermitente','trabalhador intermitente','intermitente',
      'por convocacao','trabalho por convocacao','contrato por convocacao'],
    'Sem vínculo empregatício': ['sem vinculo empregaticio','sem vinculo','sem emprego formal',
      'prestador autonomo','trabalhador autonomo','autonomo sem vinculo',
      'prestacao de servicos sem vinculo'],
  }),
  address_type: Object.freeze({
    Urbano: ['urbano','zona urbana','area urbana','endereco urbano','centro urbano','no centro urbano'],
    Rural: ['rural','zona rural','area rural','endereco rural','sitio rural'],
    Exterior: ['exterior','fora do brasil','outro pais','endereco no exterior','no exterior'],
  }),
  transport_benefit: Object.freeze({
    Sim: ['sim','quero vale transporte','preciso de vale transporte','recebo vale transporte',
      'vou usar vale transporte'],
    Não: ['nao','dispenso vale transporte','sem vale transporte','nao quero vale transporte',
      'nao preciso de vale transporte'],
  }),
});
const NEGATED = /(?:\bnao\b|\bnunca\b|\bnem\b|\bdeixa de\b|\bexclui\b)/;
const QUESTION = /(?:\bqual\b|\bquais\b|\bo que\b|\bcomo\b|\bporque\b|\bpor que\b|\bexplique\b|\bexplica\b|\bdiferenca\b|\be se\b|\bsera que\b|\bposso\b)/;
const COMMAND = /(?:\bcoloque\b|\bcoloca\b|\bcolocar\b|\bcontrata\b|\bponha\b|\bpoe\b|\bescolha\b|\bseleciona\b|\bselecione\b|\bmarque\b|\bpreenche\b|\bpreencha\b|\bcorrige\b|\baltere\b|\bmude\b|\bquero\b|\bsou\b|\be\b|\bsera\b|\bregime\b|\bcontrato\b|\bmodalidade\b|\btrabalho\b|\bvinculo\b)/;

export function fold(value) {
  return String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
    .toLocaleLowerCase('pt-BR').replace(/[–—\-_]/g,' ')
    .replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
}
function matchAlias(haystack,alias) {
  return (' '+haystack+' ').includes(' '+alias+' ');
}
function detect(field,raw,{utterance=false}={}) {
  const options=ALIASES[field];
  if(!options || typeof raw!=='string' || raw.length>400)return null;
  const text=fold(raw);
  if(!text || text.length<2)return null;
  const questionLike=text.startsWith('como ') || QUESTION.test(text.replaceAll(' como ',' '));
  if(utterance && (questionLike || text.includes('?')))return null;
  if(utterance && text.split(' ').length>24)return null;
  const found=[];
  for(const [canonical,words] of Object.entries(options)){
    if(field==='transport_benefit' && canonical==='Sim' && NEGATED.test(text))continue;
    if(words.some(word=>matchAlias(text,word)))found.push(canonical);
  }
  if(found.length!==1)return null;
  const canonical=found[0];
  // "Não é intermitente": nunca deve preencher 'intermitente' por correspondência parcial.
  // Só a opção "Não" do vale-transporte aceita negação isolada.
  if(field!=='transport_benefit' && NEGATED.test(text)){
    if(canonical==='Sem vínculo empregatício' && /\bsem vinculo\b/.test(text)) {
      if(/\bnao (?:e|sou|quero|tem|tenho)\b/.test(text))return null;
    } else if(!/\bnao tem vinculo\b/.test(text))return null;
  }
  if(field==='transport_benefit'){
    if(canonical==='Sim' && NEGATED.test(text))return null;
    if(canonical==='Não' && /\bnao\b/.test(text) &&
       /\bnao (?:deixo|dispenso)\b/.test(text))return null;
  }
  // 'Clt comum ou intermitente?' / debate e exemplos nunca são decisões.
  if(utterance && text.includes(' ou '))return null;
  if(utterance && !COMMAND.test(text) &&
      !options[canonical].some(word=>fold(raw)===word))return null;
  return canonical;
}

/** Valor sugerido pelo modelo: aceita somente opção exata ou sinônimo inequívoco. */
export function canonicalizeOnboardingValue(field,raw) {
  if(!(field in ALIASES))return raw;
  const exact=Object.keys(ALIASES[field]).find(value=>fold(value)===fold(raw));
  return exact || detect(field,raw);
}

/** Linguagem natural digitada pelo usuário, só para SELECT de campos seguros ativos. */
export function resolveNaturalSelect(field,utterance,availableOptions) {
  if(!Array.isArray(availableOptions) || !ALIASES[field])return null;
  const detected=detect(field,utterance,{utterance:true});
  return detected && availableOptions.includes(detected) ? detected : null;
}

export const SUPPORTED_SELECT_FIELDS=Object.freeze(Object.keys(ALIASES));
