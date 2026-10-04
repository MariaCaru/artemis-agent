"""
watch.py — Reinicia o agente automaticamente quando arquivos .py são salvos.

Uso:
    python watch.py

Pressione Ctrl+C para encerrar.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---- Configurações ----
PROJECT_DIR = Path(__file__).parent.resolve()
WATCH_DIRS = ["agent", "."]           # pastas monitoradas
WATCH_EXTENSIONS = [".py"]            # extensões monitoradas
IGNORE_DIRS = {"venv", "__pycache__", ".git", "notes", "keys", ".vscode"}
DEBOUNCE_SECONDS = 1.0                # agrupa saves próximos
AGENT_CMD = [sys.executable, "main.py"]
# Se o usuário passou um argumento (ex.: python watch.py 2), repassa ao main.py
if len(sys.argv) > 1:
    AGENT_CMD.append(sys.argv[1])


class AgentRunner:
    """Gerencia o processo do agente (start/stop/restart)."""

    def __init__(self):
        self.process = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.process is not None:
                return
            print("\n" + "=" * 60)
            print(f"[watch] Iniciando agente: {' '.join(AGENT_CMD)}")
            print("=" * 60)
            # new_process_group permite matar o processo e filhos no Windows
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            self.process = subprocess.Popen(
                AGENT_CMD,
                cwd=str(PROJECT_DIR),
                creationflags=creationflags,
            )

    def stop(self):
        with self.lock:
            if self.process is None:
                return
            print("[watch] Parando agente...")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("[watch] Forçando encerramento...")
                    self.process.kill()
                    self.process.wait(timeout=3)
            except Exception as e:
                print(f"[watch] Erro ao parar: {e}")
            finally:
                self.process = None

    def restart(self):
        self.stop()
        time.sleep(0.3)
        self.start()


class ChangeHandler(FileSystemEventHandler):
    """Detecta mudanças em arquivos .py e agenda reinícios."""

    def __init__(self, runner: AgentRunner):
        self.runner = runner
        self.last_event_time = 0
        self.pending_timer = None
        self.timer_lock = threading.Lock()

    def _should_ignore(self, path: str) -> bool:
        p = Path(path)
        # Ignora pastas indesejadas
        for part in p.parts:
            if part in IGNORE_DIRS:
                return True
        # Ignora não-.py
        if p.suffix not in WATCH_EXTENSIONS:
            return True
        return False

    def _schedule_restart(self):
        """Debounce: agrupa múltiplos saves em um só restart."""
        with self.timer_lock:
            if self.pending_timer is not None:
                self.pending_timer.cancel()
            self.pending_timer = threading.Timer(DEBOUNCE_SECONDS, self._do_restart)
            self.pending_timer.daemon = True
            self.pending_timer.start()

    def _do_restart(self):
        print("\n[watch] Mudança detectada. Reiniciando agente...")
        self.runner.restart()

    def on_modified(self, event):
        if event.is_directory:
            return
        if self._should_ignore(event.src_path):
            return
        rel = os.path.relpath(event.src_path, PROJECT_DIR)
        print(f"[watch] Modificado: {rel}")
        self._schedule_restart()

    def on_created(self, event):
        self.on_modified(event)


def main():
    print("=" * 60)
    print("  Agent Moon — Modo desenvolvimento (auto-reload)")
    print("=" * 60)
    print(f"Projeto: {PROJECT_DIR}")
    print(f"Comando: {' '.join(AGENT_CMD)}")
    print(f"Monitorando: {', '.join(WATCH_DIRS)}")
    print(f"Extensões: {', '.join(WATCH_EXTENSIONS)}")
    print("Pressione Ctrl+C para encerrar.\n")

    runner = AgentRunner()
    runner.start()

    handler = ChangeHandler(runner)
    observer = Observer()
    for d in WATCH_DIRS:
        full = (PROJECT_DIR / d).resolve()
        if full.exists():
            observer.schedule(handler, str(full), recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watch] Encerrando...")
    finally:
        observer.stop()
        observer.join()
        runner.stop()
        print("[watch] Até logo!")


if __name__ == "__main__":
    main()