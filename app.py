# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Configuração do aplicativo
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de codificação
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Inicialização das extensões
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = u'Por favor, faça login para acessar esta página.'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.String(20), default=u'Média')
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

CATEGORIES = [u'Trabalho', u'Pessoal', u'Estudos', u'Compras', u'Saúde', u'Finanças', u'Outros']
PRIORITIES = [u'Baixa', u'Média', u'Alta', u'Urgente']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    category_filter = request.args.get('category')
    priority_filter = request.args.get('priority')
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
        
    tasks = query.order_by(Task.due_date.asc(), Task.priority.desc()).all()
    
    stats = {
        'total': len(tasks),
        'completed': len([t for t in tasks if t.completed]),
        'pending': len([t for t in tasks if not t.completed]),
        'urgent': len([t for t in tasks if t.priority == u'Urgente' and not t.completed])
    }
    
    return render_template('index.html', 
                         tasks=tasks, 
                         categories=CATEGORIES,
                         priorities=PRIORITIES,
                         stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash(u'Bem-vindo de volta, {}!'.format(username), 'success')
            return redirect(url_for('index'))
        
        flash(u'Usuário ou senha inválidos.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if len(username) < 3:
        flash(u'O nome de usuário deve ter pelo menos 3 caracteres.', 'error')
        return redirect(url_for('login'))
        
    if len(password) < 6:
        flash(u'A senha deve ter pelo menos 6 caracteres.', 'error')
        return redirect(url_for('login'))
    
    if password != confirm_password:
        flash(u'As senhas não coincidem.', 'error')
        return redirect(url_for('login'))
    
    if User.query.filter_by(username=username).first():
        flash(u'Este nome de usuário já está em uso.', 'error')
        return redirect(url_for('login'))
    
    user = User(
        username=username,
        password_hash=generate_password_hash(password)
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        flash(u'Conta criada com sucesso! Faça login para continuar.', 'success')
    except:
        db.session.rollback()
        flash(u'Ocorreu um erro ao criar sua conta. Tente novamente.', 'error')
    
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'Você saiu do sistema.', 'success')
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority')
        due_date_str = request.form.get('due_date')
        
        if not title:
            flash(u'O título da tarefa é obrigatório.', 'error')
            return redirect(url_for('index'))
            
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except:
                flash(u'Data inválida.', 'error')
                return redirect(url_for('index'))
        
        task = Task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        flash(u'Tarefa adicionada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(u'Erro ao adicionar tarefa.', 'error')
        
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash(u'Acesso negado.', 'error')
        return redirect(url_for('index'))
        
    try:
        task.completed = not task.completed
        task.completed_at = datetime.utcnow() if task.completed else None
        db.session.commit()
        
        status = u'concluída' if task.completed else u'reaberta'
        flash(u'Tarefa {} com sucesso!'.format(status), 'success')
    except:
        db.session.rollback()
        flash(u'Erro ao atualizar tarefa.', 'error')
        
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash(u'Acesso negado.', 'error')
        return redirect(url_for('index'))
        
    try:
        db.session.delete(task)
        db.session.commit()
        flash(u'Tarefa removida com sucesso!', 'success')
    except:
        db.session.rollback()
        flash(u'Erro ao remover tarefa.', 'error')
        
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True) 