import os
import sys
from dotenv import load_dotenv
from agent.core import PersonalAgent
from agent import memory as mem_module

load_dotenv()
os.system("")

BACKEND_MAP = {
    "1": "local",
    "2": "groq",
    "3": "huggingface",
    "4": "deepseek",
}
BACKEND_LABEL = {
    "local": "Ollama (local)",
    "groq": "Groq",
    "huggingface": "Hugging Face",
    "deepseek": "DeepSeek",
}

# --- Cores ANSI ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[97m"
RED = "\033[31m"

LINE = "=" * 60


def print_help(backend: str = None, routing: bool = False):
    backend_label = BACKEND_LABEL.get(backend, backend or "?")
    routing_str = "ativo" if routing else "inativo"

    print()
    print(f"{BOLD}{WHITE}{LINE}{RESET}")
    print(f"{BOLD}{CYAN}Agent Moon — Assistente Pessoal{RESET}")
    print(f"{BOLD}{WHITE}{LINE}{RESET}")
    print(f"{DIM}Backend padrão:{RESET} {GREEN}{backend_label}{RESET} "
          f"{DIM}|{RESET} {DIM}Roteamento:{RESET} "
          f"{GREEN if routing else YELLOW}{routing_str}{RESET}")
    print(f"{DIM}Ferramentas disponíveis:{RESET}")
    print()

    print(f"{BOLD}{GREEN}📁 ORGANIZAÇÃO{RESET}")
    print(f"  {GREEN}•{RESET} {BOLD}save_note{RESET}         {DIM}— Salva uma nota em notes/{RESET}")
    print(f"  {GREEN}•{RESET} {BOLD}list_files{RESET}        {DIM}— Lista arquivos de um diretório{RESET}")
    print(f"  {GREEN}•{RESET} {BOLD}run_safe_command{RESET}  {DIM}— Executa comando seguro (whitelist){RESET}")
    print()

    print(f"{BOLD}{MAGENTA}🔐 SEGURANÇA DE DADOS{RESET}")
    print(f"  {MAGENTA}•{RESET} {BOLD}encrypt_file{RESET}            {DIM}— Criptografa arquivo (AES){RESET}")
    print(f"  {MAGENTA}•{RESET} {BOLD}decrypt_file{RESET}            {DIM}— Descriptografa arquivo .enc{RESET}")
    print(f"  {MAGENTA}•{RESET} {BOLD}check_password_strength{RESET} {DIM}— Avalia força de senha{RESET}")
    print(f"  {MAGENTA}•{RESET} {BOLD}hash_text{RESET}               {DIM}— Gera hash (sha256, etc.){RESET}")
    print(f"  {MAGENTA}•{RESET} {BOLD}generate_password{RESET}       {DIM}— Gera senha aleatória{RESET}")
    print()

    print(f"{BOLD}{YELLOW}🛡️  PENTEST{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}nmap_scan{RESET}         {DIM}— Varredura com nmap{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}port_scan_python{RESET}  {DIM}— Varredura de portas TCP{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}http_headers{RESET}      {DIM}— Cabeçalhos HTTP{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}ssl_cert_info{RESET}     {DIM}— Certificado SSL/TLS{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}check_robots_txt{RESET}  {DIM}— Lê robots.txt{RESET}")
    print(f"  {YELLOW}•{RESET} {BOLD}ping_host{RESET}         {DIM}— Testa se host responde{RESET}")
    print()

    print(f"{BOLD}{CYAN}💻 CODIFICAÇÃO{RESET}")
    print(f"  {CYAN}•{RESET} {BOLD}read_file{RESET}           {DIM}— Lê arquivo de código{RESET}")
    print(f"  {CYAN}•{RESET} {BOLD}list_project_tree{RESET}   {DIM}— Mostra estrutura de diretórios{RESET}")
    print(f"  {CYAN}•{RESET} {BOLD}search_in_code{RESET}      {DIM}— Busca termo no código{RESET}")
    print(f"  {CYAN}•{RESET} {BOLD}git_diff{RESET}            {DIM}— Mostra alterações não commitadas{RESET}")
    print(f"  {CYAN}•{RESET} {BOLD}git_log{RESET}             {DIM}— Últimos commits do repositório{RESET}")
    print()

    print(f"{BOLD}{BLUE}💬 SESSÃO{RESET}")
    print(f"  {BLUE}•{RESET} {BOLD}historico{RESET}         {DIM}— Últimas 10 mensagens desta sessão{RESET}")
    print(f"  {BLUE}•{RESET} {BOLD}buscar <termo>{RESET}    {DIM}— Busca no histórico completo{RESET}")
    print(f"  {BLUE}•{RESET} {BOLD}limpar{RESET}            {DIM}— Apaga todo o histórico{RESET}")
    print()

    print(f"{BOLD}{BLUE}Dicas:{RESET}")
    print(f"  {BLUE}•{RESET} \"Liste os arquivos da pasta\"")
    print(f"  {BLUE}•{RESET} \"Gere uma senha de 24 caracteres\"")
    print(f"  {BLUE}•{RESET} \"Faça um scan rápido no localhost\"")

    print(f"{BOLD}{WHITE}{LINE}{RESET}")
    print()


