import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="E-commerce Brasil · Análise Olist",
    page_icon="🛒",
    layout="wide",
)

CORES = {
    "primaria":   "#7C83FD",
    "secundaria": "#A78BFA",
    "terciaria":  "#C4B5FD",
    "bg_card":    "#1a1d27",
    "bg_plot":    "#13151f",
    "bg_page":    "#0e1117",
    "borda":      "#2d3048",
    "texto":      "#b0b3c8",
    "texto_claro":"#e8e9f0",
}

ESCALA_PRINCIPAL = [
    "#3730a3", "#4338ca", "#4f46e5",
    "#6366f1", "#7C83FD", "#a5b4fc",
    "#c7d2fe",
]

ESCALA_AVALIACOES = {
    1: "#ef4444",
    2: "#f97316",
    3: "#eab308",
    4: "#84cc16",
    5: "#22c55e",
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        background-color: {CORES['bg_page']};
        color: {CORES['texto_claro']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #12141e !important;
        border-right: 1px solid {CORES['borda']};
    }}
    [data-testid="stSidebar"] * {{
        color: {CORES['texto_claro']} !important;
    }}

    /* Métricas nativas do Streamlit */
    [data-testid="stMetric"] {{
        background: {CORES['bg_card']};
        border: 1px solid {CORES['borda']};
        border-radius: 14px;
        padding: 20px 24px !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.8rem !important;
        color: {CORES['texto']} !important;
        font-weight: 500;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: {CORES['primaria']} !important;
        font-family: 'DM Mono', monospace !important;
    }}

    /* Título de seção */
    .section-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {CORES['texto_claro']};
        margin: 28px 0 12px;
        border-left: 3px solid {CORES['primaria']};
        padding-left: 10px;
        letter-spacing: 0.02em;
    }}

    /* Header */
    .header-container {{
        background: linear-gradient(135deg, #1a1d27 0%, #1e2035 60%, #252840 100%);
        border: 1px solid {CORES['borda']};
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }}
    .header-container::before {{
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(124,131,253,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .header-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {CORES['texto_claro']};
        margin: 0 0 6px;
    }}
    .header-sub {{
        font-size: 0.9rem;
        color: {CORES['texto']};
        margin: 0;
    }}
    .header-badge {{
        display: inline-block;
        background: rgba(124,131,253,0.15);
        border: 1px solid rgba(124,131,253,0.3);
        color: {CORES['primaria']};
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 10px;
        vertical-align: middle;
    }}

    /* Remover toolbar do plotly */
    .modebar {{ display: none !important; }}

    /* Divider */
    hr {{ border-color: {CORES['borda']} !important; }}

    /* Selectbox sidebar */
    [data-testid="stSelectbox"] > div {{
        background: #1a1d27 !important;
        border-color: {CORES['borda']} !important;
    }}
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'olist.db')

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)

    orders = pd.read_sql("""
        SELECT order_id, order_status, customer_state, customer_city,
               revenue, freight, items_count, avg_review_score,
               year, month, year_month, order_purchase_timestamp
        FROM orders
        WHERE revenue IS NOT NULL
    """, conn)

    revenue_by_month = pd.read_sql("""
        SELECT year_month, SUM(revenue) as total_revenue, COUNT(order_id) as total_orders
        FROM orders
        WHERE order_status = 'delivered' AND year_month IS NOT NULL
        GROUP BY year_month
        ORDER BY year_month
    """, conn)

    top_categories = pd.read_sql("""
        SELECT category, SUM(price) as revenue, COUNT(*) as items_sold
        FROM order_items
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 10
    """, conn)

    by_state = pd.read_sql("""
        SELECT customer_state, COUNT(order_id) as orders, SUM(revenue) as revenue
        FROM orders
        WHERE order_status = 'delivered'
        GROUP BY customer_state
        ORDER BY orders DESC
    """, conn)

    review_dist = pd.read_sql("""
        SELECT review_score, COUNT(*) as count
        FROM reviews
        GROUP BY review_score
        ORDER BY review_score
    """, conn)

    status_dist = pd.read_sql("""
        SELECT order_status, COUNT(*) as count
        FROM orders
        GROUP BY order_status
        ORDER BY count DESC
    """, conn)

    conn.close()
    return orders, revenue_by_month, top_categories, by_state, review_dist, status_dist

orders, revenue_by_month, top_categories, by_state, review_dist, status_dist = load_data()

