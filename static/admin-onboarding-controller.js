/* Contrato determinístico do cadastro conversacional. Não recebe nem transmite valores protegidos. */
(function (root, create) {
  const contract = create();
  if (typeof module !== 'undefined' && module.exports) module.exports = contract;
  if (root) root.PotiguarOnboardingController = contract;
})(typeof window === 'undefined' ? null : window, function () {
  'use strict';
  const SAFE = Object.freeze({
    0: ['relation_type', 'other_relation'],
    1: ['full_name', 'social_name', 'nationality', 'education'],
    2: ['country', 'address_type', 'city', 'state'],
    3: ['department', 'job_role', 'manager', 'schedule', 'contract_type', 'transport_benefit', 'benefit_policy'],
    4: [], 5: [], 6: [], 7: [],
  });
  const RURAL = ['rural_locality', 'rural_road', 'rural_km', 'rural_property', 'rural_city', 'rural_state', 'rural_reference'];
  const FOREIGN = ['foreign_street', 'foreign_number', 'foreign_postal', 'foreign_city', 'foreign_region'];
  const URBAN = ['cep', 'street', 'address_number', 'no_number', 'complement', 'district', 'city', 'state', 'reference'];
  const BANK = ['bank', 'account_type', 'agency', 'account'];
  const SALARY_BANK = ['salary_bank', 'salary_account'];
  const PIX = ['pix_type', 'pix_key'];
  const THIRD_PARTY = ['third_party_name', 'third_party_cpf', 'third_party_reason'];
  const ACCESS = ['access_role', 'access_login', 'access_scope'];
  function applicable(name, data) {
    const relation = data.relation_type || '';
    const address = data.address_type || '';
    const payment = data.payment_method || '';
    if (name === 'other_relation') return relation === 'Sem vínculo empregatício';
    if (name === 'intermittent_date' || name === 'hour_value') return relation === 'CLT intermitente';
    if (name === 'non_employee_type' || name === 'relation_start') return relation === 'Sem vínculo empregatício';
    if (name === 'salary' || name === 'salary_unit' || name === 'admission_date') return relation !== 'Sem vínculo empregatício';
    if (RURAL.includes(name)) return address === 'Rural';
    if (FOREIGN.includes(name)) return address === 'Exterior';
    if (URBAN.includes(name)) return address === 'Urbano';
    if (BANK.includes(name)) return payment === 'Conta bancária';
    if (SALARY_BANK.includes(name)) return payment === 'Conta-salário';
    if (PIX.includes(name)) return payment === 'PIX';
    if (name === 'other_payment') return payment === 'Outra';
    if (THIRD_PARTY.includes(name)) return Boolean(data.third_party_holder);
    if (name === 'third_party_holder') return Boolean(payment);
    if (ACCESS.includes(name)) return Boolean(data.has_system_access);
    if (name === 'biometric_notice_ack') return data.biometric_timing === 'Agora';
    if (name === 'dependent_name' || name === 'dependent_type') return data.has_dependents === 'Sim';
    if (name === 'pcd_type') return data.pcd_record === 'Sim';
    if (name === 'emergency_name' || name === 'emergency_phone') return !data.same_emergency_contact;
    if (name === 'sensitive_data_ack') return ['race', 'pcd_record', 'pcd_type', 'rehabilitated', 'dependent_name', 'dependent_type']
      .some(field => Boolean(data[field] && !['Não informado', 'Prefiro não informar'].includes(data[field])));
    return true;
  }
  function isSafe(step, name) { return (SAFE[step] || []).includes(name); }
  function hasValue(control) {
    if (!control) return false;
    if (control.type === 'checkbox') return Boolean(control.checked);
    return Boolean(String(control.value || '').trim());
  }
  function nextField(controls, values, visited) {
    return controls.find(control => {
      if (!control.name || control.disabled || !applicable(control.name, values)) return false;
      if (visited.has(control.name) || hasValue(control)) return false;
      return true;
    }) || null;
  }
  function validSafeValue(control, raw) {
    if (!control || control.disabled || control.type === 'checkbox' || typeof raw !== 'string') return false;
    const value = raw.trim();
    if (!value || value.length > 120 || /[<>\x00-\x1f]/.test(value)) return false;
    if (control.name === 'full_name' && value.length < 3) return false;
    if (control.tagName === 'SELECT' &&
        !Array.from(control.options).some(option => option.value === value)) return false;
    return true;
  }
  return Object.freeze({SAFE, applicable, isSafe, hasValue, nextField, validSafeValue});
});
