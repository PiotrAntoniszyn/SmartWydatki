from flask import Blueprint, request, jsonify
from uuid import UUID
from typing import Optional

from app.schemas import CategoryCreate, CategoryUpdate, CategoryRead, CategorySuggestion
from app.services.categories import CategoryService

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_service = CategoryService()

@categories_bp.route('', methods=['GET'])
def list_categories():
    """Get all categories for the authenticated user."""
    # Extract user_id from JWT token
    user_id = request.user_id  # Assuming middleware adds this
    
    try:
        categories = category_service.list_categories(user_id)
        return jsonify([cat.dict() for cat in categories]), 200
    except Exception as e:
        # Log error
        return jsonify({"error": str(e)}), 500

@categories_bp.route('', methods=['POST'])
def create_category():
    """Create a new category for the authenticated user."""
    user_id = request.user_id
    
    try:
        # Validate request body using Pydantic
        category_data = CategoryCreate.parse_obj(request.json)
        
        # Create category
        created_category = category_service.create_category(user_id, category_data.name)
        return jsonify(created_category.dict()), 201
        
    except ValueError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except Exception as e:
        # Handle conflict or other errors
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return jsonify({"error": "Category with this name already exists"}), 409
        
        # Log critical errors
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/<uuid:id>', methods=['GET'])
def get_category(id: UUID):
    """Get a specific category by ID."""
    user_id = request.user_id
    
    try:
        category = category_service.get_category(user_id, id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
        
        return jsonify(category.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/<uuid:id>', methods=['PUT'])
def update_category(id: UUID):
    """Update a category by ID."""
    user_id = request.user_id
    
    try:
        # Validate request body
        category_data = CategoryUpdate.parse_obj(request.json)
        
        # Update category
        updated_category = category_service.update_category(user_id, id, category_data.name)
        if not updated_category:
            return jsonify({"error": "Category not found"}), 404
            
        return jsonify(updated_category.dict()), 200
    
    except ValueError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return jsonify({"error": "Category with this name already exists"}), 409
            
        # Log critical errors
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_category(id: UUID):
    """Delete a category by ID."""
    user_id = request.user_id
    
    try:
        success = category_service.delete_category(user_id, id)
        if not success:
            return jsonify({"error": "Category not found"}), 404
            
        return "", 204
    except ValueError as e:
        # Handle attempt to delete default category
        if "default" in str(e).lower():
            return jsonify({"error": "Cannot delete the default category"}), 400
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log critical errors
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/suggestions', methods=['GET'])
def get_category_suggestions():
    """Get AI-powered category suggestions based on expense description and amount."""
    user_id = request.user_id
    
    # Get and validate query parameters
    description = request.args.get('description')
    amount_str = request.args.get('amount')
    
    if not description or not amount_str:
        return jsonify({"error": "Both description and amount parameters are required"}), 400
    
    try:
        amount = float(amount_str)
        
        # Get suggestions
        suggestions = category_service.suggest_categories(user_id, description, amount)
        return jsonify([suggestion.dict() for suggestion in suggestions]), 200
        
    except ValueError:
        return jsonify({"error": "Invalid amount format. Must be a number"}), 400
    except Exception as e:
        error_message = str(e).lower()
        
        # Handle different types of errors with appropriate status codes
        if "timeout" in error_message or "timed out" in error_message:
            # AI timeout error - return 502 Bad Gateway
            return jsonify({
                "error": "AI suggestion service unavailable", 
                "message": "The service is temporarily unavailable. Please try again later."
            }), 502
            
        elif "database" in error_message or "db error" in error_message:
            # Database error - return 500 Internal Server Error
            return jsonify({
                "error": "Database error", 
                "message": "An error occurred while retrieving category data."
            }), 500
            
        elif "unable to access" in error_message:
            # Data access error - return 500 Internal Server Error
            return jsonify({
                "error": "System error", 
                "message": "Unable to process category suggestions at this time."
            }), 500
            
        else:
            # General AI service error - return 502 Bad Gateway
            return jsonify({
                "error": "AI service error", 
                "message": "An error occurred while generating suggestions."
            }), 502 