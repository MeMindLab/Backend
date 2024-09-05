import random
import string

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from uuid import UUID

from app.models.user import User
from app.models.lemon import Lemon
from app.repository.chat import ConversationRepository, MessageRepository
from app.repository.image import ImageRepository
from app.repository.lemon import LemonRepository
from app.repository.report import ReportRepository
from app.repository.user import UserRepository

from app.core.config import get_config, ConfigTemplate

from app.auth import hashpassword
from app.schemas.user import UserUpdate, UserCreate
from app.schemas.lemon import LemonCreate
from app.service import LemonService

hash_password = hashpassword.HashPassword()


class ReferralService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        lemon_repository: LemonRepository = Depends(LemonRepository),
        config: ConfigTemplate = Depends(get_config),
    ):
        self.referral_code = self.generate_referral_code()
        self.user_repository = user_repository
        self.lemon_repository = lemon_repository
        self.config = config

    async def find_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        """추천인 코드를 통해 유저를 조회합니다."""
        user = await self.user_repository.find_user_by_referral_code(referral_code)
        if user is None:
            raise HTTPException(status_code=404, detail="Referrer not found")
        return user

    async def apply_referral_benefit(self, new_user: User, referrer: Optional[User]):
        """추천인 혜택을 적용하고 레몬을 초기화합니다."""
        initial_lemons = (
            self.config.REFERRAL_LEMON_BONUS
            if referrer
            else self.config.INITIAL_LEMON_COUNT
        )
        lemon_create = LemonCreate(lemon_count=initial_lemons)
        await self.lemon_repository.save_lemon(
            Lemon(user_id=new_user.id, **lemon_create.dict())
        )

    @staticmethod
    def set_referral_code(self, user: User, code: str):
        """추천인 코드를 설정하고 생성 날짜를 업데이트합니다."""
        user.referral_code = code
        user.referral_code_creation_date = datetime.now()  # 현재 시간으로 설정

    @staticmethod
    def generate_referral_code(length: int = 8) -> str:
        """랜덤한 추천인 코드를 생성합니다."""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def is_referral_code_valid(referral_code_expiry: Optional[datetime]) -> bool:
        """추천인 코드 유효성을 확인합니다."""
        if referral_code_expiry is None:
            return False  # 유효 기간이 설정되지 않은 경우 유효하지 않음
        return referral_code_expiry > datetime.now()  # 현재 시간이 유효 기간보다 작으면 True

    def get_referral_code(self) -> str:
        """유저의 추천인 코드를 반환합니다."""
        return self.referral_code


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
        config: ConfigTemplate = Depends(get_config),
        referral_service: ReferralService = Depends(ReferralService),
    ):
        self.user_repository = user_repository
        self.report_repository = report_repository
        self.conversation_repository = conversation_repository
        self.image_repository = image_repository
        self.message_repository = message_repository
        self.lemon_repository = lemon_repository
        self.config = config
        self.referral_service = referral_service

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

    async def create_new_user(self, user: UserCreate) -> User:
        new_user = User(
            email=user.email,
            password=hash_password.create_hash(user.password),
            nickname=user.nickname,
        )

        return await self.user_repository.save_user(user=new_user)

    async def signup_user(self, user: UserCreate) -> User:
        # 닉네임 길이 검증
        self.validate_nickname_length(user.nickname)

        # 데이터베이스에서 이메일과 닉네임 중복 검사
        db_user_by_email = await self.find_user_by_email(user.email)
        db_user_by_nickname = await self.get_user_by_nickname(user.nickname)

        if db_user_by_email and db_user_by_nickname:
            raise HTTPException(status_code=400, detail="Invalid nickname and email")
        elif db_user_by_email:
            raise HTTPException(status_code=400, detail="Invalid Email")
        elif db_user_by_nickname:
            raise HTTPException(status_code=400, detail="Invalid nickname")

        # 새 사용자 객체 생성
        new_user = User(
            email=user.email,
            password=hash_password.create_hash(user.password),
            nickname=user.nickname,
        )

        # 추천인 코드가 있을 경우 처리

        referrer = await self.referral_service.find_user_by_referral_code(
            user.referral_code,
        )

        # 사용자 저장
        saved_user = await self.user_repository.save_user(user=new_user)

        # 추천인 혜택 적용 및 레몬 초기화
        await self.referral_service.apply_referral_benefit(saved_user, referrer)

        return saved_user

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
