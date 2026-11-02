import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from ollama import ResponseError

from core.config import Settings
from core.errors import LlmUnavailableException
from rag.prompt import SYSTEM_PROMPT

_LLM_ERRORS = (ResponseError, ConnectionError, httpx.TimeoutException)


class Llm:
    def __init__(self, settings: Settings):
        self.client = ChatOllama(
            base_url=settings.ollama_url, model=settings.ollama_model
        )

    def generate(self, prompt) -> str:
        messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt)]
        try:
            response = self.client.invoke(messages)
            return response.content

        except _LLM_ERRORS as exc:
            raise LlmUnavailableException() from exc
