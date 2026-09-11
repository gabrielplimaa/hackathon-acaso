import sqlite3

def popular_banco():
    conn = sqlite3.connect("datalogic.db")
    cursor = conn.cursor()
    
    query = """
    INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi) 
    VALUES 
    ('Carlos Mendes', 'admin123', 'chefe', 'Tecnologia', 15, DATE('now'), 100, 100, 100),
    ('Fernanda Lima', 'admin123', 'chefe', 'Dados', 12, DATE('now', '-1 day'), 100, 100, 100),
    ('Ana Silva', '123456', 'funcionario', 'Dados', 14, DATE('now'), 100, 100, 100),
    ('Rafael Ferreira', '123456', 'funcionario', 'Dados', 11, DATE('now'), 100, 100, 100),
    ('Rodrigo Alves', '123456', 'funcionario', 'Tecnologia', 8, DATE('now', '-1 day'), 100, 100, 100),
    ('Gabriel Santos', '123456', 'funcionario', 'Tecnologia', 10, DATE('now'), 100, 100, 0),
    ('Mariana Costa', '123456', 'funcionario', 'Financeiro', 7, DATE('now', '-2 days'), 100, 0, 100),
    ('Beatriz Souza', '123456', 'funcionario', 'RH', 3, DATE('now'), 0, 0, 100),
    ('Lucas Oliveira', '123456', 'funcionario', 'Operações', 1, DATE('now'), 0, 0, 0)
    ON CONFLICT(nome) DO NOTHING;
    """
    
    cursor.execute(query)
    conn.commit()
    conn.close()
    print("Banco populado com sucesso!")

if __name__ == "__main__":
    popular_banco()