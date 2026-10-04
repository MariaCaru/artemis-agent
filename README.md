🌙 Agent Moon
Agente pessoal de IA com suporte a múltiplos backends (local e nuvem), focado em organização pessoal, segurança de dados e hacking ético (varreduras autorizadas).

Aviso legal: as ferramentas de varredura de rede devem ser usadas apenas em sistemas que você possui ou tem autorização explícita por escrito para testar. O uso não autorizado é crime (Lei nº 12.737/2012 no Brasil). Este projeto é destinado a aprendizado, hardening dos próprios sistemas e laboratórios controlados.

📋 Índice
Visão Geral

Funcionalidades

Arquitetura

Requisitos

Instalação

Configuração

Uso

Ferramentas Disponíveis

Segurança

Estrutura do Projeto

Roadmap

Solução de Problemas

Licença

🎯 Visão Geral
O Agent Moon é um assistente pessoal que roda no seu computador e pode ser configurado para usar:

Backends locais (Ollama + Qwen 2.5) — privacidade total, sem custo, sem internet.

Backends em nuvem (Groq, Hugging Face, DeepSeek) — respostas mais rápidas e modelos maiores.

O agente usa um loop ReAct (Reasoning + Acting) implementado em Python puro, sem depender das abstrações de agentes do LangChain. Isso torna o sistema mais robusto a mudanças de versão e mais fácil de entender.

✨ Funcionalidades
📁 Organização
Salvar notas em arquivos de texto.

Listar arquivos e diretórios.

Executar comandos seguros do sistema (whitelist).

🔐 Segurança de Dados
Criptografar/descriptografar arquivos (Fernet/AES).

Gerar senhas seguras com tamanho customizável.

Avaliar força de senhas (via zxcvbn).

Gerar hash de textos (SHA-256, SHA-512, etc.).

🛡️ Hacking Ético (varreduras autorizadas)
Varredura de portas com nmap (detecção de serviço).

Varredura de portas com Python puro (sem nmap).

Obter cabeçalhos HTTP de um site.

Ler certificado SSL/TLS de um host.

Baixar robots.txt de um site.

Testar se um host responde (ping).

🔒 Salvaguardas de Segurança
Lista de alvos autorizados (authorized_targets.txt) — nada é escaneado fora dela.

Whitelist de flags do nmap — evita injeção de comandos.

Log de auditoria (agent_audit.log) — todas as ações registradas.

Confirmação implícita — o agente só age em alvos autorizados.

🏗️ Arquitetura
+-------------------+
|   Interface CLI   |
+---------+---------+
          |
          v
+-------------------+      +---------------------------+
|  PersonalAgent    |<---->|  Backends de LLM          |
|  - Loop ReAct     |      |  - Ollama (local)         |
|  - Ferramentas    |      |  - Groq / HF / DeepSeek   |
|  - Histórico      |      +---------------------------+
+---------+---------+
          |
          v
+-------------------+
|  Ferramentas      |
|  - tools.py       |  (organização)
|  - security_tools |  (criptografia, senhas)
|  - pentest_tools  |  (varreduras com salvaguardas)
+-------------------+

O agente envia um prompt ao LLM contendo:

Descrição das ferramentas disponíveis.

Regras de comportamento (formato ReAct, segurança, etc.).

Histórico recente (últimas 3 interações).

A pergunta do usuário.

O LLM responde com Action: + Action Input: (para chamar uma ferramenta) ou Final Answer: (resposta final). O agente executa a ferramenta, adiciona a Observation ao prompt e repete até o LLM dar a resposta final ou atingir 5 iterações.

💻 Requisitos
Hardware
Mínimo: CPU com 4 núcleos, 8 GB RAM.

Recomendado: GPU com 4+ GB VRAM (para rodar modelos locais com aceleração CUDA).

Testado em: Intel i3-7100, 16 GB RAM, NVIDIA GTX 1050 Ti (4 GB).

Software
Windows 10/11 (testado), Linux ou macOS.

Python 3.10+

Ollama — baixar aqui

nmap — baixar aqui (para varreduras de rede)

Git (opcional)

🚀 Instalação
1. Clonar ou criar o projeto
mkdir D:\projetos_dev\agent_moon
cd D:\projetos_dev\agent_moon

2. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

    Se aparecer erro de política de execução no PowerShell:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

3. Instalar dependências Python
pip install langchain langchain-community langchain-core langchain-ollama langchain-groq langchain-openai
pip install ollama chromadb python-dotenv cryptography zxcvbn huggingface-hub

