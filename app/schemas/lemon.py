from pydantic import BaseModel


class LemonBase(BaseModel):
    lemon_count: int

    class Config:
        from_attributes = True


class LemonCreate(LemonBase):
    pass


class LemonUpdate(LemonBase):
    pass


class LemonRead(LemonBase):
    id: int


class LemonResponse(LemonBase):
    user_id: int
