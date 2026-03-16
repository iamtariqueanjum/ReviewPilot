from app.utils.llm_constants import LLMProvider


from app.config.settings import get_settings

from langchain_openai import OpenAI
# TODO fix later
# from langchain_google_genai import ChatGoogleGenerativeAI


settings = get_settings()


class LLMFactory(object):

    @staticmethod
    def get_llm(provider: str):

        provider = provider or settings.DEFAULT_LLM_PROVIDER

        if provider == LLMProvider.OPENAI:
            return OpenAI(model=settings.OPENAI_BASE_MODEL, api_key=settings.OPENAI_API_KEY)
        # elif provider == LLMProvider.GOOGLE:
        #     return ChatGoogleGenerativeAI(model=settings.GEMINI_BASE_MODEL, api_key=settings.GEMINI_API_KEY)

        raise ValueError(f"Unsupported LLM provider: {provider}")
