import os
import time
import funcoes as fc

# --- Cores ---
VERMELHO = '\033[91m'
VERDE    = '\033[92m'
AMARELO  = '\033[93m'
AZUL     = '\033[94m'
CIANO    = '\033[96m'
BOLD     = '\033[1m'
RESET    = '\033[0m'
EMOJI_SUCESSO = "✅"
EMOJI_ALERTA  = "⚠️"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

while True:
    limpar_tela()
    print(f"{BOLD}{AZUL}========================================={RESET}")
    print(f"{BOLD}{AZUL}      BEM-VINDO À PONTE ACADÊMICA      {RESET}")
    print(f"{BOLD}{AZUL}========================================={RESET}")
    time.sleep(0.3)

    print(f"{CIANO}1 - Login (RGM + Senha){RESET}")
    print(f"{CIANO}2 - Cadastrar Usuário{RESET}")
    print(f"{VERMELHO}0 - Sair{RESET}")
    print(f"{BOLD}{AZUL}========================================={RESET}")

    opt = input(f"{BOLD}Entre com a opção desejada: {RESET}").strip()
    limpar_tela()

    if opt == "1":
        rgm_logado = fc.realizar_login()     # retorna RGM se ok
        if rgm_logado:
            fc.menu_projetos(rgm_logado)     # abre o menu interno
    elif opt == "2":
        fc.realizar_cadastro_usuario()
    elif opt == "0":
        print(f"Saindo do sistema... {EMOJI_SUCESSO}")
        break
    else:
        print(f"{VERMELHO}Opção inválida! {EMOJI_ALERTA}{RESET}")
        input(f"{AZUL}Digite Enter para voltar ao menu{RESET}")