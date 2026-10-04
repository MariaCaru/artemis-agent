# 🏹 Artemis Agent

> Assistente pessoal de IA modular com backends locais e em nuvem, focado em **organização pessoal**, **segurança de dados**, **hacking ético** (varreduras autorizadas) e **análise de código**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Version-0.5.0-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

> ⚠️ **Aviso legal**
> As ferramentas de varredura de rede devem ser usadas **apenas em sistemas que você possui ou tem autorização explícita por escrito** para testar. O uso não autorizado é crime (Lei nº 12.737/2012 no Brasil). Este projeto é destinado a aprendizado, hardening dos próprios sistemas e laboratórios controlados.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [Ferramentas Disponíveis](#-ferramentas-disponíveis)
- [Comandos de Sessão](#-comandos-de-sessão)
- [Segurança](#-segurança)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Roadmap](#️-roadmap)
- [Solução de Problemas](#-solução-de-problemas)
- [Licença](#-licença)

---

## 🎯 Visão Geral

O **Artemis Agent** é um assistente pessoal que roda no seu computador com suporte a múltiplos backends de LLM:

- **Backends locais** (Ollama + Qwen 2.5) — privacidade total, sem custo, sem internet.
- **Backends em nuvem** (Groq, Hugging Face, DeepSeek) — respostas mais rápidas e modelos maiores.

Diferenciais:

- **Loop ReAct próprio** implementado em Python puro (sem dependência das abstrações de agentes do LangChain).
- **Roteamento inteligente** por palavras-chave: perguntas sensíveis vão para o backend local; demais vão para a nuvem.
- **Memória persistente** em SQLite, com redação automática de resultados sensíveis.
- **Duas interfaces**: CLI (terminal) e Web (Streamlit).
- **Salvaguardas fortes** para ferramentas de varredura (alvos autorizados + log de auditoria).
- **Ferramentas de código**: leitura de arquivos, árvore de projeto, busca e git (somente leitura).

---

## ✨ Funcionalidades

### 📁 Organização
- Salvar notas em arquivos de texto com timestamp.
- Listar arquivos e diretórios.
- Executar comandos seguros do sistema (whitelist).

### 🔐 Segurança de Dados
- Criptografar/descriptografar arquivos (Fernet/AES).
- Gerar senhas seguras com tamanho customizável.
- Avaliar força de senhas (via zxcvbn).
- Gerar hash de textos (SHA-256, SHA-512, etc.).

### 🛡️ Hacking Ético (varreduras autorizadas)
- Varredura de portas com **nmap** (detecção de serviço).
- Varredura de portas com Python puro (sem nmap).
- Obter cabeçalhos HTTP de um site.
- Ler certificado SSL/TLS de um host.
- Baixar `robots.txt` de um site.
- Testar se um host responde (ping).

### 💻 Análise de Código (somente leitura)
- Ler arquivos de código.
- Mostrar árvore de diretórios de um projeto.
- Buscar termos no código-fonte.
- Ver alterações não commitadas (`git diff`).
- Ver histórico de commits (`git log`).

### 🔒 Salvaguardas de Segurança
- **Lista de alvos autorizados** (`authorized_targets.txt`) — nada é escaneado fora dela.
- **Whitelist de flags do nmap** — evita injeção de comandos.
- **Log de auditoria** (`agent_audit.log`) — todas as ações registradas.
- **Redação de resultados sensíveis** — senhas, hashes e chaves nunca vão para a nuvem.
- **Acesso restrito ao código** — leitura limitada a `D:\projetos_dev`.

---

## 🏗️ Arquitetura

```
┌──────────────────────┐     ┌──────────────────────┐
│   Interface CLI      │     │  Interface Web       │
│   (main.py)          │     │  (app.py/Streamlit)  │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
           └────────────┬───────────────┘
                        ▼
           ┌────────────────────────┐
           │   PersonalAgent        │
           │   (agent/core.py)      │
           │   - Loop ReAct         │
           │   - Histórico          │
           │   - Síntese forçada    │
           └────────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────────┐
  │ Router   │   │ Memory   │   │  Tools       │
  │ (kw)     │   │ (SQLite) │   │  - tools.py  │
  └────┬─────┘   └──────────┘   │  - security  │
       │                        │  - pentest   │
       │                        │  - code      │
       ▼                        └──────────────┘
  ┌────────────────────────┐
  │  Backends de LLM       │
  │  - Ollama (local)      │
  │  - Groq / HF / DeepSeek│
  └────────────────────────┘
```

**Fluxo de uma pergunta:**

1. Usuário envia pergunta via CLI ou Streamlit.
2. `router.py` decide o backend (local vs. nuvem) baseado em palavras-chave.
3. `core.py` monta o prompt ReAct com as ferramentas disponíveis.
4. LLM responde com `Action: <ferramenta>` + `Action Input: <entrada>` **ou** `Final Answer: <resposta>`.
5. Se for Action, o agente executa a ferramenta, adiciona a `Observation` ao prompt e repete (até 6 ferramentas).
6. Se for Final Answer, retorna ao usuário.
7. Toda interação é salva no SQLite via `memory.py`.

---

## 💻 Requisitos

### Hardware

| Configuração | Especificação |
|--------------|---------------|
| **Mínimo** | CPU 4 núcleos, 8 GB RAM |
| **Recomendado** | GPU com 4+ GB VRAM (para modelos locais com CUDA) |
| **Testado em** | Intel i3-7100, 16 GB RAM, NVIDIA GTX 1050 Ti (4 GB) |

### Software

- **Windows 10/11** (testado), Linux ou macOS
- **Python 3.10+**
- **[Ollama](https://ollama.com/download)** — execução local de LLMs
- **[nmap](https://nmap.org/download)** — varredura de rede
- **Git** (opcional)

---

## 🚀 Instalação

### 1. Clonar o repositório

```powershell
git clone https://github.com/MariaCaru/artemis-agent.git
cd artemis-agent
```

### 2. Criar ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Se aparecer erro de política de execução no PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

Ou manualmente:

```powershell
pip install langchain-ollama langchain-groq langchain-openai langchain-community
pip install ollama chromadb python-dotenv cryptography zxcvbn huggingface-hub
pip install streamlit watchdog
```

### 4. Instalar Ollama e baixar um modelo

```powershell
ollama pull qwen2.5:3b
```

| Modelo | Tamanho | Uso |
|--------|---------|-----|
| `qwen2:1.5b` | ~1 GB | Rápido, menos preciso |
| `qwen2.5:3b` | ~2 GB | **Recomendado** para GPU 4 GB |
| `qwen2.5:7b` | ~4,7 GB | Mais confiável, com offload para RAM |

### 5. Instalar nmap

Baixe em [nmap.org/download](https://nmap.org/download). Durante a instalação:

- Marque **"Add Nmap to the system PATH"**.
- Aceite a instalação do **Npcap**.

Verifique:

```powershell
nmap --version
```

---

## ⚙️ Configuração

### Arquivo `.env`

Crie na raiz do projeto:

```
GROQ_API_KEY=sua_chave_groq
HF_API_TOKEN=seu_token_huggingface
DEEPSEEK_API_KEY=sua_chave_deepseek
```

Deixe em branco as que não for usar.

### Arquivo `authorized_targets.txt`

Lista de alvos permitidos para varredura (um por linha). Comentários começam com `#`.

```
# Alvos autorizados
localhost
127.0.0.1
# example.com
```

> ⚠️ **Nunca** adicione hosts que você não possui ou não tem autorização para testar.

---

## 🎮 Uso

### Interface CLI

```powershell
.\venv\Scripts\Activate.ps1
python main.py 2
```

O `2` seleciona o backend Groq. Use `1` para Ollama local.

Exemplo:

```
(venv) PS D:\projetos_dev\artemis_agent> python main.py 2
Backend pré-selecionado: groq
Roteamento ativo: sensíveis → local | demais → groq
Sessão: 20261004_101520 | total no histórico: 45

Agente iniciado. Digite 'help' para ver comandos, 'sair' para encerrar.

Você: Liste os arquivos da pasta
Agente: Os arquivos são: .env, agent, main.py, notes, venv, watch.py.

Você: Gere uma senha de 20 caracteres
Agente: Senha gerada (20 caracteres): K9K-Q_*h$9eKWjX9nUbg

Você: Faça um scan rápido no localhost
Agente: O scan revelou 2 portas abertas: 135/tcp (msrpc) e 445/tcp (microsoft-ds).
```

### Interface Web (Streamlit)

```powershell
streamlit run app.py
```

Abre automaticamente em `http://localhost:8501`.

A interface oferece:

- **Sidebar** com escolha de backend, toggle de roteamento e lista de ferramentas.
- **Chat interativo** com histórico visual.
- **Expanders** mostrando quais ferramentas foram usadas em cada resposta.
- **Botões**: Nova sessão · Limpar chat · Ver histórico.

### Modo Desenvolvimento (auto-reload)

```powershell
python watch.py 2
```

Reinicia o agente automaticamente ao salvar arquivos `.py`. Ideal durante o desenvolvimento.

### Atalhos PowerShell

Adicione ao seu `$PROFILE` (`notepad $PROFILE`):

```powershell
function artemis { 
    cd D:\projetos_dev\artemis_agent
    .\venv\Scripts\Activate.ps1
    python main.py 2
}

function artemis-dev { 
    cd D:\projetos_dev\artemis_agent
    .\venv\Scripts\Activate.ps1
    python watch.py 2
}

function artemis-web { 
    cd D:\projetos_dev\artemis_agent
    .\venv\Scripts\Activate.ps1
    streamlit run app.py
}
```

Agora basta digitar `artemis`, `artemis-dev` ou `artemis-web` de qualquer pasta.

---

## 🧰 Ferramentas Disponíveis

### 📁 Organização

| Ferramenta | Descrição | Exemplo |
|------------|-----------|---------|
| `save_note` | Salva nota em `notes/` | "Salve uma nota dizendo comprar leite" |
| `list_files` | Lista arquivos do diretório | "Liste os arquivos da pasta" |
| `run_safe_command` | Executa comando da whitelist | "Execute o comando date" |

### 🔐 Segurança de Dados

| Ferramenta | Descrição | Exemplo |
|------------|-----------|---------|
| `encrypt_file` | Criptografa arquivo (Fernet/AES) | "Criptografe notes/nota.txt" |
| `decrypt_file` | Descriptografa arquivo `.enc` | "Descriptografe notes/nota.txt.enc" |
| `check_password_strength` | Avalia força de senha (zxcvbn) | "Qual a força de 'senha123'?" |
| `hash_text` | Gera hash | "Gere o hash sha256 de 'olá'" |
| `generate_password` | Gera senha aleatória | "Gere uma senha de 24 caracteres" |

### 🛡️ Hacking Ético

| Ferramenta | Descrição | Exemplo |
|------------|-----------|---------|
| `nmap_scan` | Varredura com nmap | "Faça um scan rápido no localhost" |
| `port_scan_python` | Varredura TCP em Python | "Varra as portas 22,80,443 no localhost" |
| `http_headers` | Cabeçalhos HTTP | "Mostre os headers de https://example.com" |
| `ssl_cert_info` | Certificado SSL/TLS | "Veja o certificado SSL de example.com" |
| `check_robots_txt` | Lê `robots.txt` | "Veja o robots.txt de example.com" |
| `ping_host` | Testa host | "Pingue localhost" |

### 💻 Análise de Código

| Ferramenta | Descrição | Exemplo |
|------------|-----------|---------|
| `read_file` | Lê arquivo (máx. 30 KB) | "Leia agent/core.py" |
| `list_project_tree` | Árvore de diretórios | "Mostre a estrutura do projeto" |
| `search_in_code` | Busca termo no código | "Busque por SENSITIVE_KEYWORDS" |
| `git_diff` | Alterações não commitadas | "O que mudou desde o último commit?" |
| `git_log` | Últimos commits | "Mostre os últimos 5 commits" |

---

## 💬 Comandos de Sessão

Digite **dentro do agente** (CLI):

| Comando | Descrição |
|---------|-----------|
| `help` / `?` / `ajuda` | Lista todas as ferramentas |
| `historico` | Últimas 10 mensagens desta sessão |
| `buscar <termo>` | Busca no histórico completo |
| `limpar` | Apaga todo o histórico (com confirmação) |
| `sair` / `exit` / `quit` | Encerra o agente |

---

## 🔐 Segurança

### Salvaguardas implementadas

1. **Lista de alvos autorizados** — nenhuma varredura fora de `authorized_targets.txt`.
2. **Whitelist de flags do nmap** — somente `-sV`, `-sS`, `-F`, `-A`, `-T4`, `-O`, `-Pn`, `-p`.
3. **Log de auditoria** — toda ação registrada em `agent_audit.log`.
4. **Fallback de nmap** — busca em `C:\Program Files (x86)\Nmap` se PATH falhar.
5. **Redação de resultados sensíveis** — senhas/hashes/chaves nunca vão para a nuvem.
6. **Restrição de escrita** — ferramentas de código apenas **leem** arquivos.
7. **Restrição de leitura** — acesso limitado a `D:\projetos_dev`.

### Boas práticas

- **Nunca** adicione hosts à lista de autorizados sem permissão.
- Execute o agente em **VM** ao testar ferramentas de pentest.
- Mantenha dependências atualizadas.
- **Não** faça commit do `.env`.
- Revise o log periodicamente: `type agent_audit.log`.

### O que o agente **NÃO** faz (por design)

- ❌ Não altera configurações do sistema (serviços, firewall, registro).
- ❌ Não instala nem remove programas.
- ❌ Não executa comandos arbitrários (só whitelist).
- ❌ Não escreve ou modifica arquivos de código (apenas leitura).
- ❌ Não envia dados sensíveis para a nuvem sem consentimento.
- ❌ Não realiza ataques destrutivos.

---

## 📂 Estrutura do Projeto

```
artemis-agent/
├── .env                      # Chaves de API (não versionar)
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                   # Interface CLI
├── app.py                    # Interface Web (Streamlit)
├── watch.py                  # Auto-reload em desenvolvimento
├── authorized_targets.txt    # Alvos permitidos para varredura
├── history.db                # Banco SQLite (gerado)
├── agent_audit.log           # Log de auditoria (gerado)
│
├── agent/
│   ├── __init__.py
│   ├── backends.py           # Integração com Ollama, Groq, HF, DeepSeek
│   ├── core.py               # Classe PersonalAgent (loop ReAct)
│   ├── router.py             # Roteamento por palavras-chave
│   ├── memory.py             # Persistência SQLite
│   ├── tools.py              # Ferramentas de organização
│   ├── security_tools.py     # Ferramentas de segurança de dados
│   ├── pentest_tools.py      # Ferramentas de varredura
│   └── code_tools.py         # Ferramentas de leitura de código
│
├── notes/                    # Notas salvas pelo agente
├── keys/                     # Chaves de criptografia (geradas)
└── venv/                     # Ambiente virtual Python
```

### `.gitignore` recomendado

```
venv/
__pycache__/
*.pyc
.env
history.db
keys/
notes/
agent_audit.log
.vscode/
.idea/
```

---

## 🗺️ Roadmap

### ✅ Fase 0 — Preparação
- [x] Ambiente virtual Python
- [x] Dependências instaladas
- [x] Ollama + Qwen 2.5
- [x] nmap instalado

### ✅ Fase 1 — Agente Básico
- [x] Loop ReAct em Python puro
- [x] Backend local funcional
- [x] Ferramentas de organização
- [x] Memória de curto prazo

### ✅ Fase 2 — Segurança de Dados
- [x] Criptografia (Fernet/AES)
- [x] Geração e análise de senhas
- [x] Hash de textos

### ✅ Fase 3 — Varreduras de Segurança
- [x] nmap, port scan Python, ping
- [x] Bloqueio de alvos não autorizados
- [x] Log de auditoria
- [x] `http_headers`, `ssl_cert_info`, `check_robots_txt`

### ✅ Fase 5 — Refinamento
- [x] `watch.py` (auto-reload)
- [x] Roteamento por palavras-chave (local ↔ nuvem)
- [x] Comando `help` enxuto com cores
- [x] Memória persistente (SQLite)
- [x] Ferramentas de código (leitura + git)
- [x] Interface Web (Streamlit)

### ⏳ Fase 4 — Ferramentas Avançadas (planejado)
- [ ] Gerenciamento de serviços e firewall (com salvaguardas)
- [ ] Brute force controlado (hydra) em alvos autorizados
- [ ] Integração com sqlmap em URLs autorizadas
- [ ] Wordlists básicas

### ⏳ Fase 5.5 — Escrita de Código (planejado)
- [ ] `write_file` com backup `.bak`
- [ ] `patch_file` (substituição segura)
- [ ] Confirmação obrigatória do usuário
- [ ] Lista de arquivos protegidos

### ⏳ Fase 6 — Extras (planejado)
- [ ] Busca web (DuckDuckGo)
- [ ] Migração para WSL/Kali
- [ ] Testes unitários
- [ ] Backup automatizado

---

## 🩺 Solução de Problemas

### "Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente"

**Causa:** o serviço do Ollama não está rodando.

**Solução:**
1. Abra o menu Iniciar, procure "Ollama" e clique para abrir.
2. Confirme com `ollama list`.
3. Se persistir, rode em outro terminal: `ollama serve`.

### "nmap não reconhecido como nome de cmdlet"

**Causa:** o nmap não está no PATH do terminal atual.

**Solução:**
1. Descubra o caminho: `where.exe nmap` (em um terminal que funcione).
2. Adicione a pasta às variáveis de ambiente do usuário.
3. **Feche e reabra o terminal** (obrigatório).
4. O agente também possui fallback para caminhos comuns.

### "pull model manifest: file does not exist"

**Causa:** a tag do modelo não existe.

**Solução:** verifique as tags disponíveis em [ollama.com/library](https://ollama.com/library). Use `qwen2.5:3b`, `qwen2:1.5b` ou `qwen2.5:7b`.

### O modelo alucina (inventa ações, nomes de arquivos)

**Causa:** modelos pequenos (1.5B–3B) têm dificuldade em seguir formatos estritos.

**Soluções:**
1. Use um modelo maior: `qwen2.5:7b`.
2. Use o backend Groq com o modelo `qwen/qwen3.8-27b` para tarefas de raciocínio.
3. Ative `DEBUG = True` no `core.py` para ver as respostas cruas do LLM.

### Erro de CUDA ao rodar o modelo

**Causa:** driver NVIDIA desatualizado ou incompatível.

**Soluções:**
1. Atualize o driver em [nvidia.com/download](https://www.nvidia.com/Download/index.aspx).
2. Alternativa: forçar CPU com `$env:OLLAMA_ACCELERATOR="cpu"`.

### Groq retorna erro "model decommissioned"

**Causa:** o Groq descontinuou o modelo (isso acontece com frequência).

**Solução:** verifique os modelos disponíveis na sua conta:

```powershell
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); client = Groq(api_key=os.getenv('GROQ_API_KEY')); print([m.id for m in client.models.list().data])"
```

Atualize o modelo em `agent/backends.py` para um da lista.

### Groq retorna erro "rate_limit_exceeded" (OTPM)

**Causa:** limite de tokens de output por minuto no plano gratuito.

**Solução:** reduza `max_tokens` em `agent/backends.py` (ex.: `max_tokens=700`) ou aguarde 60 segundos entre perguntas.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

Uso pessoal e educacional. O autor **não se responsabiliza** pelo uso indevido das ferramentas de varredura ou qualquer ação ilegal realizada com base neste software.

**Use com responsabilidade. Respeite a lei. Respeite as pessoas.**

---

## 🙏 Agradecimentos

- [Ollama](https://ollama.com/) — execução local de LLMs.
- [Alibaba Qwen](https://qwenlm.github.io/) — modelos open-source de alta qualidade.
- [Groq](https://groq.com/) — inferência ultrarrápida na nuvem.
- [nmap](https://nmap.org/) — o clássico scanner de rede.
- [LangChain](https://www.langchain.com/) — inspiração para o loop ReAct.
- [zxcvbn](https://github.com/dropbox/zxcvbn) — avaliação realista de senhas.
- [Streamlit](https://streamlit.io/) — interface web em Python puro.

---

**Última atualização:** 4 de outubro de 2026  
**Versão:** 0.5.0 (Fase 5 concluída)