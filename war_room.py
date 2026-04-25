"""
War Room — Stock Research & Portfolio Tracker
Clean, fast, actually useful.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import requests
import json
from datetime import datetime

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="War Room",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #070d1a; color: #e2e8f0; }

/* Sidebar */
div[data-testid="stSidebar"] { background: #0a1020 !important; border-right: 1px solid #1a2540; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

.block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1525;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1a2540;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #93c5fd !important;
}

/* Cards */
.card {
    background: #0d1525;
    border: 1px solid #1a2540;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.card-sm {
    background: #0d1525;
    border: 1px solid #1a2540;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
}

/* Metric pill */
.mpill { display: inline-block; }
.mlabel { font-size: 0.68rem; color: #475569; text-transform: uppercase; letter-spacing: 0.8px; }
.mvalue { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 600; color: #f1f5f9; margin-top: 1px; }
.msub { font-size: 0.68rem; color: #64748b; margin-top: 1px; }

/* Signal badges */
.sig { padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 0.95rem; display: inline-block; }
.sig-sb { background: #052e1c; border: 1px solid #10b981; color: #6ee7b7; }
.sig-b  { background: #0f2044; border: 1px solid #3b82f6; color: #93c5fd; }
.sig-n  { background: #1c1a08; border: 1px solid #f59e0b; color: #fcd34d; }
.sig-av { background: #2a0a0a; border: 1px solid #ef4444; color: #fca5a5; }

/* Score circle */
.score-big {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
}

/* Section label */
.slabel {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #334155;
    margin: 16px 0 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #1a2540;
}

/* Watchlist row */
.wrow {
    background: #0d1525;
    border: 1px solid #1a2540;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: border-color 0.15s;
}
.wrow:hover { border-color: #2d4a7a; }

/* Power card */
.pcard {
    border-radius: 8px;
    padding: 10px 13px;
    margin: 4px 0;
    border-left: 3px solid;
}
.pcard-yes  { background: #051a10; border-color: #10b981; }
.pcard-part { background: #1a1505; border-color: #f59e0b; }
.pcard-no   { background: #0d1525; border-color: #1a2540; }

/* Button overrides */
.stButton > button {
    background: #1e3a5f !important;
    color: #93c5fd !important;
    border: 1px solid #2d5a8e !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
.stButton > button:hover {
    background: #1e4a7f !important;
    border-color: #3b82f6 !important;
}

/* Input styling */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #0d1525 !important;
    border: 1px solid #1a2540 !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}
.stTextArea > div > textarea {
    background: #0d1525 !important;
    border: 1px solid #1a2540 !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
.stCheckbox > label { color: #94a3b8 !important; }
.stSelectbox > div > div { background: #0d1525 !important; border: 1px solid #1a2540 !important; color: #f1f5f9 !important; }
.stDataFrame { background: #0d1525 !important; }
div[data-testid="stDataFrame"] > div { background: #0d1525 !important; }

/* Progress bars */
.progress-bg { background: #1a2540; border-radius: 4px; height: 6px; margin-top: 4px; }
.progress-fill { border-radius: 4px; height: 6px; }

</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def sg(d, k, default=None):
    try:
        v = d.get(k, default)
        return v if v is not None else default
    except:
        return default

def sr(df, name, idx=0, default=np.nan):
    try:
        if df is None or df.empty: return default
        if name in df.index:
            v = df.loc[name].iloc[idx]
            return float(v) if not pd.isna(v) else default
        for r in df.index:
            if r.lower() == name.lower():
                v = df.loc[r].iloc[idx]
                return float(v) if not pd.isna(v) else default
        matches = sorted([r for r in df.index if name.lower() in r.lower()], key=len)
        if not matches: return default
        v = df.loc[matches[0]].iloc[idx]
        return float(v) if not pd.isna(v) else default
    except:
        return default

def pct(v, d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    return f"{v*100:.{d}f}%"

def fmtn(v, d=2, pre="", suf=""):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    if abs(v) >= 1e12: return f"{pre}{v/1e12:.{d}f}T{suf}"
    if abs(v) >= 1e9:  return f"{pre}{v/1e9:.{d}f}B{suf}"
    if abs(v) >= 1e6:  return f"{pre}{v/1e6:.{d}f}M{suf}"
    return f"{pre}{v:.{d}f}{suf}"

def safe_float(v):
    try:
        f = float(v)
        return f if not np.isnan(f) else np.nan
    except:
        return np.nan

def m(label, value, sub="", color="#f1f5f9"):
    sub_html = f"<div class='msub'>{sub}</div>" if sub else ""
    return f"<div class='card-sm'><div class='mlabel'>{label}</div><div class='mvalue' style='color:{color};'>{value}</div>{sub_html}</div>"

def sig_badge(signal):
    cls = {"STRONG BUY":"sig-sb","BUY":"sig-b","NEUTRAL":"sig-n","AVOID":"sig-av"}.get(signal,"sig-n")
    return f"<span class='sig {cls}'>{signal}</span>"

def color_val(v, good_if_positive=True):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "#94a3b8"
    return "#10b981" if (v >= 0) == good_if_positive else "#ef4444"

def cagr(series, yrs):
    try:
        s = [x for x in series if x and not np.isnan(x) and x > 0]
        if len(s) < 2: return np.nan
        n = min(yrs, len(s)-1)
        return (s[0]/s[n])**(1/n) - 1
    except:
        return np.nan

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load(ticker):
    t = yf.Ticker(ticker)
    info = {}; hist = pd.DataFrame()
    fin = pd.DataFrame(); bal = pd.DataFrame(); cf = pd.DataFrame()
    try: info = t.info or {}
    except: pass
    try: hist = t.history(period="2y", auto_adjust=True)
    except: pass
    try: fin  = t.financials
    except: pass
    try: bal  = t.balance_sheet
    except: pass
    try: cf   = t.cashflow
    except: pass
    return info, hist, fin, bal, cf

@st.cache_data(ttl=60, show_spinner=False)
def quick_quote(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="5d", auto_adjust=True)
        price = None
        for f in ["currentPrice","regularMarketPrice","previousClose"]:
            v = info.get(f)
            if v:
                try:
                    fv = float(v)
                    if not np.isnan(fv) and fv > 0:
                        price = fv
                        break
                except: pass
        if price is None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
        prev = safe_float(info.get("previousClose", np.nan))
        if np.isnan(prev) and not hist.empty and len(hist) >= 2:
            prev = float(hist["Close"].iloc[-2])
        chg = (price - prev) / prev if price and not np.isnan(prev) and prev > 0 else np.nan
        return {
            "price": price or np.nan,
            "chg": chg,
            "name": info.get("shortName", ticker),
            "mktcap": safe_float(info.get("marketCap", np.nan)),
            "pe": safe_float(info.get("trailingPE", np.nan)),
            "hi52": safe_float(info.get("fiftyTwoWeekHigh", np.nan)),
            "lo52": safe_float(info.get("fiftyTwoWeekLow", np.nan)),
        }
    except:
        return {"price": np.nan, "chg": np.nan, "name": ticker,
                "mktcap": np.nan, "pe": np.nan, "hi52": np.nan, "lo52": np.nan}

def add_ta(hist):
    if hist.empty: return hist
    h = hist.copy()
    try:
        h["SMA50"]  = h["Close"].rolling(50).mean()
        h["SMA200"] = h["Close"].rolling(200).mean()
        h["Vol20"]  = h["Volume"].rolling(20).mean()
        d = h["Close"].diff()
        g = d.clip(lower=0).rolling(14).mean()
        l = (-d.clip(upper=0)).rolling(14).mean()
        h["RSI"] = 100 - (100 / (1 + g / l.replace(0, np.nan)))
        tr = pd.concat([h["High"]-h["Low"],
                        (h["High"]-h["Close"].shift()).abs(),
                        (h["Low"]-h["Close"].shift()).abs()], axis=1).max(axis=1)
        h["ATR"] = tr.rolling(14).mean()
    except: pass
    return h

def get_price(info, hist):
    for f in ["currentPrice","regularMarketPrice","previousClose","ask","bid"]:
        v = info.get(f)
        if v:
            try:
                fv = float(v)
                if not np.isnan(fv) and fv > 0: return fv
            except: pass
    if not hist.empty: return float(hist["Close"].iloc[-1])
    return np.nan

# ── SCORING ───────────────────────────────────────────────────────────────────
def detect_stage(info, fin):
    try:
        ni = sr(fin, "Net Income")
        gm = sg(info, "grossMargins", np.nan)
        rg = sg(info, "revenueGrowth", np.nan)
        rv_r = [r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"] if not fin.empty else []
        rc_v = np.nan
        if rv_r:
            s = [float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
            rc_v = cagr(s, 3)
        fast = (not np.isnan(rc_v) and rc_v > 0.15) or (not np.isnan(rg) and rg > 0.15)
        if not np.isnan(ni) and ni < 0 and (fast or (not np.isnan(gm) and gm > 0.35)):
            return "growth"
        if np.isnan(sg(info,"trailingPE",np.nan)) and fast:
            return "growth"
    except: pass
    return "mature"

def compute_score(info, hist, fin, bal, cf):
    sc = {}; det = {}
    stage = detect_stage(info, fin)
    det["stage"] = stage

    # Quality (30 pts)
    crp_v = np.nan; crp_s = 0
    try:
        ni = sr(fin,"Net Income"); eq = sr(bal,"Stockholders Equity")
        if np.isnan(eq): eq = sr(bal,"Total Stockholders Equity")
        td = sr(bal,"Total Debt")
        if np.isnan(td): td = sr(bal,"Long Term Debt", default=0)
        denom = eq + (td if not np.isnan(td) else 0)
        if not any(np.isnan(x) for x in [ni,eq]) and denom != 0:
            crp_v = ni / denom
            if stage == "growth":
                gm = sg(info,"grossMargins",np.nan)
                crp_s = 10 if not np.isnan(gm) and gm>0.60 else 7 if not np.isnan(gm) and gm>0.45 else 5 if not np.isnan(gm) and gm>0.30 else 3
            else:
                crp_s = 10 if crp_v>0.20 else 8 if crp_v>0.15 else 5 if crp_v>0.10 else 3 if crp_v>0.05 else 1
        elif stage=="growth": crp_s = 3
    except: pass
    sc["crp"] = crp_s; det["crp"] = crp_v

    om_s = 0; om_trend = []
    try:
        if not fin.empty and fin.shape[1] >= 2:
            op_r = [r for r in fin.index if "operating" in r.lower() and "income" in r.lower()]
            rv_r = [r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"]
            if op_r and rv_r:
                for i in range(min(5, fin.shape[1])):
                    try:
                        op = float(fin.loc[op_r[0]].iloc[i]); rv = float(fin.loc[rv_r[0]].iloc[i])
                        if rv > 0: om_trend.append(op/rv)
                    except: pass
                if len(om_trend) >= 2:
                    delta = om_trend[0] - om_trend[-1]
                    if stage == "growth":
                        om_s = 10 if delta>0.05 else 7 if delta>0.02 else 5 if delta>0 else 3 if delta>-0.03 else 1
                    else:
                        om_s = 10 if delta>0.03 else 7 if delta>0 else 4 if delta>-0.02 else 1
    except: pass
    sc["om"] = om_s; det["om_trend"] = om_trend

    fcf_s = 0; fcf_v = np.nan; fcf_r = np.nan
    try:
        # Use Yahoo's pre-calculated FCF first
        fcf_yahoo = sg(info,"freeCashflow",np.nan)
        ni_ttm    = sg(info,"netIncomeToCommon",np.nan)
        if not np.isnan(fcf_yahoo):
            fcf_v = fcf_yahoo
            if stage == "growth":
                fcf_s = 10 if fcf_v>0 else 6 if fcf_v>-1e8 else 3 if fcf_v>-5e8 else 1
            else:
                if not np.isnan(ni_ttm) and ni_ttm > 0:
                    fcf_r = fcf_v / ni_ttm
                    fcf_s = 10 if fcf_r>=0.80 else 7 if fcf_r>=0.60 else 4 if fcf_r>=0.40 else 1 if fcf_r>0 else 0
                elif fcf_v > 0:
                    fcf_s = 5
        else:
            opcf = sr(cf,"Operating Cash Flow")
            cap  = sr(cf,"Capital Expenditure")
            if not np.isnan(opcf):
                fcf_v = opcf - (abs(cap) if not np.isnan(cap) else 0)
                fcf_s = 5 if fcf_v > 0 else 1
    except: pass
    sc["fcf"] = fcf_s; det["fcf"] = fcf_v; det["fcf_r"] = fcf_r

    # Expectations (20 pts)
    rc_s = 0; rc_v = np.nan
    try:
        if not fin.empty:
            rv_r = [r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"]
            if rv_r:
                s = [float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
                rc_v = cagr(s,5)
                if np.isnan(rc_v): rc_v = cagr(s,3)
                # Also consider Yahoo's recent growth
                yh_rg = sg(info,"revenueGrowth",np.nan)
                if not np.isnan(yh_rg) and np.isnan(rc_v): rc_v = yh_rg
                if not np.isnan(rc_v):
                    rc_s = 10 if rc_v>0.25 else 7 if rc_v>0.15 else 5 if rc_v>0.08 else 3 if rc_v>0 else 0
    except: pass
    sc["rc"] = rc_s; det["rc"] = rc_v

    ec_s = 0; ec_v = np.nan
    try:
        # Use Yahoo's EPS growth if available
        yh_eg = sg(info,"earningsGrowth",np.nan)
        if not np.isnan(yh_eg) and yh_eg > 0:
            ec_v = yh_eg
            ec_s = 10 if yh_eg>0.25 else 7 if yh_eg>0.15 else 5 if yh_eg>0.08 else 3 if yh_eg>0 else 0
        else:
            shares = sg(info,"sharesOutstanding",np.nan)
            ni_r   = [r for r in fin.index if "net income" in r.lower()] if not fin.empty else []
            if ni_r and not np.isnan(shares) and shares > 0:
                eps_s = [float(fin.loc[ni_r[0]].iloc[i])/shares for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[ni_r[0]].iloc[i])]
                eps_s = [x for x in eps_s if x > 0]
                ec_v  = cagr(eps_s,5)
                if np.isnan(ec_v): ec_v = cagr(eps_s,3)
                if not np.isnan(ec_v):
                    ec_s = 10 if ec_v>0.25 else 7 if ec_v>0.15 else 5 if ec_v>0.08 else 3 if ec_v>0 else 0
    except: pass
    sc["ec"] = ec_s; det["ec"] = ec_v

    # Valuation (20 pts)
    fy_s = 0; pe_s = 0; pg_s = 0
    fy_v = np.nan; pe_v = safe_float(sg(info,"trailingPE",np.nan)); pg_v = np.nan

    try:
        fcf_y = sg(info,"freeCashflow",np.nan)
        price = get_price(info, hist)
        mktcap = sg(info,"marketCap",np.nan)
        if not np.isnan(fcf_y) and not np.isnan(mktcap) and mktcap > 0:
            fy_v = fcf_y / mktcap
            T = 0.044
            if stage == "growth":
                fy_s = 7 if fy_v>0.03 else 5 if fy_v>0.01 else 3 if fy_v>0 else 1
            else:
                fy_s = 7 if fy_v>T*2 else 5 if fy_v>T else 3 if fy_v>T*0.5 else 1 if fy_v>0 else 0
    except: pass

    try:
        if stage == "growth":
            ps = safe_float(sg(info,"priceToSalesTrailingTwelveMonths",np.nan))
            rg = safe_float(sg(info,"revenueGrowth",np.nan))
            if not np.isnan(ps):
                if not np.isnan(rg) and rg > 0.30:
                    pe_s = 6 if ps<8 else 4 if ps<15 else 2 if ps<30 else 1
                else:
                    pe_s = 6 if ps<5 else 4 if ps<12 else 2 if ps<20 else 1
        else:
            if not np.isnan(pe_v):
                pe_s = 7 if pe_v<15 else 5 if pe_v<22 else 3 if pe_v<30 else 1 if pe_v<45 else 0
    except: pass

    try:
        if stage != "growth" and not np.isnan(pe_v):
            g = safe_float(sg(info,"earningsGrowth",np.nan))
            if np.isnan(g) or g <= 0: g = det.get("ec",np.nan)
            if not np.isnan(g) and g > 0:
                pg_v = pe_v / (g * 100)
                pg_s = 6 if pg_v<1.0 else 4 if pg_v<1.5 else 2 if pg_v<2.5 else 0
    except: pass

    sc["fy"] = fy_s; sc["pe"] = pe_s; sc["pg"] = pg_s
    det["fy"] = fy_v; det["pe"] = pe_v; det["pg"] = pg_v

    # Technicals (15 pts)
    st2_s = 0; rsi_s = 0; vol_s = 0
    rsi_v = np.nan; atr_p = np.nan; beta = safe_float(sg(info,"beta",np.nan))

    try:
        if not hist.empty and len(hist) > 5:
            last = hist.iloc[-1]; prev = hist.iloc[-2]
            cl = float(last["Close"]); s50 = float(last.get("SMA50",np.nan))
            s200 = float(last.get("SMA200",np.nan)); rsi_v = float(last.get("RSI",np.nan))
            atr_v = float(last.get("ATR",np.nan)); vol = float(last.get("Volume",np.nan))
            v20 = float(last.get("Vol20",np.nan)); dchg = cl - float(prev["Close"])

            if not np.isnan(atr_v) and cl > 0: atr_p = atr_v / cl

            if not any(np.isnan(x) for x in [cl,s50,s200]):
                if cl > s50 > s200:   st2_s = 6
                elif cl > s200:       st2_s = 3
                elif cl > s50:        st2_s = 2

            if not np.isnan(rsi_v):
                if 45 <= rsi_v <= 65:     rsi_s = 5
                elif 35 <= rsi_v < 45 or 65 < rsi_v <= 75: rsi_s = 3
                else:                     rsi_s = 1

            if not any(np.isnan(x) for x in [vol,v20]):
                if vol > v20 and dchg > 0: vol_s = 4
                elif vol > v20 or dchg > 0: vol_s = 2
    except: pass

    sc["st2"] = st2_s; sc["rsi"] = rsi_s; sc["vol"] = vol_s
    det["rsi"] = rsi_v; det["atr"] = atr_p; det["beta"] = beta

    # 7 Powers placeholder — AI fills this in
    sc["pw"] = 0; det["pw"] = 0

    q    = sc["crp"] + sc["om"] + sc["fcf"]
    e    = sc["rc"] + sc["ec"]
    v    = sc["fy"] + sc["pe"] + sc["pg"]
    tech = min(15, sc["st2"] + sc["rsi"] + sc["vol"])
    base = min(85, q + e + v + tech)

    return {"base": base, "total": base, "q": q, "e": e, "v": v, "tech": tech, "pw": 0,
            "sc": sc, "det": det}

def get_signal(score, hist):
    s200_ok = rsi_ok = False
    try:
        if not hist.empty:
            last = hist.iloc[-1]
            cl   = float(last["Close"])
            s200 = float(last.get("SMA200", np.nan))
            rsi  = float(last.get("RSI", np.nan))
            s200_ok = not np.isnan(s200) and cl > s200
            rsi_ok  = not np.isnan(rsi) and 45 <= rsi <= 65
    except: pass

    if score > 75 and s200_ok and rsi_ok: return "STRONG BUY", "#10b981"
    if score >= 65 and s200_ok:           return "BUY",        "#3b82f6"
    if score >= 50:                        return "NEUTRAL",   "#f59e0b"
    return "AVOID", "#ef4444"

def risk_lvl(det):
    a = det.get("atr", np.nan) or 0.04
    b = det.get("beta", np.nan) or 1.0
    stage = det.get("stage","mature")
    if stage == "growth":
        return "HIGH" if a > 0.08 or b > 2.5 else "MEDIUM"
    return "LOW" if a < 0.03 and b < 1.0 else "HIGH" if a > 0.05 or b > 1.5 else "MEDIUM"

# ── AI 7 POWERS ───────────────────────────────────────────────────────────────
ALL_POWERS = ["Scale Economies","Network Economies","Counter-Positioning",
              "Switching Costs","Branding","Cornered Resource","Process Power"]

def get_groq_key():
    """Safely get Groq API key from Streamlit secrets."""
    try:
        # Method 1: direct key access (most reliable on Streamlit Cloud)
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    try:
        # Method 2: .get() method
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    try:
        # Method 3: nested under [groq] section
        return st.secrets["groq"]["GROQ_API_KEY"]
    except Exception:
        pass
    return ""

def analyze_7_powers(ticker, name, sector, industry, desc, gm, om, rg, mktcap, stage):
    api_key = get_groq_key()
    if not api_key:
        return None

    prompt = f"""Expert equity analyst using Hamilton Helmer's 7 Powers framework.

