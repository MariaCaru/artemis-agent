"""
code_tools.py — Ferramentas de leitura de código e git.
Todas as operações são restritas a ALLOWED_ROOT (D:\\projetos_dev).
Somente leitura — nenhuma ferramenta escreve ou apaga.
"""

import os
import subprocess
from pathlib import Path

ALLOWED_ROOT = Path(r"D:\projetos_dev").resolve()

IGNORE_DIRS = {
    "venv", ".venv", "__pycache__", ".git", "node_modules",
    "dist", "build", ".idea", ".vscode", ".next", "target",
    "bin", "obj", ".pytest_cache", ".mypy_cache", "keys", "notes",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".kt",
    ".swift", ".sh", ".ps1", ".bat", ".sql",
    ".html", ".css", ".scss", ".sass", ".vue", ".svelte",
    ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".env",
    ".xml", ".dockerfile",
}

MAX_READ_CHARS = 30000
MAX_TREE_ENTRIES = 400
MAX_SEARCH_RESULTS = 30


def _safe_path(user_path: str) -> Path:
    p = Path(user_path)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p.resolve()


def _is_allowed(p: Path) -> bool:
    try:
        p.relative_to(ALLOWED_ROOT)
        return True
    except ValueError:
        return False


def read_file(entrada: str):
    """Lê um arquivo de código (máx 30 KB). Entrada: '<caminho_do_arquivo>'."""
    if not entrada.strip():
        return "Uso: read_file | '<caminho>'"
    p = _safe_path(entrada.strip().strip('"').strip("'"))
    if not _is_allowed(p):
        return f"Acesso negado: '{p}' está fora de {ALLOWED_ROOT}"
    if not p.exists():
        return f"Arquivo não encontrado: {p}"
    if p.is_dir():
        return f"'{p}' é um diretório. Use list_project_tree."
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_READ_CHARS + 1)
        if len(content) > MAX_READ_CHARS:
            content = content[:MAX_READ_CHARS] + (
                f"\n\n[... truncado em {MAX_READ_CHARS} caracteres ...]"
            )
        return f"# Arquivo: {p}\n\n{content}"
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


def list_project_tree(entrada: str):
    """Mostra a estrutura de diretórios. Entrada: '<caminho>' (padrão: diretório atual)."""
    target = _safe_path(entrada.strip()) if entrada.strip() else Path.cwd()
    if not _is_allowed(target):
        return f"Acesso negado: '{target}' está fora de {ALLOWED_ROOT}"
    if not target.exists():
        return f"Caminho não encontrado: {target}"
    if not target.is_dir():
        return f"'{target}' não é diretório."

    lines = [f"# Estrutura: {target}"]
    count = [0]

    def walk(path: Path, prefix: str = ""):
        if count[0] >= MAX_TREE_ENTRIES:
            return
        try:
            entries = sorted(
                path.iterdir(),
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
        except Exception:
            return
        for e in entries:
            if count[0] >= MAX_TREE_ENTRIES:
                lines.append(f"{prefix}... (truncado)")
                return
            if e.name in IGNORE_DIRS:
                continue
            if e.is_dir():
                lines.append(f"{prefix}📁 {e.name}/")
                count[0] += 1
                walk(e, prefix + "  ")
            else:
                lines.append(f"{prefix}📄 {e.name}")
                count[0] += 1

    walk(target)
    return "\n".join(lines)


def search_in_code(entrada: str):
    """Busca termo em arquivos de código. Entrada: '<termo> [caminho] [extensão]'."""
    if not entrada.strip():
        return "Uso: search_in_code | '<termo> [caminho] [extensão]'"
    parts = entrada.strip().split()
    term = parts[0]
    path = Path.cwd()
    ext_filter = None
    for p in parts[1:]:
        if p.startswith("."):
            ext_filter = p.lower()
        else:
            cand = _safe_path(p)
            if cand.exists():
                path = cand
    if not _is_allowed(path):
        return f"Acesso negado: '{path}' está fora de {ALLOWED_ROOT}"

    results = []
    term_lower = term.lower()
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            ext = Path(f).suffix.lower()
            if ext_filter and ext != ext_filter:
                continue
            if not ext_filter and ext not in CODE_EXTENSIONS:
                continue
            full = Path(root) / f
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        if term_lower in line.lower():
                            results.append(f"{full}:{i}: {line.rstrip()[:200]}")
                            if len(results) >= MAX_SEARCH_RESULTS:
                                break
            except Exception:
                continue
            if len(results) >= MAX_SEARCH_RESULTS:
                break
        if len(results) >= MAX_SEARCH_RESULTS:
            break

    if not results:
        return f"Nenhum resultado para '{term}' em {path}"
    return (f"# Busca por '{term}' em {path} "
            f"({len(results)} resultado(s)):\n" + "\n".join(results))


def _run_git(args: list, cwd: Path, timeout: int = 20) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, cwd=str(cwd),
            capture_output=True, text=True, timeout=timeout
        )
        out = result.stdout or result.stderr or "(sem saída)"
        if len(out) > MAX_READ_CHARS:
            out = out[:MAX_READ_CHARS] + "\n[... truncado ...]"
        return out
    except FileNotFoundError:
        return "git não encontrado no PATH."
    except subprocess.TimeoutExpired:
        return "Tempo esgotado ao executar git."
    except Exception as e:
        return f"Erro ao executar git: {e}"


def git_diff(entrada: str):
    """Mostra alterações não commitadas (staged + unstaged). Entrada: '<caminho_do_repo>'."""
    if not entrada.strip():
        return "Uso: git_diff | '<caminho_do_repo>'"
    p = _safe_path(entrada.strip())
    if not _is_allowed(p):
        return f"Acesso negado: '{p}' está fora de {ALLOWED_ROOT}"
    if not p.exists():
        return f"Caminho não encontrado: {p}"
    if p.is_file():
        p = p.parent
    return _run_git(["diff", "HEAD"], p)


def git_log(entrada: str):
    """Últimos commits do repositório. Entrada: '<caminho_do_repo> [n]' (padrão n=10)."""
    parts = entrada.strip().split()
    if not parts:
        return "Uso: git_log | '<caminho_do_repo> [n]'"
    p = _safe_path(parts[0])
    try:
        n = int(parts[1]) if len(parts) > 1 else 10
    except ValueError:
        n = 10
    n = max(1, min(n, 50))
    if not _is_allowed(p):
        return f"Acesso negado: '{p}' está fora de {ALLOWED_ROOT}"
    if not p.exists():
        return f"Caminho não encontrado: {p}"
    if p.is_file():
        p = p.parent
    return _run_git(["log", f"-{n}", "--oneline", "--decorate"], p)