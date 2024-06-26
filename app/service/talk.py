import os
import openai


from langchain_openai import ChatOpenAI
from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.prompts import ChatPromptTemplate
from app.prompt.examples import example


class MessageRespondent:
    def __init__(self, session):
        self.session = session
        self.chat_instance = self.setup_chat()

    def setup_chat(self):

        openai.api_key = os.environ.get("OPENAI_API_KEY")

        # ChatOpenAI 설정
        chat = ChatOpenAI(
            temperature=0.1,
            streaming=True,
            callbacks=[
                StreamingStdOutCallbackHandler(),
            ],
        )
        return chat

    def setup_prompt(self, example):
        example_prompt = ChatPromptTemplate.from_messages(
            [("human", "{user}"), ("ai", "{ai}")],
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=example, example_prompt=example_prompt
        )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You're a useful AI emotional counselor. 
                    Your name is 구르미.
                    You are my best friend, empathize with my feelings and ask questions.
                    You are informal and use a casual tone of voice.
                    """,
                ),
                few_shot_prompt,
                (
                    "ai",
                    """
                    Hi, I'm Gurumi! 😊
                    Tell me about your day or how you're feeling.
                    I'm here to listen to what you have to say.
                    """,
                ),
                ("human", "{user}"),
            ]
        )
        return final_prompt

    def answer_conversation(self, user_text) -> str:
        # ChatGPT를 사용하여 대화를 시작하고 응답을 반환합니다.

        try:
            prompt = self.setup_prompt(example)
            chat_chain = prompt | self.chat_instance

            response = chat_chain.invoke({"user": user_text})

            return response.content
        except Exception as e:
            # 오류 처리를 원하는 방식으로 추가합니다.
            print(f"Error in answering conversation: {e}")
