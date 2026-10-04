import os
from langchain_ollama import OllamaLLM


class LLMBackend:
    def __init__(self, backend_type="local"):
        self.backend_type = backend_type
        self.llm = self._initialize_backend()

    def _initialize_backend(self):
        if self.backend_type == "local":
            return OllamaLLM(model="qwen2.5:3b", base_url="http://localhost:11434")

        elif self.backend_type == "groq":
            try:
                from langchain_groq import ChatGroq
            except ImportError as exc:
                raise ImportError(
                    "O backend Groq requer o pacote 'langchain-groq'. "
                    "Instale com: pip install langchain-groq"
                ) from exc

            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="qwen/qwen3.8-27b",
                temperature=0.2,
                max_tokens=700
                
            )

        elif self.backend_type == "huggingface":
            try:
                from langchain_community.llms import HuggingFaceEndpoint
            except ImportError as exc:
                raise ImportError(
                    "O backend Hugging Face requer 'langchain-community' e 'huggingface-hub'."
                ) from exc

            return HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=os.getenv("HF_API_TOKEN"),
                task="text-generation",
                max_new_tokens=512
            )

        elif self.backend_type == "deepseek":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError as exc:
                raise ImportError(
                    "O backend DeepSeek requer o pacote 'langchain-openai'. "
                    "Instale com: pip install langchain-openai"
                ) from exc

            return ChatOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                temperature=0.2
            )

        else:
            raise ValueError("Backend não suportado")