4. Instalar Ollama e baixar um modelo
Após instalar o Ollama, baixe o modelo recomendado:
ollama pull qwen2.5:3b
    Alternativas mais leves: qwen2:1.5b (mais rápido, menos preciso).
    Alternativa mais robusta: qwen2.5:7b (mais lento em GPU 4 GB, mas muito mais confiável).

5. Instalar nmap
Baixe em nmap.org/download. Durante a instalação:
Marque "Add Nmap to the system PATH".
Aceite a instalação do Npcap.

Verifique:
nmap --version

⚙️ Configuração
Arquivo .env
Crie na raiz do projeto:
GROQ_API_KEY=sua_chave_groq
HF_API_TOKEN=seu_token_huggingface
DEEPSEEK_API_KEY=sua_chave_deepseek

Arquivo authorized_targets.txt
Lista de alvos permitidos para varredura (um por linha). Comentários começam com #
# Alvos autorizados
localhost
127.0.0.1
# example.com
    Nunca adicione hosts que você não possui ou não tem autorização para testar.

🎮 Uso
Ative o ambiente virtual e rode:
python main.py

Escolha o backend:
Agente Pessoal - escolha o backend:
1 - Local (Ollama)
2 - Groq
3 - Hugging Face
4 - DeepSeek
Opção (1-4):

Depois é só conversar:
Você: Liste os arquivos da pasta
Agente: Os arquivos na pasta atual são: .env, main.py, notes, venv.

Você: Gere uma senha de 20 caracteres
Agente: Senha gerada (20 caracteres): K9K-Q_*h$9eKWjX9nUbg

Você: Faça um scan rápido no localhost
Agente: Nmap foi executado no localhost e revelou que o host está ativo...

Para sair, digite sair, exit ou quit.

🧰 Ferramentas Disponíveis
Organização
Ferramenta	Descrição	Exemplo de uso
save_note	Salva uma nota em notes/ com timestamp	"Salve uma nota dizendo comprar leite"
list_files	Lista arquivos do diretório	"Liste os arquivos da pasta"
run_safe_command	Executa comando da whitelist	"Execute o comando date"
Segurança de Dados
Ferramenta	Descrição	Exemplo de uso
encrypt_file	Criptografa arquivo (Fernet/AES)	"Criptografe notes/nota.txt"
decrypt_file	Descriptografa arquivo .enc	"Descriptografe notes/nota.txt.enc"
check_password_strength	Avalia força de senha (zxcvbn)	"Qual a força da senha 'senha123'?"
hash_text	Gera hash do texto	"Gere o hash sha256 de 'olá'"
generate_password	Gera senha aleatória	"Gere uma senha de 24 caracteres"
Hacking Ético
Ferramenta	Descrição	Exemplo de uso
nmap_scan	Varredura com nmap	"Faça um scan rápido no localhost"
port_scan_python	Varredura de portas em Python	"Varra as portas 22,80,443 no localhost"
http_headers	Cabeçalhos HTTP	"Mostre os headers de https://example.com"
ssl_cert_info	Certificado SSL/TLS	"Veja o certificado SSL de example.com"
check_robots_txt	Lê robots.txt	"Veja o robots.txt de https://example.com"
ping_host	Verifica se host responde	"Pingue localhost"
🔐 Segurança
Salvaguardas implementadas
Lista de alvos autorizados
Nenhuma varredura é executada em alvos fora de authorized_targets.txt.

Whitelist de flags do nmap
Somente flags pré-aprovadas (-sV, -sS, -F, -A, -T4, -O, -Pn, -p) são aceitas. Qualquer outra é bloqueada.

Log de auditoria
Toda ação de varredura (inclusive as bloqueadas) é registrada em agent_audit.log com timestamp e resultado.

Fallback de localização do nmap
Se o PATH falhar, o agente procura o nmap em C:\Program Files (x86)\Nmap e C:\Program Files\Nmap.

Parsing defensivo
O parser do loop ReAct aceita apenas os formatos Action: / Action Input: e Final Answer:.

Boas práticas
Nunca adicione hosts à lista de autorizados sem ter certeza de que você tem permissão.

Execute o agente em uma VM se quiser testar ferramentas de pentest sem risco ao sistema principal.

Mantenha as dependências atualizadas: pip install --upgrade ....

Proteja o .env: não faça commit dele. Adicione ao .gitignore.

Revise o log periodicamente: type agent_audit.log.

O que o agente NÃO faz (por design)
❌ Não altera configurações do sistema (serviços, firewall, registro).

❌ Não instala nem remove programas.

❌ Não executa comandos arbitrários (só whitelist).

❌ Não envia dados sensíveis para nuvem sem escolha explícita do usuário.

