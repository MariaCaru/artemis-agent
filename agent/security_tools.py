import os
import hashlib
import secrets
import string
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn

NOTES_DIR = "notes"
KEYS_DIR = "keys"

def _ensure_dirs():
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(KEYS_DIR, exist_ok=True)

def encrypt_file(filepath: str):
    """Criptografa um arquivo usando Fernet (AES). Gera uma chave e salva em 'keys/'. Retorna o caminho do arquivo criptografado."""
    _ensure_dirs()
    if not os.path.exists(filepath):
        return f"Arquivo não encontrado: {filepath}"
    key = Fernet.generate_key()
    key_name = os.path.basename(filepath) + ".key"
    key_path = os.path.join(KEYS_DIR, key_name)
    with open(key_path, "wb") as kf:
        kf.write(key)
    cipher = Fernet(key)
    with open(filepath, "rb") as f:
        data = f.read()
    encrypted = cipher.encrypt(data)
    out_path = filepath + ".enc"
    with open(out_path, "wb") as f:
        f.write(encrypted)
    return f"Arquivo criptografado: {out_path}. Chave salva em: {key_path}"

def decrypt_file(filepath: str, key_path: str = ""):
    """Descriptografa um arquivo .enc. Se key_path não for fornecida, tenta 'keys/<nome>.key'."""
    if not os.path.exists(filepath):
        return f"Arquivo não encontrado: {filepath}"
    if not key_path:
        key_path = os.path.join(KEYS_DIR, os.path.basename(filepath).replace(".enc", "") + ".key")
    if not os.path.exists(key_path):
        return f"Chave não encontrada em {key_path}"
    with open(key_path, "rb") as kf:
        key = kf.read()
    cipher = Fernet(key)
    with open(filepath, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = cipher.decrypt(encrypted)
    except Exception as e:
        return f"Falha ao descriptografar (chave incorreta?): {e}"
    out_path = filepath.replace(".enc", ".dec")
    with open(out_path, "wb") as f:
        f.write(decrypted)
    return f"Arquivo descriptografado: {out_path}"

def check_password_strength(password: str):
    """Avalia a força de uma senha com zxcvbn. Retorna pontuação 0-4, tempo de quebra estimado e sugestões."""
    result = zxcvbn(password)
    score = result["score"]
    crack_time = result["crack_times_display"]["offline_slow_hashing_1e4_per_second"]
    feedback = result["feedback"]
    msg = f"Força: {score}/4 (tempo estimado de quebra: {crack_time})."
    if feedback.get("warning"):
        msg += f" Aviso: {feedback['warning']}."
    if feedback.get("suggestions"):
        msg += " Sugestões: " + "; ".join(feedback["suggestions"]) + "."
    return msg

def hash_text(text: str, algorithm: str = "sha256"):
    """Gera hash do texto. Algoritmos suportados: sha256, sha512, sha1, md5."""
    if algorithm not in hashlib.algorithms_available:
        return f"Algoritmo '{algorithm}' não suportado."
    h = hashlib.new(algorithm)
    h.update(text.encode("utf-8"))
    return f"Hash {algorithm}: {h.hexdigest()}"

def generate_password(length: str = "16"):
    """Gera uma senha aleatória segura. Passe o comprimento como texto (padrão 16)."""
    try:
        n = int(length)
    except (ValueError, TypeError):
        n = 16
    if n < 8:
        n = 8
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(n))
    return f"Senha gerada ({n} caracteres): {password}"