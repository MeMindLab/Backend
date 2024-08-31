from langchain.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import load_prompt


from app.prompt.examples import example


class PromptGenerator:
    @staticmethod
    def generate_summary_prompt():
        loaded_prompt = load_prompt("./app/prompt/summary.yaml")
        return loaded_prompt

    @staticmethod
    def generate_keyword_prompt():
        loaded_prompt = load_prompt("./app/prompt/keyword.yaml")
        return loaded_prompt

    @staticmethod
    def generate_emotion_prompt():
        loaded_prompt = load_prompt("./app/prompt/emotion.yaml")
        return loaded_prompt

    @staticmethod
    def generate_image_prompt(keywords: str):
        loaded_prompt = load_prompt("./app/prompt/image.yaml")
        prompt_with_keywords = loaded_prompt.template.format(keywords=keywords)

        return prompt_with_keywords

    @staticmethod
    def generate_chat_prompt() -> ChatPromptTemplate:
        # 사용자와 AI의 대화 예제를 기본 프롬프트로 생성합니다.
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{user}"),
                ("ai", "{ai}"),
            ],
        )

        examples = example
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples, example_prompt=example_prompt
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
                    Your first message to the user should be fixed to '안녕 난 구르미야 :) 오늘 하루 있었던 일이나 기분을 말해줘. 나 구르미가 모두 다 들어줄게!)'
                    """,
                ),
                (
                    "ai",
                    """
                    Hi, I'm Gurumi! 😊
                    Tell me about your day or how you're feeling.
                    I'm here to listen to what you have to say.
                    """,
                ),
                few_shot_prompt,
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{user}"),
            ]
        )

        return final_prompt
