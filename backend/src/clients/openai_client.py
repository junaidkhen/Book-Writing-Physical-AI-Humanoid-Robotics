import openai
from ..config.settings import settings


class LazyOpenAIClient:
    def __init__(self):
        self._client = None

    def __getattr__(self, name):
        if self._client is None:
            self._client = openai.OpenAI(api_key=settings.openai_api_key)
        return getattr(self._client, name)


# Initialize the client lazily to avoid import-time errors
openai_client = LazyOpenAIClient()