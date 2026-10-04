import subprocess
import os
from datetime import datetime

def save_note(content: str):
    """Salva uma nota em um arquivo de texto na pasta 'notes'."""
    notes_dir = os.path.abspath("notes")
    os.makedirs(notes_dir, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    filepath = os.path.join(notes_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"OK. Caminho exato do arquivo salvo: {filepath}"

def list_files(directory: str = "."):
    """Lista arquivos e pastas no diretório especificado."""
    try:
        return "\n".join(os.listdir(directory))
    except Exception as e:
        return f"Erro: {e}"

def run_safe_command(command: str):
    """Executa um comando seguro no sistema (lista branca)."""
    allowed_commands = ["dir", "ls", "pwd", "whoami", "date", "echo"]
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in allowed_commands:
        return "Comando não permitido."
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout or result.stderr
    except Exception as e:
        return f"Erro ao executar comando: {e}"