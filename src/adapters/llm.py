from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from core.config import Settings
from rag.prompt import SYSTEM_PROMPT


class Llm:
    def __init__(self, settings: Settings):
        self.client = ChatOllama(
            base_url=settings.ollama_url, model=settings.ollama_model
        )
        pass

    def generate(self, prompt) -> str:
        messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt)]
        response = self.client.invoke(messages)
        return response.content
