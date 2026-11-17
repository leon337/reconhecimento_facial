"""Contrato declarativo das oito etapas canônicas do Novo Funcionário V2."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = 'text'
    required: bool = False
    options: tuple = ()
    group: str = ''


STEPS = [
    ('Tipo de relação', 'Escolha o enquadramento operacional antes dos demais dados.', [
        Field('relation_type', 'Tipo de relação', 'select', True, ('CLT comum', 'CLT intermitente', 'Sem vínculo empregatício')),
        Field('other_relation', 'Categoria complementar'),
    ]),
    ('Dados pessoais', 'Identificação, dados civis e contatos; campos sensíveis são opcionais.', [
        Field('full_name', 'Nome completo', required=True),
        Field('cpf', 'CPF'), Field('birth_date', 'Data de nascimento', 'date'),
        Field('rg', 'Documento de identidade'), Field('profile_photo_label', 'Observação sobre foto'),
        Field('sex', 'Sexo (quando necessário)', 'select', options=('Feminino','Masculino','Outro','Prefiro não informar')),
        Field('race', 'Raça/cor (dado sensível, quando necessário)', 'select', options=('Branca','Preta','Parda','Amarela','Indígena','Prefiro não informar')),
        Field('education', 'Escolaridade'), Field('nationality', 'Nacionalidade'),
        Field('birth_country', 'País de nascimento'), Field('civil_status', 'Estado civil'),
        Field('birth_place', 'Naturalidade'), Field('social_name', 'Nome social'),
        Field('phone', 'Telefone'), Field('whatsapp', 'WhatsApp'),
        Field('personal_email', 'E-mail pessoal', 'email'),
        Field('message_contact_name', 'Contato para recados'),
        Field('message_contact_phone', 'Telefone para recados'),
        Field('message_contact_relation', 'Parentesco ou relação'),
        Field('same_emergency_contact', 'Usar contato para recados como contato de emergência', 'checkbox'),
        Field('emergency_name', 'Nome do contato de emergência'),
        Field('emergency_phone', 'Telefone de emergência'),
        Field('has_dependents', 'Possui dependentes?', 'select', options=('Não','Sim')),
        Field('dependent_name', 'Nome do dependente (se aplicável)'),
        Field('dependent_type', 'Parentesco do dependente'),
        Field('pcd_record', 'Registro de deficiência (dado sensível)', 'select', options=('Não informado','Sim','Não')),
        Field('pcd_type', 'Descrição de PCD (somente quando necessária)'),
        Field('rehabilitated', 'Situação de reabilitação (se aplicável)'),
        Field('sensitive_data_ack', 'Confirmo necessidade e transparência sobre dados sensíveis opcionais', 'checkbox'),
    ]),
    ('Endereço', 'Endereço atual com opções para contexto urbano, rural ou exterior.', [
        Field('country','País',required=True),
        Field('address_type','Tipo de endereço','select',True,('Urbano','Rural','Exterior')),
        Field('cep','CEP'), Field('street','Logradouro'), Field('address_number','Número'),
        Field('no_number','Sem número','checkbox'), Field('complement','Complemento'),
        Field('district','Bairro'), Field('city','Cidade'), Field('state','UF'),
        Field('reference','Ponto de referência'),
        Field('rural_locality','Localidade rural'), Field('rural_road','Estrada rural'),
        Field('rural_km','Quilômetro'), Field('rural_property','Propriedade'),
        Field('rural_city','Município rural'), Field('rural_state','UF rural'),
        Field('rural_reference','Referência rural'),
        Field('foreign_street','Endereço no exterior'), Field('foreign_number','Número no exterior'),
        Field('foreign_postal','Código postal exterior'), Field('foreign_city','Cidade exterior'),
        Field('foreign_region','Região exterior'),
    ]),
    ('Vínculo', 'Estrutura organizacional, contrato, datas, jornada e benefícios.', [
        Field('company','Empresa (nome descritivo)'), Field('unit','Unidade ou obra'),
        Field('department','Departamento'), Field('job_role','Cargo ou função'),
        Field('manager','Gestor responsável'), Field('schedule','Jornada / horário'),
        Field('admission_date','Data de admissão','date'),
        Field('contract_type','Tipo de contrato'), Field('salary','Remuneração'),
        Field('salary_unit','Periodicidade','select',options=('Mensal','Horária','Diária','Outra')),
        Field('intermittent_date','Data de admissão intermitente','date'),
        Field('hour_value','Valor por hora'),
        Field('non_employee_type','Tipo de serviço sem vínculo'),
        Field('relation_start','Início da relação','date'),
        Field('transport_benefit','Vale-transporte','select',options=('Não','Sim')),
        Field('benefit_policy','Política de benefícios'),
    ]),
    ('Pagamento', 'Os dados financeiros serão criptografados e tratados como confidenciais.', [
        Field('payment_method','Forma de pagamento','select',False,('Conta bancária','Conta-salário','PIX','Outra')),
        Field('bank','Banco'), Field('account_type','Tipo de conta'),
        Field('agency','Agência'), Field('account','Conta'),
        Field('salary_bank','Banco conta-salário'), Field('salary_account','Conta-salário'),
        Field('pix_type','Tipo de chave PIX'), Field('pix_key','Chave PIX'),
        Field('other_payment','Outra forma autorizada'),
        Field('third_party_holder','Conta ou chave pertence a terceiro','checkbox'),
        Field('third_party_name','Titular terceiro'), Field('third_party_cpf','CPF terceiro'),
        Field('third_party_reason','Justificativa para titularidade de terceiro','textarea'),
    ]),
    ('Acesso', 'Cadastro funcional não concede acesso administrativo automaticamente.', [
        Field('has_system_access','Solicitar acesso ao sistema','checkbox'),
        Field('access_role','Perfil solicitado','select',options=('operator','manager','auditor','admin')),
        Field('access_login','Login solicitado (pendente de ativação)'),
        Field('access_scope','Escopo solicitado'),
    ]),
    ('Biometria', 'O cadastro facial real usa a tela de captura segura depois da conclusão.', [
        Field('biometric_timing','Momento da biometria','select',True,('Depois','Agora')),
        Field('biometric_notice_ack','Confirmo que a pessoa recebeu as informações de transparência','checkbox'),
    ]),
    ('Revisão', 'Revise os dados antes de criar o funcionário. Nenhum registro é criado antes da confirmação.', []),
]

FIELD_MAP = {field.name: field for _,_,fields in STEPS for field in fields}
SENSITIVE_FIELDS = {'race','pcd_record','pcd_type','rehabilitated','dependent_name','dependent_type'}
MAX_TEXT = 500


def normalize(raw):
    """Aceitar apenas os campos definidos; nenhum segredo vai para sessionStorage."""
    if not isinstance(raw,dict):
        raise ValueError('dados_invalidos')
    unknown=set(raw)-set(FIELD_MAP)
    if unknown:
        raise ValueError('campos_nao_permitidos')
    out={}
    for name, field in FIELD_MAP.items():
        value=raw.get(name,'')
        if field.kind=='checkbox':
            if value not in (True,False,'true','false','on','',None):
                raise ValueError(f'campo_invalido:{name}')
            out[name]=value in (True,'true','on')
            continue
        if not isinstance(value,str) or len(value)>MAX_TEXT:
            raise ValueError(f'campo_invalido:{name}')
        value=value.strip()
        if field.options and value and value not in field.options:
            raise ValueError(f'opcao_invalida:{name}')
        out[name]=value
    return out
