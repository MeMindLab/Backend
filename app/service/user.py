import hashlib

from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from uuid import UUID, uuid4

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


hash_password = hashpassword.HashPassword()


class ReferralService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        lemon_repository: LemonRepository = Depends(LemonRepository),
        config: ConfigTemplate = Depends(get_config),
    ):
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
    def generate_referral_code() -> str:
        """추천인 코드를 생성합니다."""

        # 1. UUID 문자열 생성
        uuid_str = str(uuid4())

        # 2. UUID 문자열을 UTF-8로 인코딩하여 바이트 배열로 변환
        uuid_bytes = uuid_str.encode("utf-8")

        # 3. 해시 함수를 사용하여 바이트 배열을 해시
        hashed_bytes = hashlib.sha256(uuid_bytes).digest()

        # 4. 해시된 바이트를 16진수 문자열로 저장
        referral_code = "".join(f"{byte:02x}" for byte in hashed_bytes[4:8])
        return referral_code


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

    async def create_new_user(self, user: UserCreate, referral_code: str) -> User:
        new_user = User(
            email=user.email,
            password=hash_password.create_hash(user.password),
            nickname=user.nickname,
            referral_code=referral_code,
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

        referral_code = self.referral_service.generate_referral_code()
        # 새 사용자 객체 생성
        new_user = await self.create_new_user(user, referral_code)

        # 추천인 코드가 있을 경우 처리
        referrer = None
        if user.referral_code is not None:
            # 추천인 코드로 추천인을 조회합니다.
            referrer = await self.referral_service.find_user_by_referral_code(
                user.referral_code
            )

            # 추천인 ID를 새로운 사용자에 설정합니다.
            new_user.referrer_id = referrer.id

        # 추천인 혜택 적용 및 레몬 초기화
        await self.referral_service.apply_referral_benefit(new_user, referrer)

        return new_user

    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> User:
        user = await self.get_user_by_id(user_id=user_id)

        # 이메일 중복 검사 및 업데이트
        if user_data.email and user_data.email != user.email:
            email_in_use = await self.find_user_by_email(user_data.email)
            if email_in_use:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 사용중 인 이메일 입니다.",
                )
            user.email = user_data.email

        if user_data.nickname != user.nickname:
            self.validate_nickname_length(user_data.nickname)
            nickname_in_use = await self.get_user_by_nickname(user_data.nickname)
            if nickname_in_use:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 사용중 인 닉네임 입니다.",
                )
            user.nickname = user_data.nickname

        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified

        if user_data.mobile is not None:
            user.mobile = user_data.mobile

        updated_user = await self.user_repository.save_user(user=user)

        return updated_user

    async def check_email_availability(self, email: str) -> bool:
        existing_user = await self.user_repository.find_user_by_email(email)

        if existing_user:
            raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
        return not existing_user

    async def check_nickname_availability(self, nickname: str) -> bool:
        existing_user = await self.user_repository.find_user_by_nickname(nickname)

        if existing_user:
            raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")
        return not existing_user

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
