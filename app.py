@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/categories/manage')
@login_required
def categories_page():
    """Renderuje widok zarządzania kategoriami."""
    return render_template('categories.html') 