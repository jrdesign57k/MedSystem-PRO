// ══════════════════════════════════════════════════════════
// ADMIN - Gerenciamento de Usuários e Médicos
// ══════════════════════════════════════════════════════════

// ══════════════════════════════════════════════════════════
// GERENCIAR USUÁRIOS
// ══════════════════════════════════════════════════════════

async function carregarUsuarios() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/auth/usuarios', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();

    if (json.sucesso) {
      const tbody = document.querySelector('#tabela-usuarios');
      if (!tbody) return;
      tbody.innerHTML = '';

      json.dados.forEach(usuario => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${usuario.nome}</td>
          <td>${usuario.email}</td>
          <td><span class="badge badge-${usuario.tipo}">${usuario.tipo.toUpperCase()}</span></td>
          <td>${usuario.ativo ? '✅ Ativo' : '❌ Inativo'}</td>
          <td>
            <button class="btn btn-sm btn-outline" onclick="editarUsuarioModal(${usuario.id}, '${usuario.nome}', '${usuario.email}', '${usuario.tipo}', ${usuario.ativo})">Editar</button>
            <button class="btn btn-sm btn-danger" onclick="deletarUsuario(${usuario.id}, '${usuario.nome}')">Deletar</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) {
    console.error('Erro ao buscar usuários:', erro);
  }
}

async function novoUsuario() {
  const nome = document.getElementById('nu-nome').value.trim();
  const email = document.getElementById('nu-email').value.trim();
  const tipo = document.getElementById('nu-tipo').value;
  const senha = document.getElementById('nu-senha').value;

  if (!nome || !email || !tipo || !senha) {
    showToast('Preencha todos os campos', 'error');
    return;
  }

  // Validar força de senha
  const validacao = validarForcaSenha(senha);
  if (!validacao.valida) {
    showToast('❌ Senha fraca. Deve ter maiúscula, minúscula, número, caractere especial e 8+ caracteres', 'error');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ nome, email, tipo, senha })
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Usuário criado com sucesso!', 'success');
      document.getElementById('nu-nome').value = '';
      document.getElementById('nu-email').value = '';
      document.getElementById('nu-senha').value = '';
      document.getElementById('nu-tipo').value = 'recepcao';
      carregarUsuarios();
      showPage('usuarios');
    } else {
      showToast('❌ ' + json.mensagem, 'error');
    }
  } catch (erro) {
    console.error('Erro:', erro);
    showToast('Erro ao criar usuário', 'error');
  }
}

function editarUsuarioModal(id, nome, email, tipo, ativo) {
  // Remove modal anterior se existir para evitar duplicação
  const modalAntigo = document.getElementById('modal-edicao-wrapper');
  if (modalAntigo) modalAntigo.remove();

  const modal = `
    <div id="modal-edicao-wrapper">
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,.2); z-index: 1000;">
        <h3 style="margin-bottom: 20px;">Editar Usuário</h3>
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-weight: 600; margin-bottom: 5px;">Nome</label>
          <input type="text" id="eu-nome" value="${nome}" style="width: 100%; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px;">
        </div>
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-weight: 600; margin-bottom: 5px;">Email</label>
          <input type="email" id="eu-email" value="${email}" disabled style="width: 100%; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; background: #f5f5f5;">
        </div>
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-weight: 600; margin-bottom: 5px;">Role</label>
          <select id="eu-tipo" style="width: 100%; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px;">
            <option value="recepcao" ${tipo === 'recepcao' ? 'selected' : ''}>Recepção</option>
            <option value="medico" ${tipo === 'medico' ? 'selected' : ''}>Médico</option>
            <option value="admin" ${tipo === 'admin' ? 'selected' : ''}>Admin</option>
          </select>
        </div>
        <div style="margin-bottom: 15px;">
          <label style="display: flex; align-items: center; gap: 10px;">
            <input type="checkbox" id="eu-ativo" ${ativo ? 'checked' : ''}>
            <span>Ativo</span>
          </label>
        </div>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <button class="btn btn-outline" onclick="document.getElementById('modal-edicao-wrapper').remove()">Cancelar</button>
          <button class="btn btn-primary" onclick="salvarEdicaoUsuario(${id})">Salvar</button>
        </div>
      </div>
      <div data-modal-bg onclick="document.getElementById('modal-edicao-wrapper').remove()" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,.5); z-index: 999;"></div>
    </div>
  `;
  
  const container = document.createElement('div');
  container.innerHTML = modal;
  document.body.appendChild(container.firstElementChild);
}

