from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Expense, Log

@app.route('/expenses/summary', methods=['GET'])
@login_required
def get_expenses_summary():
    period = request.args.get('period', 'weekly')
    
    if period != 'weekly':
        return jsonify({'error': 'Only weekly period is supported'}), 400
    
    user_id = current_user.id
    
    # Obliczamy zakres dat dla ostatniego tygodnia
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    try:
        # Pobieramy sumę wydatków i liczbę transakcji
        expenses_query = db.session.query(
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('transaction_count')
        ).filter(
            Expense.user_id == user_id,
            Expense.date_of_expense >= start_of_week,
            Expense.date_of_expense <= end_of_week
        ).first()
        
        total_amount = expenses_query.total_amount or 0
        transaction_count = expenses_query.transaction_count or 0
        
        summary = {
            'total_amount': float(total_amount),
            'transaction_count': transaction_count
        }
        
        return jsonify(summary)
    
    except Exception as e:
        # Logowanie błędu
        log_entry = Log(
            user_id=user_id,
            type='error',
            error_code='DB_QUERY_ERROR',
            message=f'Error fetching expense summary: {str(e)}'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'error': 'Failed to fetch expense summary'}), 500

@app.route('/ai/tips', methods=['GET'])
@login_required
def get_ai_tips():
    limit = min(int(request.args.get('limit', 3)), 3)  # Ograniczamy do maksymalnie 3
    user_id = current_user.id
    
    try:
        # W rzeczywistej implementacji tutaj byłoby wywołanie do usługi AI
        # Na potrzeby tego przykładu zwracamy statyczne porady
        tips = [
            {'message': 'Rozważ utworzenie budżetu na każdy miesiąc, aby lepiej kontrolować wydatki.'},
            {'message': 'Wydatki na kategorie rozrywkowe stanowią 30% Twoich wydatków. Rozważ ich ograniczenie.'},
            {'message': 'Twoje ostatnie wydatki wykazują wzorzec impulsywnych zakupów. Spróbuj planować zakupy z wyprzedzeniem.'}
        ][:limit]
        
        return jsonify(tips)
    
    except Exception as e:
        # Logowanie błędu
        log_entry = Log(
            user_id=user_id,
            type='error',
            error_code='AI_SERVICE_ERROR',
            message=f'Error generating AI tips: {str(e)}'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'error': 'Failed to generate AI tips'}), 500 