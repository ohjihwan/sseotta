from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class TransactionBase(BaseModel):
    date: datetime
    amount: float = Field(..., gt=0)
    category: str
    sub_category: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None


class TransactionCreate(TransactionBase):
    source_type: Literal["text", "image", "csv"] = "text"
    original_text: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[datetime] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    sub_category: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    source_type: str
    ai_confidence: Optional[float] = None
    created_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}


class Transaction(TransactionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    source_type: Literal["text", "image", "csv"] = "text"
    ai_confidence: Optional[float] = Field(None, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

