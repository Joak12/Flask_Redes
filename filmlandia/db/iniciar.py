import sqlite3
import os

# Defina o caminho do banco de dados
db_path = '/var/www/html/filmlandia/db/banco.db'

# Verifique se o diretório existe, se não, crie-o
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

# Inicializar a variável conn como None
conn = None

# Conectar ao banco de dados (isso criará o arquivo se não existir)
try:
    conn = sqlite3.connect(db_path)
    print("Banco de dados criado e conectado com sucesso.")

    # Criar um cursor
    cursor = conn.cursor()

    # Criar a tabela tb_usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_usuarios (
        usu_id INTEGER PRIMARY KEY AUTOINCREMENT,
        usu_nome TEXT NOT NULL,
        usu_email TEXT NOT NULL,
        usu_senha TEXT NOT NULL
    )
    ''')
    
    # Criar a tabela tb_filmes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_filmes (
        fil_id INTEGER PRIMARY KEY AUTOINCREMENT,
        fil_nome TEXT NOT NULL,
        fil_genero TEXT NOT NULL,
        fil_usu_id INTEGER NOT NULL,
        FOREIGN KEY (fil_usu_id) REFERENCES tb_usuarios(usu_id)
    )
    ''')

    # Criar a tabela tb_avaliacoes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_avaliacoes (
        ava_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ava_nota INTEGER NOT NULL,
        ava_comentario TEXT NOT NULL,
        ava_fil_id INTEGER NOT NULL,
        ava_usu_id INTEGER NOT NULL,
        FOREIGN KEY (ava_fil_id) REFERENCES tb_filmes(fil_id),
        FOREIGN KEY (ava_usu_id) REFERENCES tb_usuarios(usu_id)
    )
    ''')

    # Confirmar as alterações
    conn.commit()
    print("Tabelas criadas com sucesso.")

except sqlite3.OperationalError as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
finally:
    # Fechar a conexão, se existir
    if conn:
        conn.close()
