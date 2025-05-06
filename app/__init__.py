from flask import Flask, request, jsonify
import os
from functools import wraps
import jwt
import traceback
from uuid import UUID
from app.services.logs import log_error

def create_app():
    app = Flask(__name__)
    
    # Setup JWT authentication middleware
    @app.before_request
    def authenticate():
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return
            
        # Get the auth token
        auth_header = request.headers.get('Authorization')
        
        # No auth header results in 401
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
            
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            jwt_secret = os.environ.get("JWT_SECRET")
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            
            # Add user_id to request object for controllers to use
            request.user_id = payload.get('user_id')
            
            if not request.user_id:
                return jsonify({"error": "Invalid token, missing user_id"}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    
    # Register blueprints
    from app.routes.categories import categories_bp
    from app.routes.expenses import expenses_bp
    from app.routes.ai_tips import ai_tips_bp
    
    app.register_blueprint(categories_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(ai_tips_bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400
        
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
        
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
        
    @app.errorhandler(409)
    def conflict(e):
        return jsonify({"error": "Conflict", "message": str(e)}), 409
        
    @app.errorhandler(500)
    def server_error(e):
        # Log unhandled internal server errors
        try:
            user_id = getattr(request, 'user_id', None)
            if user_id:
                log_error(
                    user_id=UUID(user_id),
                    error_code='INTERNAL_SERVER_ERROR',
                    message=f"Unhandled server error: {str(e)}\n{traceback.format_exc()}"
                )
        except Exception:
            # If logging fails, we still want to return a response
            pass
            
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(502)
    def bad_gateway(e):
        return jsonify({"error": "Bad Gateway", "message": "External service unavailable"}), 502
    
    return app
