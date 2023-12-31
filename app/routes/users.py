from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from app.database.db import get_db
from app.database.models import User
from app.repo import users as repository_users
from app.services.auth import auth_service
from app.conf.config import settings
from app.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Get information about the currently authenticated user.

    :param current_user: The current authenticated user.
    
    :return: The user details as a UserDb object.
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the avatar of the currently authenticated user.

    :param file: The uploaded file containing the new avatar image.
    :param current_user: The current authenticated user.
    :param db: The SQLAlchemy Session instance.

    :return: The updated user details as a UserDb object.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    cloudinary.uploader.upload(
        file.file, public_id=f"NotesApp/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"NotesApp/{current_user.username}").build_url(
        width=250, height=250, crop="fill"
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