❌ Não realiza ataques destrutivos.

📂 Estrutura do Projeto
agent_moon/
├── .env                      # Chaves de API (não versionar)
├── .gitignore
├── README.md
├── main.py                   # Interface CLI
├── authorized_targets.txt    # Alvos permitidos para varredura
├── agent_audit.log           # Log de auditoria (gerado automaticamente)
├── requirements.txt
│
├── agent/
│   ├── __init__.py           # Vazio (apenas marca o pacote)
│   ├── backends.py           # Integração com Ollama, Groq, HF, DeepSeek
│   ├── core.py               # Classe PersonalAgent (loop ReAct)
│   ├── tools.py              # Ferramentas de organização
│   ├── security_tools.py     # Ferramentas de segurança de dados
│   └── pentest_tools.py      # Ferramentas de varredura
│
├── notes/                    # Notas salvas pelo agente
├── keys/                     # Chaves de criptografia (geradas)
└── venv/                     # Ambiente virtual Python

🗺️ Roadmap
✅ Fase 0 — Preparação
☑ Ambiente virtual Python
☑ Dependências instaladas
☑ Ollama + Qwen 2.5
☑ nmap instalado
✅ Fase 1 — Agente Básico
☑ Loop ReAct em Python puro
☑ Backend local funcional
☑ Ferramentas de organização
☑ Memória de curto prazo
✅ Fase 2 — Segurança de Dados
☑ Criptografia (Fernet/AES)
☑ Geração e análise de senhas
☑ Hash de textos
🟡 Fase 3 — Varreduras de Segurança
☑ nmap, port scan Python, ping
☑ Bloqueio de alvos não autorizados
☑ Log de auditoria
□ Testar http_headers, ssl_cert_info, check_robots_txt
⏳ Fase 4 — Ferramentas Avançadas (planejado)
□ Gerenciamento de serviços e firewall (com salvaguardas fortes)
□ Brute force controlado (hydra) em alvos autorizados
□ Integração com sqlmap em URLs autorizadas
□ Wordlists básicas
⏳ Fase 5 — Refinamento (planejado)
□ Roteamento automático entre backends (local vs nuvem)
□ Interface web (Streamlit ou Gradio)
□ Memória persistente (Chroma ou SQLite)
□ Multiagentes com CrewAI (organizador, pesquisador, segurança)
⏳ Fase 6 — Hardening Final
□ Revisão de código
□ Backups automatizados
□ Documentação expandida
□ Testes unitários
🩺 Solução de Problemas
"Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente"
Causa: o serviço do Ollama não está rodando.

Solução:
Abra o menu Iniciar, procure "Ollama" e clique para abrir.
Confirme com ollama list.
Se persistir, rode em outro terminal: ollama serve.
"nmap não reconhecido como nome de cmdlet"
Causa: o nmap não está no PATH do terminal atual.

Solução:
Descubra o caminho: where.exe nmap (em um terminal que funcione).
Adicione a pasta às variáveis de ambiente do usuário.
Feche e reabra o terminal (obrigatório).
O agente também possui fallback para caminhos comuns.

"pull model manifest: file does not exist"
Causa: a tag do modelo não existe.

Solução: verifique as tags disponíveis em ollama.com/library. Use qwen2.5:3b, qwen2:1.5b ou qwen2.5:7b.

O modelo alucina (inventa ações, nomes de arquivos)
Causa: modelos pequenos (1.5B–3B) têm dificuldade em seguir formatos estritos.

Soluções:
Use um modelo maior: qwen2.5:7b.
Use o backend Groq (Llama 3 8B) para tarefas de raciocínio.
Ative o DEBUG = True no core.py para ver as respostas cruas do LLM.
Erro de CUDA ao rodar o modelo
Causa: driver NVIDIA desatualizado ou incompatível.

Soluções:
Atualize o driver em nvidia.com/download.
Alternativa: forçar CPU com $env:OLLAMA_ACCELERATOR="cpu".

📄 Licença
Este projeto é de uso pessoal e educacional. O autor não se responsabiliza pelo uso indevido das ferramentas de varredura ou qualquer ação ilegal realizada com base neste software.

Use com responsabilidade. Respeite a lei. Respeite as pessoas.

🙏 Agradecimentos
Ollama — execução local de LLMs.
Alibaba Qwen — modelos open-source de alta qualidade.
nmap — o clássico scanner de rede.
LangChain — inspiração para o loop ReAct.
zxcvbn — avaliação realista de senhas.

Última atualização: 17 de setembro de 2026
Versão: 0.3.0 (Fase 3 em andamento)