async function salvarEdicaoUsuario(id) {
  const nome = document.getElementById('eu-nome').value.trim();
  const tipo = document.getElementById('eu-tipo').value;
  const ativo = document.getElementById('eu-ativo').checked;

  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/auth/usuarios/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ nome, tipo, ativo })
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Usuário atualizado!', 'success');
      // Correção do fechamento do modal:
      const modal = document.getElementById('modal-edicao-wrapper');
      if (modal) modal.remove();
      carregarUsuarios();
    } else {
      showToast('❌ ' + json.mensagem, 'error');
    }
  } catch (erro) {
    console.error("Erro na requisição:", erro);
    showToast('Erro ao atualizar', 'error');
  }
}

async function deletarUsuario(id, nome) {
  // Aviso de exclusão permanente
  if (!confirm(`⚠️ ATENÇÃO: Tem certeza que deseja EXCLUIR DEFINITIVAMENTE o usuário "${nome}"?\n\nEsta ação apagará o acesso dele do banco de dados e não pode ser desfeita.`)) return;

  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/auth/usuarios/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token }
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Usuário excluído permanentemente!', 'success');
      carregarUsuarios();
    } else {
      showToast('❌ ' + json.mensagem, 'error');
    }
  } catch (erro) {
    showToast('Erro ao deletar o usuário', 'error');
  }
}

// ══════════════════════════════════════════════════════════
// GERENCIAR MÉDICOS
// ══════════════════════════════════════════════════════════

async function carregarEspecialidades() {
  try {
    const token = localStorage.getItem('token');
    // Assumindo que você tem uma rota GET /api/especialidades
    // Por enquanto, vou colocar as especialidades manualmente
    const select = document.getElementById('nm-especialidade');
    if (select) {
      select.innerHTML = `
        <option value="">Selecione...</option>
        <option value="1">Clínica Geral</option>
        <option value="2">Cardiologia</option>
        <option value="3">Neurologia</option>
        <option value="4">Pediatria</option>
        <option value="5">Oftalmologia</option>
      `;
    }
  } catch (erro) {
    console.error('Erro:', erro);
  }
}

async function carregarMedicos() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/medicos', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();

    if (json.sucesso) {
      const tbody = document.querySelector('#tabela-medicos');
      if (!tbody) return;
      tbody.innerHTML = '';

      json.dados.forEach(medico => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${medico.nome}</td>
          <td>${medico.crm}</td>
          <td>${medico.especialidade ? medico.especialidade.nome : 'N/A'}</td>
          <td>${medico.usuario && medico.usuario.ativo ? '✅ Ativo' : '❌ Inativo'}</td>
          <td>
            <button class="btn btn-sm btn-outline" onclick="showPage('editar_medico')">Editar</button>
            <button class="btn btn-sm btn-danger" onclick="deletarMedico(${medico.id}, '${medico.nome}')">Deletar</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) {
    console.error('Erro ao buscar médicos:', erro);
  }
}

async function novoMedico() {
  const nome = document.getElementById('nm-nome').value.trim();
  const email = document.getElementById('nm-email').value.trim();
  const crm = document.getElementById('nm-crm').value.trim();
  const id_especialidade = document.getElementById('nm-especialidade').value;

  if (!nome || !email || !crm || !id_especialidade) {
    showToast('Preencha todos os campos', 'error');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/medicos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({
        nome,
        email,
        crm,
        id_especialidade: parseInt(id_especialidade),
        senha: '123456'
      })
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Médico cadastrado com sucesso!', 'success');
      document.getElementById('nm-nome').value = '';
      document.getElementById('nm-email').value = '';
      document.getElementById('nm-crm').value = '';
      document.getElementById('nm-especialidade').value = '';
      carregarMedicos();
      showPage('medicos');
    } else {
      showToast('❌ ' + json.mensagem, 'error');
    }
  } catch (erro) {
    console.error('Erro:', erro);
    showToast('Erro ao cadastrar médico', 'error');
  }
}

async function deletarMedico(id, nome) {
  if (!confirm(`Desativar médico "${nome}"?`)) return;

  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/medicos/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token }
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Médico desativado!', 'success');
      carregarMedicos();
    } else {
      showToast('❌ ' + json.mensagem, 'error');
    }
  } catch (erro) {
    showToast('Erro ao deletar', 'error');
  }
}

