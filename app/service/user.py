from fastapi import Depends, HTTPException, status
from uuid import UUID
from app.models.user import User
from app.repository.chat import ConversationRepository, MessageRepository
from app.repository.image import ImageRepository
from app.repository.lemon import LemonRepository
from app.repository.report import ReportRepository
from app.repository.user import UserRepository
from app.auth import hashpassword
from app.schemas.user import UserUpdate


hash_password = hashpassword.HashPassword()


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        report_repository: ReportRepository = Depends(ReportRepository),
        conversation_repository: ConversationRepository = Depends(
            ConversationRepository
        ),
        message_repository: MessageRepository = Depends(),
        image_repository: ImageRepository = Depends(),
        lemon_repository: LemonRepository = Depends(),
    ):
        self.user_repository = user_repository
        self.report_repository = report_repository
        self.conversation_repository = conversation_repository
        self.image_repository = image_repository
        self.message_repository = message_repository
        self.lemon_repository = lemon_repository

    async def get_user_list(self, skip: int, limit: int) -> list[User]:
        return await self.user_repository.read_all_user(skip, limit)

    async def get_user_by_id(self, user_id: UUID) -> User:
        user = await self.user_repository.find_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def get_user_by_nickname(self, nickname: str) -> User:
        user = await self.user_repository.find_user_by_nickname(nickname=nickname)
        return user

    async def find_user_by_email(self, email: str):
        user = await self.user_repository.find_user_by_email(email=email)
        return user

    async def create_new_user(self, user: User) -> User:
        new_user = User(
            email=user.email,
            password=hash_password.create_hash(user.password),
            nickname=user.nickname,
        )

        return await self.user_repository.save_user(user=new_user)

    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> User:
        user = await self.get_user_by_id(user_id=user_id)
        user.email = user_data.email
        user.nickname = user_data.nickname

        # Check if is_verified is provided
        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified

        # Check if mobile is provided
        if user_data.mobile is not None:
            user.mobile = user_data.mobile

        updated_user = await self.user_repository.save_user(user=user)

        return updated_user

    async def deactivate_user(
        self, user_id: UUID, password: str, delete_reasons: list[str]
    ):
        user = await self.get_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not hash_password.verify_hash(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Password not matching"
            )

        # 2. 유저와 관련된 대화 조회
        conversations = (
            await self.conversation_repository.find_conversations_by_user_id(user_id)
        )

        for conversation in conversations:
            # 3. 대화에 포함된 모든 메시지 조회 및 삭제
            messages = await self.message_repository.get_messages(
                conversation_id=conversation.id
            )
            for message in messages:
                # 4. 메시지와 관련된 이미지 삭제
                if message.image:
                    await self.image_repository.delete_image_by_message_id(message.id)
                await self.message_repository.delete_message(message.id)

            # 5. 대화 삭제
            await self.conversation_repository.delete_conversation(conversation.id)

            # 6. 유저와 관련된 모든 보고서 삭제
            report = await self.report_repository.get_report_by_conversation_id(
                conversation.id
            )
            if report is not None:
                await self.report_repository.delete_report(report.id)

        # 7. 유저와 관련된 레몬 카운트 삭제
        await self.lemon_repository.delete_lemon_by_user_id(user_id=user_id)

        # 8. 유저 삭제
        await self.user_repository.deactivate_user(
            user=user, delete_reasons=delete_reasons
        )

    async def reactivate_user(self, user_id: UUID):
        user = await self.user_repository.find_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await self.user_repository.reactivate_user(user=user)

    @staticmethod
    def validate_nickname_length(nickname: str):
        """사용자 이름과 닉네임의 길이를 검증합니다."""
        if len(nickname) < 3 or len(nickname) > 10:
            detail = {"message": "Nickname must be between 3 and 10 characters"}
            status_code = 400
            raise HTTPException(status_code=status_code, detail=detail)
