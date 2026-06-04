from pydantic import BaseModel, Field
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=5)
    pricing: Optional[str] = ""
    features: List[str] = Field(default=[])

class AnalyzeRequest(BaseModel):
    competitor_name: str = Field(..., min_length=1)
    feature_name: str = Field(..., min_length=1)

class ConfigUpdate(BaseModel):
    MOCK_MODE: bool
    GEMINI_API_KEY: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = ""
    PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"

class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
