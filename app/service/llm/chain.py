from operator import itemgetter

from langchain.memory import (
    ConversationSummaryBufferMemory,
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    Runnable,
)
from langchain_core.output_parsers import StrOutputParser


class ConversationChain(Runnable):
    def __init__(
        self,
        llm,
        prompt,
        input_key: str = "user",
    ):
        self.prompt = prompt
        self.llm = llm

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=120,
            return_messages=True,
            memory_key="chat_history",
        )

        self.input_key = input_key
        self.chain = (
            RunnablePassthrough.assign(
                chat_history=RunnableLambda(self.memory.aload_memory_variables)
                | itemgetter(self.memory.memory_key)
            )
            | prompt
            | llm
            | StrOutputParser()
        )

    async def add_user_message(self, message):
        """Adds a user's message to memory."""
        await self.memory.asave_context(inputs={"human": message}, outputs={"ai": ""})

    async def add_memory(self, user_message: str, ai_message: str):
        """사용자와 AI 메시지를 모두 메모리에 추가합니다."""
        await self.memory.asave_context(
            inputs={"human": user_message}, outputs={"ai": ai_message}
        )

    async def invoke(self, query, configs=None, **kwargs):
        answer = await self.chain.ainvoke({self.input_key: query})
        await self.memory.asave_context(inputs={"human": query}, outputs={"ai": answer})
        return answer
