import streamlit as st
import boto3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime
from botocore.exceptions import ClientError

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bedrock Intelligence Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #09090f;
    color: #e8e8f0;
}

/* Main background */
.stApp { background-color: #09090f; }
.block-container { padding: 2rem 2.5rem 2rem 2.5rem; max-width: 1400px; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background-color: #111118 !important;
    border: 1px solid #2e2e4e !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput > label, .stSelectbox > label {
    color: #6b6b8a !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00d4ff, #7c3aed) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] > div > div:first-child {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #6b6b8a !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

/* Dataframe */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Divider */
hr { border-color: #1e1e2e !important; }

/* Plotly chart background override */
.js-plotly-plot { border-radius: 8px; }

/* Card container */
.dash-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Section titles */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6b6b8a;
    margin-bottom: 2px;
}
.section-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #e8e8f0;
    margin-bottom: 16px;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: #10b981;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s infinite;
    display: inline-block;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

/* Login card */
.login-card {
    background: #111118;
    border: 1px solid #2e2e4e;
    border-radius: 16px;
    padding: 48px 40px;
    max-width: 460px;
    margin: 0 auto;
}
.login-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: #e8e8f0;
    text-align: center;
    margin-bottom: 6px;
}
.login-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 5px;
    color: #00d4ff;
    text-align: center;
    margin-bottom: 8px;
}
.login-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: #6b6b8a;
    text-align: center;
    margin-bottom: 32px;
}

