import psycopg2
from datetime import date, timedelta
import pandas as pd

DB_CONFIG = {
    "dbname": "banco_hackathon",
    "user": "postgres",
    "password": "sua_senha",  # Altere para a sua senha do PostgreSQL
    "host": "localhost",
    "port": "5432"
}

def conectar_banco():
    return psycopg2.connect(**DB_CONFIG)

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            perfil VARCHAR(50) NOT NULL,
            setor VARCHAR(255) NOT NULL,
            streak INTEGER DEFAULT 0,
            ultima_atividade DATE,
            score_logic INTEGER DEFAULT 0,
            score_sql INTEGER DEFAULT 0,
            score_bi INTEGER DEFAULT 0
        )
    ''')

    # Tabela de Feedbacks com Avaliação CSAT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id SERIAL PRIMARY KEY,
            usuario_nome VARCHAR(255) NOT NULL,
            avaliacao VARCHAR(50) NOT NULL,
            comentario TEXT NOT NULL,
            data_envio DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # Carga inicial de dados de teste
    cursor.execute("SELECT COUNT(*) FROM usuarios;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi) VALUES 
            ('Carlos Mendes', 'admin123', 'chefe', 'Tecnologia', 15, CURRENT_DATE, 100, 100, 100),
            ('Fernanda Lima', 'admin123', 'chefe', 'Dados', 12, CURRENT_DATE, 100, 100, 100),
            ('Ana Silva', '123456', 'funcionario', 'Desenvolvimento', 14, CURRENT_DATE, 0, 0, 0),
            ('Rafael Ferreira', '123456', 'funcionario', 'Engenharia', 11, CURRENT_DATE, 50, 50, 0),
            ('Beatriz Souza', '123456', 'funcionario', 'Recursos Humanos', 3, CURRENT_DATE, 0, 0, 0);
        """)
        conn.commit()

    conn.commit()
    cursor.close()
    conn.close()

def registrar_usuario(nome, senha, perfil, setor):
    conn = conectar_banco()
    cursor = conn.cursor()
    hoje = date.today()
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade) 
            VALUES (%s, %s, %s, %s, 1, %s)
        ''', (nome, senha, perfil, setor, hoje))
        conn.commit()
        sucesso = True
    except psycopg2.IntegrityError:
        conn.rollback()
        sucesso = False
    finally:
        cursor.close()
        conn.close()
    return sucesso

def autenticar_usuario(nome, senha):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi 
        FROM usuarios WHERE nome = %s AND senha = %s
    """, (nome, senha))
    usuario = cursor.fetchone()
    
    if usuario:
        user_id, nome_db, perfil, setor, streak, ultima_atividade, s_log, s_sql, s_bi = usuario
        hoje = date.today()
        
        if ultima_atividade == hoje - timedelta(days=1):
            novo_streak = streak + 1
        elif ultima_atividade == hoje:
            novo_streak = streak
        else:
            novo_streak = 1
            
        cursor.execute("UPDATE usuarios SET streak = %s, ultima_atividade = %s WHERE id = %s", (novo_streak, hoje, user_id))
        conn.commit()
        streak = novo_streak
        
        cursor.close()
        conn.close()
        return {
            "id": user_id, "nome": nome_db, "perfil": perfil, "setor": setor, 
            "streak": streak, "score_logic": s_log, "score_sql": s_sql, "score_bi": s_bi
        }
        
    cursor.close()
    conn.close()
    return None

def salvar_score(nome, modulo, nota):
    conn = conectar_banco()
    cursor = conn.cursor()
    coluna = f"score_{modulo}"
    query = f"UPDATE usuarios SET {coluna} = %s WHERE nome = %s"
    cursor.execute(query, (nota, nome))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_todos_resultados():
    conn = conectar_banco()
    query = """
        SELECT nome, perfil, setor, streak, score_logic, score_sql, score_bi, 
        ROUND((score_logic + score_sql + score_bi) / 3.0, 1) AS media_geral 
        FROM usuarios 
        ORDER BY media_geral DESC, streak DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def salvar_feedback(usuario_nome, avaliacao, comentario):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedbacks (usuario_nome, avaliacao, comentario) VALUES (%s, %s, %s)",
        (usuario_nome, avaliacao, comentario)
    )
    conn.commit()
    cursor.close()
    conn.close()

def buscar_feedbacks():
    conn = conectar_banco()
    query = "SELECT usuario_nome AS \"Usuário\", avaliacao AS \"Avaliação\", comentario AS \"Comentário\", data_envio AS \"Data\" FROM feedbacks ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df