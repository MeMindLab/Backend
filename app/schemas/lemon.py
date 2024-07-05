from pydantic import BaseModel


class LemonBase(BaseModel):
    lemon_count: int

    class Config:
        orm_mode = True


class LemonCreate(LemonBase):
    pass


class LemonUpdate(LemonBase):
    pass


class LemonRead(LemonBase):
    id: int


class LemonCreateResponse(LemonBase):
    user_id: int
