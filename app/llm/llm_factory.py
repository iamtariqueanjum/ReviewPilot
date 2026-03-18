from langchain_openai import ChatOpenAI
# TODO fix later
# from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils.constants import ConfigConstants, LLMProvider


class LLMFactory(object):

    @staticmethod
    def get_llm(provider: str):

        provider = provider or ConfigConstants.DEFAULT_LLM_PROVIDER

        if provider == LLMProvider.OPENAI:
            return ChatOpenAI(model=ConfigConstants.OPENAI_BASE_MODEL)
        # elif provider == LLMProvider.GOOGLE:
            # return ChatGoogleGenerativeAI(model=ConfigConstants.GEMINI_BASE_MODEL, api_key=ConfigConstants.GEMINI_API_KEY)

        raise ValueError(f"Unsupported LLM provider: {provider}")
