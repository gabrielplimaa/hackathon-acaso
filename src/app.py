import os
import streamlit as st
import database as db

# Configuração da página
st.set_page_config(
    page_title="DataLogic | Eval & Certify", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Carregamento de Arquivos Estáticos (CSS / JS)
def load_assets():
    base_dir = os.path.dirname(__file__)
    css_path = os.path.join(base_dir, "assets", "styles.css")
    js_path = os.path.join(base_dir, "assets", "script.js")

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

load_assets()

# Inicialização do Banco
db.inicializar_banco()

# Session States
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "modulo_ativo" not in st.session_state:
    st.session_state.modulo_ativo = None

# ==========================================
# TELA DE AUTENTICAÇÃO (LOGIN / CADASTRO)
# ==========================================
if not st.session_state.usuario_logado:
    st.write("")
    st.write("")
    col_left, col_center, col_right = st.columns([1, 1.8, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-block; padding: 12px; background: rgba(99, 102, 241, 0.1); border-radius: 16px; border: 1px solid rgba(99, 102, 241, 0.2); margin-bottom: 12px;">
                <span style="font-size: 2rem;">⚡</span>
            </div>
            <h1 class="brand-title" style="margin: 0;">DataLogic Eval</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px;">Plataforma de Avaliação Contínua & Insights de Performance</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_cad = st.tabs(["🔑 Entrar no Sistema", "✨ Criar Nova Conta"])
        
        with tab_login:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            nome_login = st.text_input("Usuário", placeholder="Digite seu nome de usuário")
            senha_login = st.text_input("Senha", type="password", placeholder="••••••••")
            st.write("")
            if st.button("Acessar Plataforma 🚀"):
                user = db.autenticar_usuario(nome_login, senha_login)
                if user:
                    st.session_state.usuario_logado = user
                    st.success("Autenticado com sucesso!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Tente novamente.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_cad:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            novo_nome = st.text_input("Nome Completo", placeholder="Ex: Ana Silva")
            nova_senha = st.text_input("Senha de Acesso", type="password", placeholder="••••••••")
            c_perfil, c_setor = st.columns(2)
            with c_perfil:
                novo_perfil = st.selectbox("Perfil de Acesso", ["funcionario", "chefe"])
            with c_setor:
                novo_setor = st.text_input("Setor/Cargo", placeholder="Ex: Engenharia de Dados")
            st.write("")
            if st.button("Finalizar Cadastro"):
                if novo_nome and nova_senha and novo_setor:
                    if db.registrar_usuario(novo_nome, nova_senha, novo_perfil, novo_setor):
                        st.success("Conta criada! Alterne para a aba 'Entrar'.")
                    else:
                        st.warning("Nome de usuário já cadastrado.")
                else:
                    st.warning("Preencha todos os campos obrigatórios.")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PAINEL PRINCIPAL (AUTENTICADO)
# ==========================================
else:
    user = st.session_state.usuario_logado
    
    # TOP BAR / HEADER APLICAÇÃO
    c_brand, c_user_info, c_logout = st.columns([2.5, 3, 0.8])
    
    with c_brand:
        st.markdown('<h2 class="brand-title" style="margin:0; font-size: 1.6rem;">⚡ DataLogic</h2>', unsafe_allow_html=True)
        
    with c_user_info:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 16px; margin-top: 4px;">
            <span class="badge-streak">🔥 {user['streak']} DIAS OFENSIVA</span>
            <div style="text-align: right;">
                <div style="font-weight: 700; font-size: 0.95rem;">{user['nome']}</div>
                <div><span class="badge-role">{user['perfil']}</span> <span style="color: #64748b; font-size: 0.8rem;">| {user['setor']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_logout:
        if st.button("Sair 🚪"):
            st.session_state.usuario_logado = None
            st.session_state.modulo_ativo = None
            st.rerun()

    st.markdown("<hr style='border: none; height: 1px; background: rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)

    # ------------------------------------------
    # PERFIL: FUNCIONÁRIO
    # ------------------------------------------
    if user["perfil"] == "funcionario":
        tab_desafios, tab_feedback = st.tabs(["🎯 Módulos de Avaliação", "💬 Feedback & Experiência"])

        # ABA 1: DESAFIOS E TESTES
        with tab_desafios:
            if st.session_state.modulo_ativo is None:
                st.markdown("### Seus Módulos de Aprendizado")
                st.caption("Complete os testes para elevar seu score técnico no painel da liderança.")
                st.write("")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    score_l = user['score_logic']
                    status_l = "Completed" if score_l > 0 else "Pending"
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.8rem;">🧠</span>
                            <span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 0.75rem;">{score_l}/100 PTS</span>
                        </div>
                        <h4 style="margin: 16px 0 6px 0; font-size: 1.1rem;">Lógica de Programação</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">Estruturas condicionais, algoritmos e raciocínio lógico.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("Iniciar Módulo de Lógica", key="btn_log"):
                        st.session_state.modulo_ativo = "logic"
                        st.rerun()

                with col_m2:
                    score_s = user['score_sql']
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.8rem;">🗄️</span>
                            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 0.75rem;">{score_s}/100 PTS</span>
                        </div>
                        <h4 style="margin: 16px 0 6px 0; font-size: 1.1rem;">Banco de Dados & SQL</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">Consultas, joins, agrupamentos e manipulação de dados.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("Iniciar Módulo de SQL", key="btn_sql"):
                        st.session_state.modulo_ativo = "sql"
                        st.rerun()

                with col_m3:
                    score_b = user['score_bi']
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.8rem;">📊</span>
                            <span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 0.75rem;">{score_b}/100 PTS</span>
                        </div>
                        <h4 style="margin: 16px 0 6px 0; font-size: 1.1rem;">Business Intelligence</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">Métricas de negócios, ETL e visualização de dados.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("Iniciar Módulo de BI", key="btn_bi"):
                        st.session_state.modulo_ativo = "bi"
                        st.rerun()

            # QUIZ INTERATIVO (QUANDO UM MÓDULO É SELECIONADO)
            else:
                modulo = st.session_state.modulo_ativo
                
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                if modulo == "logic":
                    st.markdown("### 🧠 Avaliação: Lógica de Programação")
                    st.caption("Responda às questões abaixo com atenção. Cada questão vale 50 pontos.")
                    st.write("")
                    
                    with st.form("form_test_logic"):
                        q1 = st.radio("1) Qual o resultado da expressão em Python: `10 + 2 * 3`?", ["36", "16", "24", "15"])
                        st.write("")
                        q2 = st.radio("2) Qual estrutura é ideal para iterar repetidamente enquanto uma condição for verdadeira?", ["if / else", "for", "while", "switch"])
                        st.write("")
                        
                        btn_enviar = st.form_submit_button("Submeter Respostas 📤")
                        if btn_enviar:
                            nota = 0
                            if q1 == "16": nota += 50
                            if q2 == "while": nota += 50
                            
                            db.salvar_score(user["nome"], "logic", nota)
                            user["score_logic"] = nota
                            st.session_state.modulo_ativo = None
                            st.success(f"Avaliação Concluída! Nota final registrada: {nota}/100")
                            st.rerun()

                elif modulo == "sql":
                    st.markdown("### 🗄️ Avaliação: Banco de Dados & SQL")
                    st.caption("Responda às questões abaixo com atenção. Cada questão vale 50 pontos.")
                    st.write("")
                    
                    with st.form("form_test_sql"):
                        q1 = st.radio("1) Qual comando DML é utilizado para extrair e consultar dados de uma tabela?", ["UPDATE", "INSERT", "SELECT", "DELETE"])
                        st.write("")
                        q2 = st.radio("2) Qual cláusula é utilizada para filtrar resultados agregados produzidos por um `GROUP BY`?", ["WHERE", "HAVING", "ORDER BY", "JOIN"])
                        st.write("")
                        
                        btn_enviar = st.form_submit_button("Submeter Respostas 📤")
                        if btn_enviar:
                            nota = 0
                            if q1 == "SELECT": nota += 50
                            if q2 == "HAVING": nota += 50
                            
                            db.salvar_score(user["nome"], "sql", nota)
                            user["score_sql"] = nota
                            st.session_state.modulo_ativo = None
                            st.success(f"Avaliação Concluída! Nota final registrada: {nota}/100")
                            st.rerun()

                elif modulo == "bi":
                    st.markdown("### 📊 Avaliação: Business Intelligence (BI)")
                    st.caption("Responda às questões abaixo com atenção. Cada questão vale 50 pontos.")
                    st.write("")
                    
                    with st.form("form_test_bi"):
                        q1 = st.radio("1) O que representa a sigla ETL na arquitetura de Data Warehousing?", ["Extract, Transform, Load", "Evaluate, Testing, Logic", "Export, Transfer, Link", "Execute, Track, Log"])
                        st.write("")
                        q2 = st.radio("2) Qual é o objetivo primário de um indicador chave de desempenho (KPI)?", ["Armazenar registros em banco", "Medir o progresso estratégico em direção a uma meta", "Executar rotinas em Python", "Criar interfaces web"])
                        st.write("")
                        
                        btn_enviar = st.form_submit_button("Submeter Respostas 📤")
                        if btn_enviar:
                            nota = 0
                            if q1 == "Extract, Transform, Load": nota += 50
                            if q2 == "Medir o progresso estratégico em direção a uma meta": nota += 50
                            
                            db.salvar_score(user["nome"], "bi", nota)
                            user["score_bi"] = nota
                            st.session_state.modulo_ativo = None
                            st.success(f"Avaliação Concluída! Nota final registrada: {nota}/100")
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
                st.write("")
                if st.button("⬅️ Cancelar e Voltar aos Módulos"):
                    st.session_state.modulo_ativo = None
                    st.rerun()

        # ABA 2: FEEDBACK CSAT
        with tab_feedback:
            col_f_left, col_f_right = st.columns([1.5, 1])
            
            with col_f_left:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("### Como está sendo sua jornada?")
                st.caption("Seu feedback é anônimo para os colegas, mas ajuda a gestão a evoluir a cultura e as ferramentas.")
                st.write("")
                
                avaliacao_csat = st.select_slider(
                    "Qual seu nível de satisfação hoje?",
                    options=["😡 Péssimo", "😕 Ruim", "😐 Indiferente", "🙂 Bom", "🤩 Incrível!"],
                    value="🙂 Bom"
                )
                
                st.write("")
                comentario_texto = st.text_area(
                    "Deixe seus comentários ou sugestões de melhoria:",
                    placeholder="Conte o que funcionou bem ou o que pode melhorar no seu dia a dia...",
                    height=140
                )
                
                st.write("")
                if st.button("Enviar Feedback ✨"):
                    if comentario_texto.strip():
                        db.salvar_feedback(user["nome"], avaliacao_csat, comentario_texto)
                        st.success("Obrigado! Seu feedback foi registrado com sucesso.")
                    else:
                        st.warning("Escreva uma breve mensagem antes de enviar.")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_f_right:
                st.markdown("""
                <div class="glass-card" style="background: rgba(99, 102, 241, 0.05); border-color: rgba(99, 102, 241, 0.2);">
                    <h4 style="color: #a5b4fc; margin-top: 0;">Por que seu feedback importa?</h4>
                    <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6;">
                        • <b>Melhoria Contínua:</b> Ajustamos a dificuldade das avaliações com base no seu retorno.<br><br>
                        • <b>Cultura de Transparência:</b> Dê voz aos seus desafios do dia a dia de trabalho.<br><br>
                        • <b>Evolução Direcionada:</b> Auxilia seus gestores a identificarem gargalos na equipe.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # PERFIL: GERENTE / CHEFE
    # ------------------------------------------
    else:
        tab_dashboard, tab_feedbacks_recebidos = st.tabs(["📊 Visão Geral de Performance", "💬 Feedbacks da Equipe"])

        with tab_dashboard:
            df_resultados = db.buscar_todos_resultados()
            
            # KPI CARDS DE TOPO
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.markdown(f"""
                <div class="glass-card" style="padding: 16px;">
                    <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">TOTAL COLABORADORES</span>
                    <h2 style="margin: 6px 0 0 0; font-size: 1.8rem; color: #818cf8;">{len(df_resultados)}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with kpi2:
                media_equipe = round(df_resultados['media_geral'].mean(), 1) if not df_resultados.empty else 0
                st.markdown(f"""
                <div class="glass-card" style="padding: 16px;">
                    <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">MÉDIA DA EQUIPE</span>
                    <h2 style="margin: 6px 0 0 0; font-size: 1.8rem; color: #34d399;">{media_equipe} <span style="font-size: 1rem;">/100</span></h2>
                </div>
                """, unsafe_allow_html=True)

            with kpi3:
                top_streak = df_resultados['streak'].max() if not df_resultados.empty else 0
                st.markdown(f"""
                <div class="glass-card" style="padding: 16px;">
                    <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">MAIOR OFENSIVA</span>
                    <h2 style="margin: 6px 0 0 0; font-size: 1.8rem; color: #fbbf24;">🔥 {top_streak} <span style="font-size: 1rem;">dias</span></h2>
                </div>
                """, unsafe_allow_html=True)

            with kpi4:
                df_f = db.buscar_feedbacks()
                st.markdown(f"""
                <div class="glass-card" style="padding: 16px;">
                    <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">FEEDBACKS RECEBIDOS</span>
                    <h2 style="margin: 6px 0 0 0; font-size: 1.8rem; color: #f472b6;">{len(df_f)}</h2>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown("### Ranking de Desempenho Técnico")
            
            # TABELA DE DESEMPENHO ESTILIZADA
            st.dataframe(
                df_resultados,
                column_config={
                    "nome": "Colaborador",
                    "perfil": "Perfil",
                    "setor": "Setor/Área",
                    "streak": st.column_config.NumberColumn("Ofensiva (Dias)", format="%d 🔥"),
                    "score_logic": st.column_config.ProgressColumn("Lógica", format="%d", min_value=0, max_value=100),
                    "score_sql": st.column_config.ProgressColumn("SQL", format="%d", min_value=0, max_value=100),
                    "score_bi": st.column_config.ProgressColumn("BI", format="%d", min_value=0, max_value=100),
                    "media_geral": st.column_config.NumberColumn("Média Geral", format="%.1f pts"),
                },
                use_container_width=True,
                hide_index=True
            )

        with tab_feedbacks_recebidos:
            st.markdown("### Feedbacks & Avaliações da Equipe")
            st.caption("Acompanhe o clima organizacional e sugestões enviadas pelos funcionários.")
            st.write("")
            
            df_feedbacks = db.buscar_feedbacks()
            
            if not df_feedbacks.empty:
                for idx, row in df_feedbacks.iterrows():
                    st.markdown(f"""
                    <div class="feedback-item">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-weight: 700; color: #e2e8f0;">👤 {row['Usuário']}</div>
                            <span style="background: rgba(255, 255, 255, 0.08); padding: 4px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 600;">{row['Avaliação']}</span>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0 0 8px 0; line-height: 1.5;">"{row['Comentário']}"</p>
                        <small style="color: #64748b;">Enviado em: {row['Data']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum feedback registrado no momento.")