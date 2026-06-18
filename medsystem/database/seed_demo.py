"""
Dados de demonstração — pacientes, consultas, prontuário e classificação de risco.
Idempotente: cada paciente/marca é verificado antes de inserir.
"""
from datetime import datetime, date, timedelta
from extensions import db
from models import (
    Usuario, Medico, Paciente, Consulta, SinalVital, Diagnostico,
    Exame, TipoExame, Receita, Despesa, PrecoConsulta, CID10, Mensagem
)

MARCA_CPF = '52998224725'  # Carlos Alberto — prontuário médio (MODERADA)
MARCA_RISCO_CPF = '88641577900'  # Pedro — risco CRITICA (marca do seed de risco)


def _medico_demo():
    return Medico.query.join(Usuario).filter(Usuario.email == 'drcarlos@medsystem.com').first()


def _dt(d, hora):
    h, m = map(int, hora.split(':'))
    return datetime(d.year, d.month, d.day, h, m)


def _tipos_exame():
    tipos_nomes = [
        'Hemograma Completo', 'Glicemia', 'PCR', 'Raio-X Tórax', 'Teste rápido Influenza',
        'ECG', 'Troponina',
    ]
    tipos = {}
    for nome in tipos_nomes:
        t = TipoExame.query.filter_by(nome=nome).first()
        if not t:
            t = TipoExame(nome=nome)
            db.session.add(t)
            db.session.flush()
        tipos[nome] = t.id
    return tipos


def normalizar_gravidades():
    """Corrige gravidades antigas (Moderada, Grave...) para o padrão do sistema."""
    mapa = {
        'MODERADA': 'MODERADA', 'MODERADO': 'MODERADA', 'MÉDIA': 'MODERADA', 'MEDIO': 'MODERADA',
        'LEVE': 'LEVE', 'GRAVE': 'GRAVE', 'CRITICA': 'CRITICA', 'CRÍTICA': 'CRITICA',
    }
    alterou = False
    for d in Diagnostico.query.all():
        raw = (d.gravidade or '').strip().upper()
        norm = mapa.get(raw) or mapa.get(raw.replace('Í', 'I'))
        if not norm and raw:
            if 'MODER' in raw:
                norm = 'MODERADA'
            elif 'GRAV' in raw:
                norm = 'GRAVE'
            elif 'CRIT' in raw:
                norm = 'CRITICA'
            elif 'LEV' in raw:
                norm = 'LEVE'
        if norm and d.gravidade != norm:
            d.gravidade = norm
            alterou = True
    if alterou:
        db.session.commit()
        print('[OK] Gravidades de diagnosticos normalizadas')


def _criar_consulta(medico, paciente, cfg, tipos=None):
    c = Consulta(
        id_paciente=paciente.id_paciente,
        id_medico=medico.id,
        data_consulta=_dt(cfg['data'], cfg['hora']),
        hora_consulta=cfg['hora'],
        status=cfg.get('status', 'AGENDADA'),
        motivo=cfg['motivo'],
        tipo_consulta=cfg.get('tipo', '1ª Consulta'),
        convenio=cfg.get('convenio', 'Particular'),
    )
    pr = cfg.get('prontuario')
    if pr:
        c.queixa_principal = pr.get('queixa', cfg['motivo'])
        c.historia_molestia_atual = pr.get('hma', '')
        c.antecedentes_pessoais = pr.get('ap', '')
        c.antecedentes_familiares = pr.get('af', '')
        c.exame_fisico = pr.get('exame_fisico', '')
        c.hipotese_diagnostica = pr.get('hipotese', '')
        c.plano_terapeutico = pr.get('plano', '')

    db.session.add(c)
    db.session.flush()

    diag = cfg.get('diagnostico')
    if diag:
        db.session.add(Diagnostico(
            id_consulta=c.id_consulta,
            id_paciente=paciente.id_paciente,
            id_medico=medico.id,
            cid=diag['cid'],
            descricao=diag['descricao'],
            gravidade=diag['gravidade'],
            status='ATIVO',
        ))

    sv = cfg.get('sinais')
    if sv:
        db.session.add(SinalVital(id_consulta=c.id_consulta, **sv))

    if tipos and cfg.get('exames'):
        for nome_ex, tipo_key in cfg['exames']:
            db.session.add(Exame(
                id_consulta=c.id_consulta,
                id_paciente=paciente.id_paciente,
                id_medico=medico.id,
                id_tipo_exame=tipos[tipo_key],
                nome_exame=nome_ex,
                status='SOLICITADO',
                prioridade=cfg.get('prioridade_exame', 'NORMAL'),
            ))

    preco = PrecoConsulta.query.filter_by(
        tipo_consulta=c.tipo_consulta,
        modalidade='Particular' if c.convenio == 'Particular' else 'Convenio',
        nome_convenio=None if c.convenio == 'Particular' else c.convenio,
    ).first()
    db.session.add(Receita(
        id_consulta=c.id_consulta,
        id_paciente=paciente.id_paciente,
        id_medico=medico.id,
        descricao=f'Consulta — {c.tipo_consulta}',
        valor=preco.valor if preco else 150.0,
        tipo=c.convenio,
        convenio=c.convenio,
        status='PENDENTE' if c.status != 'CONCLUIDA' else 'PAGO',
    ))
    return c


