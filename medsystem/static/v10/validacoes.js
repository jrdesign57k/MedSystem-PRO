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

function aplicarMascaraTelefone(input) {
  let v = input.value.replace(/\D/g,'').slice(0,11);
  v = v.replace(/^(\d{2})(\d)/,'($1) $2');
  v = v.replace(/(\d{5})(\d)/,'$1-$2');
  input.value = v;
}

function aplicarMascaraCRM(input) {
  input.value = input.value.replace(/\D/g,'').slice(0, 6);
}

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