Company: {name} ({ticker}) | Sector: {sector} | Industry: {industry}
Stage: {stage} | Gross Margin: {gm} | Operating Margin: {om} | Revenue Growth: {rg} | Market Cap: {mktcap}
Description: {(desc or '')[:500]}

For each power give VERDICT (YES/PARTIAL/NO) and 1-sentence REASONING.
Return ONLY valid JSON, no markdown:
{{"Scale Economies":{{"verdict":"YES","reasoning":"..."}},"Network Economies":{{"verdict":"NO","reasoning":"..."}},"Counter-Positioning":{{"verdict":"NO","reasoning":"..."}},"Switching Costs":{{"verdict":"YES","reasoning":"..."}},"Branding":{{"verdict":"NO","reasoning":"..."}},"Cornered Resource":{{"verdict":"NO","reasoning":"..."}},"Process Power":{{"verdict":"NO","reasoning":"..."}}}}"""

    for _ in range(3):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type":"application/json","Authorization":f"Bearer {api_key}"},
                json={"model":"llama3-70b-8192","max_tokens":800,"temperature":0.1,
                      "messages":[{"role":"user","content":prompt}]},
                timeout=25
            )
            if r.status_code != 200: continue
            raw = r.json()["choices"][0]["message"]["content"].strip()
            # Extract JSON from anywhere in the response
            start = raw.find("{")
            end   = raw.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(raw[start:end])
                if all(p in result for p in ALL_POWERS):
                    return result
        except: continue
    return None

# ── CHARTS ────────────────────────────────────────────────────────────────────
def price_chart(hist, ticker):
    if hist.empty: return go.Figure()

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.015,
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        increasing=dict(line=dict(color="#00d4aa",width=1), fillcolor="#00d4aa"),
        decreasing=dict(line=dict(color="#ff4757",width=1), fillcolor="#ff4757"),
        name="Price", showlegend=False,
    ), row=1, col=1)

    for col_name, color, nm in [("SMA50","#fbbf24","SMA50"),("SMA200","#a78bfa","SMA200")]:
        if col_name in hist.columns:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist[col_name], name=nm,
                line=dict(color=color, width=1.8), opacity=0.9,
            ), row=1, col=1)

    # Volume
    up   = hist["Close"] >= hist["Open"]
    fig.add_trace(go.Bar(x=hist.index[up],  y=hist["Volume"][up],  name="",
                         marker_color="rgba(0,212,170,0.35)", showlegend=False), row=2, col=1)
    fig.add_trace(go.Bar(x=hist.index[~up], y=hist["Volume"][~up], name="",
                         marker_color="rgba(255,71,87,0.35)",  showlegend=False), row=2, col=1)
    if "Vol20" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Vol20"], name="Vol MA",
                                 line=dict(color="#fbbf24",width=1.2,dash="dot"),
                                 opacity=0.7), row=2, col=1)

    # RSI
    if "RSI" in hist.columns:
        rsi = hist["RSI"]
        fig.add_trace(go.Scatter(x=hist.index, y=rsi, name="RSI",
                                 line=dict(color="#60a5fa",width=1.8)), row=3, col=1)
        fig.add_hrect(y0=70,y1=100,row=3,col=1,fillcolor="rgba(239,68,68,0.07)",line_width=0)
        fig.add_hrect(y0=0, y1=30, row=3,col=1,fillcolor="rgba(239,68,68,0.07)",line_width=0)
        fig.add_hrect(y0=45,y1=65, row=3,col=1,fillcolor="rgba(16,185,129,0.05)",line_width=0)
        for lvl, clr in [(70,"rgba(239,68,68,0.5)"),(30,"rgba(239,68,68,0.5)"),(50,"rgba(100,116,139,0.4)")]:
            fig.add_hline(y=lvl, row=3, col=1, line=dict(color=clr,width=0.8,dash="dot"))

    ax = dict(gridcolor="rgba(26,37,64,0.9)", linecolor="#1a2540",
              showgrid=True, zeroline=False, tickfont=dict(color="#64748b",size=10))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#070d1a",
        font=dict(color="#94a3b8",family="Inter",size=10),
        height=520, showlegend=True, barmode="overlay",
        legend=dict(orientation="h", y=1.02, x=0,
                    font=dict(color="#94a3b8",size=10),
                    bgcolor="rgba(7,13,26,0.8)",
                    bordercolor="#1a2540", borderwidth=1),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        margin=dict(l=55,r=20,t=10,b=20),
    )
    for i in range(1,4):
        fig.update_xaxes(row=i,col=1,**ax)
        fig.update_yaxes(row=i,col=1,**ax)
    fig.update_yaxes(tickprefix="$", row=1, col=1, tickfont=dict(color="#64748b",size=10))
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0,100],
                     title_font=dict(color="#475569",size=9))
    return fig

def mini_chart(prices, color="#3b82f6"):
    fig = go.Figure(go.Scatter(
        x=list(range(len(prices))), y=prices,
        mode="lines", line=dict(color=color, width=1.5),
        fill="tozeroy", fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4)) + (0.08,)}",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=50, showlegend=False,
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig

def gauge_chart(score):
    color = "#10b981" if score>=75 else "#3b82f6" if score>=60 else "#f59e0b" if score>=45 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"color":color,"size":42,"family":"JetBrains Mono"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#334155","tickfont":{"color":"#334155","size":9}},
            "bar":{"color":color,"thickness":0.22},
            "bgcolor":"#070d1a","borderwidth":0,
            "steps":[{"range":[0,50],"color":"#120808"},
                     {"range":[50,65],"color":"#0d1020"},
                     {"range":[65,100],"color":"#081510"}],
            "threshold":{"line":{"color":color,"width":2},"thickness":0.75,"value":score}
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=20,r=20,t=10,b=10), height=180)
    return fig

def breakdown_bar(res, pw_score=0):
    cats = ["Quality","Expectations","Valuation","Technicals","7 Powers"]
    maxv = [30,20,20,15,15]
    vals = [res["q"],res["e"],res["v"],res["tech"],pw_score]
    colors = ["#10b981" if v/mx>=0.75 else "#3b82f6" if v/mx>=0.5 else "#f59e0b" if v/mx>=0.25 else "#ef4444"
              for v,mx in zip(vals,maxv)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cats, y=maxv, marker_color="rgba(26,37,64,0.6)",
                         marker_line=dict(color="#1a2540",width=1), showlegend=False))
    fig.add_trace(go.Bar(x=cats, y=vals, marker_color=colors,
                         text=[f"{v:.0f}" for v in vals], textposition="inside",
                         textfont=dict(color="white",size=11,family="JetBrains Mono"),
                         showlegend=False))
    fig.update_layout(
        barmode="overlay", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#070d1a",
        font=dict(color="#64748b",family="Inter",size=10),
        height=180, margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(tickfont=dict(color="#94a3b8",size=10),
                   gridcolor="rgba(26,37,64,0.5)", linecolor="#1a2540"),
        yaxis=dict(tickfont=dict(color="#64748b",size=9),
                   gridcolor="rgba(26,37,64,0.5)", linecolor="#1a2540"),
    )
    return fig

def radar_chart(confirmed, partial):
    vals = []
    for p in ALL_POWERS:
        if p in confirmed: vals.append(1.0)
        elif p in partial:  vals.append(0.5)
        else:               vals.append(0.0)
    vals_closed = vals + [vals[0]]
    cats_closed = ALL_POWERS + [ALL_POWERS[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals_closed, theta=cats_closed, fill="toself",
        fillcolor="rgba(59,130,246,0.12)",
        line=dict(color="#3b82f6",width=2),
        marker=dict(size=7, color=["#10b981" if v==1 else "#f59e0b" if v==0.5 else "#1a2540"
                                    for v in vals_closed])
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#070d1a",
            radialaxis=dict(visible=False, range=[0,1]),
            angularaxis=dict(tickfont=dict(color="#94a3b8",size=10),
                             linecolor="#1a2540", gridcolor="#1a2540")
        ),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        margin=dict(l=30,r=30,t=20,b=20), height=260,
    )
    return fig

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["AAPL","MSFT","NVDA","GOOGL","V"]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# ── HEADER ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown("""
    <div style="padding: 8px 0 20px;">
        <div style="font-size:1.8rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.5px;">⚔️ War Room</div>
        <div style="font-size:0.82rem;color:#475569;margin-top:2px;">Stock Research · Portfolio Tracker · 7 Powers Analysis</div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    ticker_input = st.text_input("", placeholder="Enter ticker (e.g. NVDA)", label_visibility="collapsed")

