import os
import json
import streamlit as st
import database as db
from google import genai

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

# Função da IA para ler e avaliar o Portfólio
def analisar_portfolio_ia(texto_portfolio):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.error("Chave API do Gemini não configurada na variável de ambiente GEMINI_API_KEY!")
        return None

    try:
        # Passando a chave diretamente ou via variável de ambiente
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Você é um avaliador técnico sênior em Tecnologia e Dados.
        Analise o portfólio/projetos descritos e atribua uma nota de 0 a 100 para três competências:
        1. Lógica de Programação (score_logic)
        2. Banco de Dados & SQL (score_sql)
        3. Business Intelligence (score_bi)

        Dê também um parecer bem resumido com a justificativa.

        Retorne EXCLUSIVAMENTE um objeto JSON estrito no seguinte formato:
        {{
            "score_logic": 85,
            "score_sql": 90,
            "score_bi": 70,
            "feedback": "Texto explicativo curto..."
        }}

        Portfólio / Projetos:
        {texto_portfolio}
        """

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )

        content = response.text.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(content)
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return None

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
            <div class="brand-icon-box">
                <span>⚡</span>
            </div>
            <h1 class="brand-title" style="margin: 0;">DataLogic Eval</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 8px; font-weight: 500;">Plataforma de Avaliação Contínua & Insights de Performance</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_cad = st.tabs(["🔑 Entrar no Sistema", "✨ Criar Nova Conta"])
        
        with tab_login:
            st.markdown("""
            <div class="welcome-box">
                💡 <b>Bem-vindo de volta!</b> Insira suas credenciais abaixo para acessar seus módulos e acompanhar sua evolução.
            </div>
            """, unsafe_allow_html=True)
            
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

        with tab_cad:
            st.markdown("""
            <div class="welcome-box">
                🚀 <b>Primeira vez por aqui?</b> Crie sua conta corporativa em poucos segundos e inicie suas avaliações.
            </div>
            """, unsafe_allow_html=True)
            
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

# ==========================================
# PAINEL PRINCIPAL (AUTENTICADO)
# ==========================================
else:
    user = st.session_state.usuario_logado
    
    # TOP BAR
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

        with tab_desafios:
            if st.session_state.modulo_ativo is None:
                st.markdown("### Seus Módulos de Aprendizado")
                st.caption("Complete os testes ou submeta seu portfólio para calcular sua nota via IA.")
                
                # AVALIAÇÃO VIA IA
                st.markdown('<div class="glass-card" style="margin-bottom: 24px;">', unsafe_allow_html=True)
                st.markdown("#### 🤖 Avaliação de Portfólio com IA")
                st.caption("Insira o resumo do seu portfólio, experiências ou links de projetos no GitHub/LinkedIn para receber notas automáticas.")
                
                portfolio_input = st.text_area(
                    "Portfólio / Projetos Realizados:",
                    placeholder="Cole aqui a descrição dos seus projetos técnicos em Lógica, SQL ou BI...",
                    height=90
                )
                
                if st.button("✨ Analisar Portfólio com Gemini IA"):
                    if portfolio_input.strip():
                        with st.spinner("Analisando competências técnicas com IA..."):
                            res = analisar_portfolio_ia(portfolio_input)
                            if res:
                                db.salvar_score(user["nome"], "logic", res["score_logic"])
                                db.salvar_score(user["nome"], "sql", res["score_sql"])
                                db.salvar_score(user["nome"], "bi", res["score_bi"])
                                
                                user["score_logic"] = res["score_logic"]
                                user["score_sql"] = res["score_sql"]
                                user["score_bi"] = res["score_bi"]
                                
                                st.success("Avaliação realizada!")
                                st.info(f"**Análise da IA:** {res['feedback']}")
                                st.rerun()
                    else:
                        st.warning("Cole a descrição do seu portfólio antes de solicitar a avaliação.")
                st.markdown('</div>', unsafe_allow_html=True)

                # CARDS DOS MÓDULOS
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    score_l = user['score_logic']
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

            else:
                modulo = st.session_state.modulo_ativo
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                if modulo == "logic":
                    st.markdown("### 🧠 Avaliação: Lógica de Programação")
                    with st.form("form_test_logic"):
                        q1 = st.radio("1) Qual o resultado da expressão em Python: `10 + 2 * 3`?", ["36", "16", "24", "15"])
                        q2 = st.radio("2) Qual estrutura é ideal para iterar repetidamente enquanto uma condição for verdadeira?", ["if / else", "for", "while", "switch"])
                        if st.form_submit_button("Submeter Respostas 📤"):
                            nota = (50 if q1 == "16" else 0) + (50 if q2 == "while" else 0)
                            db.salvar_score(user["nome"], "logic", nota)
                            user["score_logic"] = nota
                            st.session_state.modulo_ativo = None
                            st.rerun()

                elif modulo == "sql":
                    st.markdown("### 🗄️ Avaliação: Banco de Dados & SQL")
                    with st.form("form_test_sql"):
                        q1 = st.radio("1) Qual comando DML é utilizado para extrair dados?", ["UPDATE", "INSERT", "SELECT", "DELETE"])
                        q2 = st.radio("2) Qual cláusula filtra agrupamentos?", ["WHERE", "HAVING", "ORDER BY", "JOIN"])
                        if st.form_submit_button("Submeter Respostas 📤"):
                            nota = (50 if q1 == "SELECT" else 0) + (50 if q2 == "HAVING" else 0)
                            db.salvar_score(user["nome"], "sql", nota)
                            user["score_sql"] = nota
                            st.session_state.modulo_ativo = None
                            st.rerun()

                elif modulo == "bi":
                    st.markdown("### 📊 Avaliação: Business Intelligence (BI)")
                    with st.form("form_test_bi"):
                        q1 = st.radio("1) O que significa ETL?", ["Extract, Transform, Load", "Evaluate, Testing, Logic", "Export, Transfer, Link", "Execute, Track, Log"])
                        q2 = st.radio("2) Qual o papel de um KPI?", ["Armazenar registros em banco", "Medir o progresso estratégico em direção a uma meta", "Executar rotinas Python", "Criar interfaces web"])
                        if st.form_submit_button("Submeter Respostas 📤"):
                            nota = (50 if q1 == "Extract, Transform, Load" else 0) + (50 if q2 == "Medir o progresso estratégico em direção a uma meta" else 0)
                            db.salvar_score(user["nome"], "bi", nota)
                            user["score_bi"] = nota
                            st.session_state.modulo_ativo = None
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
                st.write("")
                if st.button("⬅️ Cancelar"):
                    st.session_state.modulo_ativo = None
                    st.rerun()

        # ABA CSAT
        with tab_feedback:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Como está sendo sua jornada?")
            avaliacao_csat = st.select_slider("Qual seu nível de satisfação hoje?", options=["😡 Péssimo", "😕 Ruim", "😐 Indiferente", "🙂 Bom", "🤩 Incrível!"], value="🙂 Bom")
            comentario_texto = st.text_area("Deixe seu comentário:", height=120)
            if st.button("Enviar Feedback ✨"):
                if comentario_texto.strip():
                    db.salvar_feedback(user["nome"], avaliacao_csat, comentario_texto)
                    st.success("Feedback registrado com sucesso!")
                else:
                    st.warning("Preencha o comentário.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # PERFIL: CHEFE
    # ------------------------------------------
    else:
        tab_dashboard, tab_feedbacks_recebidos = st.tabs(["📊 Visão Geral de Performance", "💬 Feedbacks da Equipe"])

        with tab_dashboard:
            df_resultados = db.buscar_todos_resultados()
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.markdown(f'<div class="glass-card" style="padding:16px;"><span style="color:#94a3b8;font-size:0.8rem;">COLABORADORES</span><h2 style="margin:6px 0 0 0;color:#818cf8;">{len(df_resultados)}</h2></div>', unsafe_allow_html=True)
            with kpi2:
                media_equipe = round(df_resultados['media_geral'].mean(), 1) if not df_resultados.empty else 0
                st.markdown(f'<div class="glass-card" style="padding:16px;"><span style="color:#94a3b8;font-size:0.8rem;">MÉDIA DA EQUIPE</span><h2 style="margin:6px 0 0 0;color:#34d399;">{media_equipe}</h2></div>', unsafe_allow_html=True)
            with kpi3:
                top_streak = df_resultados['streak'].max() if not df_resultados.empty else 0
                st.markdown(f'<div class="glass-card" style="padding:16px;"><span style="color:#94a3b8;font-size:0.8rem;">MAIOR OFENSIVA</span><h2 style="margin:6px 0 0 0;color:#fbbf24;">🔥 {top_streak}d</h2></div>', unsafe_allow_html=True)
            with kpi4:
                df_f = db.buscar_feedbacks()
                st.markdown(f'<div class="glass-card" style="padding:16px;"><span style="color:#94a3b8;font-size:0.8rem;">FEEDBACKS</span><h2 style="margin:6px 0 0 0;color:#f472b6;">{len(df_f)}</h2></div>', unsafe_allow_html=True)

            st.write("")
            st.dataframe(
                df_resultados,
                column_config={
                    "nome": "Colaborador",
                    "perfil": "Perfil",
                    "setor": "Setor",
                    "streak": st.column_config.NumberColumn("Ofensiva", format="%d 🔥"),
                    "score_logic": st.column_config.ProgressColumn("Lógica", format="%d", min_value=0, max_value=100),
                    "score_sql": st.column_config.ProgressColumn("SQL", format="%d", min_value=0, max_value=100),
                    "score_bi": st.column_config.ProgressColumn("BI", format="%d", min_value=0, max_value=100),
                    "media_geral": st.column_config.NumberColumn("Média Geral", format="%.1f pts"),
                },
                use_container_width=True,
                hide_index=True
            )

        with tab_feedbacks_recebidos:
            df_feedbacks = db.buscar_feedbacks()
            if not df_feedbacks.empty:
                for idx, row in df_feedbacks.iterrows():
                    st.markdown(f"""
                    <div class="feedback-item">
                        <div style="display: flex; justify-content: space-between;">
                            <b>👤 {row['Usuário']}</b>
                            <span>{row['Avaliação']}</span>
                        </div>
                        <p style="margin: 8px 0; color: #cbd5e1;">"{row['Comentário']}"</p>
                        <small style="color: #64748b;">{row['Data']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum feedback disponível.")