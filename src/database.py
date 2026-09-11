import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "datalogic.db"

def conectar_banco():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela de Usuários atualizada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL,
        setor TEXT NOT NULL,
        streak INTEGER DEFAULT 1,
        ultima_atividade TEXT DEFAULT CURRENT_DATE,
        score_logic INTEGER DEFAULT 0,
        score_sql INTEGER DEFAULT 0,
        score_bi INTEGER DEFAULT 0
    )
    """)
    
    # Tabela de Feedbacks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        avaliacao TEXT NOT NULL,
        comentario TEXT NOT NULL,
        data_envio TEXT NOT NULL
    )
    """)
    
    # Inserir usuário demo chefe por padrão
    cursor.execute("SELECT * FROM usuarios WHERE nome = ?", ("Admin Chefe",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi)
        VALUES (?, ?, ?, ?, ?, CURRENT_DATE, ?, ?, ?)
        """, ("Admin Chefe", "admin123", "chefe", "Gestão de TI", 15, 100, 100, 100))
        
    conn.commit()
    conn.close()

def autenticar_usuario(nome, senha):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, perfil, setor, streak, score_logic, score_sql, score_bi FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {
            "id": usuario[0],
            "nome": usuario[1],
            "perfil": usuario[2],
            "setor": usuario[3],
            "streak": usuario[4],
            "score_logic": usuario[5],
            "score_sql": usuario[6],
            "score_bi": usuario[7]
        }
    return None

def registrar_usuario(nome, senha, perfil, setor):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi)
        VALUES (?, ?, ?, ?, 1, CURRENT_DATE, 0, 0, 0)
        """, (nome, senha, perfil, setor))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def salvar_score(nome, modulo, nota):
    conn = conectar_banco()
    cursor = conn.cursor()
    coluna = f"score_{modulo}"
    cursor.execute(f"UPDATE usuarios SET {coluna} = ? WHERE nome = ?", (nota, nome))
    conn.commit()
    conn.close()

def salvar_feedback(usuario, avaliacao, comentario):
    conn = conectar_banco()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute("""
    INSERT INTO feedbacks (usuario, avaliacao, comentario, data_envio)
    VALUES (?, ?, ?, ?)
    """, (usuario, avaliacao, comentario, data_atual))
    conn.commit()
    conn.close()

def buscar_todos_resultados():
    conn = conectar_banco()
    query = """
    SELECT 
        nome, 
        perfil, 
        setor, 
        streak, 
        score_logic, 
        score_sql, 
        score_bi,
        ROUND((score_logic + score_sql + score_bi) / 3.0, 1) as media_geral
    FROM usuarios
    WHERE perfil = 'funcionario'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def buscar_feedbacks():
    conn = conectar_banco()
    query = "SELECT usuario as Usuário, avaliacao as Avaliação, comentario as Comentário, data_envio as Data FROM feedbacks ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df