def seed_pacientes_risco():
    """Pacientes baixo / médio / alto / crítico para o sino de alertas."""
    niveis_necessarios = {'LEVE', 'MODERADA', 'GRAVE', 'CRITICA'}
    existentes = {
        (d.gravidade or '').upper()
        for d in Diagnostico.query.filter_by(status='ATIVO').all()
    }
    if niveis_necessarios.issubset(existentes):
        return False

    medico = _medico_demo()
    if not medico:
        print('[INFO] Seed risco: medico demo nao encontrado')
        return False

    tipos = _tipos_exame()
    hoje = date.today()
    inseridos = 0

    tiers = [
        {
            'cpf': '11144477735',
            'nome': 'Lucia Ferreira',
            'data_nascimento': date(1995, 4, 10),
            'sexo': 'F',
            'telefone': '11911112222',
            'alergias': None,
            'consulta': {
                'data': hoje, 'hora': '08:00', 'status': 'CONCLUIDA',
                'motivo': 'Check-up anual', 'tipo': '1ª Consulta',
                'diagnostico': {
                    'cid': 'Z00.0', 'descricao': 'Exame geral e investigação de pessoas sem queixas',
                    'gravidade': 'LEVE',
                },
            },
        },
        {
            'cpf': '55667788903',
            'nome': 'Fernanda Costa',
            'data_nascimento': date(1972, 8, 15),
            'sexo': 'F',
            'telefone': '11922223333',
            'alergias': 'Sulfas',
            'consulta': {
                'data': hoje, 'hora': '15:30', 'status': 'EM_ATENDIMENTO',
                'motivo': 'Pressão elevada e cefaleia', 'tipo': 'Retorno',
                'diagnostico': {
                    'cid': 'I10', 'descricao': 'Hipertensão essencial (primária) — controle irregular',
                    'gravidade': 'MODERADA',
                },
                'prontuario': {
                    'queixa': 'Cefaleia occipital há 5 dias, PA medida em casa 150/95',
                    'hma': 'Paciente hipertensa em uso irregular de Losartana 50mg. Relata tontura matinal.',
                    'ap': 'HAS diagnosticada há 8 anos. Nega DM. Sedentária.',
                    'af': 'Mãe: HAS. Pai: falecido IAM.',
                    'exame_fisico': 'PA 148/94 mmHg, bulhas rítmicas normofonéticas, edema de MMII ausente.',
                    'hipotese': 'HAS estágio 2 — controle pressórico inadequado',
                    'plano': 'Ajuste Losartana 100mg/dia. Dieta hipossódica. MAPA. Retorno 30 dias.',
                },
                'sinais': {
                    'pressao_arterial': '148/94', 'frequencia_cardiaca': 82,
                    'saturacao_oxigenio': 98, 'temperatura': 36.7, 'peso': 78.5,
                },
                'exames': [
                    ('MAPA 24h', 'ECG'),
                    ('Creatinina e ureia', 'Glicemia'),
                ],
            },
        },
        {
            'cpf': '39053344705',
            'nome': 'Maria Oliveira',
            'skip_if_exists': True,
            'only_diag': True,
            'consulta': {
                'data': hoje, 'hora': '11:00', 'status': 'EM_ATENDIMENTO',
                'motivo': 'Dispneia progressiva', 'tipo': 'Urgência',
                'diagnostico': {
                    'cid': 'J44.1', 'descricao': 'Doença pulmonar obstrutiva crônica com exacerbação aguda',
                    'gravidade': 'GRAVE',
                },
                'sinais': {
                    'pressao_arterial': '135/88', 'frequencia_cardiaca': 105,
                    'saturacao_oxigenio': 89, 'temperatura': 37.2, 'peso': 62.0,
                },
                'exames': [('Gasometria arterial', 'Glicemia'), ('Rx Tórax PA', 'Raio-X Tórax')],
                'prioridade_exame': 'URGENTE',
            },
        },
        {
            'cpf': MARCA_RISCO_CPF,
            'nome': 'Pedro Almeida',
            'data_nascimento': date(1960, 12, 3),
            'sexo': 'M',
            'telefone': '11933334444',
            'alergias': 'AAS',
            'consulta': {
                'data': hoje, 'hora': '17:00', 'status': 'EM_ATENDIMENTO',
                'motivo': 'Dor torácica intensa', 'tipo': 'Urgência',
                'diagnostico': {
                    'cid': 'I21.9', 'descricao': 'Infarto agudo do miocárdio — suspeita clínica',
                    'gravidade': 'CRITICA',
                },
                'sinais': {
                    'pressao_arterial': '90/60', 'frequencia_cardiaca': 118,
                    'saturacao_oxigenio': 91, 'temperatura': 36.5, 'peso': 81.0,
                },
                'exames': [('ECG 12 derivações', 'ECG'), ('Troponina I', 'Troponina')],
                'prioridade_exame': 'URGENTE',
            },
        },
    ]

    for tier in tiers:
        paciente = Paciente.query.filter_by(cpf=tier['cpf']).first()
        if tier.get('only_diag'):
            if not paciente:
                continue
            cfg = tier['consulta']
            grav = cfg['diagnostico']['gravidade']
            if grav in existentes:
                continue
            ja_tem = Diagnostico.query.filter_by(
                id_paciente=paciente.id_paciente,
                gravidade=grav,
                status='ATIVO',
            ).first()
            if ja_tem:
                continue
            _criar_consulta(medico, paciente, cfg, tipos)
            existentes.add(grav)
            inseridos += 1
            continue

        if paciente:
            continue

        if 'data_nascimento' not in tier:
            continue

        paciente = Paciente(
            cpf=tier['cpf'], nome=tier['nome'],
            data_nascimento=tier['data_nascimento'],
            sexo=tier['sexo'], telefone=tier.get('telefone'),
            alergias=tier.get('alergias'), ativo=True,
        )
        db.session.add(paciente)
        db.session.flush()
        _criar_consulta(medico, paciente, tier['consulta'], tipos)
        existentes.add(tier['consulta']['diagnostico']['gravidade'])
        inseridos += 1

    if inseridos:
        db.session.commit()
        print(f'[OK] Seed risco: {inseridos} paciente(s)/consulta(s) clinicas inseridos')
        print('  Sino: LEVE (Lucia), MÉDIO (Fernanda+Carlos), ALTO (Maria), CRÍTICO (Pedro)')
    return inseridos > 0


