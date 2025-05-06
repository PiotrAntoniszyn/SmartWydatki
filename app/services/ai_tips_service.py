import time
import requests
import os
from typing import List, Dict, Any, Optional
from uuid import UUID
import json

from app.schemas import AiTip
from app.services.logs import log_error
from app.services.database import get_supabase_client

class AiTipsService:
    """Service for generating AI-powered financial tips for users."""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.timeout = 10  # 10-second timeout
        self.max_retries = 3
        
    def get_tips(self, user_id: UUID, limit: int = 3) -> List[AiTip]:
        """
        Get AI-generated financial tips for the authenticated user.
        
        Args:
            user_id (UUID): The ID of the authenticated user
            limit (int): Maximum number of tips to return (default: 3, max: 3)
            
        Returns:
            List[AiTip]: List of AI-generated financial tips
            
        Raises:
            Exception: If AI service fails after retries
        """
        try:
            # Build prompt with user's financial data
            prompt = self._build_prompt(user_id)
            
            # Call AI service with retry logic
            response = self._call_ai_service_with_retry(user_id, prompt)
            
            # Process the AI response
            tips = self._process_ai_response(response, limit)
            
            return tips
            
        except Exception as e:
            # Log any unexpected errors
            log_error(
                user_id=user_id,
                error_code='AI_TIPS_ERROR',
                message=f"Error getting AI tips: {str(e)}"
            )
            # Return a generic tip for MVP (in production we'd re-raise)
            return [AiTip(message="Consider reviewing your recent expenses to identify potential savings opportunities.")]
    
    def _build_prompt(self, user_id: UUID) -> str:
        """
        Build the prompt for the AI service using the user's expense patterns.
        
        Args:
            user_id (UUID): The ID of the authenticated user
            
        Returns:
            str: Prompt for the AI service
        """
        # Get user's expense data from Supabase
        expense_data = self._get_user_expense_data(user_id)
        
        # Check if we have enough data to generate meaningful tips
        has_expenses = expense_data.get('recent_expenses') and len(expense_data.get('recent_expenses', [])) > 0
        has_categories = expense_data.get('category_summary') and len(expense_data.get('category_summary', [])) > 0
        
        if not has_expenses:
            # If no expenses, use a prompt for new users
            prompt = """
            You are a financial advisor assistant. The user is new and hasn't recorded any expenses yet.
            
            Provide up to three concise, specific and actionable financial tips for new users.
            
            Your response should ONLY include the tips in a JSON array format, each with a 'message' field.
            Focus on:
            1. Getting started with expense tracking
            2. Basic financial health tips
            3. Habit formation for financial tracking
            
            Format example:
            [
                {"message": "Start by tracking all your expenses for a week to get a baseline understanding of your spending habits."},
                {"message": "Set up categories for your regular expenses to help identify where your money is going."}
            ]
            """
            return prompt
        
        # Build prompt based on expense data
        prompt = f"""
        You are a financial advisor assistant. Based on the following user's expense data, 
        provide up to three concise, specific and actionable financial tips:
        
        User's recent expenses:
        {json.dumps(expense_data, indent=2)}
        
        Your response should ONLY include the tips in a JSON array format, each with a 'message' field.
        Focus on:
        1. Spending trends and anomalies
        2. Budget recommendations
        3. Savings opportunities
        
        Format example:
        [
            {{"message": "Your dining out expenses increased by 20% this week."}},
            {{"message": "Consider setting a budget for entertainment."}}
        ]
        """
        
        return prompt
    
    def _get_user_expense_data(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get the user's expense data from the database.
        
        Args:
            user_id (UUID): The ID of the authenticated user
            
        Returns:
            Dict[str, Any]: User's expense data
        """
        try:
            supabase = get_supabase_client()
            
            # Get last 2 weeks of expenses
            two_weeks_ago = time.strftime("%Y-%m-%d", time.localtime(time.time() - 14 * 24 * 60 * 60))
            
            # Query expenses
            response = supabase.table('expenses').select(
                'id,amount,description,date_of_expense,category:categories(id,name)'
            ).eq(
                'user_id', str(user_id)
            ).gte(
                'date_of_expense', two_weeks_ago
            ).order(
                'date_of_expense', desc=True
            ).execute()
            
            # Get category summary
            category_summary = supabase.table('expenses').select(
                'category_id,categories(name),sum_amount:amount(sum),count:id(count)'
            ).eq(
                'user_id', str(user_id)
            ).gte(
                'date_of_expense', two_weeks_ago
            ).group(
                'category_id,categories(name)'
            ).execute()
            
            expense_data = {
                'recent_expenses': response.data[:20],  # Limit to 20 most recent expenses
                'category_summary': category_summary.data
            }
            
            return expense_data
            
        except Exception as e:
            # Log the error
            log_error(
                user_id=user_id,
                error_code='DATABASE_ERROR',
                message=f"Error getting expense data: {str(e)}"
            )
            # Return empty data structure for MVP
            return {'recent_expenses': [], 'category_summary': []}
    
    def _call_ai_service_with_retry(self, user_id: UUID, prompt: str) -> Dict[str, Any]:
        """
        Call the AI service with retry logic and timeout handling.
        
        Args:
            user_id (UUID): The ID of the authenticated user
            prompt (str): The prompt for the AI service
            
        Returns:
            Dict[str, Any]: Response from the AI service
            
        Raises:
            Exception: If AI service fails after retries
        """
        # Check if API key is available
        if not self.api_key:
            log_error(
                user_id=user_id,
                error_code='AI_CONFIG_ERROR',
                message="OpenRouter API key not configured"
            )
            raise Exception("OpenRouter API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful financial advisor assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        # Try up to max_retries times
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                # Raise exception for HTTP errors
                response.raise_for_status()
                
                # Return JSON response
                return response.json()
                
            except requests.exceptions.Timeout:
                # Log timeout error
                log_error(
                    user_id=user_id,
                    error_code='AI_TIMEOUT',
                    message=f"AI service timeout (attempt {attempt + 1}/{self.max_retries})"
                )
                
                # Retry or raise exception on last attempt
                if attempt == self.max_retries - 1:
                    raise Exception("AI service timeout after maximum retries")
                    
            except requests.exceptions.RequestException as e:
                # Log error
                log_error(
                    user_id=user_id,
                    error_code='AI_ERROR',
                    message=f"AI service error: {str(e)} (attempt {attempt + 1}/{self.max_retries})"
                )
                
                # Retry or raise exception on last attempt
                if attempt == self.max_retries - 1:
                    raise Exception(f"AI service error after maximum retries: {str(e)}")
                    
                # Wait before retrying (exponential backoff)
                time.sleep(2 ** attempt)  # 1, 2, 4 seconds
    
    def _process_ai_response(self, response: Dict[str, Any], limit: int) -> List[AiTip]:
        """
        Process the AI service response and extract tips.
        
        Args:
            response (Dict[str, Any]): Response from the AI service
            limit (int): Maximum number of tips to return
            
        Returns:
            List[AiTip]: List of AI-generated financial tips
        """
        try:
            # Extract content from response
            content = response['choices'][0]['message']['content']
            
            # Parse JSON from content
            tips_data = json.loads(content)
            
            # Validate and convert to AiTip objects
            tips = []
            for tip_data in tips_data[:limit]:
                if isinstance(tip_data, dict) and 'message' in tip_data:
                    tips.append(AiTip(message=tip_data['message']))
            
            # If we got no valid tips, fall back to a generic tip
            if not tips:
                return [AiTip(message="Consider reviewing your recent expenses to identify potential savings opportunities.")]
                
            return tips
            
        except (KeyError, json.JSONDecodeError, TypeError, IndexError) as e:
            # If parsing fails, try to extract any text that looks like a tip
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Create fallback tips
            fallback_tips = []
            lines = content.split('\n')
            for line in lines:
                # Look for lines that might be tips
                line = line.strip()
                if line and len(line) > 10 and len(line) < 200 and not line.startswith('{') and not line.startswith('['):
                    fallback_tips.append(AiTip(message=line))
                    if len(fallback_tips) >= limit:
                        break
            
            # If we found any usable tips, return them
            if fallback_tips:
                return fallback_tips
                
            # Otherwise, return a generic tip
            return [AiTip(message="Consider reviewing your recent expenses to identify potential savings opportunities.")] 