// ══════════════════════════════════════════════════════════
// FUNÇÕES AUXILIARES
// ══════════════════════════════════════════════════════════

function limparForm() {
  // Limpar campos do formulário de novo usuário
  const nuNome = document.getElementById('nu-nome');
  const nuEmail = document.getElementById('nu-email');
  const nuTipo = document.getElementById('nu-tipo');
  const nuSenha = document.getElementById('nu-senha');

  if (nuNome) nuNome.value = '';
  if (nuEmail) nuEmail.value = '';
  if (nuTipo) nuTipo.value = '';
  if (nuSenha) nuSenha.value = '';

  // Limpar campos do formulário de novo médico
  const nmNome = document.getElementById('nm-nome');
  const nmEmail = document.getElementById('nm-email');
  const nmCrm = document.getElementById('nm-crm');
  const nmEspecialidade = document.getElementById('nm-especialidade');

  if (nmNome) nmNome.value = '';
  if (nmEmail) nmEmail.value = '';
  if (nmCrm) nmCrm.value = '';
  if (nmEspecialidade) nmEspecialidade.value = '';

  // Limpar campos do formulário de novo paciente
  const npNome = document.getElementById('np-nome');
  const npCpf = document.getElementById('np-cpf');
  const npNasc = document.getElementById('np-nasc');
  const npSexo = document.getElementById('np-sexo');
  const npTel = document.getElementById('np-tel');
  const npEmail = document.getElementById('np-email');
  const npSangue = document.getElementById('np-sangue');
  const npEndereco = document.getElementById('np-endereco');
  const npCep = document.getElementById('np-cep');
  const npLogradouro = document.getElementById('np-logradouro');
  const npNumero = document.getElementById('np-numero');
  const npComplemento = document.getElementById('np-complemento');
  const npBairro = document.getElementById('np-bairro');
  const npCidade = document.getElementById('np-cidade');
  const npUf = document.getElementById('np-uf');
  const npAlergias = document.getElementById('np-alergias');
  const npObservacoes = document.getElementById('np-observacoes');
  
  // Sinais Vitais
  const npPeso = document.getElementById('np-peso');
  const npAltura = document.getElementById('np-altura');
  const npPressao = document.getElementById('np-pressao');
  const npFc = document.getElementById('np-fc');

  if (npNome) npNome.value = '';
  if (npCpf) npCpf.value = '';
  if (npNasc) npNasc.value = '';
  if (npSexo) npSexo.value = '';
  if (npTel) npTel.value = '';
  if (npEmail) npEmail.value = '';
  if (npSangue) npSangue.value = '';
  if (npEndereco) npEndereco.value = '';
  if (npCep) npCep.value = '';
  if (npLogradouro) npLogradouro.value = '';
  if (npNumero) npNumero.value = '';
  if (npComplemento) npComplemento.value = '';
  if (npBairro) npBairro.value = '';
  if (npCidade) npCidade.value = '';
  if (npUf) npUf.value = '';
  if (npAlergias) npAlergias.value = '';
  if (npObservacoes) npObservacoes.value = '';
  if (npPeso) npPeso.value = '';
  if (npAltura) npAltura.value = '';
  if (npPressao) npPressao.value = '';
  if (npFc) npFc.value = '';

  // Limpar indicador de força de senha
  const forceIndicator = document.getElementById('nu-senha-force');
  if (forceIndicator) forceIndicator.innerHTML = '';
}

// Garantir que as especialidades carreguem ao abrir a tela de novo médico
function prepararNovoMedico() {
  carregarEspecialidades();
  showPage('novo_medico');
}

async function carregarEspecialidades() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/especialidades', { headers: { 'Authorization': 'Bearer ' + token } });
    const json = await res.json();
    
    const select = document.getElementById('nm-especialidade');
    if (select && json.sucesso) {
      select.innerHTML = '<option value="">Selecione...</option>';
      json.dados.forEach(esp => {
        select.innerHTML += `<option value="${esp.id}">${esp.nome}</option>`;
      });
    }
  } catch (erro) {
    // Fallback de segurança se a API não existir
    document.getElementById('nm-especialidade').innerHTML = `
      <option value="">Selecione...</option>
      <option value="1">Clínica Geral</option>
      <option value="2">Cardiologia</option>
      <option value="3">Pediatria</option>`;
  }
}