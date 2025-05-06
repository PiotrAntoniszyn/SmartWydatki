from flask import Blueprint, jsonify, request
from functools import wraps
from typing import List
from uuid import UUID

from app.schemas import AiTip
from app.services.logs import log_error, log_info

# Create AI tips blueprint
ai_tips_bp = Blueprint('ai_tips', __name__, url_prefix='/ai')

# Authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Authentication is handled by the @app.before_request in __init__.py
        # This decorator is mainly used to clarify that the route requires auth
        return f(*args, **kwargs)
    return decorated

@ai_tips_bp.route('/tips', methods=['GET'])
@requires_auth
def get_ai_tips():
    """
    Get AI-generated financial tips for the authenticated user.
    
    Query Parameters:
    - limit (int, optional): Maximum number of tips to return (default: 3, max: 3)
    
    Returns:
    - 200: List of AI-generated financial tips
    - 400: Invalid limit parameter
    - 401: Unauthorized (handled by authentication middleware)
    - 502: AI service timeout or error
    - 500: Internal server error
    """
    try:
        # Get user_id from request (set by authentication middleware)
        user_id = UUID(request.user_id)
        
        # Parse and validate limit parameter
        limit = request.args.get('limit', default=3, type=int)
        
        # Validate limit parameter
        if limit < 1 or limit > 3:
            return jsonify({"error": "Invalid limit parameter", "message": "Limit must be between 1 and 3"}), 400
        
        # Import here to avoid circular imports
        from app.services.ai_tips_service import AiTipsService
        
        try:
            # Get AI tips
            ai_tips_service = AiTipsService()
            tips = ai_tips_service.get_tips(user_id, limit)
            
            # Log successful tips generation
            log_info(
                user_id=user_id,
                message=f"Successfully generated {len(tips)} AI tips"
            )
            
            # Return tips as JSON
            return jsonify(tips), 200
            
        except Exception as e:
            # Check if this is an AI service error
            error_message = str(e).lower()
            if "timeout" in error_message or "ai service" in error_message:
                # Log bad gateway error
                log_error(
                    user_id=user_id,
                    error_code='AI_SERVICE_ERROR',
                    message=f"AI service error: {str(e)}"
                )
                return jsonify({"error": "External AI service unavailable", "message": str(e)}), 502
            else:
                # Re-raise other exceptions to be caught by the outer try/except
                raise
        
    except ValueError as e:
        # Invalid UUID format in user_id or other value error
        return jsonify({"error": "Bad request", "message": str(e)}), 400
        
    except Exception as e:
        # Log unexpected errors
        try:
            log_error(
                user_id=user_id,
                error_code='SERVER_ERROR',
                message=f"Unexpected error in get_ai_tips: {str(e)}"
            )
        except Exception:
            # If logging fails, continue with response
            pass
            
        return jsonify({"error": "Internal server error"}), 500 