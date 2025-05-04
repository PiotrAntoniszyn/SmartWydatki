from typing import List, Optional, Dict, Any
from uuid import UUID

from app.schemas import CategoryRead, CategorySuggestion
from app.services.database import get_supabase_client
from app.services.logs import log_error
from app.services.ai import get_category_suggestions_with_timeout, AiTimeout

class CategoryService:
    """Service class for managing category operations."""
    
    def __init__(self):
        """Initialize the category service with Supabase client."""
        self.supabase = get_supabase_client()
    
    def list_categories(self, user_id: UUID) -> List[CategoryRead]:
        """
        Retrieve all categories belonging to the user.
        
        Args:
            user_id: UUID of the authenticated user
            
        Returns:
            List of CategoryRead objects
        """
        # Query categories from Supabase
        response = self.supabase.table('categories') \
            .select('id, name, is_default') \
            .eq('user_id', str(user_id)) \
            .execute()
        
        # Convert to Pydantic models
        categories = []
        for item in response.data:
            categories.append(CategoryRead(
                id=UUID(item['id']),
                name=item['name'],
                is_default=item['is_default']
            ))
        
        return categories
    
    def get_category(self, user_id: UUID, category_id: UUID) -> Optional[CategoryRead]:
        """
        Get a specific category by ID.
        
        Args:
            user_id: UUID of the authenticated user
            category_id: UUID of the category to retrieve
            
        Returns:
            CategoryRead object or None if not found
        """
        response = self.supabase.table('categories') \
            .select('id, name, is_default') \
            .eq('user_id', str(user_id)) \
            .eq('id', str(category_id)) \
            .execute()
        
        if not response.data:
            return None
            
        item = response.data[0]
        return CategoryRead(
            id=UUID(item['id']),
            name=item['name'],
            is_default=item['is_default']
        )
    
    def create_category(self, user_id: UUID, name: str) -> CategoryRead:
        """
        Create a new category for the user.
        
        Args:
            user_id: UUID of the authenticated user
            name: Name of the new category (max 30 chars)
            
        Returns:
            The created CategoryRead object
            
        Raises:
            Exception: If a duplicate name is found
        """
        # Check for duplicate name
        existing = self.supabase.table('categories') \
            .select('id') \
            .eq('user_id', str(user_id)) \
            .eq('name', name) \
            .execute()
            
        if existing.data:
            raise ValueError("Category with this name already exists")
        
        # Insert new category
        response = self.supabase.table('categories') \
            .insert({
                'name': name,
                'user_id': str(user_id),
                'is_default': False
            }) \
            .execute()
        
        if not response.data:
            raise Exception("Failed to create category")
            
        item = response.data[0]
        return CategoryRead(
            id=UUID(item['id']),
            name=item['name'],
            is_default=item['is_default']
        )
    
    def update_category(self, user_id: UUID, category_id: UUID, name: str) -> Optional[CategoryRead]:
        """
        Update an existing category.
        
        Args:
            user_id: UUID of the authenticated user
            category_id: UUID of the category to update
            name: New name for the category
            
        Returns:
            Updated CategoryRead object or None if not found
            
        Raises:
            ValueError: If attempting to rename the default category
            Exception: If a duplicate name is found
        """
        # First get the category to check if it's default
        category = self.get_category(user_id, category_id)
        if not category:
            return None
            
        if category.is_default:
            raise ValueError("Cannot rename the default category")
        
        # Check for duplicate name
        existing = self.supabase.table('categories') \
            .select('id') \
            .eq('user_id', str(user_id)) \
            .eq('name', name) \
            .neq('id', str(category_id)) \
            .execute()
            
        if existing.data:
            raise ValueError("Category with this name already exists")
        
        # Update the category
        response = self.supabase.table('categories') \
            .update({'name': name}) \
            .eq('user_id', str(user_id)) \
            .eq('id', str(category_id)) \
            .execute()
        
        if not response.data:
            return None
            
        item = response.data[0]
        return CategoryRead(
            id=UUID(item['id']),
            name=item['name'],
            is_default=item['is_default']
        )
    
    def delete_category(self, user_id: UUID, category_id: UUID) -> bool:
        """
        Delete a category.
        
        Args:
            user_id: UUID of the authenticated user
            category_id: UUID of the category to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If attempting to delete the default category
        """
        # Check if it's the default category
        category = self.get_category(user_id, category_id)
        if not category:
            return False
            
        if category.is_default:
            raise ValueError("Cannot delete the default category")
        
        # Delete the category
        response = self.supabase.table('categories') \
            .delete() \
            .eq('user_id', str(user_id)) \
            .eq('id', str(category_id)) \
            .execute()
            
        return len(response.data) > 0
    
    def get_categories_with_usage(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Get categories with their usage counts for the user.
        
        Args:
            user_id: UUID of the authenticated user
            
        Returns:
            List of dictionaries with category data including usage counts
            
        Raises:
            Exception: If database errors occur
        """
        try:
            # Query stored procedure to get categories with usage counts
            response = self.supabase.rpc(
                'get_category_usage_counts',
                {'user_id_param': str(user_id)}
            ).execute()
            
            return response.data
        except Exception as e:
            # Log the database error
            log_error(
                user_id=user_id,
                error_code='DB_ERROR',
                message=f"Database error getting category usage: {str(e)}"
            )
            # Re-raise as a database error
            raise Exception(f"Database error: {str(e)}")
    
    def suggest_categories(self, user_id: UUID, description: str, amount: float) -> List[CategorySuggestion]:
        """
        Get AI-powered category suggestions based on description and amount.
        
        Args:
            user_id: UUID of the authenticated user
            description: Description of the expense
            amount: Amount of the expense
            
        Returns:
            List of CategorySuggestion objects, ranked by relevance
            
        Raises:
            Exception: If AI service errors or times out
        """
        try:
            # Get categories with usage data for AI processing
            try:
                user_categories = self.get_categories_with_usage(user_id)
            except Exception as e:
                # If database error, log and re-raise with appropriate message
                log_error(
                    user_id=user_id,
                    error_code='DB_ERROR',
                    message=f"Database error during AI suggestions: {str(e)}"
                )
                raise Exception("Unable to access category data for AI processing")
            
            # Check if user has any categories
            if not user_categories:
                # If user has no categories, return empty list
                return []
            
            # Get AI suggestions with timeout handling
            suggestions = get_category_suggestions_with_timeout(
                user_id=user_id,
                description=description,
                amount=amount,
                user_categories=user_categories,
                timeout_seconds=2.0
            )
            
            return suggestions
            
        except AiTimeout as e:
            # AI timeout is already logged in the AI service
            # Just re-raise with a user-friendly message
            raise Exception("AI suggestion service timed out")
            
        except Exception as e:
            # Log the error if it wasn't already logged
            if not str(e).startswith("Unable to access category data"):
                log_error(
                    user_id=user_id,
                    error_code='AI_ERROR',
                    message=str(e)
                )
            # Re-raise to be handled by controller
            raise Exception(f"AI suggestion service error: {str(e)}") 