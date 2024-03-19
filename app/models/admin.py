from sqladmin import ModelView
from app.models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.nickname,
        User.email,
        User.password,
        User.is_active,
        User.role,
        User.created_at,
        User.updated_at,
    ]
