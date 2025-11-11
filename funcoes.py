import os
import sqlite3
import hashlib
import getpass
from datetime import datetime

# --- Cores e Emojis ---
VERMELHO = '\033[91m'
VERDE    = '\033[92m'
AMARELO  = '\033[93m'
AZUL     = '\033[94m'
CIANO    = '\033[96m'
BOLD     = '\033[1m'
RESET    = '\033[0m'
EMOJI_SUCESSO = "✅"
EMOJI_ALERTA  = "⚠️"

DB_PATH = os.path.join(os.path.dirname(__file__), "usuarios.db")

# ------------- Conexão / Setup -------------
def _conexao():
    return sqlite3.connect(DB_PATH)

def _inicializar_db():
    with _conexao() as conn:
        cur = conn.cursor()
        # Usuários (login por RGM)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                rgm INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );
        """)
        # Tabela PROJETO (modelo do professor)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projeto (
                id_projeto INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                rgm_aluno INTEGER NULL,          -- nulo = disponível
                cnpj_org INTEGER NOT NULL
            );
        """)
        conn.commit()

# ------------- Utilidades -------------
def _hash_senha(senha: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
    return h, salt

def _verifica_senha(senha_digitada: str, hash_salvo: str, salt_salvo: str) -> bool:
    h, _ = _hash_senha(senha_digitada, salt_salvo)
    return h == hash_salvo

def _pausar():
    input(f"{AZUL}Pressione Enter para continuar...{RESET}")

def _input_obrigatorio(msg: str) -> str:
    while True:
        v = input(msg).strip()
        if v:
            return v
        print(f"{AMARELO}Campo obrigatório.{RESET}")

def _input_int(msg: str) -> int:
    while True:
        v = input(msg).strip()
        if v.isdigit():
            return int(v)
        print(f"{AMARELO}Digite um número inteiro válido.{RESET}")

def _linha():
    print(f"{AZUL}" + "="*60 + f"{RESET}")

# ------------- Cadastro / Login (RGM) -------------
def realizar_cadastro_usuario():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== CADASTRAR USUÁRIO (RGM + SENHA) ==={RESET}")
    rgm = _input_int("RGM (somente números): ")
    nome = _input_obrigatorio("Nome completo: ")
    senha = getpass.getpass("Senha: ")
    senha2 = getpass.getpass("Confirmar senha: ")

    if senha != senha2:
        print(f"{VERMELHO}{EMOJI_ALERTA} Senhas não conferem.{RESET}")
        return _pausar()

    h, salt = _hash_senha(senha)
    try:
        with _conexao() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (rgm, nome, senha_hash, salt, criado_em) VALUES (?, ?, ?, ?, ?)",
                (rgm, nome, h, salt, datetime.now().isoformat(timespec="seconds"))
            )
            conn.commit()
        print(f"{VERDE}{EMOJI_SUCESSO} Usuário cadastrado! RGM: {rgm}{RESET}")
    except sqlite3.IntegrityError:
        print(f"{VERMELHO}{EMOJI_ALERTA} Já existe usuário com esse RGM.{RESET}")
    _pausar()

def realizar_login():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== LOGIN (RGM + SENHA) ==={RESET}")
    rgm = _input_int("RGM: ")
    senha = getpass.getpass("Senha: ")

    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute("SELECT senha_hash, salt, nome FROM usuarios WHERE rgm = ?", (rgm,))
        row = cur.fetchone()

    if not row:
        print(f"{VERMELHO}{EMOJI_ALERTA} RGM não encontrado.{RESET}")
        _pausar()
        return None

    senha_hash, salt, nome = row
    if _verifica_senha(senha, senha_hash, salt):
        print(f"{VERDE}{EMOJI_SUCESSO} Login ok! Bem-vindo(a), {BOLD}{nome}{RESET}{VERDE}.{RESET}")
        _pausar()
        return rgm
    else:
        print(f"{VERMELHO}{EMOJI_ALERTA} Senha incorreta.{RESET}")
        _pausar()
        return None

# ------------- MENU PROJETOS -------------
def menu_projetos(rgm_logado: int):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        _linha()
        print(f"{BOLD}{AZUL}SISTEMA PONTE ACADÊMICA - PROJETOS{RESET}")
        _linha()
        print("1 - Cadastrar Projeto")
        print("2 - Listar Projetos")
        print("3 - Atualizar Projeto")
        print("4 - Excluir Projeto")
        print("5 - Relatório de Pesquisa")
        print("6 - Candidatar ao projeto")
        print("0 - Sair")
        _linha()
        op = input("Escolha uma opção: ").strip()

        if op == "1":
            cadastrar_projeto()
        elif op == "2":
            listar_projetos()
        elif op == "3":
            atualizar_projeto()
        elif op == "4":
            excluir_projeto()
        elif op == "5":
            relatorio_pesquisa()
        elif op == "6":
            candidatar_projeto(rgm_logado)
        elif op == "0":
            break
        else:
            print(f"{AMARELO}Opção inválida.{RESET}")
            _pausar()

