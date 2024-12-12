CREATE TABLE IF NOT EXISTS tb_usuarios (
    usu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usu_nome TEXT NOT NULL,
    usu_email TEXT NOT NULL,
    usu_senha TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_filmes (
    fil_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fil_nome TEXT NOT NULL,
    fil_genero TEXT NOT NULL,
    fil_usu_id INTEGER NOT NULL,
    FOREIGN KEY (fil_usu_id) REFERENCES tb_usuarios(usu_id)
);

CREATE TABLE IF NOT EXISTS tb_avaliacoes (
    ava_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ava_nota INTEGER NOT NULL,
    ava_comentario TEXT NOT NULL,
    ava_fil_id INTEGER NOT NULL,
    ava_usu_id INTEGER NOT NULL,
    FOREIGN KEY (ava_fil_id) REFERENCES tb_filmes(fil_id),
    FOREIGN KEY (ava_usu_id) REFERENCES tb_usuarios(usu_id)
);
