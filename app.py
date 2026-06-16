import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta
import calendar

# =========================================================
# CAPITAL CRED ONLINE - SUPABASE
# Login Pedro: Pedro / pedro12
# =========================================================

st.set_page_config(page_title="CRED - Online", layout="wide")

SUPABASE_URL = "https://uyklbdzjqhxmdgjdppcs.supabase.co"
SUPABASE_KEY = "sb_publishable_5sWqJesHJGnEJcMVhovetg_9Qj3XSDa"
TABELA = "emprestimos"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

USUARIOS = {
    "Pedro": {"senha": "pedro12", "nome": "Pedro Henrick", "grupo": "pedro"},
}

COLUNAS = [
    "id", "usuario_grupo", "Cliente", "Descricao", "Valor Emprestado",
    "Porcentagem Juros (%)", "Juros Aplicado", "Modalidade", "Periodicidade",
    "Prazo Meses", "Data Emprestimo", "Data Vencimento", "Status"
]

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at top left,#1b1404 0%,#080808 38%,#020202 100%);color:white;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#090909 0%,#111111 100%);border-right:2px solid #D4AF37;}
h1,h2,h3{color:#D4AF37!important}.block-container{padding-top:2rem}.stButton>button{background:linear-gradient(90deg,#D4AF37,#F0C95A);color:black;border:none;border-radius:10px;font-weight:800}.stButton>button:hover{background:#FFD76A;color:black}.brand-box{text-align:center;padding:22px 0 12px 0}.brand-name{color:#D4AF37;font-family:Georgia,'Times New Roman',serif;font-size:46px;font-weight:900;letter-spacing:5px;white-space:nowrap;text-shadow:0 0 20px rgba(212,175,55,.7)}.brand-line{height:1px;width:80%;margin:12px auto;background:linear-gradient(90deg,transparent,#D4AF37,transparent)}.user-box{display:flex;align-items:center;gap:12px;padding:12px 10px;border:1px solid rgba(212,175,55,.55);border-radius:14px;background:rgba(27,27,27,.75);box-shadow:0 0 12px rgba(212,175,55,.16);margin-bottom:15px}.user-avatar{width:46px;height:46px;border-radius:50%;border:2px solid #D4AF37;display:flex;align-items:center;justify-content:center;color:#D4AF37;font-size:24px}.user-name{color:white;font-size:17px;font-weight:900}.user-status{color:#00FF66;font-size:13px;font-weight:700}.metric-card{background:linear-gradient(145deg,rgba(28,28,28,.95),rgba(9,9,9,.95));border:1px solid rgba(212,175,55,.85);border-radius:18px;padding:18px;min-height:118px;box-shadow:0 0 18px rgba(212,175,55,.18)}.metric-icon{color:#D4AF37;font-size:28px;margin-bottom:8px}.metric-label{color:white;font-size:15px;font-weight:700}.metric-value{color:white;font-size:22px;font-weight:900;line-height:1.15}.loan-card{background:linear-gradient(145deg,rgba(30,30,30,.95),rgba(8,8,8,.95));border:1px solid rgba(212,175,55,.55);border-radius:18px;padding:18px;min-height:250px;box-shadow:0 0 18px rgba(212,175,55,.12);margin-bottom:18px}.loan-title{color:white;font-size:20px;font-weight:900}.loan-sub{color:#BBBBBB;font-size:13px}.loan-value{color:white;font-size:28px;font-weight:900;margin-top:10px}.badge-green,.badge-yellow,.badge-red{border-radius:20px;padding:4px 10px;font-size:12px;font-weight:900}.badge-green{color:#00FF8A;border:1px solid #00FF8A}.badge-yellow{color:#FFD44D;border:1px solid #FFD44D}.badge-red{color:#FF4D4D;border:1px solid #FF4D4D}.progress-bg{width:100%;background:#252525;border-radius:10px;height:8px;margin-top:12px}.progress-fill{background:linear-gradient(90deg,#D4AF37,#00FF8A);height:8px;border-radius:10px}.info-card{background:rgba(27,27,27,.86);border:1px solid rgba(212,175,55,.55);border-radius:16px;padding:16px;margin-bottom:14px;box-shadow:0 0 14px rgba(212,175,55,.18)}.info-title{color:#D4AF37;font-size:20px;font-weight:900;margin-bottom:10px}.info-line{color:white;font-size:16px;line-height:1.6}.footer-box{color:#AAAAAA;font-size:13px;margin-top:25px;padding-top:15px;border-top:1px solid rgba(212,175,55,.25)}
</style>
""", unsafe_allow_html=True)


def dinheiro(valor):
    texto = f"R$ {float(valor):,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def api_url():
    return f"{SUPABASE_URL}/rest/v1/{TABELA}"


def carregar_dados():
    grupo = st.session_state.get("usuario_grupo", "pedro")
    params = {
        "select": "*",
        "usuario_grupo": f"eq.{grupo}",
        "order": "created_at.desc"
    }
    r = requests.get(api_url(), headers=HEADERS, params=params, timeout=20)
    if r.status_code >= 300:
        st.error(f"Erro ao buscar dados no Supabase: {r.text}")
        return pd.DataFrame(columns=COLUNAS)
    dados = r.json()
    if not dados:
        return pd.DataFrame(columns=COLUNAS)
    df = pd.DataFrame(dados)
    mapa = {
        "cliente": "Cliente",
        "descricao": "Descricao",
        "valor_emprestado": "Valor Emprestado",
        "porcentagem_juros": "Porcentagem Juros (%)",
        "juros_aplicado": "Juros Aplicado",
        "modalidade": "Modalidade",
        "periodicidade": "Periodicidade",
        "prazo_meses": "Prazo Meses",
        "data_emprestimo": "Data Emprestimo",
        "data_vencimento": "Data Vencimento",
        "status": "Status",
    }
    df = df.rename(columns=mapa)
    for col in COLUNAS:
        if col not in df.columns:
            df[col] = ""
    if not df.empty:
        df["Valor Emprestado"] = pd.to_numeric(df["Valor Emprestado"], errors="coerce").fillna(0.0)
        df["Porcentagem Juros (%)"] = pd.to_numeric(df["Porcentagem Juros (%)"], errors="coerce").fillna(40.0)
        df["Prazo Meses"] = pd.to_numeric(df["Prazo Meses"], errors="coerce").fillna(1).astype(int)
        df["Data Emprestimo"] = pd.to_datetime(df["Data Emprestimo"], errors="coerce").dt.date
        df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], errors="coerce").dt.date
        df["Status"] = df["Status"].fillna("Pendente")
        df["Descricao"] = df["Descricao"].fillna("Empréstimo")
        df["Juros Aplicado"] = df["Juros Aplicado"].fillna("Sobre Total")
        df["Modalidade"] = df["Modalidade"].fillna("Pag. Único")
        df["Periodicidade"] = df["Periodicidade"].fillna("Mensal")
    return recalcular(df[COLUNAS])


def linha_para_supabase(row):
    return {
        "usuario_grupo": st.session_state.get("usuario_grupo", "pedro"),
        "cliente": str(row.get("Cliente", "")).strip(),
        "descricao": str(row.get("Descricao", "Empréstimo")).strip() or "Empréstimo",
        "valor_emprestado": float(row.get("Valor Emprestado", 0) or 0),
        "porcentagem_juros": float(row.get("Porcentagem Juros (%)", 40) or 40),
        "juros_aplicado": str(row.get("Juros Aplicado", "Sobre Total")),
        "modalidade": str(row.get("Modalidade", "Pag. Único")),
        "periodicidade": str(row.get("Periodicidade", "Mensal")),
        "prazo_meses": int(row.get("Prazo Meses", 1) or 1),
        "data_emprestimo": str(row.get("Data Emprestimo", date.today())),
        "data_vencimento": str(row.get("Data Vencimento", date.today() + timedelta(days=30))),
        "status": str(row.get("Status", "Pendente")),
    }


def inserir(row):
    r = requests.post(api_url(), headers=HEADERS, json=linha_para_supabase(row), timeout=20)
    if r.status_code >= 300:
        st.error(f"Erro ao salvar no Supabase: {r.text}")
        return False
    return True


def atualizar(id_registro, row):
    url = f"{api_url()}?id=eq.{id_registro}"
    r = requests.patch(url, headers=HEADERS, json=linha_para_supabase(row), timeout=20)
    if r.status_code >= 300:
        st.error(f"Erro ao atualizar no Supabase: {r.text}")
        return False
    return True


def excluir(id_registro):
    url = f"{api_url()}?id=eq.{id_registro}"
    r = requests.delete(url, headers=HEADERS, timeout=20)
    if r.status_code >= 300:
        st.error(f"Erro ao excluir no Supabase: {r.text}")
        return False
    return True


def recalcular(df):
    if df.empty:
        return df.copy()
    novo = df.copy()
    novo["Lucro"] = novo["Valor Emprestado"] * (novo["Porcentagem Juros (%)"] / 100)
    novo["Valor Total"] = novo["Valor Emprestado"] + novo["Lucro"]
    return novo


def adicionar_meses(data_base, meses):
    mes = data_base.month - 1 + int(meses)
    ano = data_base.year + mes // 12
    mes = mes % 12 + 1
    dia = min(data_base.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def preparar_exibicao(df_base):
    tabela = df_base.copy()
    for c in ["Data Emprestimo", "Data Vencimento"]:
        if c in tabela.columns:
            tabela[c] = pd.to_datetime(tabela[c], errors="coerce").dt.strftime("%d/%m/%Y")
    return tabela.drop(columns=["id", "usuario_grupo"], errors="ignore")


def card(titulo, valor, icone):
    st.markdown(f"""<div class="metric-card"><div class="metric-icon">{icone}</div><div class="metric-label">{titulo}</div><div class="metric-value">{valor}</div></div>""", unsafe_allow_html=True)


def info_card(titulo, linhas):
    conteudo = "".join([f"<div class='info-line'>{linha}</div>" for linha in linhas])
    st.markdown(f"<div class='info-card'><div class='info-title'>{titulo}</div>{conteudo}</div>", unsafe_allow_html=True)


def selecionar_data(titulo, valor_padrao, chave):
    if pd.isna(valor_padrao):
        valor_padrao = date.today()
    valor_padrao = pd.to_datetime(valor_padrao).date()
    st.markdown(f"**{titulo}**")
    anos = list(range(date.today().year - 2, date.today().year + 6))
    dias = list(range(1, 32))
    dia = st.selectbox("Dia", dias, index=valor_padrao.day - 1, key=f"{chave}_dia")
    mes_nome = st.selectbox("Mês", MESES, index=valor_padrao.month - 1, key=f"{chave}_mes")
    ano = st.selectbox("Ano", anos, index=anos.index(valor_padrao.year) if valor_padrao.year in anos else 2, key=f"{chave}_ano")
    mes = MESES.index(mes_nome) + 1
    dia = min(dia, calendar.monthrange(ano, mes)[1])
    st.caption(f"Selecionado: {dia:02d}/{mes:02d}/{ano}")
    return date(ano, mes, dia)


def montar_cobrancas_amanha(df_base, hoje):
    pendentes = df_base[df_base["Status"] == "Pendente"].copy()
    if pendentes.empty:
        return []
    pendentes["Dias Restantes"] = (pd.to_datetime(pendentes["Data Vencimento"]) - pd.to_datetime(hoje)).dt.days
    amanha = pendentes[pendentes["Dias Restantes"] == 1].copy().sort_values("Data Vencimento").head(10)
    return [f"🔔 <b>Amanhã</b>: {r['Cliente']} - {dinheiro(r['Valor Total'])}" for _, r in amanha.iterrows()]


def card_emprestimo(row):
    hoje_local = date.today()
    venc = pd.to_datetime(row["Data Vencimento"]).date()
    dias = (venc - hoje_local).days
    if row["Status"] == "Pago":
        badge = "<span class='badge-green'>QUITADO</span>"; situacao = "Quitado"; progresso = 100
    elif dias < 0:
        badge = "<span class='badge-red'>EM ATRASO</span>"; situacao = f"Atrasado há {abs(dias)} dia(s)"; progresso = 100
    elif dias == 0:
        badge = "<span class='badge-yellow'>VENCE HOJE</span>"; situacao = "Vence hoje"; progresso = 75
    else:
        badge = "<span class='badge-green'>EM DIA</span>"; situacao = f"Próximo: {venc.strftime('%d/%m')}"; progresso = 25
    st.markdown(f"""
    <div class="loan-card"><div style="display:flex;justify-content:space-between;align-items:start;"><div><div class="loan-title">{row['Cliente']}</div><div class="loan-sub">{row['Descricao']}</div></div><div>{badge}</div></div><div style="margin-top:12px;"><span class="badge-yellow">PRICE</span> <span class="badge-yellow">{float(row['Porcentagem Juros (%)']):.1f}% a.m.</span></div><div class="loan-sub" style="margin-top:14px;">SALDO DEVEDOR</div><div class="loan-value">{dinheiro(row['Valor Total'])}</div><div class="loan-sub">Principal: {dinheiro(row['Valor Emprestado'])}</div><div class="progress-bg"><div class="progress-fill" style="width:{progresso}%;"></div></div><div class="loan-sub" style="margin-top:10px;">✅ {situacao}</div></div>
    """, unsafe_allow_html=True)


# LOGIN
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.markdown("## 🔐 Login CRED Online")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in USUARIOS and senha == USUARIOS[usuario]["senha"]:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["usuario_nome"] = USUARIOS[usuario]["nome"]
            st.session_state["usuario_grupo"] = USUARIOS[usuario]["grupo"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# SIDEBAR
st.sidebar.markdown(f"""
<div class="brand-box"><div class="brand-name">CRED</div><div class="brand-line"></div></div>
<div class="user-box"><div class="user-avatar">👤</div><div><div class="user-name">{st.session_state.get('usuario_nome','Conta')}</div><div class="user-status">● 🚀 PEDRO ONLINE</div></div></div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.rerun()

menu = st.sidebar.radio("Menu", ["Painel", "Empréstimos", "Novo Empréstimo", "Editar / Remover / Excluir"])

df = carregar_dados()
hoje = date.today()

if menu == "Novo Empréstimo":
    st.title("➕ Novo Empréstimo")
    aba1, aba2, aba3 = st.tabs(["1️⃣ Contrato", "2️⃣ Configurações", "3️⃣ Extras"])
    with aba1:
        st.subheader("Contrato")
        cliente_opcoes = ["Novo cliente"] + (df["Cliente"].dropna().unique().tolist() if not df.empty else [])
        cliente = st.selectbox("Cliente", cliente_opcoes)
        nome = st.text_input("Nome do Cliente") if cliente == "Novo cliente" else cliente
        descricao = st.text_input("Descrição", placeholder="Ex: Capital de Giro")
        valor = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=100.0)
        taxa = st.number_input("Taxa % a.m.", min_value=0.0, value=40.0, step=1.0)
        juros_aplicado = st.radio("Juros Aplicado", ["Por Parcela", "Sobre Total", "Compostos"], horizontal=True)
    with aba2:
        st.subheader("Configurações")
        modalidade = st.radio("Modalidade", ["Parcelado", "Pag. Único", "Americano"], horizontal=True)
        periodicidade = st.radio("Periodicidade das Parcelas", ["Mensal", "Quinzenal", "Semanal", "Diário"], horizontal=True)
        prazo = st.number_input("Prazo (meses)", min_value=1, value=1, step=1)
        data_inicio = selecionar_data("Data de Início", hoje, "novo_inicio")
        if periodicidade == "Mensal":
            data_vencimento = adicionar_meses(data_inicio, prazo)
        else:
            dias_periodo = {"Quinzenal": 15, "Semanal": 7, "Diário": 1}.get(periodicidade, 30)
            data_vencimento = data_inicio + timedelta(days=dias_periodo * int(prazo))
    with aba3:
        st.subheader("Resumo do Contrato")
        lucro_previsto = valor * (taxa / 100)
        total_receber = valor + lucro_previsto
        c1, c2, c3 = st.columns(3)
        with c1: card("Parcela", dinheiro(total_receber / max(1, prazo)), "💳")
        with c2: card("Juros total", dinheiro(lucro_previsto), "📈")
        with c3: card("Total a receber", dinheiro(total_receber), "💰")
        st.write(f"Data de vencimento: **{data_vencimento.strftime('%d/%m/%Y')}**")
        if st.button("💾 Salvar Empréstimo"):
            if not nome.strip(): st.error("Digite o nome do cliente.")
            elif valor <= 0: st.error("Digite um valor maior que zero.")
            else:
                row = {"Cliente": nome.strip(), "Descricao": descricao.strip() if descricao.strip() else "Empréstimo", "Valor Emprestado": valor, "Porcentagem Juros (%)": taxa, "Juros Aplicado": juros_aplicado, "Modalidade": modalidade, "Periodicidade": periodicidade, "Prazo Meses": prazo, "Data Emprestimo": data_inicio, "Data Vencimento": data_vencimento, "Status": "Pendente"}
                if inserir(row):
                    st.success("Empréstimo salvo online com sucesso!")
                    st.rerun()

