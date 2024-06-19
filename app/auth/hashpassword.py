from passlib.context import CryptContext


class HashPassword:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def create_hash(password: str):
        return HashPassword.pwd_context.hash(password)

    @staticmethod
    def verify_hash(plain_password: str, hashed_password: str):
        return HashPassword.pwd_context.verify(plain_password, hashed_password)
