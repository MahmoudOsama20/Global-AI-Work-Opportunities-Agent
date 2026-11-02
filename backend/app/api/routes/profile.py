from typing import Dict, Any
from fastapi import APIRouter
import yaml
from app.core.config import config_manager, CONFIG_DIR
from app.schemas.profile import UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_model=Dict[str, Any])
def get_profile():
    """Returns the active user profile configuration."""
    return config_manager.get_profile(reload=True)

@router.put("", response_model=Dict[str, Any])
def update_profile(profile_data: Dict[str, Any]):
    """Updates the user profile configuration."""
    profile_path = CONFIG_DIR / "profile.yaml"
    with open(profile_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(profile_data, f, sort_keys=False)
    return config_manager.get_profile(reload=True)