def seed_dados_demo():
    if Paciente.query.filter_by(cpf=MARCA_CPF).first():
        return False

    medico = _medico_demo()
    if not medico:
        print('[INFO] Seed demo: medico drcarlos@medsystem.com nao encontrado - pulando')
        return False

    tipos = _tipos_exame()
    hoje = date.today()

    pacientes_data = [
        {
            'cpf': MARCA_CPF,
            'nome': 'Carlos Alberto Silva',
            'data_nascimento': date(1985, 3, 12),
            'sexo': 'M',
            'telefone': '11987654321',
            'email': 'carlos.alberto@email.com',
            'tipo_sanguineo': 'O+',
            'alergias': 'Dipirona',
            'endereco': 'Rua das Flores, 120 — São Paulo/SP',
        },
        {
            'cpf': '39053344705',
            'nome': 'Maria Oliveira',
            'data_nascimento': date(1978, 7, 22),
            'sexo': 'F',
            'telefone': '11976543210',
            'email': 'maria.oliveira@email.com',
            'tipo_sanguineo': 'A+',
        },
        {
            'cpf': '15350946056',
            'nome': 'João da Silva',
            'data_nascimento': date(1992, 11, 5),
            'sexo': 'M',
            'telefone': '11965432109',
            'alergias': 'Penicilina',
        },
        {
            'cpf': '23100299900',
            'nome': 'Ana Beatriz Costa',
            'data_nascimento': date(1990, 1, 18),
            'sexo': 'F',
            'telefone': '11954321098',
        },
    ]

    pacientes = {}
    for pd in pacientes_data:
        p = Paciente(ativo=True, **pd)
        db.session.add(p)
        db.session.flush()
        pacientes[pd['cpf']] = p

    carlos = pacientes[MARCA_CPF]
    maria = pacientes['39053344705']
    joao = pacientes['15350946056']

    consultas_cfg = [
        {
            'paciente': carlos, 'data': hoje, 'hora': '09:30',
            'status': 'EM_ATENDIMENTO', 'motivo': 'Febre e tosse seca',
            'tipo': '1ª Consulta', 'convenio': 'Particular', 'prontuario': True,
        },
        {
            'paciente': maria, 'data': hoje, 'hora': '14:00',
            'status': 'AGENDADA', 'motivo': 'Retorno HAS',
            'tipo': 'Retorno', 'convenio': 'Unimed', 'prontuario': False,
        },
        {
            'paciente': joao, 'data': hoje + timedelta(days=1), 'hora': '11:00',
            'status': 'AGENDADA', 'motivo': 'Check-up anual',
            'tipo': '1ª Consulta', 'convenio': 'Particular', 'prontuario': False,
        },
        {
            'paciente': carlos, 'data': hoje - timedelta(days=7), 'hora': '08:00',
            'status': 'CONCLUIDA', 'motivo': 'Retorno pós-gripe',
            'tipo': 'Retorno', 'convenio': 'Particular', 'prontuario': True, 'concluido': True,
        },
    ]

    consulta_prontuario = None
    for cfg in consultas_cfg:
        c = Consulta(
            id_paciente=cfg['paciente'].id_paciente,
            id_medico=medico.id,
            data_consulta=_dt(cfg['data'], cfg['hora']),
            hora_consulta=cfg['hora'],
            status=cfg['status'],
            motivo=cfg['motivo'],
            tipo_consulta=cfg['tipo'],
            convenio=cfg['convenio'],
        )
        if cfg.get('prontuario'):
            c.queixa_principal = cfg['motivo']
            c.historia_molestia_atual = (
                'Paciente relata febre entre 38-39°C, mais intensa à tarde. '
                'Tosse seca sem expectoração. Nega dispneia.'
            )
            c.antecedentes_pessoais = 'Sem comorbidades prévias. Vacinação COVID em dia.'
            c.antecedentes_familiares = 'Pai: HAS. Mãe: DM2.'
            c.exame_fisico = 'MV presente bilateralmente, sem ruídos adventícios.'
            c.hipotese_diagnostica = 'Síndrome gripal — provável origem viral'
            c.plano_terapeutico = 'Repouso, hidratação e Dipirona 500mg 6/6h se febre > 37,8°C.'
        if cfg.get('concluido'):
            c.plano_terapeutico = 'Alta com orientações.'

        db.session.add(c)
        db.session.flush()
        if cfg['data'] == hoje and cfg['hora'] == '09:30':
            consulta_prontuario = c

        preco = PrecoConsulta.query.filter_by(
            tipo_consulta=cfg['tipo'],
            modalidade='Particular' if cfg['convenio'] == 'Particular' else 'Convenio',
            nome_convenio=None if cfg['convenio'] == 'Particular' else cfg['convenio'],
        ).first()
        db.session.add(Receita(
            id_consulta=c.id_consulta,
            id_paciente=cfg['paciente'].id_paciente,
            id_medico=medico.id,
            descricao=f"Consulta — {cfg['tipo']}",
            valor=preco.valor if preco else 150.0,
            tipo=cfg['convenio'], convenio=cfg['convenio'],
            status='PENDENTE' if cfg['status'] != 'CONCLUIDA' else 'PAGO',
        ))

    if consulta_prontuario:
        db.session.add(SinalVital(
            id_consulta=consulta_prontuario.id_consulta,
            pressao_arterial='120/80', frequencia_cardiaca=88,
            saturacao_oxigenio=97, temperatura=38.4, peso=74.0,
        ))
        db.session.add(Diagnostico(
            id_consulta=consulta_prontuario.id_consulta,
            id_paciente=carlos.id_paciente, id_medico=medico.id,
            cid='J06.9', descricao='Infecção aguda das vias aéreas superiores',
            gravidade='MODERADA', status='ATIVO',
        ))
        for nome_ex, tipo_n in [
            ('Hemograma completo', 'Hemograma Completo'),
            ('PCR', 'PCR'),
            ('Rx Tórax', 'Raio-X Tórax'),
        ]:
            db.session.add(Exame(
                id_consulta=consulta_prontuario.id_consulta,
                id_paciente=carlos.id_paciente, id_medico=medico.id,
                id_tipo_exame=tipos[tipo_n], nome_exame=nome_ex,
                status='SOLICITADO', prioridade='NORMAL',
            ))

    if not Despesa.query.first():
        db.session.add_all([
            Despesa(descricao='Aluguel consultório', valor=3500.0, categoria='Aluguel', tipo='FIXA', status='PAGO'),
            Despesa(descricao='Material descartável', valor=890.0, categoria='Material', tipo='VARIAVEL', status='PENDENTE'),
        ])

    db.session.commit()
    print('[OK] Dados demo base inseridos')
    return True


