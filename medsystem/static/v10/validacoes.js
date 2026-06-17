// ══════════════════════════════════════════════════════════
// VALIDAÇÕES - CPF, Email, Telefone
// ══════════════════════════════════════════════════════════

// Validar CPF com dígitos verificadores
function validarCPF(cpf) {
  cpf = cpf.replace(/\D/g, '');
  
  if (cpf.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(cpf)) return false; // Todos os dígitos iguais
  
  // Primeiro dígito verificador
  let soma = 0;
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpf.charAt(i)) * (10 - i);
  }
  let resto = soma % 11;
  let digito1 = resto < 2 ? 0 : 11 - resto;
  
  if (parseInt(cpf.charAt(9)) !== digito1) return false;
  
  // Segundo dígito verificador
  soma = 0;
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpf.charAt(i)) * (11 - i);
  }
  resto = soma % 11;
  let digito2 = resto < 2 ? 0 : 11 - resto;
  
  if (parseInt(cpf.charAt(10)) !== digito2) return false;
  
  return true;
}

// Validar email
function validarEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

// Validar data de nascimento
function validarDataNascimento(dataStr) {
  const data = new Date(dataStr);
  const hoje = new Date();
  const idade = hoje.getFullYear() - data.getFullYear();
  const mes = hoje.getMonth() - data.getMonth();
  
  if (mes < 0 || (mes === 0 && hoje.getDate() < data.getDate())) {
    return idade - 1;
  }
  
  return idade;
}

// Validar telefone
function validarTelefone(tel) {
  const numeros = tel.replace(/\D/g, '');
  return numeros.length >= 10 && numeros.length <= 11;
}

// Aplicar máscara em tempo real
function aplicarMascaraCPF(input) {
  let v = input.value.replace(/\D/g,'').slice(0,11);
  v = v.replace(/(\d{3})(\d)/,'$1.$2');
  v = v.replace(/(\d{3})(\d)/,'$1.$2');
  v = v.replace(/(\d{3})(\d{1,2})$/,'$1-$2');
  input.value = v;
}

// Formatar telefone brasileiro: (34) 99858-2010 ou (34) 3456-7890
function formatarTelefone(valor) {
  const v = String(valor || '').replace(/\D/g, '').slice(0, 11);
  if (!v) return '';
  if (v.length <= 2) return '(' + v;
  if (v.length <= 6) return '(' + v.slice(0, 2) + ') ' + v.slice(2);
  if (v.length <= 10) {
    return '(' + v.slice(0, 2) + ') ' + v.slice(2, 6) + '-' + v.slice(6);
  }
  return '(' + v.slice(0, 2) + ') ' + v.slice(2, 7) + '-' + v.slice(7);
}

function aplicarMascaraTelefone(input) {
  const cursor = input.selectionStart;
  const digitsBefore = input.value.slice(0, cursor).replace(/\D/g, '').length;
  input.value = formatarTelefone(input.value);
  let pos = 0;
  let count = 0;
  while (pos < input.value.length && count < digitsBefore) {
    if (/\d/.test(input.value[pos])) count++;
    pos++;
  }
  input.setSelectionRange(pos, pos);
}

function aplicarMascaraCEP(input) {
  let v = input.value.replace(/\D/g, '').slice(0, 8);
  if (v.length > 5) v = v.slice(0, 5) + '-' + v.slice(5);
  input.value = v;
}

function montarEnderecoCompleto() {
  const log = document.getElementById('np-logradouro')?.value?.trim() || '';
  const num = document.getElementById('np-numero')?.value?.trim() || '';
  const comp = document.getElementById('np-complemento')?.value?.trim() || '';
  const bairro = document.getElementById('np-bairro')?.value?.trim() || '';
  const cidade = document.getElementById('np-cidade')?.value?.trim() || '';
  const uf = document.getElementById('np-uf')?.value?.trim() || '';
  const cep = document.getElementById('np-cep')?.value?.trim() || '';

  const ruaNum = [log, num].filter(Boolean).join(', ');
  const cidadeUf = [cidade, uf].filter(Boolean).join('/');
  const partes = [ruaNum, comp, bairro, cidadeUf, cep ? 'CEP ' + cep : ''].filter(Boolean);
  return partes.length ? partes.join(' — ') : null;
}

async function buscarCep() {
  const input = document.getElementById('np-cep');
  if (!input) return;
  const cep = input.value.replace(/\D/g, '');
  if (cep.length !== 8) {
    if (typeof showToast === 'function') showToast('Informe um CEP com 8 digitos', 'warn');
    input.focus();
    return;
  }

  const btn = document.querySelector('#page-novo_paciente .input-with-btn .btn');
  if (btn) { btn.disabled = true; btn.textContent = '...'; }

  try {
    const res = await fetch('https://viacep.com.br/ws/' + cep + '/json/');
    const data = await res.json();
    if (data.erro) {
      if (typeof showToast === 'function') showToast('CEP nao encontrado', 'error');
      return;
    }
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
    set('np-logradouro', data.logradouro);
    set('np-bairro', data.bairro);
    set('np-cidade', data.localidade);
    set('np-uf', data.uf);
    if (data.complemento) set('np-complemento', data.complemento);
    document.getElementById('np-numero')?.focus();
    if (typeof showToast === 'function') showToast('Endereco encontrado pelo CEP', 'success');
  } catch (e) {
    if (typeof showToast === 'function') showToast('Erro ao buscar CEP. Tente novamente.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Buscar'; }
  }
}

