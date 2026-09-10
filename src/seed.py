INSERT INTO usuarios (nome, senha, perfil, setor, streak, ultima_atividade, score_logic, score_sql, score_bi) 
VALUES 
('Carlos Mendes', 'admin123', 'chefe', 'Tecnologia', 15, CURRENT_DATE, 100, 100, 100),
('Fernanda Lima', 'admin123', 'chefe', 'Dados', 12, CURRENT_DATE - INTERVAL '1 day', 100, 100, 100),
('Ana Silva', '123456', 'funcionario', 'Dados', 14, CURRENT_DATE, 100, 100, 100),
('Rafael Ferreira', '123456', 'funcionario', 'Dados', 11, CURRENT_DATE, 100, 100, 100),
('Rodrigo Alves', '123456', 'funcionario', 'Tecnologia', 8, CURRENT_DATE - INTERVAL '1 day', 100, 100, 100),
('Gabriel Santos', '123456', 'funcionario', 'Tecnologia', 10, CURRENT_DATE, 100, 100, 0),
('Mariana Costa', '123456', 'funcionario', 'Financeiro', 7, CURRENT_DATE - INTERVAL '2 days', 100, 0, 100),
('Beatriz Souza', '123456', 'funcionario', 'RH', 3, CURRENT_DATE, 0, 0, 100),
('Lucas Oliveira', '123456', 'funcionario', 'Operações', 1, CURRENT_DATE, 0, 0, 0)
ON CONFLICT (nome) DO NOTHING;