elif menu == "Editar / Remover / Excluir":
    st.title("⚙️ Editar Empréstimo")
    if df.empty:
        st.info("Nenhum cliente cadastrado.")
    else:
        cliente = st.selectbox("Escolha o cliente", df["Cliente"].tolist())
        idx = df[df["Cliente"] == cliente].index[0]
        nome = st.text_input("Nome do Cliente", value=str(df.at[idx, "Cliente"]))
        descricao = st.text_input("Descrição", value=str(df.at[idx, "Descricao"]))
        valor = st.number_input("Valor Emprestado", min_value=0.0, value=float(df.at[idx, "Valor Emprestado"]), step=100.0)
        juros = st.number_input("Juros (%)", min_value=0.0, value=float(df.at[idx, "Porcentagem Juros (%)"]), step=1.0)
        data_emp = selecionar_data("📅 Data do Empréstimo", df.at[idx, "Data Emprestimo"], "edit_emp")
        data_venc = selecionar_data("📅 Data de Vencimento", df.at[idx, "Data Vencimento"], "edit_venc")
        status = st.selectbox("Status", ["Pendente", "Pago"], index=0 if str(df.at[idx, "Status"]) != "Pago" else 1)
        id_registro = df.at[idx, "id"]
        colA, colB, colC, colD = st.columns(4)
        row = {"Cliente": nome.strip(), "Descricao": descricao.strip(), "Valor Emprestado": valor, "Porcentagem Juros (%)": juros, "Juros Aplicado": df.at[idx, "Juros Aplicado"], "Modalidade": df.at[idx, "Modalidade"], "Periodicidade": df.at[idx, "Periodicidade"], "Prazo Meses": df.at[idx, "Prazo Meses"], "Data Emprestimo": data_emp, "Data Vencimento": data_venc, "Status": status}
        with colA:
            if st.button("💾 Salvar Alterações") and atualizar(id_registro, row): st.success("Alterações salvas online!"); st.rerun()
        with colB:
            if st.button("💵 Só Pagou os Juros (+30 dias)"):
                row["Data Vencimento"] = pd.to_datetime(df.at[idx, "Data Vencimento"]).date() + timedelta(days=30)
                row["Status"] = "Pendente"
                if atualizar(id_registro, row): st.success("Vencimento renovado +30 dias."); st.rerun()
        with colC:
            if st.button("✅ Receber Total"):
                row["Status"] = "Pago"
                if atualizar(id_registro, row): st.success("Empréstimo marcado como pago."); st.rerun()
        with colD:
            if st.button("🗑️ Excluir") and excluir(id_registro): st.warning("Excluído."); st.rerun()