function aplicarMascaraCRM(input) {
  input.value = input.value.replace(/\D/g,'').slice(0, 6);
}

function vincularMascara(input, tipo) {
  if (!input || input.dataset.maskBound) return;
  input.dataset.maskBound = '1';
  const handlers = {
    cpf: () => aplicarMascaraCPF(input),
    telefone: () => aplicarMascaraTelefone(input),
    cep: () => aplicarMascaraCEP(input),
    crm: () => aplicarMascaraCRM(input),
  };
  const fn = handlers[tipo];
  if (!fn) return;
  input.addEventListener('input', fn);
  input.addEventListener('blur', fn);
  if (tipo === 'cep') {
    input.addEventListener('blur', () => {
      if (input.value.replace(/\D/g, '').length === 8) buscarCep();
    });
  }
  if (input.value) fn();
}

function inicializarMascaras() {
  const ids = { 'np-tel': 'telefone', 'np-cpf': 'cpf', 'nm-crm': 'crm' };
  Object.entries(ids).forEach(([id, tipo]) => {
    const el = document.getElementById(id);
    if (el) vincularMascara(el, tipo);
  });
  document.querySelectorAll('[data-mask="telefone"]').forEach(el => vincularMascara(el, 'telefone'));
  document.querySelectorAll('[data-mask="cpf"]').forEach(el => vincularMascara(el, 'cpf'));
  document.querySelectorAll('[data-mask="cep"]').forEach(el => vincularMascara(el, 'cep'));
}

document.addEventListener('DOMContentLoaded', inicializarMascaras);

window.formatarTelefone = formatarTelefone;
window.inicializarMascaras = inicializarMascaras;
window.buscarCep = buscarCep;
window.montarEnderecoCompleto = montarEnderecoCompleto;

// ══════════════════════════════════════════════════════════
// VALIDAÇÃO DE FORÇA DE SENHA
// ══════════════════════════════════════════════════════════

function validarForcaSenha(senha) {
  // Verifica se atende aos critérios mínimos
  const temLetrasMaiusculas = /[A-Z]/.test(senha);
  const temLetrasMinusculas = /[a-z]/.test(senha);
  const temNumeros = /[0-9]/.test(senha);
  const temCaracteresEspeciais = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(senha);
  const tamanhoMinimo = senha.length >= 8;

  return {
    valida: temLetrasMaiusculas && temLetrasMinusculas && temNumeros && temCaracteresEspeciais && tamanhoMinimo,
    requisitos: {
      maiusculas: temLetrasMaiusculas,
      minusculas: temLetrasMinusculas,
      numeros: temNumeros,
      especiais: temCaracteresEspeciais,
      tamanho: tamanhoMinimo
    }
  };
}

function exibirIndicadorForcaSenha(inputSenha, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  inputSenha.addEventListener('input', function() {
    const senha = this.value;
    const validacao = validarForcaSenha(senha);
    
    let html = '<div style="margin-top: 8px;">';
    html += '<small style="color: #666;"><strong>Requisitos da Senha:</strong></small><br>';
    html += `<small style="color: ${validacao.requisitos.maiusculas ? '#27ae60' : '#e74c3c'};">
      ${validacao.requisitos.maiusculas ? '✅' : '❌'} Letra maiúscula (A-Z)
    </small><br>`;
    html += `<small style="color: ${validacao.requisitos.minusculas ? '#27ae60' : '#e74c3c'};">
      ${validacao.requisitos.minusculas ? '✅' : '❌'} Letra minúscula (a-z)
    </small><br>`;
    html += `<small style="color: ${validacao.requisitos.numeros ? '#27ae60' : '#e74c3c'};">
      ${validacao.requisitos.numeros ? '✅' : '❌'} Número (0-9)
    </small><br>`;
    html += `<small style="color: ${validacao.requisitos.especiais ? '#27ae60' : '#e74c3c'};">
      ${validacao.requisitos.especiais ? '✅' : '❌'} Caractere especial (!@#$%^&*)
    </small><br>`;
    html += `<small style="color: ${validacao.requisitos.tamanho ? '#27ae60' : '#e74c3c'};">
      ${validacao.requisitos.tamanho ? '✅' : '❌'} Mínimo 8 caracteres
    </small>`;
    html += '</div>';
    
    container.innerHTML = html;
  });
}
