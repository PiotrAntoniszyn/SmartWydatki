from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta, date
from decimal import Decimal
import calendar

from app.schemas import ExpenseRead, ExpenseCreate, ExpenseUpdate, ExpenseSummary, Pagination, ExpenseList
from app.services.database import get_supabase_client
from app.services.logs import log_error, log_info, LogType


class ExpenseService:
    """Service class for managing expense operations."""
    
    def __init__(self):
        """Initialize the expense service with Supabase client."""
        self.supabase = get_supabase_client()
    
    def list_expenses(self, user_id: UUID, limit: int = 20, offset: int = 0, 
                     search: Optional[str] = None, date_from: Optional[str] = None,
                     date_to: Optional[str] = None, amount_min: Optional[float] = None,
                     amount_max: Optional[float] = None) -> ExpenseList:
        """
        Retrieve a paginated, filterable list of expenses for the user.
        
        Args:
            user_id: UUID of the authenticated user
            limit: Number of records to return (default 20, max 100)
            offset: Number of records to skip (default 0)
            search: Optional search term for description field
            date_from: Optional ISO date to filter expenses from
            date_to: Optional ISO date to filter expenses to
            amount_min: Optional minimum amount filter
            amount_max: Optional maximum amount filter
            
        Returns:
            ExpenseList with data and pagination metadata
        """
        # Ensure limit is within allowed range
        if limit > 100:
            limit = 100
            
        # Start building the query
        query = self.supabase.table('expenses') \
            .select('id, amount, description, category_id, date_of_expense, created_at', count='exact') \
            .eq('user_id', str(user_id))
        
        # Apply filters if provided
        if search:
            query = query.ilike('description', f'%{search}%')
            
        if date_from:
            query = query.gte('date_of_expense', date_from)
            
        if date_to:
            query = query.lte('date_of_expense', date_to)
            
        if amount_min is not None:
            query = query.gte('amount', amount_min)
            
        if amount_max is not None:
            query = query.lte('amount', amount_max)
        
        # Add pagination and execute
        response = query.order('date_of_expense', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        # Convert to Pydantic models
        expenses = []
        for item in response.data:
            expenses.append(ExpenseRead(
                id=UUID(item['id']),
                amount=Decimal(str(item['amount'])),
                description=item['description'],
                category_id=UUID(item['category_id']),
                date_of_expense=item['date_of_expense'],
                created_at=item['created_at']
            ))
        
        # Create pagination metadata
        pagination = Pagination(
            limit=limit,
            offset=offset,
            total=response.count
        )
        
        return ExpenseList(
            data=expenses,
            pagination=pagination
        )
    
    def get_expense(self, user_id: UUID, expense_id: UUID) -> Optional[ExpenseRead]:
        """
        Get a specific expense by ID.
        
        Args:
            user_id: UUID of the authenticated user
            expense_id: UUID of the expense to retrieve
            
        Returns:
            ExpenseRead object or None if not found
        """
        response = self.supabase.table('expenses') \
            .select('id, amount, description, category_id, date_of_expense, created_at') \
            .eq('user_id', str(user_id)) \
            .eq('id', str(expense_id)) \
            .execute()
        
        if not response.data:
            return None
            
        item = response.data[0]
        return ExpenseRead(
            id=UUID(item['id']),
            amount=Decimal(str(item['amount'])),
            description=item['description'] or "",
            category_id=UUID(item['category_id']),
            date_of_expense=item['date_of_expense'],
            created_at=item['created_at']
        )
    
    def create_expense(self, user_id: UUID, expense_data: ExpenseCreate) -> ExpenseRead:
        """
        Create a new expense for the user.
        
        Args:
            user_id: UUID of the authenticated user
            expense_data: ExpenseCreate data with amount, description, and optional category_id
            
        Returns:
            The created ExpenseRead object
            
        Raises:
            Exception: If creation fails
        """
        try:
            # If no category_id provided, find the default category
            if expense_data.category_id is None:
                default_category = self.supabase.table('categories') \
                    .select('id') \
                    .eq('user_id', str(user_id)) \
                    .eq('is_default', True) \
                    .execute()
                
                if not default_category.data:
                    raise ValueError("Default category not found")
                    
                category_id = default_category.data[0]['id']
            else:
                category_id = str(expense_data.category_id)
                
            # Prepare expense data
            expense = {
                'amount': float(expense_data.amount),
                'description': expense_data.description,
                'category_id': category_id,
                'user_id': str(user_id),
                'date_of_expense': datetime.now().isoformat()
            }
            
            # Insert the expense
            response = self.supabase.table('expenses') \
                .insert(expense) \
                .execute()
                
            if not response.data:
                raise Exception("Failed to create expense")
                
            item = response.data[0]
            
            # Log success
            log_info(
                user_id=user_id,
                expense_id=UUID(item['id']),
                message=f"Created expense of {expense_data.amount} with description: '{expense_data.description}'"
            )
            
            # Return the created expense
            return ExpenseRead(
                id=UUID(item['id']),
                amount=Decimal(str(item['amount'])),
                description=item['description'],
                category_id=UUID(item['category_id']),
                date_of_expense=item['date_of_expense'],
                created_at=item['created_at']
            )
            
        except Exception as e:
            # Log error
            log_error(
                user_id=user_id,
                message=f"Failed to create expense: {str(e)}",
                error_code="CREATE_EXPENSE_ERROR"
            )
            raise
            
    def update_expense(self, user_id: UUID, expense_id: UUID, expense_data: ExpenseUpdate) -> Optional[ExpenseRead]:
        """
        Update an existing expense.
        
        Args:
            user_id: UUID of the authenticated user
            expense_id: UUID of the expense to update
            expense_data: ExpenseUpdate data with amount, description, and category_id
            
        Returns:
            Updated ExpenseRead object or None if not found
            
        Raises:
            Exception: If update fails
        """
        try:
            # First check if the expense exists
            existing_expense = self.get_expense(user_id, expense_id)
            if not existing_expense:
                return None
                
            # Prepare update data
            update_data = {}
            
            if expense_data.amount is not None:
                update_data['amount'] = float(expense_data.amount)
                
            if expense_data.description is not None:
                update_data['description'] = expense_data.description
                
            if expense_data.category_id is not None:
                update_data['category_id'] = str(expense_data.category_id)
            
            # Update the expense
            response = self.supabase.table('expenses') \
                .update(update_data) \
                .eq('user_id', str(user_id)) \
                .eq('id', str(expense_id)) \
                .execute()
                
            if not response.data:
                raise Exception("Failed to update expense")
                
            item = response.data[0]
            
            # Log success
            log_info(
                user_id=user_id,
                expense_id=expense_id,
                message=f"Updated expense {expense_id}"
            )
            
            # Return the updated expense
            return ExpenseRead(
                id=UUID(item['id']),
                amount=Decimal(str(item['amount'])),
                description=item['description'],
                category_id=UUID(item['category_id']),
                date_of_expense=item['date_of_expense'],
                created_at=item['created_at']
            )
            
        except Exception as e:
            # Log error
            log_error(
                user_id=user_id,
                expense_id=expense_id,
                message=f"Failed to update expense: {str(e)}",
                error_code="UPDATE_EXPENSE_ERROR"
            )
            raise
            
    def delete_expense(self, user_id: UUID, expense_id: UUID) -> bool:
        """
        Delete an expense.
        
        Args:
            user_id: UUID of the authenticated user
            expense_id: UUID of the expense to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            Exception: If deletion fails
        """
        try:
            # First check if the expense exists
            existing_expense = self.get_expense(user_id, expense_id)
            if not existing_expense:
                return False
                
            # Delete the expense
            response = self.supabase.table('expenses') \
                .delete() \
                .eq('user_id', str(user_id)) \
                .eq('id', str(expense_id)) \
                .execute()
                
            if not response.data:
                raise Exception("Failed to delete expense")
                
            # Log success
            log_info(
                user_id=user_id,
                expense_id=expense_id,
                message=f"Deleted expense {expense_id}"
            )
            
            return True
            
        except Exception as e:
            # Log error
            log_error(
                user_id=user_id,
                expense_id=expense_id,
                message=f"Failed to delete expense: {str(e)}",
                error_code="DELETE_EXPENSE_ERROR"
            )
            raise
    
    def bulk_delete_expenses(self, user_id: UUID, expense_ids: List[UUID]) -> Dict[str, Any]:
        """
        Delete multiple expenses in a single operation.
        
        Args:
            user_id: UUID of the authenticated user
            expense_ids: List of expense UUIDs to delete
            
        Returns:
            Dictionary with success/failure counts and details
            
        Raises:
            Exception: If the operation completely fails
        """
        if not expense_ids:
            return {
                "success": True,
                "deleted_count": 0,
                "failed_count": 0,
                "details": "No expenses to delete"
            }
            
        # Convert UUIDs to strings for Supabase
        expense_ids_str = [str(expense_id) for expense_id in expense_ids]
        
        try:
            # Verify expenses belong to user before deletion
            verification = self.supabase.table('expenses') \
                .select('id') \
                .eq('user_id', str(user_id)) \
                .in_('id', expense_ids_str) \
                .execute()
            
            # IDs that actually belong to the user
            valid_ids = [item['id'] for item in verification.data]
            
            # Find which IDs were invalid
            invalid_ids = [id for id in expense_ids_str if id not in valid_ids]
            
            if not valid_ids:
                # If none of the IDs are valid
                return {
                    "success": False,
                    "deleted_count": 0,
                    "failed_count": len(expense_ids),
                    "failed_ids": [str(id) for id in expense_ids],
                    "details": "None of the provided expense IDs belong to the user or exist"
                }
            
            # Delete the valid expenses
            delete_response = self.supabase.table('expenses') \
                .delete() \
                .eq('user_id', str(user_id)) \
                .in_('id', valid_ids) \
                .execute()
                
            deleted_ids = [item['id'] for item in delete_response.data]
            failed_valid_ids = [id for id in valid_ids if id not in deleted_ids]
            
            # Log the bulk deletion
            log_info(
                user_id=user_id,
                message=f"Bulk deleted {len(deleted_ids)} expenses"
            )
            
            # Return the result
            return {
                "success": len(deleted_ids) > 0,
                "deleted_count": len(deleted_ids),
                "failed_count": len(invalid_ids) + len(failed_valid_ids),
                "deleted_ids": deleted_ids,
                "failed_ids": invalid_ids + failed_valid_ids,
                "details": "Bulk delete operation completed"
            }
            
        except Exception as e:
            # Log error
            log_error(
                user_id=user_id,
                message=f"Failed to bulk delete expenses: {str(e)}",
                error_code="BULK_DELETE_EXPENSES_ERROR"
            )
            
            # Re-raise for controller to handle
            raise Exception(f"Bulk delete operation failed: {str(e)}")
            
    def get_summary(self, user_id: UUID, period: str, 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> ExpenseSummary:
        """
        Get a summary of expenses for a specific period.
        
        Args:
            user_id: UUID of the authenticated user
            period: Period to aggregate ('weekly', 'monthly', or 'custom')
            start_date: Custom start date in ISO format (required for 'custom' period)
            end_date: Custom end date in ISO format (required for 'custom' period)
            
        Returns:
            ExpenseSummary with total_amount and transaction_count
            
        Raises:
            ValueError: If period is not supported or required dates are missing
        """
        period = period.lower()
        today = datetime.now()
        
        if period == 'weekly':
            # Calculate date range for current week (starting Monday)
            start_of_week = today - timedelta(days=today.weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_week = start_of_week + timedelta(days=7)
            
            start_date_iso = start_of_week.isoformat()
            end_date_iso = end_of_week.isoformat()
            
        elif period == 'monthly':
            # Calculate date range for current month
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Get last day of current month
            _, last_day = calendar.monthrange(today.year, today.month)
            end_of_month = today.replace(day=last_day, hour=23, minute=59, second=59)
            end_of_month = end_of_month + timedelta(days=1)  # Move to next day's 00:00:00
            
            start_date_iso = start_of_month.isoformat()
            end_date_iso = end_of_month.isoformat()
            
        elif period == 'custom':
            # Use custom date range
            if not start_date or not end_date:
                raise ValueError("Both start_date and end_date are required for custom period")
                
            # Parse and validate dates
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if start_dt > end_dt:
                    raise ValueError("start_date cannot be later than end_date")
                    
                start_date_iso = start_dt.isoformat()
                end_date_iso = end_dt.isoformat()
                
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid date format: {str(e)}")
                
        else:
            raise ValueError("Period must be one of: 'weekly', 'monthly', or 'custom'")
            
        # Query expenses for the specified period
        response = self.supabase.table('expenses') \
            .select('id, amount') \
            .eq('user_id', str(user_id)) \
            .gte('date_of_expense', start_date_iso) \
            .lt('date_of_expense', end_date_iso) \
            .execute()
            
        # Calculate summary
        total_amount = sum(Decimal(str(item['amount'])) for item in response.data)
        transaction_count = len(response.data)
        
        return ExpenseSummary(
            total_amount=total_amount,
            transaction_count=transaction_count
        ) 