def cmd_historico(session_id):
    rows = mem_module.get_session_history(session_id, limit=10)
    if not rows:
        print(f"{DIM}Nenhuma mensagem nesta sessão ainda.{RESET}")
        return
    print()
    print(f"{BOLD}{CYAN}Histórico desta sessão:{RESET}")
    for row in rows:
        role = row["role"]
        content = row["content"]
        if len(content) > 150:
            content = content[:150] + "..."
        if role == "user":
            print(f"  {BOLD}Você:{RESET} {content}")
        else:
            print(f"  {GREEN}Agente:{RESET} {content}")
    print()


def cmd_buscar(term):
    if not term:
        print(f"{YELLOW}Uso: buscar <termo>{RESET}")
        return
    rows = mem_module.search(term, limit=10)
    if not rows:
        print(f"{DIM}Nada encontrado para '{term}'.{RESET}")
        return
    print()
    print(f"{BOLD}{CYAN}Resultados para '{term}':{RESET}")
    for row in rows:
        role = row["role"]
        content = row["content"]
        if len(content) > 150:
            content = content[:150] + "..."
        date = row["created_at"]
        color = BOLD if role == "user" else GREEN
        label = "Você" if role == "user" else "Agente"
        print(f"  {DIM}[{date}]{RESET} {color}{label}:{RESET} {content}")
    print()


def cmd_limpar():
    total = mem_module.count_messages()
    if total == 0:
        print(f"{DIM}Histórico já está vazio.{RESET}")
        return
    resp = input(f"{RED}Apagar todas as {total} mensagens do histórico? (s/N): {RESET}")
    if resp.strip().lower() == "s":
        mem_module.clear_all()
        print(f"{GREEN}Histórico apagado.{RESET}")
    else:
        print(f"{DIM}Cancelado.{RESET}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in BACKEND_MAP:
        backend = BACKEND_MAP[sys.argv[1]]
        print(f"{GREEN}Backend pré-selecionado:{RESET} {backend}")
    else:
        print("Agente Pessoal - escolha o backend:")
        print("1 - Local (Ollama)")
        print("2 - Groq")
        print("3 - Hugging Face")
        print("4 - DeepSeek")
        choice = input("Opção (1-4): ")
        backend = BACKEND_MAP.get(choice, "local")

    enable_routing = backend in ("groq", "huggingface", "deepseek")
    agent = PersonalAgent(
        backend_type=backend,
        enable_routing=enable_routing,
        default_backend=backend,
    )

    total_hist = mem_module.count_messages()
    if enable_routing:
        print(f"{GREEN}Roteamento ativo:{RESET} sensíveis → local | demais → {backend}")
    if agent.past_context:
        print(f"{DIM}Memórias de sessões anteriores: {len(agent.past_context)} mensagens{RESET}")
    if total_hist:
        print(f"{DIM}Sessão:{RESET} {agent.session_id} {DIM}| total no histórico: {total_hist}{RESET}")
    print(f"\n{BOLD}Agente iniciado.{RESET} Digite {CYAN}'help'{RESET} para ver comandos, "
          f"{CYAN}'sair'{RESET} para encerrar.\n")

    while True:
        try:
            user_input = input(f"{BOLD}Você:{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        cmd = user_input.strip().lower()
        if cmd in ["sair", "exit", "quit"]:
            print("Até logo!")
            break
        if cmd in ["help", "?", "ajuda"]:
            print_help(backend=backend, routing=enable_routing)
            continue
        if cmd == "historico":
            cmd_historico(agent.session_id)
            continue
        if cmd.startswith("buscar "):
            cmd_buscar(user_input.strip()[7:].strip())
            continue
        if cmd == "limpar":
            cmd_limpar()
            continue
        if not cmd:
            continue

        try:
            response = agent.ask(user_input)
            print(f"{BOLD}Agente:{RESET} {response}")
        except Exception as e:
            print(f"{YELLOW}Erro:{RESET} {e}")


if __name__ == "__main__":
    main()