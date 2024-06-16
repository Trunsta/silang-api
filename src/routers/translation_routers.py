from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, UploadFile, Depends
from sqlalchemy.orm import Session

from ..schemas import auth_schemas
from ..schemas.translation_schemas import TranslationBase, TranslationRead, FeedbackUpdate
from ..services.auth_services import get_current_user
from ..services.translation_services import TranslationServices
from ..utils import get_db
from ..crud.translation_crud import TranslationCRUD

router = APIRouter(
    prefix="/api/v1/translations",
    tags=["Translation"],
)


@router.get(
    "/all",
    response_model=list[TranslationRead],
    responses={
        200: {"description": "Succesfully retrieved all translations"},
        404: {"description": "No translations found"},
    }
)
def get_all(
        current_user: Annotated[auth_schemas.UserRead, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    translation_crud = TranslationCRUD(db)

    if not translation_crud.get_all_translations():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No translations found.")

    return translation_crud.get_all_translations()


@router.get(
    "/history",
    response_model=list[TranslationBase],
    responses={
        200: {"description": "Succesfully retrieved translation history"},
        404: {"description": "No translations found"}
    }
)
def get_history(
        current_user: Annotated[auth_schemas.UserRead, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    """
    Returns the current user's translations ordered by the most recent.
    """
    current_user_id = current_user.id

    translation_crud = TranslationCRUD(db)

    if not translation_crud.get_sorted_translations_by_user_id(current_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No translations found.")

    return translation_crud.get_sorted_translations_by_user_id(current_user_id)


@router.post(
    "/",
    status_code=201,
    response_model=TranslationRead,
    responses={
        201: {"description": "Translation created"},
        413: {"description": "Request Entity Too Large"},
        415: {"description": "Unsupported Media Type"}
    }
)
def create_translation(
        file: UploadFile,
        current_user: Annotated[auth_schemas.UserRead, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    service = TranslationServices(db)
    return service.create_translation(file, current_user)


# udh barengan get translation
# @router.get(
#     "/{id}/feedbacks",
#     response_model=TranslationRead,
#     responses={
#         200: {"description": "Get feedback by id"},
#         404: {"description": "Translation not found"}
#     }
# )
# async def get_feedback_by_id(id: int, current_user: Annotated[str, Depends(oauth2_scheme)] = Depends(get_current_user)):
#     # TODO
#     return TranslationRead(id=1, video_url="video_url", translation_text="translation_text", date_time_created="", feedback="feedback")


@router.put(
    "/{id}/feedbacks",
    response_model=TranslationRead,
    responses={
        200: {"description": "Feedback updated"},
        404: {"description": "Translation not found"}
    }
)
def update_feedback_by_id(
        id: int, feedback: FeedbackUpdate,
        current_user: Annotated[auth_schemas.UserRead, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # TODO
    return TranslationRead(id=1, video_url="video_url", translation_text="translation_text", translation_date=datetime.now(), feedback="feedback")