def seed_cid10():
    """Popula a tabela CID-10 (busca de diagnósticos). Idempotente."""
    if CID10.query.first():
        return
    cid_data = [
        {'codigo': 'I10', 'descricao': 'Hipertensão Arterial Sistêmica', 'categoria': 'Cardiovascular'},
        {'codigo': 'I25', 'descricao': 'Doença isquêmica crônica do coração', 'categoria': 'Cardiovascular'},
        {'codigo': 'I63', 'descricao': 'Acidente vascular cerebral isquêmico', 'categoria': 'Cardiovascular'},
        {'codigo': 'J06.9', 'descricao': 'Infecção aguda VAS não especificada', 'categoria': 'Respiratória'},
        {'codigo': 'J45', 'descricao': 'Asma', 'categoria': 'Respiratória'},
        {'codigo': 'J20.9', 'descricao': 'Bronquite aguda', 'categoria': 'Respiratória'},
        {'codigo': 'E11', 'descricao': 'Diabetes Mellitus tipo 2', 'categoria': 'Endócrina'},
        {'codigo': 'E10', 'descricao': 'Diabetes Mellitus tipo 1', 'categoria': 'Endócrina'},
        {'codigo': 'R73.0', 'descricao': 'Glicemia de jejum alterada', 'categoria': 'Endócrina'},
        {'codigo': 'M54', 'descricao': 'Dorsalgia', 'categoria': 'Musculoesquelética'},
        {'codigo': 'M79.3', 'descricao': 'Mialgia', 'categoria': 'Musculoesquelética'},
        {'codigo': 'M17', 'descricao': 'Gonartrose (artrose de joelho)', 'categoria': 'Musculoesquelética'},
        {'codigo': 'F41', 'descricao': 'Ansiedade', 'categoria': 'Mental'},
        {'codigo': 'F32', 'descricao': 'Depressão unipolar', 'categoria': 'Mental'},
        {'codigo': 'F43.2', 'descricao': 'Transtorno de ajustamento', 'categoria': 'Mental'},
        {'codigo': 'K21', 'descricao': 'Doença do refluxo gastroesofágico', 'categoria': 'Digestiva'},
        {'codigo': 'K29', 'descricao': 'Gastrite', 'categoria': 'Digestiva'},
        {'codigo': 'K59.1', 'descricao': 'Diarreia', 'categoria': 'Digestiva'},
        {'codigo': 'N39.0', 'descricao': 'Infecção do trato urinário', 'categoria': 'Genitourinária'},
        {'codigo': 'N40', 'descricao': 'Hiperplasia da próstata', 'categoria': 'Genitourinária'},
        {'codigo': 'L89', 'descricao': 'Úlcera de pressão', 'categoria': 'Dermatológica'},
        {'codigo': 'L30', 'descricao': 'Dermatite', 'categoria': 'Dermatológica'},
    ]
    for item in cid_data:
        db.session.add(CID10(**item))
    db.session.commit()
    print(f'[OK] {len(cid_data)} registros de CID-10 inseridos')


