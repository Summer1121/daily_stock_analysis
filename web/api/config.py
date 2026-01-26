# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import find_dotenv, set_key

from config import get_config, Config

router = APIRouter()


class ConfigUpdate(BaseModel):
    stock_list: Optional[List[str]] = None
    feishu_app_id: Optional[str] = None
    feishu_app_secret: Optional[str] = None
    feishu_folder_token: Optional[str] = None
    tushare_token: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    wechat_webhook_url: Optional[str] = None
    feishu_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_sender: Optional[str] = None
    email_password: Optional[str] = None
    email_receivers: Optional[List[str]] = None
    pushover_user_key: Optional[str] = None
    pushover_api_token: Optional[str] = None
    custom_webhook_urls: Optional[List[str]] = None
    custom_webhook_bearer_token: Optional[str] = None
    single_stock_notify: Optional[bool] = None
    schedule_enabled: Optional[bool] = None
    schedule_time: Optional[str] = None
    market_review_enabled: Optional[bool] = None


@router.post("/config")
def update_config(config_update: ConfigUpdate):
    """Update system configuration"""
    dotenv_path = find_dotenv()
    if not dotenv_path:
        # if .env file does not exist, create it
        with open(".env", "w") as f:
            pass
        dotenv_path = find_dotenv()

    for key, value in config_update.dict(exclude_unset=True).items():
        if value is not None:
            if isinstance(value, list):
                set_key(dotenv_path, key.upper(), ",".join(value))
            elif isinstance(value, bool):
                set_key(dotenv_path, key.upper(), str(value).lower())
            else:
                set_key(dotenv_path, key.upper(), value)

    # Reset the config instance to force a reload from the .env file
    Config.reset_instance()
    return {"message": "Configuration updated successfully"}


class ConfigView(BaseModel):
    """Configuration model for frontend"""
    stock_list: List[str]
    feishu_app_id: Optional[str]
    feishu_app_secret: Optional[str]
    feishu_folder_token: Optional[str]
    tushare_token: Optional[str]
    gemini_api_key: Optional[str]
    openai_api_key: Optional[str]
    openai_base_url: Optional[str]
    wechat_webhook_url: Optional[str]
    feishu_webhook_url: Optional[str]
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    email_sender: Optional[str]
    email_password: Optional[str]
    email_receivers: List[str]
    pushover_user_key: Optional[str]
    pushover_api_token: Optional[str]
    custom_webhook_urls: List[str]
    custom_webhook_bearer_token: Optional[str]
    single_stock_notify: bool
    schedule_enabled: bool
    schedule_time: str
    market_review_enabled: bool


@router.get("/config", response_model=ConfigView)
def get_current_config():
    """Get the current system configuration"""
    conf = get_config()
    return ConfigView(**conf.__dict__)
