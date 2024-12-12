from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def get_conexao():
    conn = sqlite3.connect('/var/www/html/filmlandia/db/banco.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def commit_con(conn):
    conn.commit()  # Fazer commits


class User(UserMixin):  # Definindo a classe usuário
    _hash: str

    def __init__(self, **kwargs):
        self._id = None

        if 'usu_id' in kwargs.keys():  # ID do usuário
            self._id = kwargs['usu_id']
        if 'usu_nome' in kwargs.keys():
            self._nome = kwargs['usu_nome']  # Nome do usuário
        if 'usu_email' in kwargs.keys():
            self._email = kwargs['usu_email']  # Email do usuário
        if 'usu_senha' in kwargs.keys():
            self._senha = kwargs['usu_senha']  # Senha (hash) do usuário

    # Sobrescrever get_id do UserMixin
    def get_id(self):
        return str(self._id)

    # ---------- Métodos para manipular o banco --------------#
    def save(self):  # Salvar os dados
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tb_usuarios (usu_nome, usu_email, usu_senha) VALUES (?, ?, ?)", 
                       (self._nome, self._email, self._senha))
        # Salva o id no objeto recém salvo no banco
        self._id = cursor.lastrowid
        commit_con(conn)
        cursor.close()
        conn.close()
        return True

    @classmethod
    def get(cls, user_id):  # Pegar os dados de um usuário
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_id = ?", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            loaduser = User(usu_nome=user['usu_nome'], usu_senha=user['usu_senha'])
            loaduser._id = user['usu_id']
            return loaduser
        else:
            return None

    @classmethod
    def exists(cls, nome):  # Verificar se usuário existe
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_nome = ?", (nome,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user is not None

    @classmethod
    def all(cls):  # Pegar todos os dados
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT usu_id, usu_nome, usu_email FROM tb_usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users

    @classmethod
    def get_by_nome(cls, nome):  # Pegar usuário pelo nome
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT usu_id, usu_nome, usu_email, usu_senha FROM tb_usuarios WHERE usu_nome = ?", (nome,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
