import socket

"""
router.py — Decide qual backend usar para cada pergunta.

Estratégia (v1): palavras-chave.
- Se a pergunta contém termos sensíveis → backend local (privacidade).
- Caso contrário → backend padrão (definido pelo usuário, geralmente nuvem).
"""

# Palavras-chave que acionam o backend local (privacidade)
SENSITIVE_KEYWORDS = [
    # senhas e credenciais
    "senha", "password", "passwd", "credencial",
    # criptografia
    "criptograf", "descriptograf", "encrypt", "decrypt",
    "chave", "key", "fernet", "aes",
    # hash
    "hash", "sha256", "sha512", "md5",
    # notas pessoais
    "nota", "notas", "note", "notes",
    "pessoal", "pessoais", "privado", "privada",
    "privados", "privadas", "secreto", "secreta",
    "secredos", "secretos",
    # arquivos pessoais
    "meu arquivo", "meus arquivos", "documento pessoal",
    # ferramentas locais explícitas
    "save_note", "encrypt_file", "decrypt_file",
    "check_password_strength", "generate_password", "hash_text",
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def should_use_local(question: str) -> bool:
    """Retorna True se a pergunta deve ser processada localmente."""
    q = _normalize(question)
    for kw in SENSITIVE_KEYWORDS:
        if kw in q:
            return True
    return False


def route(question: str, default_backend: str = "groq",
          local_backend: str = "local") -> str:
    """
    Decide o backend para esta pergunta.
    - default_backend: usado quando a pergunta é neutra (ex.: 'groq')
    - local_backend: usado quando a pergunta é sensível (ex.: 'local')
    """
    if should_use_local(question):
        return local_backend
    return default_backend

def is_ollama_alive(host: str = "localhost", port: int = 11434,
                    timeout: float = 0.5) -> bool:
    """Verifica se o serviço do Ollama está escutando."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False