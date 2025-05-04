from uuid import UUID
from typing import Optional
from enum import Enum

from app.services.database import get_supabase_client

class LogType(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"

def log_error(
    user_id: UUID,
    error_code: str, 
    message: str,
    expense_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None
) -> None:
    """
    Log an error to the database.
    
    Args:
        user_id: UUID of the user experiencing the error
        error_code: Classification code for the error
        message: Detailed error message
        expense_id: Optional UUID of related expense
        category_id: Optional UUID of related category
    """
    supabase = get_supabase_client()
    
    # Insert log entry
    log_data = {
        'user_id': str(user_id),
        'type': 'error',
        'error_code': error_code,
        'message': message[:500]  # Truncate to fit schema constraint
    }
    
    # Add optional IDs if provided
    if expense_id:
        log_data['expense_id'] = str(expense_id)
    if category_id:
        log_data['category_id'] = str(category_id)
        
    # Insert into logs table
    supabase.table('logs').insert(log_data).execute()

def log_info(
    user_id: UUID,
    message: str,
    expense_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None
) -> None:
    """
    Log an informational message to the database.
    
    Args:
        user_id: UUID of the user performing the action
        message: Detailed information message
        expense_id: Optional UUID of related expense
        category_id: Optional UUID of related category
    """
    supabase = get_supabase_client()
    
    # Insert log entry
    log_data = {
        'user_id': str(user_id),
        'type': 'info',
        'message': message[:500]  # Truncate to fit schema constraint
    }
    
    # Add optional IDs if provided
    if expense_id:
        log_data['expense_id'] = str(expense_id)
    if category_id:
        log_data['category_id'] = str(category_id)
        
    # Insert into logs table
    supabase.table('logs').insert(log_data).execute() 