def seed_mensagens_demo():
    """Conversas demo entre recepção, médico e admin."""
    if Mensagem.query.first():
        return False

    recepcao = Usuario.query.filter_by(email='recepcao@medsystem.com').first()
    medico = Usuario.query.filter_by(email='drcarlos@medsystem.com').first()
    admin = Usuario.query.filter_by(email='medico@medsystem.com').first()
    if not recepcao or not medico:
        print('[INFO] Seed mensagens: usuarios demo nao encontrados - pulando')
        return False

    agora = datetime.utcnow()
    mensagens = [
        Mensagem(
            id_remetente=recepcao.id,
            id_destinatario=medico.id,
            conteudo='Dr. Carlos, o paciente Carlos Alberto chegou para a consulta das 09:00.',
            data_envio=agora - timedelta(hours=2),
            lida=False,
        ),
        Mensagem(
            id_remetente=medico.id,
            id_destinatario=recepcao.id,
            conteudo='Obrigado, Ana. Já estou a caminho da sala de consulta.',
            data_envio=agora - timedelta(hours=1, minutes=55),
            lida=True,
        ),
        Mensagem(
            id_remetente=recepcao.id,
            id_destinatario=medico.id,
            conteudo='Exames do João da Silva também chegaram. Posso anexar ao prontuário?',
            data_envio=agora - timedelta(hours=1, minutes=30),
            lida=False,
        ),
    ]

    if admin:
        mensagens.extend([
            Mensagem(
                id_remetente=admin.id,
                id_destinatario=recepcao.id,
                conteudo='Ana, favor confirmar a agenda de amanhã antes das 18h.',
                data_envio=agora - timedelta(minutes=45),
                lida=False,
            ),
            Mensagem(
                id_remetente=recepcao.id,
                id_destinatario=admin.id,
                conteudo='Confirmado! Todas as consultas de amanhã estão agendadas.',
                data_envio=agora - timedelta(minutes=20),
                lida=True,
            ),
        ])

    db.session.add_all(mensagens)
    db.session.commit()
    print(f'[OK] {len(mensagens)} mensagens demo inseridas')
    return True


def executar_seeds():
    """Roda todos os seeds de demonstração."""
    seed_cid10()
    normalizar_gravidades()
    seed_dados_demo()
    seed_pacientes_risco()
    seed_mensagens_demo()
    normalizar_gravidades()
