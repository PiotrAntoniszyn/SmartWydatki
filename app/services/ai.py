import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.schemas import CategorySuggestion
from app.services.logs import log_error

class AiTimeout(Exception):
    """Exception raised when AI processing times out."""
    pass

def analyze_expense(description: str, amount: float, user_categories: List[Dict[str, Any]]) -> List[CategorySuggestion]:
    """
    Simulated AI model to analyze expense and suggest relevant categories.
    In a real implementation, this would call an actual AI service or model.
    
    Args:
        description: The expense description
        amount: The expense amount
        user_categories: List of user's categories with usage data
        
    Returns:
        List of CategorySuggestion objects, ranked by relevance
    """
    # This function simulates the AI processing time
    time.sleep(0.5)  # Simulate AI processing delay
    
    # For now, we'll just rank by usage_count and return top matches
    # In a real implementation, we would use NLP to analyze the description
    # and possibly consider the amount as well
    
    # Sort categories by usage_count (descending)
    sorted_categories = sorted(
        user_categories, 
        key=lambda x: x.get('usage_count', 0), 
        reverse=True
    )
    
    # Return top 3 as suggestions
    suggestions = []
    for item in sorted_categories[:3]:
        suggestions.append(CategorySuggestion(
            id=UUID(item['id']),
            name=item['name'],
            usage_count=item['usage_count']
        ))
    
    return suggestions

def get_category_suggestions_with_timeout(
    user_id: UUID, 
    description: str, 
    amount: float,
    user_categories: List[Dict[str, Any]],
    timeout_seconds: float = 2.0
) -> List[CategorySuggestion]:
    """
    Get AI-powered category suggestions with timeout handling.
    
    Args:
        user_id: UUID of the authenticated user
        description: Description of the expense
        amount: Amount of the expense
        user_categories: List of user's categories with usage data
        timeout_seconds: Maximum time to wait for AI processing
        
    Returns:
        List of CategorySuggestion objects, ranked by relevance
        
    Raises:
        AiTimeout: If processing exceeds the timeout limit
    """
    result = None
    
    # Create a thread pool executor
    with ThreadPoolExecutor(max_workers=1) as executor:
        # Submit the AI analysis task
        future = executor.submit(analyze_expense, description, amount, user_categories)
        
        try:
            # Wait for the result with a timeout
            result = future.result(timeout=timeout_seconds)
        except TimeoutError:
            # Log the timeout error
            log_error(
                user_id=user_id,
                error_code='AI_TIMEOUT',
                message=f"AI suggestion timed out after {timeout_seconds} seconds for description: {description[:100]}"
            )
            # Cancel the task if possible
            future.cancel()
            # Raise a custom timeout exception
            raise AiTimeout(f"AI suggestion processing timed out after {timeout_seconds} seconds")
    
    return result 