with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; padding: 16px 0 24px;">
            <div style="font-size:2.5rem;">🛒</div>
            <div style="font-size:1.1rem; font-weight:700; color:{CORES['texto_claro']}; margin-top:8px;">E-commerce Brasil</div>
            <div style="font-size:0.75rem; color:{CORES['texto']}; margin-top:4px;">Dataset Olist · Análise</div>
        </div>
        <hr style="border-color:{CORES['borda']}; margin-bottom:24px;">
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:0.75rem; font-weight:600; color:{CORES['texto']}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>Filtrar por ano</div>", unsafe_allow_html=True)
    anos = sorted(orders['year'].dropna().unique().astype(int).tolist())
    ano_sel = st.selectbox("", ["Todos"] + anos, index=0, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:{CORES['bg_card']}; border:1px solid {CORES['borda']}; border-radius:10px; padding:14px 16px;">
            <div style="font-size:0.7rem; color:{CORES['texto']}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">Período disponível</div>
            <div style="font-size:0.9rem; color:{CORES['texto_claro']}; font-weight:600;">2016 — 2018</div>
            <div style="font-size:0.75rem; color:{CORES['texto']}; margin-top:4px;">{len(orders):,} pedidos no total</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem; color:{CORES['texto']}; text-align:center;'>Fonte: Kaggle · Olist<br>Desenvolvido por Matheus Guimarães</div>", unsafe_allow_html=True)

if ano_sel != "Todos":
    orders_f = orders[orders['year'] == ano_sel]
else:
    orders_f = orders

delivered = orders_f[orders_f['order_status'] == 'delivered']

ano_label = str(ano_sel) if ano_sel != "Todos" else "2016 – 2018"
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🛒 E-commerce Brasil <span class="header-badge">{ano_label}</span></div>
        <div class="header-sub">Análise completa do dataset Olist · Pedidos, receita, categorias e satisfação de clientes</div>
    </div>
""", unsafe_allow_html=True)

total_pedidos = len(delivered)
receita_total = delivered['revenue'].sum()
ticket_medio  = delivered['revenue'].mean()
score_medio   = delivered['avg_review_score'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Pedidos Entregues", f"{total_pedidos:,}".replace(",", "."))
with col2:
    st.metric("💰 Receita Total", f"R$ {receita_total:,.0f}".replace(",", "."))
with col3:
    st.metric("🎟️ Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "."))
with col4:
    st.metric("⭐ Avaliação Média", f"{score_medio:.2f} / 5.0")

col_a, col_b = st.columns([2, 1])

with col_a:
    st.markdown('<div class="section-title">Receita Mensal (R$)</div>', unsafe_allow_html=True)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=revenue_by_month['year_month'],
        y=revenue_by_month['total_revenue'],
        mode='lines+markers',
        line=dict(color=CORES['primaria'], width=2.5),
        marker=dict(size=6, color=CORES['primaria'], line=dict(width=1.5, color=CORES['bg_card'])),
        fill='tozeroy',
        fillcolor='rgba(124,131,253,0.08)',
    ))
    fig_line.update_layout(
        plot_bgcolor=CORES['bg_plot'], paper_bgcolor=CORES['bg_plot'],
        font=dict(color=CORES['texto'], family='DM Sans'),
        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=CORES['borda'], tickfont=dict(size=11)),
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode='x unified',
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">Status dos Pedidos</div>', unsafe_allow_html=True)

    STATUS_CORES = [
        "#6366f1", "#7C83FD", "#a5b4fc",
        "#c7d2fe", "#818cf8", "#4f46e5", "#4338ca",
    ]
    fig_status = px.pie(
        status_dist, values='count', names='order_status',
        color_discrete_sequence=STATUS_CORES,
        hole=0.45,
    )
    fig_status.update_traces(
        textfont=dict(size=11, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value:,} pedidos<extra></extra>',
    )
    fig_status.update_layout(
        plot_bgcolor=CORES['bg_plot'], paper_bgcolor=CORES['bg_plot'],
        font=dict(color=CORES['texto'], family='DM Sans'),
        legend=dict(font=dict(size=10), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_status, use_container_width=True)

col_c, col_d = st.columns([1, 1])

with col_c:
    st.markdown('<div class="section-title">Top 10 Categorias por Receita</div>', unsafe_allow_html=True)

    df_cat = top_categories.sort_values('revenue')
    fig_cat = go.Figure(go.Bar(
        x=df_cat['revenue'],
        y=df_cat['category'],
        orientation='h',
        marker=dict(
            color=df_cat['revenue'],
            colorscale=[[0, '#3730a3'], [0.5, '#6366f1'], [1, '#a5b4fc']],
            line=dict(width=0),
        ),
        hovertemplate='<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>',
    ))
    fig_cat.update_layout(
        plot_bgcolor=CORES['bg_plot'], paper_bgcolor=CORES['bg_plot'],
        font=dict(color=CORES['texto'], family='DM Sans'),
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_d:
    st.markdown('<div class="section-title">Pedidos por Estado</div>', unsafe_allow_html=True)

    df_state = by_state.head(15).sort_values('orders')
    fig_state = go.Figure(go.Bar(
        x=df_state['orders'],
        y=df_state['customer_state'],
        orientation='h',
        marker=dict(
            color=df_state['orders'],
            colorscale=[[0, '#3730a3'], [0.5, '#6366f1'], [1, '#a5b4fc']],
            line=dict(width=0),
        ),
        hovertemplate='<b>%{y}</b><br>%{x:,} pedidos<extra></extra>',
    ))
    fig_state.update_layout(
        plot_bgcolor=CORES['bg_plot'], paper_bgcolor=CORES['bg_plot'],
        font=dict(color=CORES['texto'], family='DM Sans'),
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_state, use_container_width=True)

st.markdown('<div class="section-title">Distribuição de Avaliações</div>', unsafe_allow_html=True)

review_dist['label'] = review_dist['review_score'].astype(str) + ' ⭐'
review_dist['cor'] = review_dist['review_score'].map(ESCALA_AVALIACOES)

fig_review = go.Figure(go.Bar(
    x=review_dist['label'],
    y=review_dist['count'],
    marker=dict(color=review_dist['cor'], line=dict(width=0)),
    hovertemplate='<b>Nota %{x}</b><br>%{y:,} avaliações<extra></extra>',
))
fig_review.update_layout(
    plot_bgcolor=CORES['bg_plot'], paper_bgcolor=CORES['bg_plot'],
    font=dict(color=CORES['texto'], family='DM Sans'),
    xaxis=dict(showgrid=False, tickfont=dict(size=13)),
    yaxis=dict(gridcolor=CORES['borda'], tickfont=dict(size=11)),
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig_review, use_container_width=True)