else:
    st.title("📊 CRED" if menu == "Painel" else "💼 Empréstimos")
    if df.empty:
        st.info("Nenhum empréstimo cadastrado ainda.")
    else:
        total_emp = df["Valor Emprestado"].sum(); total_lucro = df["Lucro"].sum(); total_geral = df["Valor Total"].sum()
        atrasados = df[(df["Data Vencimento"] < hoje) & (df["Status"] == "Pendente")]
        cobrancas = df[(df["Data Vencimento"] == hoje) & (df["Status"] == "Pendente")]
        clientes_em_dia = df[(df["Data Vencimento"] > hoje) & (df["Status"] == "Pendente")]
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: card("Clientes", len(df), "👥")
        with c2: card("Emprestado", dinheiro(total_emp), "💰")
        with c3: card("Lucro", dinheiro(total_lucro), "📊")
        with c4: card("Total", dinheiro(total_geral), "🪙")
        with c5: card("Atrasados", len(atrasados), "⏰")
        st.markdown("---")
        info_card("📊 Resumo Inteligente", [f"🟢 Clientes em dia: <b>{len(clientes_em_dia)}</b>", f"🟡 Cobranças hoje: <b>{len(cobrancas)}</b>", f"🔴 Clientes atrasados: <b>{len(atrasados)}</b>", f"💰 Valor total em atraso: <b>{dinheiro(atrasados['Valor Total'].sum() if not atrasados.empty else 0)}</b>"])
        amanha = montar_cobrancas_amanha(df, hoje)
        info_card("📅 Cobranças de Amanhã", amanha if amanha else ["✅ Nenhuma cobrança para amanhã."])
        st.subheader("🔔 Cobranças do Dia")
        if cobrancas.empty:
            st.success("✅ Nenhuma cobrança para hoje.")
        else:
            st.dataframe(preparar_exibicao(cobrancas), use_container_width=True)
        st.subheader("⏰ Atrasados")
        if atrasados.empty:
            st.success("✅ Nenhum cliente atrasado.")
        else:
            st.dataframe(preparar_exibicao(atrasados), use_container_width=True)
        st.subheader("🔎 Buscar e Filtrar")
        busca = st.text_input("Buscar por cliente ou descrição")
        filtro_status = st.selectbox("Filtrar por situação", ["Todos", "Pendente", "Pago", "Atrasado", "Cobrança Hoje", "Em dia"])
        tabela = df.copy()
        if busca:
            tabela = tabela[tabela["Cliente"].str.contains(busca, case=False, na=False) | tabela["Descricao"].str.contains(busca, case=False, na=False)]
        if filtro_status == "Pendente": tabela = tabela[tabela["Status"] == "Pendente"]
        elif filtro_status == "Pago": tabela = tabela[tabela["Status"] == "Pago"]
        elif filtro_status == "Atrasado": tabela = tabela[(tabela["Data Vencimento"] < hoje) & (tabela["Status"] == "Pendente")]
        elif filtro_status == "Cobrança Hoje": tabela = tabela[(tabela["Data Vencimento"] == hoje) & (tabela["Status"] == "Pendente")]
        elif filtro_status == "Em dia": tabela = tabela[(tabela["Data Vencimento"] > hoje) & (tabela["Status"] == "Pendente")]
        if menu == "Empréstimos":
            cols = st.columns(3)
            for i, (_, row) in enumerate(tabela.iterrows()):
                with cols[i % 3]: card_emprestimo(row)
        else:
            st.dataframe(preparar_exibicao(tabela), use_container_width=True)
        graf = pd.DataFrame({"Categoria":["Emprestado","Lucro","Total"],"Valor":[total_emp,total_lucro,total_geral]})
        fig = px.bar(graf, x="Categoria", y="Valor", text="Valor", color="Categoria", color_discrete_sequence=["#D4AF37", "#B8860B", "#FFD700"])
        fig.update_layout(paper_bgcolor="#0B0B0B", plot_bgcolor="#0B0B0B", font_color="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("""<div class="footer-box">🛡️ Sistema CRED Online<br>Preto & Dourado</div>""", unsafe_allow_html=True)