# ── MAIN TABS ─────────────────────────────────────────────────────────────────
tab_research, tab_watchlist, tab_compare = st.tabs(["🔍 Research", "📋 Watchlist", "⚖️ Compare"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ════════════════════════════════════════════════════════════════════════════
with tab_research:
    ticker = (ticker_input or "AAPL").strip().upper()

    with st.spinner(f"Loading {ticker}..."):
        info, hist_raw, fin, bal, cf = load(ticker)
        hist = add_ta(hist_raw)

    if not info and hist.empty:
        st.error(f"No data found for **{ticker}**")
        st.stop()

    # ETF detection
    is_etf = sg(info,"quoteType","") in ["ETF","MUTUALFUND"] or sg(info,"fundFamily",None) is not None

    if is_etf:
        name    = sg(info,"longName",ticker)
        category= sg(info,"category","—")
        fund_fam= sg(info,"fundFamily","—")
        price   = get_price(info, hist)
        prev    = safe_float(sg(info,"previousClose",np.nan))
        if np.isnan(prev) and not hist.empty and len(hist)>=2:
            prev = float(hist["Close"].iloc[-2])
        chg     = (price-prev)/prev if not np.isnan(price) and not np.isnan(prev) and prev>0 else np.nan
        chg_c   = "#10b981" if not np.isnan(chg) and chg>=0 else "#ef4444"
        aum     = safe_float(sg(info,"totalAssets",np.nan))
        exp_r   = safe_float(sg(info,"annualReportExpenseRatio",np.nan))
        w52h    = safe_float(sg(info,"fiftyTwoWeekHigh",np.nan))
        w52l    = safe_float(sg(info,"fiftyTwoWeekLow",np.nan))

        st.markdown(f"""
        <div style="background:#0d1525;border:1px solid #1a2540;border-radius:14px;padding:22px 28px;margin-bottom:20px;">
            <div style="font-size:1.6rem;font-weight:700;color:#f1f5f9;">{name}</div>
            <div style="font-size:0.82rem;color:#64748b;margin-top:5px;">📊 ETF · {category} · {fund_fam}</div>
        </div>
        """, unsafe_allow_html=True)

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        for col,(lbl,val) in zip([c1,c2,c3,c4,c5,c6],[
            ("Price",          f"${price:.2f}" if not np.isnan(price) else "N/A"),
            ("Day Change",     f'<span style="color:{chg_c}">{pct(chg)}</span>'),
            ("52W High",       f"${w52h:.2f}" if not np.isnan(w52h) else "N/A"),
            ("52W Low",        f"${w52l:.2f}" if not np.isnan(w52l) else "N/A"),
            ("Expense Ratio",  pct(exp_r) if not np.isnan(exp_r) else "N/A"),
            ("AUM",            fmtn(aum,pre="$")),
        ]):
            with col: st.markdown(m(lbl,val), unsafe_allow_html=True)

        if not hist.empty:
            st.plotly_chart(price_chart(hist, ticker), use_container_width=True, config={"displayModeBar":False})
        st.markdown(m("ℹ️ Note","ETF/Fund — scoring model applies to individual stocks only.","","#f59e0b"), unsafe_allow_html=True)

    else:
        # ── STOCK RESEARCH ────────────────────────────────────────────────────
        res   = compute_score(info, hist, fin, bal, cf)
        det   = res["det"]
        price = get_price(info, hist)
        prev  = safe_float(sg(info,"previousClose",np.nan))
        if np.isnan(prev) and not hist.empty and len(hist)>=2:
            prev = float(hist["Close"].iloc[-2])
        day_chg  = (price-prev)/prev if not np.isnan(price) and not np.isnan(prev) and prev>0 else np.nan
        name     = sg(info,"longName",ticker)
        sector   = sg(info,"sector","—")
        industry = sg(info,"industry","—")
        stage    = det.get("stage","mature")

        # AI 7 Powers
        with st.spinner("🤖 Running 7 Powers AI analysis..."):
            powers_ai = analyze_7_powers(
                ticker=ticker, name=name, sector=sector, industry=industry,
                desc=sg(info,"longBusinessSummary",""),
                gm=pct(sg(info,"grossMargins",np.nan)),
                om=pct(sg(info,"operatingMargins",np.nan)),
                rg=pct(sg(info,"revenueGrowth",np.nan)),
                mktcap=fmtn(sg(info,"marketCap",np.nan),pre="$"),
                stage=stage,
            )

        if powers_ai:
            ai_confirmed = [p for p,v in powers_ai.items() if v.get("verdict","NO").upper().startswith("YES")]
            ai_partial   = [p for p,v in powers_ai.items() if v.get("verdict","NO").upper().startswith("PARTIAL")]
            pw_score     = round(min(15,(len(ai_confirmed)+len(ai_partial)*0.5)*(15/7)),1)
        else:
            ai_confirmed = []; ai_partial = []; pw_score = 0

        total_score = round(min(100, res["base"] + pw_score), 1)
        signal, sig_color = get_signal(total_score, hist)
        rl = risk_lvl(det)

        # ── ROW 1: Header ─────────────────────────────────────────────────────
        c_name, c_score, c_gauge = st.columns([2.5, 1, 1.2])

        with c_name:
            chg_c = "#10b981" if not np.isnan(day_chg) and day_chg>=0 else "#ef4444"
            mktcap = safe_float(sg(info,"marketCap",np.nan))
            w52h   = safe_float(sg(info,"fiftyTwoWeekHigh",np.nan))
            w52l   = safe_float(sg(info,"fiftyTwoWeekLow",np.nan))
            beta_v = det.get("beta",np.nan)

            st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="font-size:1.7rem;font-weight:700;color:#f1f5f9;line-height:1.2;">{name}</div>
                <div style="font-size:0.8rem;color:#475569;margin-top:4px;">{ticker} · {sector} · {industry}</div>
                <div style="margin-top:10px;display:flex;align-items:center;gap:12px;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#f1f5f9;">${price:.2f}</span>
                    <span style="font-size:1rem;color:{chg_c};font-weight:600;">{pct(day_chg)} today</span>
                    {sig_badge(signal)}
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1,c2,c3,c4,c5 = st.columns(5)
            rl_color = "#10b981" if rl=="LOW" else "#f59e0b" if rl=="MEDIUM" else "#ef4444"
            stage_color = "#f59e0b" if stage=="growth" else "#64748b"
            for col,(lbl,val,vc) in zip([c1,c2,c3,c4,c5],[
                ("Market Cap",   fmtn(mktcap,pre="$"),  "#f1f5f9"),
                ("52W High",     f"${w52h:.2f}" if not np.isnan(w52h) else "N/A", "#f1f5f9"),
                ("52W Low",      f"${w52l:.2f}" if not np.isnan(w52l) else "N/A", "#f1f5f9"),
                ("Risk",         rl,       rl_color),
                ("Stage",        stage.upper(), stage_color),
            ]):
                with col: st.markdown(m(lbl,val,color=vc), unsafe_allow_html=True)

        with c_score:
            st.markdown(f"""
            <div style="background:#0d1525;border:1px solid #1a2540;border-radius:14px;padding:18px;text-align:center;">
                <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Score</div>
                <div class="score-big" style="color:{sig_color};">{total_score}</div>
                <div style="font-size:0.68rem;color:#334155;margin-top:2px;">out of 100</div>
                <div style="margin-top:12px;">
                    <div style="font-size:0.7rem;color:#475569;">Q:{res['q']} · E:{res['e']} · V:{res['v']}</div>
                    <div style="font-size:0.7rem;color:#475569;">T:{res['tech']} · 7P:{pw_score:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_gauge:
            st.plotly_chart(gauge_chart(total_score), use_container_width=True,
                            config={"displayModeBar":False})

        st.markdown("---")

        # ── ROW 2: Chart + Financials ─────────────────────────────────────────
        c_chart, c_fin = st.columns([2.2, 1])

        with c_chart:
            st.plotly_chart(price_chart(hist, ticker), use_container_width=True,
                            config={"displayModeBar":False})

        with c_fin:
            st.markdown('<div class="slabel">Financials (Yahoo Finance)</div>', unsafe_allow_html=True)

            gm     = safe_float(sg(info,"grossMargins",np.nan))
            om_    = safe_float(sg(info,"operatingMargins",np.nan))
            nm     = safe_float(sg(info,"profitMargins",np.nan))
            roe    = safe_float(sg(info,"returnOnEquity",np.nan))
            roa    = safe_float(sg(info,"returnOnAssets",np.nan))
            rev    = safe_float(sg(info,"totalRevenue",np.nan))
            ni     = safe_float(sg(info,"netIncomeToCommon",np.nan))
            fcf    = safe_float(sg(info,"freeCashflow",np.nan))
            ebitda = safe_float(sg(info,"ebitda",np.nan))
            pe_v   = det.get("pe",np.nan)
            fwd_pe = safe_float(sg(info,"forwardPE",np.nan))
            ps_r   = safe_float(sg(info,"priceToSalesTrailingTwelveMonths",np.nan))
            pb_r   = safe_float(sg(info,"priceToBook",np.nan))
            ev_eb  = safe_float(sg(info,"enterpriseToEbitda",np.nan))
            de     = safe_float(sg(info,"debtToEquity",np.nan))
            cr     = safe_float(sg(info,"currentRatio",np.nan))
            dy     = safe_float(sg(info,"dividendYield",np.nan))
            rsi_v  = det.get("rsi",np.nan)
            atr_p  = det.get("atr",np.nan)

            metrics_groups = [
                ("MARGINS", [
                    ("Gross Margin",    pct(gm)),
                    ("Operating Margin",pct(om_)),
                    ("Net Margin",      pct(nm)),
                ]),
                ("RETURNS", [
                    ("ROE",    pct(roe)),
                    ("ROA",    pct(roa)),
                ]),
                ("INCOME (TTM)", [
                    ("Revenue",  fmtn(rev,pre="$")),
                    ("Net Income",fmtn(ni,pre="$")),
                    ("FCF",      fmtn(fcf,pre="$")),
                    ("EBITDA",   fmtn(ebitda,pre="$")),
                ]),
                ("VALUATION", [
                    ("Trailing P/E", f"{pe_v:.1f}x" if not np.isnan(pe_v) else "N/A"),
                    ("Forward P/E",  f"{fwd_pe:.1f}x" if not np.isnan(fwd_pe) else "N/A"),
                    ("P/S",          f"{ps_r:.2f}x" if not np.isnan(ps_r) else "N/A"),
                    ("P/B",          f"{pb_r:.2f}x" if not np.isnan(pb_r) else "N/A"),
                    ("EV/EBITDA",    f"{ev_eb:.1f}x" if not np.isnan(ev_eb) else "N/A"),
                ]),
                ("BALANCE SHEET", [
                    ("D/E Ratio",    f"{de/100:.2f}" if not np.isnan(de) else "N/A"),
                    ("Current Ratio",f"{cr:.2f}" if not np.isnan(cr) else "N/A"),
                    ("Dividend Yield",pct(dy) if not np.isnan(dy) else "None"),
                ]),
                ("TECHNICALS", [
                    ("RSI (14D)",  f"{rsi_v:.1f}" if not np.isnan(rsi_v) else "N/A"),
                    ("ATR %",     pct(atr_p) if not np.isnan(atr_p) else "N/A"),
                    ("Beta",      f"{det.get('beta',np.nan):.2f}" if not np.isnan(det.get("beta",np.nan)) else "N/A"),
                ]),
            ]

            for group_name, items in metrics_groups:
                st.markdown(f'<div class="slabel">{group_name}</div>', unsafe_allow_html=True)
                for lbl, val in items:
                    st.markdown(m(lbl, val), unsafe_allow_html=True)

        st.markdown("---")

        # ── ROW 3: Score Breakdown + 7 Powers ────────────────────────────────
        c_bd, c_7p = st.columns([1, 1.6])

        with c_bd:
            st.markdown('<div class="slabel">Score Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(breakdown_bar(res, pw_score), use_container_width=True,
                            config={"displayModeBar":False})

            st.markdown('<div class="slabel">Module Detail</div>', unsafe_allow_html=True)
            modules = [
                ("Quality (30)",    res["q"],    30),
                ("  CRP / GM",      res["sc"]["crp"], 10),
                ("  OM Trend",      res["sc"]["om"],  10),
                ("  FCF Quality",   res["sc"]["fcf"], 10),
                ("Expectations (20)",res["e"],   20),
                ("  Rev CAGR",      res["sc"]["rc"],  10),
                ("  EPS CAGR",      res["sc"]["ec"],  10),
                ("Valuation (20)",  res["v"],    20),
                ("  FCF Yield",     res["sc"]["fy"],   7),
                ("  P/E or P/S",    res["sc"]["pe"],   7),
                ("  PEG",           res["sc"]["pg"],   6),
                ("Technicals (15)", res["tech"], 15),
                ("  Stage 2",       res["sc"]["st2"],  6),
                ("  RSI Zone",      res["sc"]["rsi"],  5),
                ("  Volume",        res["sc"]["vol"],  4),
                ("7 Powers (15)",   pw_score,   15),
            ]
            rows = []
            for lbl, val, mx in modules:
                bar = "█" * int((val/mx)*8) + "░" * (8-int((val/mx)*8)) if mx > 0 else ""
                rows.append({"":lbl, "Score":f"{val:.1f}/{mx}", "▓":bar})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                         column_config={"▓":st.column_config.TextColumn("",width="small")})

        with c_7p:
            st.markdown('<div class="slabel">7 Powers — Helmer Framework (AI Analysis)</div>', unsafe_allow_html=True)

            if powers_ai:
                col_radar, col_list = st.columns([1, 1.5])
                with col_radar:
                    st.plotly_chart(radar_chart(ai_confirmed, ai_partial), use_container_width=True,
                                    config={"displayModeBar":False})
                    confirmed_cnt = len(ai_confirmed)
                    partial_cnt   = len(ai_partial)
                    pw_color = "#10b981" if confirmed_cnt>=3 else "#f59e0b" if confirmed_cnt>=1 else "#ef4444"
                    st.markdown(f"""
                    <div style="text-align:center;background:#0d1525;border:1px solid #1a2540;border-radius:10px;padding:12px;">
                        <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;">Powers Score</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;font-weight:700;color:{pw_color};">{pw_score:.1f}/15</div>
                        <div style="font-size:0.72rem;color:#64748b;">✅ {confirmed_cnt} confirmed · ⚡ {partial_cnt} partial</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_list:
                    for p in ALL_POWERS:
                        pdata   = powers_ai.get(p,{})
                        verdict = pdata.get("verdict","NO").upper()
                        reason  = pdata.get("reasoning","")
                        if verdict.startswith("YES"):
                            cls = "pcard-yes"; icon = "✅"; vc = "#10b981"
                        elif verdict.startswith("PARTIAL"):
                            cls = "pcard-part"; icon = "⚡"; vc = "#f59e0b"
                        else:
                            cls = "pcard-no"; icon = "❌"; vc = "#475569"
                        st.markdown(f"""
                        <div class="pcard {cls}" style="margin-bottom:5px;">
                            <div style="font-size:0.8rem;font-weight:600;color:#e2e8f0;">{icon} {p}</div>
                            <div style="font-size:0.74rem;color:#64748b;margin-top:2px;line-height:1.4;">{reason}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                key_found = bool(get_groq_key())
                if key_found:
                    st.warning("⚠️ Groq API key found but AI analysis failed — Groq may be rate-limited or down. Try again in a moment.")
                else:
                    st.warning("⚠️ GROQ_API_KEY not found in Streamlit secrets. Go to your app → ⋮ → Settings → Secrets and add: `GROQ_API_KEY = \"gsk_...\"` then save.")
                for p in ALL_POWERS:
                    from_7p = {
                        "Scale Economies": "Does unit cost fall as volume grows?",
                        "Network Economies": "Does each new user make it more valuable?",
                        "Counter-Positioning": "Superior model incumbents can't copy?",
                        "Switching Costs": "Pain to switch = pricing power?",
                        "Branding": "Can it charge 20%+ premium over identical product?",
                        "Cornered Resource": "Exclusive access to scarce asset?",
                        "Process Power": "Embedded operational superiority?",
                    }
                    st.markdown(f'<div class="pcard pcard-no"><div style="font-size:0.8rem;font-weight:600;color:#475569;">⬜ {p}</div><div style="font-size:0.72rem;color:#334155;margin-top:2px;">{from_7p.get(p,"")}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── ROW 4: Bull / Bear ────────────────────────────────────────────────
        c_bull, c_bear = st.columns(2)

        with c_bull:
            st.markdown('<div class="slabel">🟢 Bull Case</div>', unsafe_allow_html=True)
            bulls = []
            if res["q"] >= 22: bulls.append(f"Strong financial quality score: {res['q']}/30")
            gm_v = safe_float(sg(info,"grossMargins",np.nan))
            if not np.isnan(gm_v) and gm_v > 0.50: bulls.append(f"High gross margin: {pct(gm_v)}")
            if not np.isnan(det.get("rc",np.nan)) and det["rc"] > 0.15: bulls.append(f"Strong revenue growth: {pct(det['rc'])}")
            fcf_v = safe_float(sg(info,"freeCashflow",np.nan))
            if not np.isnan(fcf_v) and fcf_v > 0: bulls.append(f"Positive FCF: {fmtn(fcf_v,pre='$')}")
            if res["sc"].get("st2",0) >= 6: bulls.append("Stage 2 uptrend: Price > 50D > 200D SMA")
            if not np.isnan(det.get("rsi",np.nan)) and 45<=det["rsi"]<=65: bulls.append(f"RSI {det['rsi']:.0f} in optimal zone")
            if ai_confirmed: bulls.append(f"{len(ai_confirmed)} Helmer power(s): {', '.join(ai_confirmed[:2])}{'…' if len(ai_confirmed)>2 else ''}")
            target = safe_float(sg(info,"targetMeanPrice",np.nan))
            if not np.isnan(target) and not np.isnan(price) and price > 0:
                up = (target/price-1)*100
                if up > 15: bulls.append(f"Analyst target: ${target:.2f} ({up:.0f}% upside)")
            if not bulls: bulls.append("No strong bull signals at current levels.")
            for b in bulls:
                st.markdown(f'<div style="background:#051a0e;border-left:3px solid #10b981;border-radius:0 6px 6px 0;padding:8px 12px;margin:4px 0;font-size:0.82rem;color:#cbd5e1;">✅ {b}</div>', unsafe_allow_html=True)

        with c_bear:
            st.markdown('<div class="slabel">🔴 Bear Case / Risks</div>', unsafe_allow_html=True)
            bears = []
            if not hist.empty:
                try:
                    last = hist.iloc[-1]
                    cl   = float(last["Close"])
                    s200 = float(last.get("SMA200",np.nan))
                    if not np.isnan(s200) and cl < s200:
                        bears.append(f"Price ${cl:.2f} below 200D SMA ${s200:.2f}")
                except: pass
            rsi_v = det.get("rsi",np.nan)
            if not np.isnan(rsi_v):
                if rsi_v > 75: bears.append(f"RSI {rsi_v:.0f} overbought")
                if rsi_v < 30: bears.append(f"RSI {rsi_v:.0f} oversold")
            if stage == "mature":
                pe_v = det.get("pe",np.nan)
                if not np.isnan(pe_v) and pe_v > 40: bears.append(f"High P/E {pe_v:.1f}x")
                if not np.isnan(det.get("atr",np.nan)) and det["atr"] > 0.05:
                    bears.append(f"High volatility: ATR {pct(det['atr'])}")
            beta_v = det.get("beta",np.nan)
            if not np.isnan(beta_v) and beta_v > 2: bears.append(f"High beta {beta_v:.2f}")
            if total_score < 50: bears.append(f"Low score {total_score}/100 — AVOID")
            if not ai_confirmed and powers_ai: bears.append("No Helmer powers confirmed — weak moat")
            if not bears: bears.append("No major red flags at current levels.")
            for b in bears:
                st.markdown(f'<div style="background:#1a0808;border-left:3px solid #ef4444;border-radius:0 6px 6px 0;padding:8px 12px;margin:4px 0;font-size:0.82rem;color:#cbd5e1;">⚠️ {b}</div>', unsafe_allow_html=True)

        # ── ROW 5: Analyst + Description ─────────────────────────────────────
        st.markdown("---")
        c_an, c_desc = st.columns([1,2])

        with c_an:
            st.markdown('<div class="slabel">Analyst Consensus</div>', unsafe_allow_html=True)
            rec     = sg(info,"recommendationKey","")
            target  = safe_float(sg(info,"targetMeanPrice",np.nan))
            n_anal  = safe_float(sg(info,"numberOfAnalystOpinions",np.nan))
            upside  = (target/price-1)*100 if not np.isnan(target) and not np.isnan(price) and price>0 else np.nan
            rc_c    = {"buy":"#10b981","strongbuy":"#10b981","hold":"#f59e0b",
                       "sell":"#ef4444","underperform":"#ef4444"}.get((rec or "").lower().replace(" ",""),"#94a3b8")
            for lbl,val,vc in [
                ("Recommendation", rec.upper() if rec else "N/A", rc_c),
                ("Price Target",   f"${target:.2f}" if not np.isnan(target) else "N/A","#f1f5f9"),
                ("Analysts",       str(int(n_anal)) if not np.isnan(n_anal) else "N/A","#f1f5f9"),
                ("Upside",         f"{upside:.1f}%" if not np.isnan(upside) else "N/A",
                 "#10b981" if not np.isnan(upside) and upside>0 else "#ef4444"),
            ]:
                st.markdown(m(lbl,val,color=vc), unsafe_allow_html=True)

            st.markdown('<div class="slabel">Final Signal</div>', unsafe_allow_html=True)
            logic = {"STRONG BUY":"Score>75 + Price>200D SMA + RSI 45-65 + Volume confirmed.",
                     "BUY":"Score≥65 + Price above 200D SMA.",
                     "NEUTRAL":"Score 50-65. Monitor for improvement.",
                     "AVOID":"Score<50. Wait for recovery evidence."}
            st.markdown(f"""
            <div style="background:#0d1525;border:1px solid {sig_color};border-radius:10px;padding:14px;">
                <div style="font-size:1.1rem;font-weight:700;color:{sig_color};margin-bottom:6px;">{signal}</div>
                <div style="font-size:0.78rem;color:#64748b;line-height:1.5;">{logic.get(signal,"")}</div>
            </div>
            """, unsafe_allow_html=True)

        with c_desc:
            st.markdown('<div class="slabel">About</div>', unsafe_allow_html=True)
            desc = sg(info,"longBusinessSummary","")
            if desc:
                st.markdown(f'<div style="font-size:0.82rem;color:#94a3b8;line-height:1.7;background:#0d1525;border:1px solid #1a2540;border-radius:10px;padding:16px;">{desc[:700]}{"..." if len(desc)>700 else ""}</div>', unsafe_allow_html=True)

            st.markdown('<div class="slabel">Competitors & Partners</div>', unsafe_allow_html=True)
            ind_low = industry.lower()
            peers_map = {
                "consumer electronics": ["Samsung (005930.KS)","Sony (SONY)","Microsoft (MSFT)"],
                "semiconductors":       ["AMD (AMD)","Intel (INTC)","Qualcomm (QCOM)","Broadcom (AVGO)"],
                "software":             ["Microsoft (MSFT)","Salesforce (CRM)","Oracle (ORCL)"],
                "internet":             ["Meta (META)","Alphabet (GOOGL)","Amazon (AMZN)"],
                "drug":                 ["Pfizer (PFE)","AbbVie (ABBV)","Merck (MRK)","Eli Lilly (LLY)"],
                "bank":                 ["JPMorgan (JPM)","Bank of America (BAC)","Wells Fargo (WFC)"],
                "auto":                 ["Tesla (TSLA)","Toyota (TM)","Ford (F)","GM (GM)"],
            }
            peers = []
            for key, pl in peers_map.items():
                if key in ind_low:
                    peers = [p for p in pl if ticker not in p]
                    break
            if peers:
                peer_html = " · ".join([f'<span style="color:#3b82f6;">{p}</span>' for p in peers[:4]])
                st.markdown(f'<div style="font-size:0.8rem;color:#64748b;background:#0d1525;border:1px solid #1a2540;border-radius:8px;padding:10px 14px;">⚔️ {peer_html}</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;color:#1e2a45;font-size:0.68rem;margin-top:24px;padding-top:8px;border-top:1px solid #0f1525;">War Room · Educational purposes only · Not financial advice</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — WATCHLIST
# ════════════════════════════════════════════════════════════════════════════
with tab_watchlist:
    st.markdown('<div class="slabel">Your Watchlist</div>', unsafe_allow_html=True)

    # Add ticker
    c_add, c_btn = st.columns([3,1])
    with c_add:
        new_ticker = st.text_input("", placeholder="Add ticker (e.g. TSLA)", key="wl_add",
                                   label_visibility="collapsed")
    with c_btn:
        if st.button("＋ Add"):
            t = new_ticker.strip().upper()
            if t and t not in st.session_state.watchlist:
                st.session_state.watchlist.append(t)
                st.rerun()

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add a ticker above.")
    else:
        with st.spinner("Loading watchlist..."):
            wl_data = []
            for t in st.session_state.watchlist:
                q = quick_quote(t)
                wl_data.append({"ticker":t, **q})

        # Header row
        hcols = st.columns([1.2,2,1.2,1.2,1.2,1.2,1.2,0.8])
        for col, hdr in zip(hcols,["Ticker","Name","Price","Change","Mkt Cap","P/E","52W Range",""]):
            with col:
                st.markdown(f'<div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.8px;padding:4px 0;">{hdr}</div>', unsafe_allow_html=True)

        for row in wl_data:
            chg_c = "#10b981" if not np.isnan(row["chg"]) and row["chg"]>=0 else "#ef4444"
            chg_str = f"{row['chg']*100:+.2f}%" if not np.isnan(row["chg"]) else "—"
            price_str = f"${row['price']:.2f}" if not np.isnan(row["price"]) else "—"
            pe_str = f"{row['pe']:.1f}x" if not np.isnan(row["pe"]) else "—"
            mc_str = fmtn(row["mktcap"],pre="$")

            # 52W range bar
            lo, hi = row["lo52"], row["hi52"]
            pr = row["price"]
            if not any(np.isnan(x) for x in [lo,hi,pr]) and hi > lo:
                pct_range = (pr-lo)/(hi-lo)*100
                range_bar = f"""
                <div style="font-size:0.68rem;color:#475569;">${lo:.0f}</div>
                <div style="background:#1a2540;border-radius:3px;height:4px;margin:3px 0;">
                    <div style="background:#3b82f6;width:{pct_range:.0f}%;height:4px;border-radius:3px;"></div>
                </div>
                <div style="font-size:0.68rem;color:#475569;">${hi:.0f}</div>
                """
            else:
                range_bar = '<div style="color:#334155;font-size:0.75rem;">—</div>'

            rcols = st.columns([1.2,2,1.2,1.2,1.2,1.2,1.2,0.8])
            with rcols[0]:
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.95rem;font-weight:700;color:#93c5fd;padding:10px 0;">{row["ticker"]}</div>', unsafe_allow_html=True)
            with rcols[1]:
                st.markdown(f'<div style="font-size:0.82rem;color:#94a3b8;padding:10px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["name"][:22]}</div>', unsafe_allow_html=True)
            with rcols[2]:
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.95rem;color:#f1f5f9;padding:10px 0;">{price_str}</div>', unsafe_allow_html=True)
            with rcols[3]:
                st.markdown(f'<div style="font-size:0.9rem;color:{chg_c};font-weight:600;padding:10px 0;">{chg_str}</div>', unsafe_allow_html=True)
            with rcols[4]:
                st.markdown(f'<div style="font-size:0.82rem;color:#94a3b8;padding:10px 0;">{mc_str}</div>', unsafe_allow_html=True)
            with rcols[5]:
                st.markdown(f'<div style="font-size:0.82rem;color:#94a3b8;padding:10px 0;">{pe_str}</div>', unsafe_allow_html=True)
            with rcols[6]:
                st.markdown(range_bar, unsafe_allow_html=True)
            with rcols[7]:
                if st.button("✕", key=f"rm_{row['ticker']}"):
                    st.session_state.watchlist.remove(row["ticker"])
                    st.rerun()

        st.markdown("---")
        if st.button("🔄 Refresh Prices"):
            st.cache_data.clear()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPARE
# ════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown('<div class="slabel">Compare up to 4 stocks side by side</div>', unsafe_allow_html=True)

    cols_input = st.columns(4)
    compare_tickers = []
    defaults = ["AAPL","MSFT","NVDA","GOOGL"]
    for i, col in enumerate(cols_input):
        with col:
            t = st.text_input(f"Stock {i+1}", value=defaults[i], key=f"cmp_{i}")
            compare_tickers.append(t.strip().upper())

    compare_tickers = [t for t in compare_tickers if t]

    if st.button("⚡ Run Comparison"):
        with st.spinner("Analyzing all stocks..."):
            compare_results = []
            for t in compare_tickers:
                try:
                    info_c, hist_c, fin_c, bal_c, cf_c = load(t)
                    hist_c = add_ta(hist_c)
                    res_c  = compute_score(info_c, hist_c, fin_c, bal_c, cf_c)
                    det_c  = res_c["det"]
                    price_c = get_price(info_c, hist_c)
                    prev_c  = safe_float(sg(info_c,"previousClose",np.nan))
                    chg_c_v = (price_c-prev_c)/prev_c if not np.isnan(price_c) and not np.isnan(prev_c) and prev_c>0 else np.nan
                    sig_c, sc_c = get_signal(res_c["base"], hist_c)
                    compare_results.append({
                        "Ticker":    t,
                        "Name":      sg(info_c,"shortName",t),
                        "Price":     f"${price_c:.2f}" if not np.isnan(price_c) else "N/A",
                        "Change":    f"{chg_c_v*100:+.2f}%" if not np.isnan(chg_c_v) else "—",
                        "Score":     res_c["base"],
                        "Signal":    sig_c,
                        "Quality":   res_c["q"],
                        "Expectations": res_c["e"],
                        "Valuation": res_c["v"],
                        "Technicals":res_c["tech"],
                        "Gross Margin": pct(safe_float(sg(info_c,"grossMargins",np.nan))),
                        "Op Margin":    pct(safe_float(sg(info_c,"operatingMargins",np.nan))),
                        "FCF":          fmtn(safe_float(sg(info_c,"freeCashflow",np.nan)),pre="$"),
                        "P/E":          f"{det_c.get('pe',np.nan):.1f}x" if not np.isnan(det_c.get("pe",np.nan)) else "N/A",
                        "Rev CAGR":     pct(det_c.get("rc",np.nan)),
                        "Stage":        det_c.get("stage","mature").upper(),
                        "info": info_c, "hist": hist_c,
                    })
                except Exception as e:
                    st.warning(f"Failed to load {t}: {e}")

        if compare_results:
            # Score comparison chart
            fig_cmp = go.Figure()
            cats = ["Quality","Expectations","Valuation","Technicals"]
            colors_cmp = ["#3b82f6","#10b981","#f59e0b","#a78bfa"]
            for cr, color in zip(compare_results, colors_cmp):
                fig_cmp.add_trace(go.Bar(
                    name=cr["Ticker"],
                    x=cats,
                    y=[cr["Quality"],cr["Expectations"],cr["Valuation"],cr["Technicals"]],
                    marker_color=color, opacity=0.85,
                ))
            fig_cmp.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#070d1a",
                font=dict(color="#94a3b8",family="Inter",size=11),
                height=280, margin=dict(l=20,r=20,t=10,b=10),
                legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#1a2540",tickfont=dict(color="#94a3b8")),
                yaxis=dict(gridcolor="#1a2540",tickfont=dict(color="#64748b")),
            )
            st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar":False})

            # Table
            display_keys = ["Ticker","Name","Price","Change","Score","Signal",
                            "Quality","Expectations","Valuation","Technicals",
                            "Gross Margin","Op Margin","FCF","P/E","Rev CAGR","Stage"]
            df_cmp = pd.DataFrame([{k:r[k] for k in display_keys} for r in compare_results])

            # Color score column
            st.dataframe(
                df_cmp,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Score": st.column_config.ProgressColumn("Score (base)", max_value=85, format="%f"),
                    "Signal": st.column_config.TextColumn("Signal"),
                }
            )

            # Mini price charts
            st.markdown('<div class="slabel">Price History (2Y)</div>', unsafe_allow_html=True)
            chart_cols = st.columns(len(compare_results))
            mc_colors = ["#3b82f6","#10b981","#f59e0b","#a78bfa"]
            for col, cr, color in zip(chart_cols, compare_results, mc_colors):
                with col:
                    if not cr["hist"].empty:
                        st.markdown(f'<div style="font-size:0.8rem;font-weight:600;color:#94a3b8;text-align:center;margin-bottom:4px;">{cr["Ticker"]}</div>', unsafe_allow_html=True)
                        prices = cr["hist"]["Close"].tolist()
                        st.plotly_chart(mini_chart(prices, color), use_container_width=True,
                                        config={"displayModeBar":False})
                        chg_total = (prices[-1]-prices[0])/prices[0]*100 if len(prices)>1 else 0
                        chg_c2 = "#10b981" if chg_total>=0 else "#ef4444"
                        st.markdown(f'<div style="text-align:center;font-size:0.8rem;color:{chg_c2};font-weight:600;">{chg_total:+.1f}% (2Y)</div>', unsafe_allow_html=True)
