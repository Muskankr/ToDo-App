import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Todo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
@login_required
def dashboard():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', todos=todos)

# ---------------- ADD TODO ----------------
@app.route('/add', methods=['POST'])
@login_required
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    due_date = request.form.get('due_date')

    todo = Todo(
        task=task,
        priority=priority,
        due_date=due_date,
        user_id=current_user.id)
    # task = request.form['task']
    # todo = Todo(task=task, user_id=current_user.id)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ---------------- COMPLETE TODO ----------------
@app.route('/complete/<int:id>')
@login_required
def complete(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return redirect(url_for('dashboard'))

    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('dashboard'))
# @app.route('/complete/<int:id>')
# @login_required
# def complete(id):
#     todo = Todo.query.get(id)
#     todo.completed = not todo.completed
#     db.session.commit()
#     return redirect(url_for('dashboard'))

# ---------------- DELETE TODO ----------------

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return redirect(url_for('dashboard'))

    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('dashboard'))


# @app.route('/delete/<int:id>')
# @login_required
# def delete(id):
#     todo = Todo.query.get(id)
#     db.session.delete(todo)
#     db.session.commit()
#     return redirect(url_for('dashboard'))


# ---------------- LOGOUT ----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# if __name__ == '__main__':
#     app.run(debug=True)
