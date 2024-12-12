from flask import Flask, session, request, render_template, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, commit_con
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Iniciar Banco
def init_db():
    conn = None
    try:
        conn = sqlite3.connect('./db/banco.db')
        with conn:
            # Lê e executa o script SQL
            with open('/var/www/html/filmlandia/db/banco.sql') as db_file:
                conn.executescript(db_file.read())
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()
init_db()

# Configurações para usar SQLite:
app.config['DATABASE'] = '/var/www/html/filmlandia/db/banco.db'

# Chave para criptografia de cookies na sessão
app.config['SECRET_KEY'] = 'superdificil'

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        user = User.get_by_nome(nome)

        if user is None:
            flash("Usuário não cadastrado. <a href='" + url_for('cadastro') + "'>Cadastre-se aqui</a>", "error")
            return redirect(url_for('login'))
        if check_password_hash(user['usu_senha'], senha):
            login_user(User.get(user['usu_id']))
            return redirect(url_for('meusfilmes'))
        flash("Senha Incorreta", "error")
        return redirect(url_for('login'))
    
    return render_template('pages/login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('pages/cadastro.html')
    else:
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        if not User.exists(nome):
            user = User(usu_nome=nome, usu_email=email, usu_senha=senha)
            user.save()
            # Logar o usuário depois de cadastrar
            login_user(user)
            flash('Cadastro Realizado!', 'success')
            return redirect(url_for('meusfilmes'))
        else:
            flash("Esse usuário já existe! <a href='" + url_for('login') + "'>Faça Login</a>", 'error')
            return redirect(url_for('cadastro'))

@app.route('/meusfilmes/', methods=['POST', 'GET'])
@login_required
def meusfilmes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fil_id, fil_nome, fil_genero 
        FROM tb_filmes
        WHERE fil_usu_id = ?
    """, (current_user._id,))

    filmes = cursor.fetchall()
    conn.close()
    return render_template('pages/meusfilmes.html', filmes=filmes)

@app.route('/addfilme', methods=['POST', 'GET'])
@login_required
def addfilme():
    if request.method == 'POST':
        nome_filme = request.form['adicionar-nome-filme']
        genero_filme = request.form['genero']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tb_filmes (fil_nome, fil_genero, fil_usu_id) 
            VALUES (?, ?, ?)
        """, (nome_filme, genero_filme, current_user._id))
        conn.commit()
        conn.close()
        return redirect(url_for('meusfilmes'))

    return render_template('pages/addfilme.html')

@app.route('/removefilme/<int:fil_id>', methods=['POST'])
@login_required
def removefilme(fil_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM tb_avaliacoes WHERE ava_fil_id = ? 
    """, (fil_id,))

    cursor.execute("""
        DELETE FROM tb_filmes WHERE fil_id = ?
    """, (fil_id,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('meusfilmes'))

@app.route('/avaliar/<int:fil_id>', methods=['POST', 'GET'])
@login_required
def avaliarfilme(fil_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT fil_nome FROM tb_filmes WHERE fil_id = ?', (fil_id,))
        fil_nome = cursor.fetchone()['fil_nome']
        conn.close()
        return render_template('pages/addavaliacao.html', fil_id=fil_id, fil_nome=fil_nome)

    if request.method == 'POST':
        comentario = request.form['comentario']
        nota = request.form['nota']

        cursor.execute('SELECT ava_fil_id FROM tb_avaliacoes WHERE ava_usu_id = ?', (current_user._id,))
        filmes_avaliados = cursor.fetchall()
        filmes_avaliados_ids = [row['ava_fil_id'] for row in filmes_avaliados]

        for id_filme in filmes_avaliados_ids:
            if id_filme == fil_id:
                novo_comentario = request.form['comentario']
                nova_nota = request.form['nota']

                cursor.execute("""
                    UPDATE tb_avaliacoes SET ava_comentario = ?, ava_nota = ?
                    WHERE ava_fil_id = ?;
                """, (novo_comentario, nova_nota, id_filme))
                conn.commit()
                conn.close()
                return redirect(url_for('veravaliacao', fil_id=fil_id))

        cursor.execute("""
            INSERT INTO tb_avaliacoes(ava_comentario, ava_nota, ava_fil_id, ava_usu_id)
            VALUES (?, ?, ?, ?)
        """, (comentario, nota, fil_id, current_user._id))
        conn.commit()
        conn.close()
        return redirect(url_for('veravaliacao', fil_id=fil_id))

@app.route('/veravaliacao/<int:fil_id>', methods=['GET'])
@login_required
def veravaliacao(fil_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ava_nota, ava_comentario, fil_nome, fil_genero
        FROM tb_avaliacoes
        JOIN tb_filmes ON ava_fil_id=fil_id
        WHERE ava_fil_id = ? AND ava_usu_id = ?
    """, (fil_id, current_user._id,))
    
    avaliacao = cursor.fetchone()

    if not avaliacao:
        nota = None
        filme_genero = ''
        filme_nome = ''
        filme_id = fil_id
        comentario = 'Opa! Você ainda não avaliou esse filme!'
    else:
        nota = avaliacao['ava_nota']
        comentario = avaliacao['ava_comentario']
        filme_nome = avaliacao['fil_nome']
        filme_genero = avaliacao['fil_genero']
        filme_id = fil_id

    conn.close()
    return render_template('pages/veravaliacao.html', nota=nota, comentario=comentario, filme_nome=filme_nome, filme_genero=filme_genero, filme_id=filme_id)

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
