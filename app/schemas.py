# app/schemas.py

from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, condecimal, constr


# 1. Category DTOs and Commands

class CategoryRead(BaseModel):
    """DTO for reading categories."""
    id: UUID
    name: str
    is_default: bool


class CategoryCreate(BaseModel):
    """Command model for creating a new category."""
    name: constr(max_length=30)  # ≤ 30 characters


# Alias for update (same structure as create)
CategoryUpdate = CategoryCreate


class CategorySuggestion(BaseModel):
    """AI-powered suggestion for existing categories."""
    id: UUID
    name: str
    usage_count: int


# 2. Expense DTOs and Commands

class ExpenseRead(BaseModel):
    """DTO for reading a single expense."""
    id: UUID
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)
    description: Optional[constr(max_length=100)] = None
    category_id: UUID
    date_of_expense: datetime
    created_at: datetime


class ExpenseCreate(BaseModel):
    """Command model for creating a new expense."""
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)
    description: constr(max_length=100) = Field(default="")
    category_id: Optional[UUID] = None


# Alias for update (same as create)
ExpenseUpdate = ExpenseCreate


class Pagination(BaseModel):
    """Generic pagination metadata."""
    limit: int
    offset: int
    total: int


class ExpenseList(BaseModel):
    """DTO for paginated list of expenses."""
    data: List[ExpenseRead]
    pagination: Pagination


class ExpenseSummary(BaseModel):
    """DTO for weekly summary of expenses."""
    total_amount: condecimal(ge=0, max_digits=14, decimal_places=2)
    transaction_count: int


# 3. AI Tips

class AiTip(BaseModel):
    """DTO for a single AI-generated financial tip."""
    message: str


# 4. Logs (internal)

class LogType(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class LogRead(BaseModel):
    """DTO for reading internal log entries."""
    id: UUID
    user_id: UUID
    expense_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    type: LogType
    error_code: Optional[constr(max_length=50)] = None
    message: constr(max_length=500)
    created_at: datetime