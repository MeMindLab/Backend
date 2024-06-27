from fastapi import APIRouter, Path, Depends
from app.core.dependencies import get_db
from app.service.lemon import LemonService

# sqlalchemy
from sqlalchemy.orm import Session


lemon_module = APIRouter(prefix="")


# Lemon CRUD operations
@lemon_module.get("/{user_id}/lemon")
def read_lemons_by_user(
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    db: Session = Depends(get_db),
):
    lemon_service = LemonService(db)
    lemons = lemon_service.get_lemon_by_user(user_id)

    return lemons