/* Table styling */
.user-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
}
.user-table th {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b6b8a;
    padding: 8px 10px;
    border-bottom: 1px solid #1e1e2e;
    text-align: left;
}
.user-table td {
    padding: 10px 10px;
    border-bottom: 1px solid #1e1e2e;
    color: #e8e8f0;
}
.user-table tr:last-child td { border-bottom: none; }
.user-table .rank { color: #6b6b8a; font-size: 11px; }
.user-table .tokens { color: #00d4ff; font-weight: 600; font-size: 13px; }
.user-table .models-count { color: #7c3aed; }

/* Error box */
.error-box {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 8px;
    padding: 12px 16px;
    color: #ef4444;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Design Tokens ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":      "#09090f",
    "card":    "#111118",
    "accent":  "#00d4ff",
    "purple":  "#7c3aed",
    "green":   "#10b981",
    "amber":   "#f59e0b",
    "red":     "#ef4444",
    "muted":   "#6b6b8a",
    "border":  "#1e1e2e",
    "text":    "#e8e8f0",
}
PALETTE = ["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#ec4899","#06b6d4","#84cc16"]

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color=COLORS["text"], size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    colorway=PALETTE,
)

AXIS_STYLE = dict(gridcolor="#1e1e2e", zeroline=False, tickfont=dict(size=11))

# ── Session State ─────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "creds" not in st.session_state:
    st.session_state.creds = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None


# ── AWS Helpers ───────────────────────────────────────────────────────────────
def validate_credentials(access_key, secret_key, region):
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        sts.get_caller_identity()
        return True, None
    except ClientError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def run_query(client, log_group, query_str, hours=24 * 7 * 4):
    end_time   = int(time.time())
    start_time = end_time - hours * 3600
    try:
        resp     = client.start_query(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            queryString=query_str,
            limit=10000,
        )
        query_id = resp["queryId"]
        while True:
            result = client.get_query_results(queryId=query_id)
            if result["status"] in ("Complete", "Failed", "Cancelled"):
                return result["results"]
            time.sleep(1)
    except Exception as e:
        st.error(f"CloudWatch query error: {e}")
        return []


def results_to_df(results, cols):
    rows = [{item["field"]: item["value"] for item in rec} for rec in results]
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)


@st.cache_data(ttl=60, show_spinner=False)
def fetch_data(access_key, secret_key, region):
    client    = boto3.client(
        "logs",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    LOG_GROUP = "/aws/bedrock/invocations"

    q_um = """
fields identity.arn, modelId, input.inputTokenCount, output.outputTokenCount
| stats
    sum(input.inputTokenCount)  as totalInput,
    sum(output.outputTokenCount) as totalOutput
by identity.arn, modelId
| sort totalOutput desc
| limit 500
"""
    q_tl = """
fields @timestamp, modelId, input.inputTokenCount, output.outputTokenCount
| stats
    sum(input.inputTokenCount)  as totalInput,
    sum(output.outputTokenCount) as totalOutput
by datefloor(@timestamp, 1h) as hour, modelId
| sort hour asc
| limit 500
"""

    raw_um = run_query(client, LOG_GROUP, q_um)
    raw_tl = run_query(client, LOG_GROUP, q_tl)

    df_um = results_to_df(raw_um, ["identity.arn", "modelId", "totalInput", "totalOutput"])
    df_tl = results_to_df(raw_tl, ["hour", "modelId", "totalInput", "totalOutput"])

    for df in [df_um, df_tl]:
        for col in ["totalInput", "totalOutput"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df_um, df_tl


# ── Formatting Helpers ────────────────────────────────────────────────────────
def fmt(n):
    n = int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def short_user(arn):
    parts = str(arn).split("/")
    return parts[-1] if parts else arn

def short_model(mid):
    parts = str(mid).split(".")
    return parts[-1][:32] if len(parts) > 1 else str(mid)[:32]


# ── Chart Builders ────────────────────────────────────────────────────────────
def make_pie(df_um):
    agg = df_um.groupby("modelShort", as_index=False)["totalTokens"].sum().sort_values("totalTokens", ascending=False)
    fig = go.Figure(go.Pie(
        labels=agg["modelShort"], values=agg["totalTokens"],
        hole=0.58,
        marker=dict(colors=PALETTE, line=dict(color=COLORS["bg"], width=2)),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Tokens: %{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE, height=340,
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=10, family="JetBrains Mono")),
        annotations=[dict(
            text=f"<b>{len(agg)}</b><br><span style='font-size:11px'>models</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["text"], size=15, family="JetBrains Mono"),
        )],
    )
    return fig


def make_top5_users(user_summary):
    top5 = user_summary.head(5)
    fig = go.Figure(go.Bar(
        x=top5["totalTokens"], y=top5["user"], orientation="h",
        marker=dict(color=PALETTE[:len(top5)], line=dict(width=0)),
        text=[fmt(v) for v in top5["totalTokens"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=COLORS["muted"]),
        hovertemplate="<b>%{y}</b><br>Tokens: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE, height=260,
        yaxis=dict(autorange="reversed", gridcolor=COLORS["border"], tickfont=dict(size=11, family="JetBrains Mono")),
        xaxis=dict(gridcolor=COLORS["border"]),
    )
    return fig


def make_top5_models(df_um):
    top5 = df_um.groupby("modelShort", as_index=False)["totalTokens"].sum().sort_values("totalTokens", ascending=False).head(5)
    fig = go.Figure(go.Bar(
        x=top5["totalTokens"], y=top5["modelShort"], orientation="h",
        marker=dict(color=PALETTE[:len(top5)], line=dict(width=0)),
        text=[fmt(v) for v in top5["totalTokens"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=COLORS["muted"]),
        hovertemplate="<b>%{y}</b><br>Tokens: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE, height=260,
        yaxis=dict(autorange="reversed", gridcolor=COLORS["border"], tickfont=dict(size=11, family="JetBrains Mono")),
        xaxis=dict(gridcolor=COLORS["border"]),
    )
    return fig


def make_heatmap(df_um, user_summary):
    top_users = user_summary.head(10)["user"].tolist()
    df_f = df_um[df_um["user"].isin(top_users)]
    pivot = df_f.groupby(["user", "modelShort"], as_index=False)["totalTokens"].sum()
    top3  = pivot.sort_values("totalTokens", ascending=False).groupby("user").head(3)
    if top3.empty:
        return None
    heat = top3.pivot_table(index="user", columns="modelShort", values="totalTokens", fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=heat.values.tolist(),
        x=list(heat.columns),
        y=list(heat.index),
        colorscale=[[0, COLORS["card"]], [0.3, COLORS["purple"]], [1, COLORS["accent"]]],
        hovertemplate="User: <b>%{y}</b><br>Model: <b>%{x}</b><br>Tokens: <b>%{z:,}</b><extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(family="JetBrains Mono", size=10, color=COLORS["muted"])),
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        height=max(300, len(heat.index) * 40 + 80),
        xaxis=dict(tickfont=dict(family="JetBrains Mono", size=10), gridcolor=COLORS["border"]),
        yaxis=dict(tickfont=dict(family="JetBrains Mono", size=10), gridcolor=COLORS["border"]),
    )
    return fig


def make_timeline(df_tl):
    if df_tl.empty or "hour" not in df_tl.columns:
        return None
    df_tl = df_tl.copy()
    df_tl["time"]       = pd.to_datetime(df_tl["hour"], errors="coerce")
    df_tl["modelShort"] = df_tl["modelId"].apply(short_model)
    fig = go.Figure()
    for i, model in enumerate(df_tl["modelShort"].unique()):
        sub = df_tl[df_tl["modelShort"] == model].sort_values("time")
        c   = PALETTE[i % len(PALETTE)]
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        fig.add_trace(go.Scatter(
            x=sub["time"], y=sub["totalOutput"],
            name=model, mode="lines",
            line=dict(color=c, width=2),
            fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.06)",
            hovertemplate=f"<b>{model}</b><br>%{{x}}<br>Output tokens: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_BASE, height=340,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
    )
    return fig


# ── Login Page ────────────────────────────────────────────────────────────────
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class="login-sub">AWS BEDROCK</div>
        <div class="login-title">Intelligence Hub</div>
        <div class="login-desc">CloudWatch analytics for your Bedrock workloads</div>
        """, unsafe_allow_html=True)

        access_key = st.text_input("AWS Access Key ID", placeholder="AKIAIOSFODNN7EXAMPLE", key="login_ak")
        secret_key = st.text_input("AWS Secret Access Key", placeholder="wJalrXUtnFEMI/K7MDENG...", type="password", key="login_sk")
        region = st.selectbox("AWS Region", options=[
            "ap-south-1", "us-east-1", "us-west-2", "eu-west-1",
            "eu-central-1", "ap-northeast-1", "ap-southeast-1",
            "ap-southeast-2", "ca-central-1", "sa-east-1",
        ], key="login_region")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Connect to AWS", use_container_width=True):
            if not access_key or not secret_key:
                st.markdown('<div class="error-box">Access Key and Secret Key are required.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Validating credentials..."):
                    valid, err = validate_credentials(access_key, secret_key, region)
                if valid:
                    st.session_state.authenticated = True
                    st.session_state.creds = {"access_key": access_key, "secret_key": secret_key, "region": region}
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">Authentication failed: {err}</div>', unsafe_allow_html=True)


# ── Dashboard Page ────────────────────────────────────────────────────────────
def render_dashboard():
    creds  = st.session_state.creds
    region = creds["region"]

    # ── Header ──
    h_left, h_right = st.columns([3, 1])
    with h_left:
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:4px;color:{COLORS['accent']};margin-bottom:2px;">AWS BEDROCK</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:24px;font-weight:700;color:{COLORS['text']};">Intelligence Hub</div>
        """, unsafe_allow_html=True)
    with h_right:
        st.markdown(f"""
        <div style="text-align:right;padding-top:8px;">
            <span class="status-dot"></span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;color:{COLORS['green']};margin-left:6px;">LIVE &nbsp; {region.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.creds = {}
            fetch_data.clear()
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Fetch Data ──
    with st.spinner("Fetching CloudWatch data..."):
        df_um, df_tl = fetch_data(creds["access_key"], creds["secret_key"], region)

    now = datetime.now().strftime("%H:%M:%S  %d %b %Y")

    if df_um.empty:
        st.warning("No data found in /aws/bedrock/invocations for the last 4 weeks. Ensure Bedrock model invocation logging is enabled.")
        st.markdown(f'<div style="font-family:JetBrains Mono;font-size:10px;color:{COLORS["muted"]};margin-top:8px;">Last refresh: {now}</div>', unsafe_allow_html=True)
        return

    # ── Prepare dataframes ──
    df_um = df_um.copy()
    df_um["user"]        = df_um["identity.arn"].apply(short_user)
    df_um["modelShort"]  = df_um["modelId"].apply(short_model)
    df_um["totalTokens"] = df_um["totalInput"] + df_um["totalOutput"]

    user_summary = (
        df_um.groupby("user", as_index=False)
             .agg(totalTokens=("totalTokens", "sum"), models=("modelId", "nunique"))
             .sort_values("totalTokens", ascending=False)
             .reset_index(drop=True)
    )
    user_summary.index = user_summary.index + 1

    total_users  = df_um["user"].nunique()
    total_models = df_um["modelId"].nunique()
    total_input  = df_um["totalInput"].sum()
    total_output = df_um["totalOutput"].sum()

    # ── Metric Cards ──
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Unique Users",        fmt(total_users))
    m2.metric("Models Used",         fmt(total_models))
    m3.metric("Total Input Tokens",  fmt(total_input))
    m4.metric("Total Output Tokens", fmt(total_output))

    # ── Color the metric values ──
    st.markdown(f"""
    <style>
    div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] {{ color: {COLORS['accent']} !important; }}
    div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] {{ color: {COLORS['purple']} !important; }}
    div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] {{ color: {COLORS['green']} !important; }}
    div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] {{ color: {COLORS['amber']} !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Users Table + Model Pie ──
    col_table, col_pie = st.columns(2)

    with col_table:
        st.markdown(f'<div class="section-label">USAGE BREAKDOWN</div><div class="section-title">Active Users on Bedrock</div>', unsafe_allow_html=True)
        rows_html = ""
        for i, row in user_summary.iterrows():
            rows_html += f"""
            <tr>
                <td class="rank">#{i}</td>
                <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{row['user']}">{row['user']}</td>
                <td class="tokens" style="text-align:right">{fmt(row['totalTokens'])}</td>
                <td class="models-count" style="text-align:right">{int(row['models'])}</td>
            </tr>"""
        st.markdown(f"""
        <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};border-radius:12px;padding:16px;max-height:400px;overflow-y:auto;">
        <table class="user-table">
            <thead><tr>
                <th>#</th><th>User</th>
                <th style="text-align:right">Tokens</th>
                <th style="text-align:right">Models</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

    with col_pie:
        st.markdown(f'<div class="section-label">MODEL DISTRIBUTION</div><div class="section-title">Token Share by Model</div>', unsafe_allow_html=True)
        st.plotly_chart(make_pie(df_um), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Top 5 Users + Top 5 Models ──
    col_u, col_m = st.columns(2)
    with col_u:
        st.markdown(f'<div class="section-label">TOP CONSUMERS</div><div class="section-title">Top 5 Users by Total Tokens</div>', unsafe_allow_html=True)
        st.plotly_chart(make_top5_users(user_summary), use_container_width=True, config={"displayModeBar": False})
    with col_m:
        st.markdown(f'<div class="section-label">MOST INVOKED</div><div class="section-title">Top 5 Models by Total Tokens</div>', unsafe_allow_html=True)
        st.plotly_chart(make_top5_models(df_um), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Heatmap ──
    st.markdown(f'<div class="section-label">USER AFFINITY</div><div class="section-title">Top 3 Models per User (Token Volume)</div>', unsafe_allow_html=True)
    heatmap_fig = make_heatmap(df_um, user_summary)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough data to build the user-model heatmap.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 4: Timeline ──
    st.markdown(f'<div class="section-label">TOKEN TIMELINE</div><div class="section-title">Hourly Token Usage by Model</div>', unsafe_allow_html=True)
    timeline_fig = make_timeline(df_tl)
    if timeline_fig:
        st.plotly_chart(timeline_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No timeline data available.")

    # ── Footer ──
    st.markdown(f"""
    <div style="margin-top:24px;padding-top:16px;border-top:1px solid {COLORS['border']};
         display:flex;justify-content:space-between;align-items:center;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:{COLORS['muted']};">
            Last refresh: {now}
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:{COLORS['muted']};">
            Auto-refresh every 60s
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-refresh every 60 seconds ──
    time.sleep(60)
    fetch_data.clear()
    st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.authenticated:
    render_dashboard()
else:
    render_login()
