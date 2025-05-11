from flask import Blueprint, request, jsonify
from src.db.supabase_client import supabase
from app.services.logs import log_error
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Simple email regex
EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

# REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    password_confirm = data.get('passwordConfirm') or ''

    # Validation
    if not email:
        return jsonify({'field':'email','error':'Email jest wymagany'}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({'field':'email','error':'Nieprawidłowy format email'}), 400
    if not password:
        return jsonify({'field':'password','error':'Hasło jest wymagane'}), 400
    if len(password) < 8:
        return jsonify({'field':'password','error':'Hasło musi mieć co najmniej 8 znaków'}), 400
    if not password_confirm:
        return jsonify({'field':'passwordConfirm','error':'Potwierdzenie hasła jest wymagane'}), 400
    if password != password_confirm:
        return jsonify({'field':'passwordConfirm','error':'Hasła nie są identyczne'}), 400

    try:
        result = supabase.auth.sign_up({'email': email, 'password': password})
        if result.error:
            msg = str(result.error)
            if 'already registered' in msg.lower() or 'duplicate' in msg.lower():
                return jsonify({'field':'email','error':'E-mail jest już używany'}), 409
            return jsonify({'error': msg}), 400

        # Get access token from session
        session = getattr(result.data, 'session', None)
        access_token = session.access_token if session else None
        if not access_token:
            return jsonify({'error':'Brak tokenu w odpowiedzi'}), 500

        # Set HTTP-only cookie
        resp = jsonify({'status':'ok', 'token': access_token})
        resp.set_cookie('sb-access-token', access_token, httponly=True, secure=False, samesite='Lax')
        return resp, 200

    except Exception as e:
        log_error(user_id=None, error_code='REGISTER_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się zarejestrować konta. Spróbuj ponownie.'}), 500


# LOGIN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    # Validation
    if not email:
        return jsonify({'field':'email','error':'Email jest wymagany'}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({'field':'email','error':'Nieprawidłowy format email'}), 400
    if not password:
        return jsonify({'field':'password','error':'Hasło jest wymagane'}), 400

    try:
        result = supabase.auth.sign_in_with_password({'email': email, 'password': password})
        if result.error:
            return jsonify({'error':'Nieprawidłowy email lub hasło'}), 401

        session = getattr(result.data, 'session', None)
        access_token = session.access_token if session else None
        if not access_token:
            return jsonify({'error':'Brak tokenu w odpowiedzi'}), 500

        resp = jsonify({'status':'ok', 'token': access_token})
        resp.set_cookie('sb-access-token', access_token, httponly=True, secure=False, samesite='Lax')
        return resp, 200

    except Exception as e:
        log_error(user_id=None, error_code='LOGIN_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się zalogować'}), 500


# LOGOUT
@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Supabase sign out uses the cookie token implicitly
        supabase.auth.sign_out()
        resp = jsonify({'status':'ok'})
        resp.delete_cookie('sb-access-token')
        return resp, 200
    except Exception as e:
        log_error(user_id=None, error_code='LOGOUT_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się wylogować'}), 500


# CHANGE PASSWORD
@auth_bp.route('/password/change', methods=['POST'])
def change_password():
    data = request.get_json() or {}
    current_password = data.get('currentPassword') or ''
    new_password = data.get('newPassword') or ''
    confirm_new = data.get('passwordConfirm') or ''

    # Validation
    if not current_password:
        return jsonify({'field':'currentPassword','error':'Obecne hasło jest wymagane'}), 400
    if not new_password:
        return jsonify({'field':'newPassword','error':'Nowe hasło jest wymagane'}), 400
    if len(new_password) < 8:
        return jsonify({'field':'newPassword','error':'Hasło musi mieć co najmniej 8 znaków'}), 400
    if not confirm_new:
        return jsonify({'field':'passwordConfirm','error':'Potwierdzenie nowego hasła jest wymagane'}), 400
    if new_password != confirm_new:
        return jsonify({'field':'passwordConfirm','error':'Hasła nie są identyczne'}), 400

    try:
        # Verify current password by re-authenticating
        user_res = supabase.auth.sign_in_with_password({'email': supabase.auth.user().email, 'password': current_password})
        if user_res.error:
            return jsonify({'field':'currentPassword','error':'Nieprawidłowe obecne hasło'}), 401

        update_res = supabase.auth.update({'password': new_password})
        if update_res.error:
            return jsonify({'error':'Nie udało się zmienić hasła'}), 500

        return jsonify({'status':'ok'}), 200

    except Exception as e:
        log_error(user_id=None, error_code='PASSWORD_CHANGE_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się zmienić hasła. Spróbuj ponownie.'}), 500


# RESET PASSWORD REQUEST
@auth_bp.route('/password/reset-request', methods=['POST'])
def reset_request():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()

    if not email:
        return jsonify({'field':'email','error':'Email jest wymagany'}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({'field':'email','error':'Nieprawidłowy format email'}), 400

    try:
        supabase.auth.api.reset_password_for_email(email)
        return jsonify({'status':'ok'}), 200
    except Exception as e:
        log_error(user_id=None, error_code='RESET_REQUEST_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się wysłać linku resetującego. Spróbuj ponownie.'}), 500


# RESET PASSWORD CONFIRM
@auth_bp.route('/password/reset-confirm', methods=['POST'])
def reset_confirm():
    data = request.get_json() or {}
    token = data.get('token') or ''
    new_password = data.get('password') or ''
    confirm_new = data.get('passwordConfirm') or ''

    if not token:
        return jsonify({'error':'Link resetujący jest nieprawidłowy lub wygasł.'}), 400
    if not new_password:
        return jsonify({'field':'password','error':'Hasło jest wymagane'}), 400
    if len(new_password) < 8:
        return jsonify({'field':'password','error':'Hasło musi mieć co najmniej 8 znaków'}), 400
    if not confirm_new:
        return jsonify({'field':'passwordConfirm','error':'Potwierdzenie hasła jest wymagane'}), 400
    if new_password != confirm_new:
        return jsonify({'field':'passwordConfirm','error':'Hasła nie są identyczne'}), 400

    try:
        supabase.auth.api.update_user(token, {'password': new_password})
        return jsonify({'status':'ok'}), 200
    except Exception as e:
        log_error(user_id=None, error_code='RESET_CONFIRM_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się zmienić hasła. Spróbuj ponownie.'}), 500


# DELETE ACCOUNT
@auth_bp.route('/account', methods=['DELETE'])
def delete_account():
    data = request.get_json() or {}
    password = data.get('password') or ''

    if not password:
        return jsonify({'field':'password','error':'Hasło jest wymagane'}), 400

    try:
        # Verify password
        user = supabase.auth.user()
        email = user.email if user else None
        if not email:
            return jsonify({'error':'Nieautoryzowany'}), 401
        verify = supabase.auth.sign_in_with_password({'email': email, 'password': password})
        if verify.error:
            return jsonify({'field':'password','error':'Nieprawidłowe hasło'}), 401

        # Delete user
        supabase.auth.api.delete_user(user.id)
        resp = jsonify({'status':'ok'})
        resp.delete_cookie('sb-access-token')
        return resp, 200

    except Exception as e:
        log_error(user_id=None, error_code='DELETE_ACCOUNT_ERROR', message=str(e))
        return jsonify({'error':'Nie udało się usunąć konta. Spróbuj ponownie.'}), 500 