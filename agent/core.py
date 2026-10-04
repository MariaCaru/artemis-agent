from .backends import LLMBackend
from . import tools as tool_module
from . import security_tools as sec_module
from . import pentest_tools as pt_module
from . import memory as mem_module
from . import router as router_module
from . import code_tools as code_module

DEBUG = True  # mude para False quando estiver tudo OK
SENSITIVE_TOOLS = {"generate_password", "hash_text", "encrypt_file", "decrypt_file"}


class PersonalAgent:
    def __init__(self, backend_type="local", enable_routing=False,
                 default_backend="groq", session_id=None):
        self.enable_routing = enable_routing
        self.default_backend = default_backend
        self.session_id = session_id or mem_module.new_session_id()

        # Inicializa o banco
        mem_module.init_db()

        # Carrega memórias curtas de sessões anteriores (opção A)
        self.past_context = mem_module.get_recent_from_other_sessions(
            self.session_id, limit=5
        )

        if enable_routing:
            self.backend_default = LLMBackend(default_backend)
            self.backend_local = LLMBackend("local")
            self.llm = self.backend_default.llm
        else:
            self.backend = LLMBackend(backend_type)
            self.llm = self.backend.llm

        self.tools = {
            "save_note": tool_module.save_note,
            "list_files": tool_module.list_files,
            "run_safe_command": tool_module.run_safe_command,
            "encrypt_file": sec_module.encrypt_file,
            "decrypt_file": sec_module.decrypt_file,
            "check_password_strength": sec_module.check_password_strength,
            "hash_text": sec_module.hash_text,
            "generate_password": sec_module.generate_password,
            "nmap_scan": pt_module.nmap_scan,
            "http_headers": pt_module.http_headers,
            "ssl_cert_info": pt_module.ssl_cert_info,
            "check_robots_txt": pt_module.check_robots_txt,
            "ping_host": pt_module.ping_host,
            "port_scan_python": pt_module.port_scan_python,
            "read_file": code_module.read_file,
            "list_project_tree": code_module.list_project_tree,
            "search_in_code": code_module.search_in_code,
            "git_diff": code_module.git_diff,
            "git_log": code_module.git_log,
        }
        self.history = []
        self.last_turn_metadata = {"backend": None, "tools": []}

    # --------------------------------------------------------------
    # Prompt
    # --------------------------------------------------------------
    def _format_past_context(self) -> str:
        if not self.past_context:
            return ""
        lines = ["\n[MEMÓRIAS DE SESSÕES ANTERIORES]"]
        for row in self.past_context:
            role = "User" if row["role"] == "user" else "Assistant"
            content = row["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"  {role}: {content}")
        lines.append("[/MEMÓRIAS]")
        return "\n".join(lines) + "\n"

    def _build_prompt(self, user_input, tool_history=None):
        """
        tool_history: lista de dicts com {'action', 'input', 'observation'}.
        Se fornecida, é renderizada no formato ReAct (Action → Observation inline).
        """
        tool_desc = "\n".join([
            f"- {name}: {func.__doc__.strip()}" for name, func in self.tools.items()
        ])
        history_str = ""
        for h in self.history[-2:]:
            history_str += f"User: {h['user']}\nAssistant: {h['assistant']}\n"

        past = self._format_past_context()

        # Renderiza o histórico ReAct desta tarefa
        react_history = ""
        if tool_history:
            react_history = "\n\nCONVERSA ATÉ AGORA (formato ReAct):\n"
            react_history += f"User: {user_input}\n"
            for step in tool_history:
                react_history += (
                    f"Assistant: Action: {step['action']}\n"
                    f"Action Input: {step['input']}\n"
                )
                obs = step["observation"]
                if len(obs) > 3000:
                    obs = obs[:3000] + "\n[... truncado ...]"
                react_history += f"Observation: {obs}\n"
            react_history += "Assistant:\n"

        prompt = f"""Você é um assistente pessoal que segue instruções rigorosamente.

Ferramentas disponíveis:
{tool_desc}

COMO RESPONDER:
- Se precisar de uma ferramenta, responda EXATAMENTE com 2 linhas:
Action: <nome_da_ferramenta>
Action Input: <entrada>
- Se já tem a informação, responda EXATAMENTE com 1 linha:
Final Answer: <sua resposta>

REGRAS CRÍTICAS:
1. NUNCA escreva "User:", "Assistant:" ou "(após Observation...)" na resposta.
2. NUNCA chame a MESMA ferramenta com a MESMA entrada duas vezes na mesma tarefa.
   Se já recebeu uma Observation dessa ferramenta, use-a e responda com Final Answer.
3. NUNCA invente dados. Use APENAS o que aparece nas observações.
4. Reproduza na Final Answer APENAS os valores que aparecem na Observation.
   Se houver apenas um valor (ex.: uma senha), cite apenas esse valor, sem duplicar.
5. NUNCA use frases genéricas como "informações típicas" ou "entre outros".
6. Você tem MEMÓRIAS de sessões anteriores ao final. Use-as apenas se forem relevantes.

REGRAS DE SEGURANÇA DE DADOS:
- "criptografar" → encrypt_file
- "descriptografar" → decrypt_file
- "gerar senha" sem número → use 16 (entrada: "16")
- "gerar senha" com número → use generate_password (entrada: apenas número)
- "força da senha" → check_password_strength
- "hash" → hash_text (sha256 se não especificado)

REGRAS DE CODIFICAÇÃO E LEITURA DE CÓDIGO:
- Para ver a estrutura de pastas → list_project_tree | "<caminho>"
- Para ler um arquivo → read_file | "<caminho_do_arquivo>"
- Para buscar termo no código → search_in_code | "<termo> [caminho] [extensão]"
- Para ver alterações não commitadas → git_diff | "<caminho_do_repo>"
- Para ver últimos commits → git_log | "<caminho_do_repo> [n]"
- Você só pode LER. NUNCA diga que escreveu, editou ou apagou um arquivo.
- NUNCA invente conteúdo de arquivos. Leia com read_file antes de opinar.
- Ao sugerir código, use blocos com a linguagem marcada (```python ... ```).
- Ao comparar arquiteturas, liste prós e contras de cada alternativa.

REGRAS DE PENTEST:
- Alvo precisa estar em authorized_targets.txt.
- Scan nmap → nmap_scan | "<alvo> [opções]"
- Scan portas Python → port_scan_python | "<host> [portas]"
- Cabeçalhos HTTP → http_headers | "<url>"
- Certificado SSL → ssl_cert_info | "<host> [porta]"
- robots.txt → check_robots_txt | "<url>"
- Ping → ping_host | "<host>"

EXEMPLO — listar arquivos:
User: Liste os arquivos da pasta
Assistant: Action: list_files
Action Input: .
Observation: .env, main.py, notes, venv
Assistant: Final Answer: Os arquivos são: .env, main.py, notes e venv.

EXEMPLO — analisar projeto em várias etapas:
User: Analise a arquitetura do projeto
Assistant: Action: list_project_tree
Action Input: D:\\projetos_dev\\agent_moon
Observation: agent/, main.py, watch.py, README.md
Assistant: Action: read_file
Action Input: D:\\projetos_dev\\agent_moon\\agent\\core.py
Observation: from .backends import LLMBackend...
Assistant: Final Answer: O projeto segue uma arquitetura modular em camadas...

EXEMPLO — cabeçalhos HTTP:
User: Mostre os cabeçalhos HTTP de https://example.com
Assistant: Action: http_headers
Action Input: https://example.com
Observation: Server: cloudflare, Content-Type: text/html, cf-cache-status: HIT
Assistant: Final Answer: Os cabeçalhos retornados foram: Server: cloudflare, Content-Type: text/html e cf-cache-status: HIT.
{past}
Histórico recente:
{history_str}
User: {user_input}{react_history}
Assistant:"""
        return prompt

    # --------------------------------------------------------------
    # Loop principal
    # --------------------------------------------------------------
    def ask(self, question):
        # Decide backend para esta pergunta
        if self.enable_routing:
            chosen = router_module.route(question, default_backend=self.default_backend)
            if chosen == "local" and not router_module.is_ollama_alive():
                if DEBUG:
                    print("[router] Ollama offline. Caindo para backend padrão.")
                chosen = self.default_backend
            llm = self.backend_local.llm if chosen == "local" else self.backend_default.llm
            if DEBUG:
                print(f"\n[router] Backend escolhido: {chosen}")
        else:
            chosen = self.backend_type
            llm = self.llm

        # Salva a pergunta
        mem_module.save_message(self.session_id, "user", question, backend=chosen)

        observations = []
        tools_used = []
        tool_history = []
        last_tool = None
        last_action = None
        MAX_TOOL_CALLS = 6
        prompt = self._build_prompt(question)

        def _save_assistant(text):
            """Salva a resposta do assistente, redigindo resultados sensíveis."""
            if last_tool in SENSITIVE_TOOLS:
                content = f"[REDIGIDO — resultado de {last_tool} não persistido]"
            else:
                content = text
            mem_module.save_message(self.session_id, "assistant", content, backend=chosen)

        for iteration in range(6):
            response = llm.invoke(prompt)

            if hasattr(response, "content"):
                response = response.content
            response = response or ""

            if DEBUG:
                print(f"\n--- [DEBUG iter {iteration+1}] ---")
                print(repr(response))
                print("--- fim ---\n")

            # Sanitiza vazamentos
            for leaked in ["User:", "Assistant:", "(após", "(Após", "Exemplo"]:
                if leaked in response:
                    response = response.split(leaked)[0].strip()
                    break

            # Caso 1: Final Answer
            for marker in ["Final Answer:", "Resposta Final:"]:
                if marker in response:
                    final_answer = response.split(marker, 1)[1].strip()
                    # dedup "X e X"
                    parts = final_answer.split(" e ")
                    if len(parts) == 2 and parts[0].strip() == parts[1].strip():
                        final_answer = parts[0].strip()
                    if not final_answer and observations:
                        final_answer = observations[-1][:800]
                    self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
                    _save_assistant(final_answer)
                    self.history.append({"user": question, "assistant": final_answer})
                    return final_answer

            # Caso 2: Action
            if "Action:" in response and "Action Input:" in response:
                try:
                    action_line = response.split("Action:", 1)[1].split("\n", 1)[0].strip()
                    input_line = response.split("Action Input:", 1)[1].split("\n", 1)[0].strip()
                except Exception:
                    return "Não consegui interpretar a resposta do modelo."

                if DEBUG:
                    print(f"[DEBUG] Ferramenta: {action_line} | Entrada: {input_line}")

                # Proteção: já usou essa ferramenta com o mesmo input?
                already_used = any(
                    t["name"] == action_line and t["input"] == input_line
                    for t in tools_used
                )
                if already_used:
                    if DEBUG:
                        print("[DEBUG] Ferramenta repetida. Forçando Final Answer.")
                    if observations:
                        final_answer = observations[-1][:1000]
                    else:
                        final_answer = "Ferramenta repetida sem progresso."
                    self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
                    _save_assistant(final_answer)
                    self.history.append({"user": question, "assistant": final_answer})
                    return final_answer

                # Proteção: limite de ferramentas
                                # Proteção: limite de ferramentas
                if len(observations) >= MAX_TOOL_CALLS:
                    if DEBUG:
                        print(f"[DEBUG] Limite de {MAX_TOOL_CALLS} ferramentas atingido. "
                              "Forçando síntese final.")
                    synthesis_prompt = prompt + (
                        "\n\nLIMITE DE FERRAMENTAS ATINGIDO. Você NÃO pode chamar mais ferramentas.\n"
                        "Responda AGORA com 'Final Answer:' sintetizando TODAS as observações acima.\n"
                        "Assistant: Final Answer:"
                    )
                    try:
                        forced = llm.invoke(synthesis_prompt)
                        if hasattr(forced, "content"):
                            forced = forced.content
                        forced = (forced or "").strip()
                        # Remove eventual prefixo duplicado
                        if forced.startswith("Final Answer:"):
                            forced = forced.split("Final Answer:", 1)[1].strip()
                        if forced:
                            final_answer = forced
                        else:
                            final_answer = "Análise:\n\n" + "\n\n".join(
                                f"**Observação {i+1}:** {o[:500]}"
                                for i, o in enumerate(observations)
                            )
                    except Exception as e:
                        if DEBUG:
                            print(f"[DEBUG] Erro na síntese forçada: {e}")
                        final_answer = "Análise parcial:\n\n" + "\n\n".join(
                            f"**Observação {i+1}:** {o[:500]}"
                            for i, o in enumerate(observations)
                        )
                    self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
                    _save_assistant(final_answer)
                    self.history.append({"user": question, "assistant": final_answer})
                    return final_answer

                last_action = (action_line, input_line)

                # Executa a ferramenta
                if action_line in self.tools:
                    last_tool = action_line
                    try:
                        observation = self.tools[action_line](input_line)
                        if DEBUG:
                            print(f"[DEBUG] Observation: {observation[:300]}")
                    except Exception as e:
                        observation = f"Erro ao executar ferramenta: {e}"
                        if DEBUG:
                            print(f"[DEBUG] Erro na ferramenta: {e}")
                else:
                    observation = f"Ferramenta '{action_line}' não existe."

                observations.append(observation)
                tools_used.append({
                    "name": action_line,
                    "input": input_line,
                    "observation": observation,
                })
                tool_history.append({
                    "action": action_line,
                    "input": input_line,
                    "observation": observation,
                })
                prompt = self._build_prompt(question, tool_history=tool_history)
                continue

            # Caso 3: resposta vazia
            if not response.strip():
                if observations:
                    final_answer = observations[-1][:800]
                    self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
                    _save_assistant(final_answer)
                    self.history.append({"user": question, "assistant": final_answer})
                    return final_answer
                return "O modelo retornou resposta vazia."

            # Caso 4: texto solto
            final_answer = response.strip()
            if observations and len(final_answer) < 30:
                final_answer = observations[-1][:800]
            self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
            _save_assistant(final_answer)
            self.history.append({"user": question, "assistant": final_answer})
            return final_answer

        # Loop esgotado
        if observations:
            final_answer = observations[-1][:1000]
            self.last_turn_metadata = {"backend": chosen, "tools": list(tools_used)}
            _save_assistant(final_answer)
            return final_answer
        return "Não consegui completar a tarefa no número máximo de passos."