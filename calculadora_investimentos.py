import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Calculadora de Investimentos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid #e9ecef;
        text-align: center;
        height: 100%;
    }
    .metric-label {
        font-size: 12px;
        color: #6c757d;
        margin-bottom: 4px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 600;
        color: #212529;
        margin: 0;
    }
    .metric-value.green { color: #1D9E75; }
    .metric-value.blue  { color: #3266ad; }
    .metric-value.red   { color: #E24B4A; }
    .section-title {
        font-size: 11px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    div[data-testid="stNumberInput"] input { font-size: 14px; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: white; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; font-size: 13px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: #3266ad !important; color: white !important; }
    h1 { font-size: 24px !important; font-weight: 600 !important; }
    .stNumberInput label { font-size: 13px; color: #495057; }
</style>
""", unsafe_allow_html=True)

COLORS = {
    "blue":   "#3266ad",
    "green":  "#1D9E75",
    "red":    "#E24B4A",
    "purple": "#534AB7",
    "gray":   "#888780",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#495057"),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=False, linecolor="#dee2e6"),
    yaxis=dict(gridcolor="#f1f3f5", linecolor="#dee2e6"),
)

def fmt(v):
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def card(label, value, color=""):
    color_class = f" {color}" if color else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <p class="metric-value{color_class}">{value}</p>
    </div>"""

def render_cards(items):
    cols = st.columns(len(items))
    for col, (label, value, color) in zip(cols, items):
        with col:
            st.markdown(card(label, value, color), unsafe_allow_html=True)

st.title("📈 Calculadora de Investimentos")
st.markdown("<p style='color:#6c757d;font-size:14px;margin-top:-8px'>Projeções interativas · Acumulação · Desacumulação · Aposentadoria</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Projeção com Aportes",
    "💰 Aporte Único",
    "🎯 Meta de Patrimônio",
    "🏖️ Aposentadoria",
])


with tab1:
    st.markdown("#### Parâmetros")
    c1, c2 = st.columns([1, 1])
    with c1:
        a_ini  = st.number_input("Capital inicial (R$)", min_value=0, value=10000, step=10, key="a_ini")
        a_pmt  = st.number_input("Aporte mensal (R$)", min_value=0, value=1000, step=10, key="a_pmt")
        a_taxa = st.number_input("Rentabilidade anual (%)", min_value=0.0, value=12.0, step=0.1, format="%.1f", key="a_taxa")
        a_anos = st.number_input("Prazo (anos)", min_value=1, max_value=50, value=20, step=1, key="a_anos")
        a_inf  = st.number_input("Inflação anual (%)", min_value=0.0, value=5.0, step=0.1, format="%.1f", key="a_inf")

    rm = (1 + a_taxa/100)**(1/12) - 1
    labels, d_nom, d_inv, d_real = [], [], [], []
    pat, inv = float(a_ini), float(a_ini)
    for m in range(int(a_anos)*12 + 1):
        if m > 0:
            pat = pat * (1 + rm) + a_pmt
            inv += a_pmt
        if m % 12 == 0:
            yr = m // 12
            labels.append("Hoje" if yr == 0 else f"Ano {yr}")
            d_nom.append(round(pat))
            d_inv.append(round(inv))
            d_real.append(round(pat / (1 + a_inf/100)**yr))

    tot, real_v, inv_v = d_nom[-1], d_real[-1], d_inv[-1]
    jur = tot - inv_v

    with c2:
        st.markdown("<div class='section-title'>Resultado projetado</div>", unsafe_allow_html=True)
        render_cards([
            ("Patrimônio nominal", fmt(tot), "blue"),
            ("Patrimônio real (inflação)", fmt(real_v), ""),
        ])
        st.markdown("")
        render_cards([
            ("Total investido", fmt(inv_v), ""),
            ("Juros gerados", fmt(jur), "green"),
        ])

    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=d_nom, name="Patrimônio nominal",
        fill="tozeroy", line=dict(color=COLORS["blue"], width=2),
        fillcolor="rgba(50,102,173,0.12)", hovertemplate="<b>%{x}</b><br>Nominal: R$ %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=labels, y=d_inv, name="Total investido",
        fill="tozeroy", line=dict(color=COLORS["green"], width=2, dash="dash"),
        fillcolor="rgba(29,158,117,0.08)", hovertemplate="Investido: R$ %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=labels, y=d_real, name="Patrimônio real",
        line=dict(color=COLORS["red"], width=1.5, dash="dot"),
        hovertemplate="Real: R$ %{y:,.0f}<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT, title="Evolução do patrimônio ao longo do tempo",
        yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f", height=380)
    st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.markdown("#### Parâmetros")
    c1, c2 = st.columns([1, 1])
    with c1:
        u_val  = st.number_input("Valor do aporte único (R$)", min_value=0, value=50000, step=10, key="u_val")
        u_taxa = st.number_input("Rentabilidade anual (%)", min_value=0.0, value=12.0, step=0.1, format="%.1f", key="u_taxa")
        u_anos = st.number_input("Prazo (anos)", min_value=1, max_value=50, value=20, step=1, key="u_anos")
        u_inf  = st.number_input("Inflação anual (%)", min_value=0.0, value=5.0, step=0.1, format="%.1f", key="u_inf")

    labels_u, d_n, d_r = [], [], []
    for yr in range(int(u_anos) + 1):
        labels_u.append("Hoje" if yr == 0 else f"Ano {yr}")
        nom = round(u_val * (1 + u_taxa/100)**yr)
        real = round(nom / (1 + u_inf/100)**yr)
        d_n.append(nom); d_r.append(real)

    fin = d_n[-1]
    mult = fin / u_val if u_val > 0 else 0

    with c2:
        st.markdown("<div class='section-title'>Resultado projetado</div>", unsafe_allow_html=True)
        render_cards([
            ("Patrimônio nominal", fmt(fin), "blue"),
            ("Patrimônio real (inflação)", fmt(d_r[-1]), ""),
        ])
        st.markdown("")
        render_cards([
            ("Capital inicial", fmt(u_val), ""),
            ("Multiplicador", f"{mult:.1f}×", "green"),
        ])

    st.markdown("---")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=labels_u, y=d_n, name="Nominal",
        fill="tozeroy", line=dict(color=COLORS["purple"], width=2),
        fillcolor="rgba(83,74,183,0.12)", hovertemplate="<b>%{x}</b><br>Nominal: R$ %{y:,.0f}<extra></extra>"))
    fig2.add_trace(go.Scatter(x=labels_u, y=d_r, name="Real (inflação)",
        line=dict(color=COLORS["red"], width=1.5, dash="dot"),
        hovertemplate="Real: R$ %{y:,.0f}<extra></extra>"))
    fig2.update_layout(**PLOTLY_LAYOUT, title="Crescimento do aporte único",
        yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f", height=360)
    st.plotly_chart(fig2, use_container_width=True)


with tab3:
    st.markdown("#### Parâmetros")
    c1, c2 = st.columns([1, 1])
    with c1:
        m_meta = st.number_input("Meta de patrimônio (R$)", min_value=0, value=1000000, step=10, key="m_meta")
        m_ini  = st.number_input("Capital inicial (R$)", min_value=0, value=10000, step=10, key="m_ini")
        m_taxa = st.number_input("Rentabilidade anual (%)", min_value=0.0, value=12.0, step=0.1, format="%.1f", key="m_taxa")
        m_anos = st.number_input("Prazo desejado (anos)", min_value=1, max_value=50, value=15, step=1, key="m_anos")

    rm_m = (1 + m_taxa/100)**(1/12) - 1
    n_m  = int(m_anos) * 12
    fv_c0 = m_ini * (1 + rm_m)**n_m
    pmt_m = max(0, (m_meta - fv_c0) * rm_m / ((1 + rm_m)**n_m - 1)) if rm_m > 0 else max(0, (m_meta - fv_c0) / n_m)
    tinv  = m_ini + pmt_m * n_m
    jur_m = max(0, m_meta - tinv)
    pct_m = round(jur_m / m_meta * 100) if m_meta > 0 else 0

    with c2:
        st.markdown("<div class='section-title'>Para atingir sua meta</div>", unsafe_allow_html=True)
        render_cards([
            ("Aporte mensal necessário", fmt(pmt_m), "blue"),
            ("Total a investir", fmt(tinv), ""),
        ])
        st.markdown("")
        render_cards([
            ("Juros que trabalham por você", fmt(jur_m), "green"),
            ("% da meta vindo dos juros", f"{pct_m}%", "green"),
        ])

    st.markdown("---")
    col_d, col_l = st.columns([1, 2])

    with col_d:
        st.markdown("**Composição do patrimônio final**")
        fig_d = go.Figure(go.Pie(
            labels=["Capital investido", "Juros acumulados"],
            values=[round(tinv), round(jur_m)],
            hole=0.62,
            marker=dict(colors=[COLORS["blue"], COLORS["green"]], line=dict(width=0)),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
            textinfo="percent",
            textfont=dict(size=12),
        ))
        fig_d.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(orientation="v", x=0.5, xanchor="center", y=-0.1, yanchor="top", font=dict(size=11)),
            margin=dict(l=0, r=0, t=20, b=40),
            height=280,
        )
        st.plotly_chart(fig_d, use_container_width=True)

    with col_l:
        st.markdown("**Evolução patrimonial — poder dos juros compostos**")
        lbl_m, dm_n, dm_i, dm_j = [], [], [], []
        pat_m, inv_m = float(m_ini), float(m_ini)
        for mm in range(n_m + 1):
            if mm > 0:
                pat_m = pat_m * (1 + rm_m) + pmt_m
                inv_m += pmt_m
            if mm % 12 == 0:
                yr = mm // 12
                lbl_m.append("Hoje" if yr == 0 else f"Ano {yr}")
                dm_n.append(round(pat_m))
                dm_i.append(round(inv_m))
                dm_j.append(round(max(0, pat_m - inv_m)))

        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=lbl_m, y=dm_n, name="Patrimônio nominal",
            fill="tozeroy", line=dict(color=COLORS["blue"], width=2),
            fillcolor="rgba(50,102,173,0.10)",
            hovertemplate="<b>%{x}</b><br>Nominal: R$ %{y:,.0f}<extra></extra>"))
        fig_l.add_trace(go.Scatter(x=lbl_m, y=dm_i, name="Total investido",
            fill="tozeroy", line=dict(color=COLORS["green"], width=2, dash="dash"),
            fillcolor="rgba(29,158,117,0.08)",
            hovertemplate="Investido: R$ %{y:,.0f}<extra></extra>"))
        fig_l.add_trace(go.Scatter(x=lbl_m, y=dm_j, name="Somente juros",
            line=dict(color=COLORS["red"], width=1.5, dash="dot"),
            hovertemplate="Juros: R$ %{y:,.0f}<extra></extra>"))
        fig_l.update_layout(**PLOTLY_LAYOUT, yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f", height=280,
            margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_l, use_container_width=True)


with tab4:
    st.markdown("#### Fase de acumulação")
    c1, c2 = st.columns([1, 1])
    with c1:
        ap_ini  = st.number_input("Patrimônio atual (R$)", min_value=0, value=50000, step=10, key="ap_ini")
        ap_pmt  = st.number_input("Aporte mensal (R$)", min_value=0, value=2000, step=10, key="ap_pmt")
        ap_na   = st.number_input("Anos até aposentadoria", min_value=1, max_value=50, value=25, step=1, key="ap_na")
        ap_ra   = st.number_input("Rentabilidade anual — acumulação (%)", min_value=0.0, value=12.0, step=0.1, format="%.1f", key="ap_ra")
    with c2:
        st.markdown("#### Fase de desacumulação")
        ap_saq  = st.number_input("Saque mensal desejado (R$)", min_value=0, value=10000, step=10, key="ap_saq")
        ap_rd   = st.number_input("Rentabilidade anual — desacumulação (%)", min_value=0.0, value=8.0, step=0.1, format="%.1f", key="ap_rd")
        ap_inf  = st.number_input("Inflação anual (%)", min_value=0.0, value=5.0, step=0.1, format="%.1f", key="ap_inf")

    rmA = (1 + ap_ra/100)**(1/12) - 1
    rmD = (1 + ap_rd/100)**(1/12) - 1

    lbl_ac, d_ac = [], []
    pat_ap = float(ap_ini)
    for m in range(int(ap_na)*12 + 1):
        if m > 0:
            pat_ap = pat_ap * (1 + rmA) + ap_pmt
        if m % 12 == 0:
            yr = m // 12
            lbl_ac.append("Hoje" if yr == 0 else f"Acum. {yr}a")
            d_ac.append(round(pat_ap))

    patrimonio = pat_ap
    renda_max  = patrimonio * rmD

    lbl_dc, d_dc, d_dc_r = [], [], []
    saldo = patrimonio
    yr_d  = 0
    while saldo > 0 and yr_d < 65:
        lbl_dc.append(f"Desacum. {yr_d}a")
        d_dc.append(round(saldo))
        d_dc_r.append(round(saldo / (1 + ap_inf/100)**yr_d))
        saque_real = ap_saq * (1 + ap_inf/100)**yr_d
        for _ in range(12):
            saldo = saldo * (1 + rmD) - saque_real / 12
            if saldo < 0:
                saldo = 0
                break
        yr_d += 1
        if saldo <= 0:
            break
    lbl_dc.append(f"Desacum. {yr_d}a")
    d_dc.append(0)
    d_dc_r.append(0)

    duracao = "Patrimônio perpétuo" if yr_d > 60 else f"{yr_d} anos"

    st.markdown("---")
    render_cards([
        ("Patrimônio na aposentadoria", fmt(patrimonio), "blue"),
        ("Renda passiva máx. (perpétua)", fmt(renda_max) + "/mês", "green"),
        ("Duração do patrimônio", duracao, ""),
        ("Saldo real ao esgotar", fmt(d_dc_r[-1]), "red" if d_dc_r[-1] < 0 else ""),
    ])

    st.markdown("---")
    st.markdown("**Trajetória completa: acumulação + desacumulação**")

    none_ac  = [None] * len(lbl_ac)
    none_dc  = [None] * len(lbl_dc)
    all_lbl  = lbl_ac + lbl_dc[1:]
    full_ac  = d_ac   + [None] * (len(lbl_dc) - 1)
    full_dc  = [None] * (len(lbl_ac) - 1) + [patrimonio] + d_dc[1:]
    full_dc_r= [None] * (len(lbl_ac) - 1) + [patrimonio] + d_dc_r[1:]

    fig_ap = go.Figure()
    fig_ap.add_trace(go.Scatter(
        x=all_lbl, y=full_ac, name="Acumulação",
        fill="tozeroy", connectgaps=False,
        line=dict(color=COLORS["blue"], width=2.5),
        fillcolor="rgba(50,102,173,0.13)",
        hovertemplate="<b>%{x}</b><br>Acumulação: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_ap.add_trace(go.Scatter(
        x=all_lbl, y=full_dc, name="Desacumulação nominal",
        fill="tozeroy", connectgaps=False,
        line=dict(color=COLORS["red"], width=2.5),
        fillcolor="rgba(226,75,74,0.10)",
        hovertemplate="Desacumulação nominal: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_ap.add_trace(go.Scatter(
        x=all_lbl, y=full_dc_r, name="Desacumulação real (inflação)",
        connectgaps=False,
        line=dict(color=COLORS["gray"], width=1.5, dash="dot"),
        hovertemplate="Desacumulação real: R$ %{y:,.0f}<extra></extra>",
    ))

    fig_ap.add_vline(
        x=lbl_ac[-1], line_dash="dash", line_color="#adb5bd", line_width=1,
        annotation_text="Aposentadoria", annotation_position="top",
        annotation_font=dict(size=11, color="#6c757d"),
    )

    fig_ap.update_layout(
        **PLOTLY_LAYOUT,
        title="Trajetória do patrimônio — acumulação e desacumulação",
        yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f",
        height=420,
    )
    st.plotly_chart(fig_ap, use_container_width=True)

    with st.expander("📋 Ver tabela de desacumulação ano a ano"):
        rows = []
        for i, (l, n, r) in enumerate(zip(lbl_dc, d_dc, d_dc_r)):
            rows.append({
                "Período": l,
                "Saldo nominal (R$)": f"R$ {n:,.0f}",
                "Saldo real (R$)": f"R$ {r:,.0f}",
                "Saque anual estimado (R$)": f"R$ {ap_saq * (1 + ap_inf/100)**i * 12:,.0f}",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:11px;color:#adb5bd'>"
    "Calculadora educacional · Projeções hipotéticas · Não constitui recomendação de investimento"
    "</p>",
    unsafe_allow_html=True
)
