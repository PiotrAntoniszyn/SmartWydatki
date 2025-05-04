from flask import Blueprint, request, jsonify
from uuid import UUID
from typing import Optional, Dict, Any, Callable, TypeVar, cast, List
from datetime import datetime
from functools import wraps

from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseRead
from app.services.expenses import ExpenseService

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')
expense_service = ExpenseService()

# Typy do dekoratorów
F = TypeVar('F', bound=Callable[..., Any])

def validate_query_params(f: F) -> F:
    """
    Dekorator walidujący parametry zapytania dla endpointów ekspensów.
    Obsługuje konwersję typów i walidację parametrów.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Pobierz parametry z query string
            params = {}
            
            # Konwersja wartości liczbowych
            for param, default, convert_func in [
                ('limit', 20, int),
                ('offset', 0, int),
                ('amount_min', None, float),
                ('amount_max', None, float),
            ]:
                val = request.args.get(param)
                if val is not None:
                    try:
                        params[param] = convert_func(val)
                    except ValueError:
                        return jsonify({
                            "error": f"Invalid value for parameter '{param}'",
                            "details": f"Value '{val}' cannot be converted to the required type."
                        }), 400
                else:
                    params[param] = default
            
            # Walidacja limitów
            if params.get('limit', 0) > 100:
                params['limit'] = 100
            
            if params.get('limit', 0) < 1:
                params['limit'] = 1
                
            # Walidacja offsetu
            if params.get('offset', 0) < 0:
                params['offset'] = 0
                
            # Walidacja zakresów kwot
            if params.get('amount_min') is not None and params.get('amount_min') < 0:
                return jsonify({
                    "error": "Invalid value for parameter 'amount_min'",
                    "details": "Minimum amount cannot be negative."
                }), 400
                
            if (params.get('amount_min') is not None and 
                params.get('amount_max') is not None and 
                params.get('amount_min') > params.get('amount_max')):
                return jsonify({
                    "error": "Invalid range for amount parameters",
                    "details": "Minimum amount cannot be greater than maximum amount."
                }), 400
            
            # Walidacja dat
            for date_param in ['date_from', 'date_to']:
                date_val = request.args.get(date_param)
                if date_val:
                    try:
                        # Normalizacja formatu daty ISO
                        params[date_param] = datetime.fromisoformat(
                            date_val.replace('Z', '+00:00')
                        ).isoformat()
                    except ValueError:
                        return jsonify({
                            "error": f"Invalid value for parameter '{date_param}'",
                            "details": f"Value '{date_val}' is not a valid ISO 8601 date format."
                        }), 400
            
            # Walidacja zakresu dat
            if ('date_from' in params and 'date_to' in params and
                params['date_from'] > params['date_to']):
                return jsonify({
                    "error": "Invalid date range",
                    "details": "Start date cannot be after end date."
                }), 400
            
            # Przekazanie parametrów zapytania
            params['search'] = request.args.get('search')
            
            # Dodanie zwalidowanych parametrów do atrybutów zapytania
            request.validated_params = params
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": "Error validating query parameters",
                "details": str(e)
            }), 400
    
    return cast(F, decorated_function)

@expenses_bp.route('', methods=['GET'])
@validate_query_params
def list_expenses():
    """Get paginated and filtered expenses for the authenticated user."""
    user_id = request.user_id  # Assuming middleware adds this
    
    try:
        # Pobierz zwalidowane parametry z dekoratora
        params = request.validated_params
        
        # Get expenses with filters
        result = expense_service.list_expenses(
            user_id=user_id,
            limit=params.get('limit', 20),
            offset=params.get('offset', 0),
            search=params.get('search'),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
            amount_min=params.get('amount_min'),
            amount_max=params.get('amount_max')
        )
        
        # Return serialized response
        return jsonify({
            "data": [expense.dict() for expense in result.data],
            "pagination": result.pagination.dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": "Invalid parameter format", "details": str(e)}), 400
    except Exception as e:
        # Log error
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/<uuid:id>', methods=['GET'])
def get_expense(id: UUID):
    """Get a specific expense by ID."""
    user_id = request.user_id
    
    try:
        expense = expense_service.get_expense(user_id, id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        
        return jsonify(expense.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('', methods=['POST'])
def create_expense():
    """Create a new expense for the authenticated user."""
    user_id = request.user_id
    
    try:
        # Validate request body using Pydantic
        expense_data = ExpenseCreate.parse_obj(request.json)
        
        # Create expense
        created_expense = expense_service.create_expense(user_id, expense_data)
        return jsonify(created_expense.dict()), 201
        
    except ValueError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except Exception as e:
        # Handle other errors
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/<uuid:id>', methods=['PUT'])
def update_expense(id: UUID):
    """Update an expense by ID."""
    user_id = request.user_id
    
    try:
        # Validate request body
        expense_data = ExpenseUpdate.parse_obj(request.json)
        
        # Update expense
        updated_expense = expense_service.update_expense(user_id, id, expense_data)
        if not updated_expense:
            return jsonify({"error": "Expense not found"}), 404
            
        return jsonify(updated_expense.dict()), 200
    
    except ValueError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except Exception as e:
        # Log critical errors
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/<uuid:id>', methods=['DELETE'])
def delete_expense(id: UUID):
    """Delete an expense by ID."""
    user_id = request.user_id
    
    try:
        success = expense_service.delete_expense(user_id, id)
        if not success:
            return jsonify({"error": "Expense not found"}), 404
            
        return "", 204
    except Exception as e:
        # Log critical errors
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_expenses():
    """Delete multiple expenses in a single operation."""
    user_id = request.user_id
    
    try:
        # Validate request body
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400
            
        data = request.json
        if not isinstance(data, dict) or 'ids' not in data:
            return jsonify({"error": "Request must contain 'ids' field"}), 400
            
        ids = data.get('ids', [])
        if not isinstance(ids, list):
            return jsonify({"error": "'ids' must be an array"}), 400
            
        # Convert string IDs to UUIDs
        try:
            expense_ids = [UUID(id) for id in ids]
        except ValueError:
            return jsonify({"error": "Invalid UUID format in ids list"}), 400
            
        # Call service method
        result = expense_service.bulk_delete_expenses(user_id, expense_ids)
        
        # Determine appropriate response code
        if not result["deleted_count"] and result["failed_count"]:
            # All operations failed
            return jsonify(result), 400
        elif result["deleted_count"] and result["failed_count"]:
            # Partial success
            return jsonify(result), 207  # Multi-Status
        else:
            # Complete success or no operations
            return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get a summary of expenses for the specified period."""
    user_id = request.user_id
    
    # Get and validate period parameter
    period = request.args.get('period')
    if not period:
        return jsonify({"error": "Period parameter is required"}), 400
        
    # Get optional date parameters for custom period
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # Validate dates if provided
        if start_date:
            try:
                datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    "error": "Invalid start_date format",
                    "details": "Date must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                }), 400
                
        if end_date:
            try:
                datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    "error": "Invalid end_date format",
                    "details": "Date must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                }), 400
        
        # Get summary data with all parameters
        summary = expense_service.get_summary(
            user_id=user_id,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(summary.dict()), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log critical errors
        return jsonify({"error": str(e)}), 500 