# ------------- Funcionalidades (CRUD + Relatório) -------------
def cadastrar_projeto():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== CADASTRAR PROJETO ==={RESET}")
    titulo = _input_obrigatorio("Título: ")
    descricao = _input_obrigatorio("Descrição: ")
    cnpj = _input_int("CNPJ da organização (somente números): ")

    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO projeto (titulo, descricao, rgm_aluno, cnpj_org)
            VALUES (?, ?, NULL, ?)
        """, (titulo, descricao, cnpj))
        conn.commit()
    print(f"{VERDE}{EMOJI_SUCESSO} Projeto cadastrado com sucesso!{RESET}")
    _pausar()

def listar_projetos():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== LISTAR PROJETOS ==={RESET}")
    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_projeto, titulo, descricao, 
                   COALESCE(CAST(rgm_aluno AS TEXT),'NULO') AS rgm_aluno,
                   cnpj_org
            FROM projeto
            ORDER BY id_projeto;
        """)
        rows = cur.fetchall()

    if not rows:
        print(f"{AMARELO}Nenhum projeto cadastrado.{RESET}")
        return _pausar()

    _linha()
    print(f"{BOLD}ID | TÍTULO | RGM_ALUNO | CNPJ_ORG{RESET}")
    _linha()
    for r in rows:
        idp, titulo, desc, rgm, cnpj = r
        print(f"{idp:>3} | {titulo} | {rgm} | {cnpj}")
    _linha()
    _pausar()

def atualizar_projeto():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== ATUALIZAR PROJETO ==={RESET}")
    idp = _input_int("ID do projeto: ")

    print("O que deseja alterar?")
    print("1 - Título")
    print("2 - Descrição")
    print("3 - Título e Descrição")
    escolha = input("Opção: ").strip()

    with _conexao() as conn:
        cur = conn.cursor()
        if escolha == "1":
            titulo = _input_obrigatorio("Novo título: ")
            cur.execute("UPDATE projeto SET titulo = ? WHERE id_projeto = ?", (titulo, idp))
        elif escolha == "2":
            descricao = _input_obrigatorio("Nova descrição: ")
            cur.execute("UPDATE projeto SET descricao = ? WHERE id_projeto = ?", (descricao, idp))
        elif escolha == "3":
            titulo = _input_obrigatorio("Novo título: ")
            descricao = _input_obrigatorio("Nova descrição: ")
            cur.execute("UPDATE projeto SET titulo = ?, descricao = ? WHERE id_projeto = ?", (titulo, descricao, idp))
        else:
            print(f"{AMARELO}Opção inválida.{RESET}")
            return _pausar()
        conn.commit()
    print(f"{VERDE}{EMOJI_SUCESSO} Projeto atualizado!{RESET}")
    _pausar()

def excluir_projeto():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== EXCLUIR PROJETO ==={RESET}")
    idp = _input_int("ID do projeto: ")
    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM projeto WHERE id_projeto = ?", (idp,))
        conn.commit()
    print(f"{VERDE}{EMOJI_SUCESSO} Projeto excluído!{RESET}")
    _pausar()

def relatorio_pesquisa():
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== RELATÓRIO DE PESQUISA ==={RESET}")
    print("Filtrar por Status:")
    print("1 - Disponível (sem aluno)")
    print("2 - Em Andamento (com aluno)")
    opc = input("Opção: ").strip()

    if opc == "1":
        status = "Disponível"
        where = "rgm_aluno IS NULL"
    elif opc == "2":
        status = "Em Andamento"
        where = "rgm_aluno IS NOT NULL"
    else:
        print(f"{AMARELO}Opção inválida.{RESET}")
        return _pausar()

    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT id_projeto, titulo, COALESCE(CAST(rgm_aluno AS TEXT),'NULO') AS rgm_aluno
            FROM projeto
            WHERE {where}
            ORDER BY id_projeto;
        """)
        rows = cur.fetchall()

    _linha()
    print(f"{BOLD}RELATÓRIO DE PESQUISA - PROJETOS {status.upper()}{RESET}")
    _linha()
    if not rows:
        print("Nenhum projeto encontrado.")
        _linha()
        return _pausar()

    for r in rows:
        print(f"{r[0]:>3} | {r[1]} | RGM_ALUNO: {r[2]}")
    _linha()
    print(f"Total de Projetos Encontrados: {len(rows)}")
    _linha()
    _pausar()

def candidatar_projeto(rgm_logado: int):
    _inicializar_db()
    print(f"{BOLD}{AZUL}=== CANDIDATAR AO PROJETO ==={RESET}")
    print("Somente projetos DISPONÍVEIS (sem aluno) podem ser escolhidos.")
    with _conexao() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_projeto, titulo FROM projeto
            WHERE rgm_aluno IS NULL
            ORDER BY id_projeto;
        """)
        livres = cur.fetchall()

    if not livres:
        print(f"{AMARELO}Não há projetos disponíveis no momento.{RESET}")
        return _pausar()

    for p in livres:
        print(f"{p[0]:>3} - {p[1]}")
    idp = _input_int("Digite o ID do projeto para se candidatar: ")

    with _conexao() as conn:
        cur = conn.cursor()
        # garante que ainda está livre
        cur.execute("SELECT rgm_aluno FROM projeto WHERE id_projeto = ?", (idp,))
        row = cur.fetchone()
        if not row:
            print(f"{VERMELHO}{EMOJI_ALERTA} Projeto não encontrado.{RESET}")
            return _pausar()
        if row[0] is not None:
            print(f"{AMARELO}Esse projeto já tem aluno vinculado.{RESET}")
            return _pausar()

        cur.execute("UPDATE projeto SET rgm_aluno = ? WHERE id_projeto = ?", (rgm_logado, idp))
        conn.commit()

    print(f"{VERDE}{EMOJI_SUCESSO} Você se candidatou ao projeto {idp} com sucesso!{RESET}")
    _pausar()