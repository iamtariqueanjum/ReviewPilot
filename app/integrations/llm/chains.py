from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.core.utils.constants import ConfigConstants

def get_chat_runnable(llm):

    def get_session_history(session_id: str):
        return RedisChatMessageHistory(
            session_id=session_id,
            url=ConfigConstants.REDIS_BACKEND_URL,
            ttl=7*24*3600  # 7 days
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm

    runnable = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return runnable
