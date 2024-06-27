from pydantic import BaseModel


class LemonBase(BaseModel):
    lemon_count: int


class LemonCreate(LemonBase):
    pass


class LemonUpdate(LemonBase):
    pass


class LemonRead(LemonBase):
    id: int

    class Config:
        orm_mode = True
