"""
War Room Research Terminal
Full-Stack Equity Research + 7 Powers Scoring Engine
Based on Hamilton Helmer's 7 Powers + Security Selection Manual (FUT, Spring 2026)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import requests
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="War Room | Equity Research Terminal",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background-color: #0a0e1a; color: #e2e8f0; }

  .war-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0f1525 100%);
    border: 1px solid #2d3a5e;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
  }
  .war-header h1 { font-size: 2rem; font-weight: 700; color: #f8fafc; margin: 0; }
  .war-header p { color: #94a3b8; margin: 6px 0 0 0; font-size: 0.9rem; }

  .score-card {
    background: linear-gradient(135deg, #1e2540 0%, #151c30 100%);
    border: 1px solid #2d3a5e;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
  }
  .score-giant {
    font-family: 'JetBrains Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
  }
  .score-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

  .signal-STRONG_BUY {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #10b981;
    color: #6ee7b7;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
  }
  .signal-BUY {
    background: linear-gradient(135deg, #1e3a5f, #1e40af);
    border: 1px solid #3b82f6;
    color: #93c5fd;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
  }
  .signal-NEUTRAL {
    background: linear-gradient(135deg, #2d2a1a, #3d3510);
    border: 1px solid #f59e0b;
    color: #fcd34d;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
  }
  .signal-AVOID {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
  }

  .metric-card {
    background: #151c30;
    border: 1px solid #1e2a45;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 4px 0;
  }
  .metric-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; }
  .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.15rem; font-weight: 600; color: #f1f5f9; }
  .metric-sub { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }

  .section-header {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #475569;
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2a45;
  }

  .insight-card {
    background: #0f1525;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
  }
  .insight-label { font-size: 0.7rem; color: #3b82f6; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
  .insight-text { color: #cbd5e1; font-size: 0.88rem; margin-top: 4px; line-height: 1.5; }

  .power-pill {
    display: inline-block;
    background: #1e2a45;
    border: 1px solid #2d3a5e;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    color: #94a3b8;
    margin: 3px;
  }
  .power-pill.active {
    background: #1e3a5f;
    border-color: #3b82f6;
    color: #93c5fd;
  }

  .risk-LOW { color: #34d399; font-weight: 600; }
  .risk-MEDIUM { color: #fbbf24; font-weight: 600; }
  .risk-HIGH { color: #f87171; font-weight: 600; }

  .stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 4px;
  }

  div[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2a45;
  }
  div[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }

  .stTextInput > div > div > input {
    background: #151c30 !important;
    border: 1px solid #2d3a5e !important;
    color: #f1f5f9 !important;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
  }
  .stButton > button {
    background: linear-gradient(135deg, #1e40af, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    width: 100%;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #6366f1) !important;
  }
  .stCheckbox > label { color: #cbd5e1 !important; }
  .stNumberInput > div > div > input {
    background: #151c30 !important;
    border: 1px solid #2d3a5e !important;
    color: #f1f5f9 !important;
    border-radius: 6px;
  }
  .stSlider > div { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS & DATA FETCHERS
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker: str):
    t = yf.Ticker(ticker)
    info = {}
    try:
        info = t.info or {}
    except Exception:
        pass

    hist = pd.DataFrame()
    try:
        hist = t.history(period="2y")
    except Exception:
        pass

    financials = pd.DataFrame()
    try:
        financials = t.financials
    except Exception:
        pass

    balance = pd.DataFrame()
    try:
        balance = t.balance_sheet
    except Exception:
        pass

    cashflow = pd.DataFrame()
    try:
        cashflow = t.cashflow
    except Exception:
        pass

    quarterly_fin = pd.DataFrame()
    try:
        quarterly_fin = t.quarterly_financials
    except Exception:
        pass

    return info, hist, financials, balance, cashflow, quarterly_fin


def safe_get(d, key, default=None):
    try:
        v = d.get(key, default)
        return v if v is not None else default
    except Exception:
        return default


def safe_row(df, row_name, col_idx=0, default=np.nan):
    try:
        if df is None or df.empty:
            return default
        matches = [r for r in df.index if row_name.lower() in r.lower()]
        if not matches:
            return default
        val = df.loc[matches[0]].iloc[col_idx]
        return float(val) if not pd.isna(val) else default
    except Exception:
        return default


def calc_cagr(series, years):
    try:
        series = [x for x in series if x and not np.isnan(x) and x > 0]
        if len(series) < 2:
            return np.nan
        n = min(years, len(series) - 1)
        return (series[0] / series[n]) ** (1 / n) - 1
    except Exception:
        return np.nan


def add_ta(hist):
    if hist.empty:
        return hist
    try:
        hist = hist.copy()
        hist["SMA50"] = hist["Close"].rolling(50).mean()
        hist["SMA200"] = hist["Close"].rolling(200).mean()
        hist["SMA20"] = hist["Close"].rolling(20).mean()
        hist["Vol20"] = hist["Volume"].rolling(20).mean()

        # RSI
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        hist["RSI"] = 100 - (100 / (1 + rs))

        # ATR
        tr = pd.concat([
            hist["High"] - hist["Low"],
            (hist["High"] - hist["Close"].shift()).abs(),
            (hist["Low"] - hist["Close"].shift()).abs()
        ], axis=1).max(axis=1)
        hist["ATR"] = tr.rolling(14).mean()

        # MACD
        ema12 = hist["Close"].ewm(span=12).mean()
        ema26 = hist["Close"].ewm(span=26).mean()
        hist["MACD"] = ema12 - ema26
        hist["Signal"] = hist["MACD"].ewm(span=9).mean()
        hist["MACD_Hist"] = hist["MACD"] - hist["Signal"]

    except Exception:
        pass
    return hist


def pct(val, decimals=1):
    if val is None or np.isnan(val):
        return "N/A"
    return f"{val * 100:.{decimals}f}%"


def fmt(val, decimals=2, prefix="", suffix=""):
    if val is None or np.isnan(val):
        return "N/A"
    if abs(val) >= 1e12:
        return f"{prefix}{val/1e12:.{decimals}f}T{suffix}"
    elif abs(val) >= 1e9:
        return f"{prefix}{val/1e9:.{decimals}f}B{suffix}"
    elif abs(val) >= 1e6:
        return f"{prefix}{val/1e6:.{decimals}f}M{suffix}"
    return f"{prefix}{val:.{decimals}f}{suffix}"


# ─────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def compute_scores(info, hist, financials, balance, cashflow, powers_selected):
    scores = {}
    details = {}

    # ── A. QUALITY & FINANCIAL HEALTH (30 pts) ──────────────────────────────

    # A1. Capital Return Proxy (CRP) = Net Income / (Total Equity + Total Debt) — max 10 pts
    crp_score = 0
    crp_val = np.nan
    try:
        net_income = safe_row(financials, "Net Income")
        total_equity = safe_row(balance, "Stockholders Equity")
        if np.isnan(total_equity):
            total_equity = safe_row(balance, "Total Stockholders Equity")
        total_debt = safe_row(balance, "Total Debt")
        if np.isnan(total_debt):
            total_debt = safe_row(balance, "Long Term Debt", default=0)

        if not any(np.isnan(x) for x in [net_income, total_equity]) and (total_equity + (total_debt if not np.isnan(total_debt) else 0)) != 0:
            crp_val = net_income / (total_equity + (total_debt if not np.isnan(total_debt) else 0))
            if crp_val > 0.20:
                crp_score = 10
            elif crp_val > 0.15:
                crp_score = 8
            elif crp_val > 0.10:
                crp_score = 5
            elif crp_val > 0.05:
                crp_score = 3
            else:
                crp_score = 1
    except Exception:
        pass

    scores["crp"] = crp_score
    details["crp"] = crp_val

    # A2. Operating Margin Trend (5 years) — max 10 pts
    om_score = 0
    om_trend = []
    try:
        if not financials.empty and financials.shape[1] >= 2:
            op_income_rows = [r for r in financials.index if "operating" in r.lower() and "income" in r.lower()]
            rev_rows = [r for r in financials.index if "total revenue" in r.lower() or r.lower() == "revenue"]
            if op_income_rows and rev_rows:
                n_years = min(5, financials.shape[1])
                for i in range(n_years):
                    try:
                        op = float(financials.loc[op_income_rows[0]].iloc[i])
                        rev = float(financials.loc[rev_rows[0]].iloc[i])
                        if rev > 0:
                            om_trend.append(op / rev)
                    except Exception:
                        pass
                if len(om_trend) >= 2:
                    trend_delta = om_trend[0] - om_trend[-1]
                    if trend_delta > 0.03:
                        om_score = 10
                    elif trend_delta > 0:
                        om_score = 7
                    elif trend_delta > -0.02:
                        om_score = 4
                    else:
                        om_score = 1
    except Exception:
        pass

    scores["om_trend"] = om_score
    details["om_trend"] = om_trend

    # A3. FCF Quality (FCF >= 80% of Net Income) — max 10 pts
    fcf_quality_score = 0
    fcf_val = np.nan
    fcf_ratio = np.nan
    try:
        op_cf = safe_row(cashflow, "Operating Cash Flow")
        if np.isnan(op_cf):
            op_cf = safe_row(cashflow, "Total Cash From Operating Activities")
        capex = safe_row(cashflow, "Capital Expenditure")
        if np.isnan(capex):
            capex = safe_row(cashflow, "Capital Expenditures")
        net_inc = safe_row(financials, "Net Income")

        if not np.isnan(op_cf):
            capex_abs = abs(capex) if not np.isnan(capex) else 0
            fcf_val = op_cf - capex_abs
            if not np.isnan(net_inc) and net_inc > 0:
                fcf_ratio = fcf_val / net_inc
                if fcf_ratio >= 0.80:
                    fcf_quality_score = 10
                elif fcf_ratio >= 0.60:
                    fcf_quality_score = 7
                elif fcf_ratio >= 0.40:
                    fcf_quality_score = 4
                elif fcf_ratio > 0:
                    fcf_quality_score = 2
            elif fcf_val > 0:
                fcf_quality_score = 5
    except Exception:
        pass

    scores["fcf_quality"] = fcf_quality_score
    details["fcf"] = fcf_val
    details["fcf_ratio"] = fcf_ratio

    # ── B. EXPECTATIONS (15 pts) ─────────────────────────────────────────────

    # B1. Revenue CAGR — max 7.5 pts
    rev_cagr_score = 0
    rev_cagr = np.nan
    try:
        if not financials.empty:
            rev_rows = [r for r in financials.index if "total revenue" in r.lower() or r.lower() == "revenue"]
            if rev_rows:
                rev_series = []
                for i in range(min(6, financials.shape[1])):
                    try:
                        v = float(financials.loc[rev_rows[0]].iloc[i])
                        rev_series.append(v)
                    except Exception:
                        pass
                rev_cagr = calc_cagr(rev_series, 5)
                if np.isnan(rev_cagr):
                    rev_cagr = calc_cagr(rev_series, 3)
                if not np.isnan(rev_cagr):
                    if rev_cagr > 0.20:
                        rev_cagr_score = 7.5
                    elif rev_cagr > 0.10:
                        rev_cagr_score = 5.5
                    elif rev_cagr > 0.05:
                        rev_cagr_score = 3.5
                    elif rev_cagr > 0:
                        rev_cagr_score = 2
    except Exception:
        pass

    scores["rev_cagr"] = rev_cagr_score
    details["rev_cagr"] = rev_cagr

    # B2. EPS CAGR — max 7.5 pts
    eps_cagr_score = 0
    eps_cagr = np.nan
    try:
        if not financials.empty:
            eps_rows = [r for r in financials.index if "eps" in r.lower() or "earnings per share" in r.lower()]
            if not eps_rows:
                # fallback: derive from net income / shares
                ni_rows = [r for r in financials.index if "net income" in r.lower()]
                shares = safe_get(info, "sharesOutstanding", np.nan)
                if ni_rows and not np.isnan(shares):
                    eps_series = []
                    for i in range(min(6, financials.shape[1])):
                        try:
                            v = float(financials.loc[ni_rows[0]].iloc[i]) / shares
                            eps_series.append(v)
                        except Exception:
                            pass
                    eps_series = [x for x in eps_series if x > 0]
                    eps_cagr = calc_cagr(eps_series, 5)
                    if np.isnan(eps_cagr):
                        eps_cagr = calc_cagr(eps_series, 3)
            if not np.isnan(eps_cagr):
                if eps_cagr > 0.20:
                    eps_cagr_score = 7.5
                elif eps_cagr > 0.10:
                    eps_cagr_score = 5.5
                elif eps_cagr > 0.05:
                    eps_cagr_score = 3.5
                elif eps_cagr > 0:
                    eps_cagr_score = 2
    except Exception:
        pass

    scores["eps_cagr"] = eps_cagr_score
    details["eps_cagr"] = eps_cagr

    # ── C. VALUATION (15 pts) ────────────────────────────────────────────────

    # Weights: FCF Yield 5, P/E vs History 5, PEG 5 (redistributed if missing)
    fcf_yield_score = 0
    pe_hist_score = 0
    peg_score = 0
    peg_available = False

    fcf_yield_val = np.nan
    peg_val = np.nan
    pe_val = safe_get(info, "trailingPE", np.nan)

    try:
        price = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice") or np.nan
        shares = safe_get(info, "sharesOutstanding", np.nan)
        if not np.isnan(fcf_val) and not np.isnan(price) and not np.isnan(shares) and price > 0:
            fcf_yield_val = (fcf_val / shares) / price
            TREASURY = 0.044
            if fcf_yield_val > TREASURY * 2:
                fcf_yield_score = 5
            elif fcf_yield_val > TREASURY:
                fcf_yield_score = 4
            elif fcf_yield_val > TREASURY * 0.5:
                fcf_yield_score = 2
            elif fcf_yield_val > 0:
                fcf_yield_score = 1
    except Exception:
        pass

    try:
        if not np.isnan(pe_val):
            if pe_val < 15:
                pe_hist_score = 5
            elif pe_val < 25:
                pe_hist_score = 4
            elif pe_val < 35:
                pe_hist_score = 2.5
            elif pe_val < 50:
                pe_hist_score = 1
    except Exception:
        pass

    try:
        growth = safe_get(info, "earningsGrowth", np.nan)
        if np.isnan(growth) or growth <= 0:
            growth = eps_cagr
        if not np.isnan(growth) and not np.isnan(pe_val) and growth > 0:
            peg_val = pe_val / (growth * 100)
            peg_available = True
            if peg_val < 1.0:
                peg_score = 5
            elif peg_val < 1.5:
                peg_score = 4
            elif peg_val < 2.0:
                peg_score = 2.5
            elif peg_val < 3.0:
                peg_score = 1
    except Exception:
        pass

    # Redistribute PEG weight if unavailable
    if not peg_available:
        total_val = fcf_yield_score + pe_hist_score
        max_available = 10
        if max_available > 0:
            fcf_yield_score = fcf_yield_score * 15 / max_available
            pe_hist_score = pe_hist_score * 15 / max_available
        peg_score = 0

    scores["fcf_yield"] = fcf_yield_score
    scores["pe_hist"] = pe_hist_score
    scores["peg"] = peg_score
    details["fcf_yield"] = fcf_yield_val
    details["pe"] = pe_val
    details["peg"] = peg_val

    # ── D. TECHNICALS & MOMENTUM (15 pts) ───────────────────────────────────
    # Stage 2: 6 pts | RSI Zone: 5 pts | Volume: 4 pts

    stage2_score = 0
    rsi_score = 0
    vol_score = 0

    rsi_val = np.nan
    atr_pct = np.nan
    beta = safe_get(info, "beta", np.nan)

    try:
        if not hist.empty and len(hist) > 5:
            last = hist.iloc[-1]
            prev = hist.iloc[-2]

            close = last["Close"]
            sma50 = last.get("SMA50", np.nan)
            sma200 = last.get("SMA200", np.nan)
            rsi_val = last.get("RSI", np.nan)
            atr_val = last.get("ATR", np.nan)
            vol = last.get("Volume", np.nan)
            vol20 = last.get("Vol20", np.nan)
            daily_change = close - prev["Close"]

            if not np.isnan(atr_val) and close > 0:
                atr_pct = atr_val / close

            # Stage 2: Price > SMA50 > SMA200 — max 6 pts
            if not any(np.isnan(x) for x in [close, sma50, sma200]):
                if close > sma50 > sma200:
                    stage2_score = 6
                elif close > sma200:
                    stage2_score = 3.5
                elif close > sma50:
                    stage2_score = 2
                else:
                    stage2_score = 0

            # RSI Zone (45–65 optimal) — max 5 pts
            if not np.isnan(rsi_val):
                if 45 <= rsi_val <= 65:
                    rsi_score = 5
                elif 35 <= rsi_val < 45 or 65 < rsi_val <= 75:
                    rsi_score = 3
                elif 25 <= rsi_val < 35:
                    rsi_score = 1.5
                elif rsi_val > 75:
                    rsi_score = 1
                else:
                    rsi_score = 0.5

            # Volume Rule — max 4 pts
            if not any(np.isnan(x) for x in [vol, vol20]):
                if vol > vol20 and daily_change > 0:
                    vol_score = 4
                elif vol > vol20:
                    vol_score = 2
                elif daily_change > 0:
                    vol_score = 2
                else:
                    vol_score = 0.5
    except Exception:
        pass

    scores["stage2"] = stage2_score
    scores["rsi"] = rsi_score
    scores["volume"] = vol_score
    details["rsi"] = rsi_val
    details["atr_pct"] = atr_pct
    details["beta"] = beta

    # ── E. 7 POWERS (30 pts) ────────────────────────────────────────────────
    n_powers = len(powers_selected)
    powers_score = min(30, n_powers * (30 / 7))
    scores["powers"] = powers_score

    # ── TOTALS ───────────────────────────────────────────────────────────────
    quality_total = scores["crp"] + scores["om_trend"] + scores["fcf_quality"]
    expectations_total = scores["rev_cagr"] + scores["eps_cagr"]
    valuation_total = scores["fcf_yield"] + scores["pe_hist"] + scores["peg"]
    technicals_total = min(15, scores["stage2"] + scores["rsi"] + scores["volume"])
    powers_total = scores["powers"]

    total_score = quality_total + expectations_total + valuation_total + technicals_total + powers_total

    return {
        "total": round(total_score, 1),
        "base": round(quality_total + expectations_total + valuation_total + technicals_total, 1),
        "quality": round(quality_total, 1),
        "expectations": round(expectations_total, 1),
        "valuation": round(valuation_total, 1),
        "technicals": round(technicals_total, 1),
        "powers": round(powers_total, 1),
        "scores": scores,
        "details": details,
    }


def get_signal(result, hist):
    total = result["total"]
    details = result["details"]

    # Check technicals for STRONG BUY
    sma200_ok = False
    rsi_ok = False
    vol_ok = False

    try:
        if not hist.empty:
            last = hist.iloc[-1]
            prev = hist.iloc[-2]
            close = last["Close"]
            sma200 = last.get("SMA200", np.nan)
            rsi = last.get("RSI", np.nan)
            vol = last.get("Volume", np.nan)
            vol20 = last.get("Vol20", np.nan)
            daily_change = close - prev["Close"]

            sma200_ok = not np.isnan(sma200) and close > sma200
            rsi_ok = not np.isnan(rsi) and 45 <= rsi <= 65
            vol_ok = not any(np.isnan(x) for x in [vol, vol20]) and vol > vol20 and daily_change > 0
    except Exception:
        pass

    if total > 75 and sma200_ok and rsi_ok and vol_ok:
        return "STRONG BUY", "#10b981"
    elif total > 75 and sma200_ok:
        return "BUY", "#3b82f6"
    elif total >= 60 and sma200_ok:
        return "BUY", "#3b82f6"
    elif total < 60:
        return "AVOID", "#ef4444"
    else:
        return "NEUTRAL", "#f59e0b"


def get_risk_level(details):
    atr_pct = details.get("atr_pct", np.nan)
    beta = details.get("beta", np.nan)

    atr_num = atr_pct if not (atr_pct is None or np.isnan(atr_pct)) else 0.04
    beta_num = beta if not (beta is None or np.isnan(beta)) else 1.0

    if atr_num < 0.03 and beta_num < 1.0:
        return "LOW"
    elif atr_num > 0.05 or beta_num > 1.5:
        return "HIGH"
    else:
        return "MEDIUM"


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,14,26,0.8)",
    font=dict(color="#94a3b8", family="Inter"),
    xaxis=dict(gridcolor="#1e2a45", showgrid=True, linecolor="#2d3a5e"),
    yaxis=dict(gridcolor="#1e2a45", showgrid=True, linecolor="#2d3a5e"),
    margin=dict(l=50, r=20, t=30, b=40),
)


def price_chart(hist, ticker):
    if hist.empty:
        return go.Figure()

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.25, 0.20],
                        vertical_spacing=0.03)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        name="Price",
        increasing_line_color="#10b981", decreasing_line_color="#ef4444",
        increasing_fillcolor="#10b981", decreasing_fillcolor="#ef4444",
    ), row=1, col=1)

    for sma, color, name in [("SMA50", "#f59e0b", "50D"), ("SMA200", "#8b5cf6", "200D")]:
        if sma in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index, y=hist[sma], name=name,
                                     line=dict(color=color, width=1.5, dash="dot"),
                                     opacity=0.8), row=1, col=1)

    # Volume bars
    colors = ["#10b981" if c >= o else "#ef4444"
              for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
                         marker_color=colors, opacity=0.5), row=2, col=1)
    if "Vol20" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Vol20"], name="Vol20",
                                 line=dict(color="#f59e0b", width=1), opacity=0.7), row=2, col=1)

    # RSI
    if "RSI" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], name="RSI",
                                 line=dict(color="#3b82f6", width=1.5)), row=3, col=1)
        fig.add_hrect(y0=45, y1=65, row=3, col=1,
                      fillcolor="rgba(59,130,246,0.08)", line_width=0)
        for level, color in [(30, "#ef4444"), (70, "#ef4444"), (50, "#64748b")]:
            fig.add_hline(y=level, row=3, col=1,
                          line=dict(color=color, width=0.8, dash="dot"))

    fig.update_layout(
        title=f"{ticker} — Price, Volume & RSI",
        **CHART_LAYOUT,
        height=560,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1, font=dict(size=10)),
        xaxis_rangeslider_visible=False,
    )
    return fig


def score_gauge(score):
    color = "#10b981" if score >= 75 else "#3b82f6" if score >= 60 else "#f59e0b" if score >= 45 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"color": color, "size": 48, "family": "JetBrains Mono"}},
        gauge={
            "axis": {"range": [0, 105], "tickcolor": "#475569",
                     "tickfont": {"color": "#475569", "size": 10}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#0a0e1a",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "#1a0a0a"},
                {"range": [60, 75], "color": "#151520"},
                {"range": [75, 115], "color": "#0a1510"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            }
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=20), height=200)
    return fig


def radar_chart(powers_selected, all_powers):
    vals = [1 if p in powers_selected else 0 for p in all_powers]
    vals.append(vals[0])
    cats = all_powers + [all_powers[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats,
        fill="toself",
        fillcolor="rgba(59,130,246,0.15)",
        line=dict(color="#3b82f6", width=2),
        marker=dict(color=["#3b82f6" if v else "#1e2a45" for v in vals], size=8)
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(10,14,26,0.8)",
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(tickfont=dict(color="#94a3b8", size=11),
                             linecolor="#2d3a5e", gridcolor="#1e2a45")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=300
    )
    return fig


def breakdown_bar(result):
    cats = ["Quality\n(30)", "Expectations\n(15)", "Valuation\n(15)", "Technicals\n(15)", "7 Powers\n(30)"]
    maxes = [30, 15, 15, 15, 30]
    vals = [result["quality"], result["expectations"], result["valuation"],
            result["technicals"], result["powers"]]

    colors = []
    for v, m in zip(vals, maxes):
        ratio = v / m if m > 0 else 0
        if ratio >= 0.75:
            colors.append("#10b981")
        elif ratio >= 0.5:
            colors.append("#3b82f6")
        elif ratio >= 0.25:
            colors.append("#f59e0b")
        else:
            colors.append("#ef4444")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cats, y=maxes,
        marker_color="rgba(30,42,69,0.5)",
        marker_line=dict(color="#2d3a5e", width=1),
        name="Max", showlegend=False
    ))
    fig.add_trace(go.Bar(
        x=cats, y=vals,
        marker_color=colors,
        name="Score",
        text=[f"{v:.1f}" for v in vals],
        textposition="inside",
        textfont=dict(color="white", size=12, family="JetBrains Mono"),
        showlegend=False
    ))
    fig.update_layout(
        barmode="overlay",
        **CHART_LAYOUT,
        height=220,
        title="Score Breakdown by Module",
        yaxis_title="Points",
        xaxis_tickfont=dict(size=10),
    )
    return fig


def om_trend_chart(om_trend):
    if not om_trend:
        return None
    years = list(range(len(om_trend), 0, -1))
    labels = [f"FY-{y-1}" if y > 1 else "FY0 (latest)" for y in years]
    pcts = [v * 100 for v in om_trend]
    fig = go.Figure(go.Scatter(
        x=labels[::-1], y=pcts[::-1],
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=2),
        marker=dict(color="#8b5cf6", size=8),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.08)"
    ))
    fig.update_layout(**CHART_LAYOUT, height=180, title="Operating Margin Trend (%)",
                      yaxis_ticksuffix="%")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── HEADER ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="war-header">
        <h1>⚔️ War Room Research Terminal</h1>
        <p>Full-Stack Equity Analysis · Quality(30) · Expectations(15) · Valuation(15) · Technicals(15) · 7 Powers(30) = 105 pts · FUT Investment Portfolio Management · Spring 2026</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎯 Target Stock")
        ticker_input = st.text_input("", value="AAPL", placeholder="e.g. NVDA", label_visibility="collapsed")
        ticker = ticker_input.strip().upper()

        st.markdown('<div class="section-header">Sanity Check</div>', unsafe_allow_html=True)
        business_model = st.text_area("Explain this business model in one sentence:",
                                       placeholder="e.g. Apple sells premium consumer electronics and earns recurring revenue through its software/services ecosystem.",
                                       height=80)

        st.markdown('<div class="section-header">Portfolio Context</div>', unsafe_allow_html=True)
        portfolio_size = st.number_input("Portfolio Size ($)", min_value=1000, value=100000, step=1000)
        entry_price_input = st.number_input("Entry Price ($)", min_value=0.01, value=0.0, step=0.01,
                                             help="Leave 0 to use current market price")

        st.markdown('<div class="section-header">7 Powers · Helmer (30 pts)</div>', unsafe_allow_html=True)
        all_powers = ["Scale Economies", "Network Economies", "Counter-Positioning",
                      "Switching Costs", "Branding", "Cornered Resource", "Process Power"]

        powers_selected = []
        power_descs = {
            "Scale Economies": "Lower unit costs at volume",
            "Network Economies": "Value grows with users",
            "Counter-Positioning": "Superior model incumbent won't copy",
            "Switching Costs": "Pain to leave = pricing power",
            "Branding": "Price premium from perception",
            "Cornered Resource": "Exclusive access to key asset",
            "Process Power": "Embedded operational superiority"
        }
        for p in all_powers:
            if st.checkbox(p, help=power_descs[p]):
                powers_selected.append(p)

        analyze_btn = st.button("⚡ Run War Room Analysis")

    # ── MAIN CONTENT ─────────────────────────────────────────────────────────
    if not analyze_btn:
        st.markdown("""
        <div style="text-align:center; padding: 80px 20px; color: #475569;">
            <div style="font-size: 4rem; margin-bottom: 16px;">⚔️</div>
            <div style="font-size: 1.4rem; color: #64748b; font-weight: 600;">Enter a ticker and click Run War Room Analysis</div>
            <div style="font-size: 0.9rem; margin-top: 12px; color: #334155;">
                Scores across Quality · Expectations · Valuation · Technicals · 7 Powers
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── SANITY CHECK ─────────────────────────────────────────────────────────
    if not business_model.strip():
        st.warning("⚠️ **Sanity Check Required:** Complete the 'Explain this business model in one sentence' field before proceeding. If you can't describe the business simply, you don't understand it well enough to invest.")
        return

    # ── LOAD DATA ────────────────────────────────────────────────────────────
    with st.spinner(f"Loading {ticker} data..."):
        try:
            info, hist_raw, financials, balance, cashflow, quarterly_fin = fetch_data(ticker)
            hist = add_ta(hist_raw)
        except Exception as e:
            st.error(f"Failed to load data for **{ticker}**: {e}")
            return

    if not info and hist.empty:
        st.error(f"No data found for **{ticker}**. Check the ticker symbol.")
        return

    # ── SCORE ────────────────────────────────────────────────────────────────
    result = compute_scores(info, hist, financials, balance, cashflow, powers_selected)
    signal, signal_color = get_signal(result, hist)
    risk_level = get_risk_level(result["details"])
    details = result["details"]

    # ── POSITION SIZING ──────────────────────────────────────────────────────
    current_price = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice") or np.nan
    entry_price = entry_price_input if entry_price_input > 0 else (current_price or np.nan)

    position_size = np.nan
    stop_loss = np.nan
    shares_qty = np.nan
    try:
        if not hist.empty and not np.isnan(entry_price):
            atr_val = hist["ATR"].iloc[-1] if "ATR" in hist.columns else np.nan
            if not np.isnan(atr_val):
                stop_loss = entry_price - 2 * atr_val
                risk_per_share = entry_price - stop_loss
                if risk_per_share > 0:
                    risk_dollars = portfolio_size * 0.01
                    shares_qty = risk_dollars / risk_per_share
                    position_size = shares_qty * entry_price
    except Exception:
        pass

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1: Signal + Score + Company Overview
    # ─────────────────────────────────────────────────────────────────────────
    col_sig, col_gauge, col_info = st.columns([1.2, 1.5, 2])

    with col_sig:
        st.markdown(f'<div class="signal-{signal.replace(" ", "_")}">{signal}</div>', unsafe_allow_html=True)
        st.markdown("")

        # Score pillbox
        st.markdown(f"""
        <div class="score-card">
            <div class="score-giant" style="color:{signal_color};">{result['total']}</div>
            <div class="score-label">Composite Score / 105</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        risk_class = f"risk-{risk_level}"
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="metric-label">Risk Level</div>
            <div class="metric-value {risk_class}" style="font-size:1.4rem;">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        st.plotly_chart(score_gauge(result["total"]), use_container_width=True, config={"displayModeBar": False})

    with col_info:
        name = safe_get(info, "longName", ticker)
        sector = safe_get(info, "sector", "—")
        industry = safe_get(info, "industry", "—")
        market_cap = safe_get(info, "marketCap", np.nan)
        prev_close = safe_get(info, "previousClose", np.nan)
        day_change = (current_price - prev_close) / prev_close if not any(
            [v is None or (isinstance(v, float) and np.isnan(v)) for v in [current_price, prev_close]]) and prev_close else np.nan
        day_change_color = "#10b981" if (not np.isnan(day_change) if isinstance(day_change, float) else False) and day_change >= 0 else "#ef4444"

        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <div style="font-size:1.5rem; font-weight:700; color:#f1f5f9;">{name}</div>
            <div style="font-size:0.82rem; color:#64748b;">{sector} · {industry}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            (c1, "Price", f"${current_price:.2f}" if current_price and not np.isnan(current_price) else "N/A", ""),
            (c2, "Day Chg", pct(day_change), ""),
            (c3, "Mkt Cap", fmt(market_cap, prefix="$"), ""),
            (c4, "Beta", f"{details.get('beta', np.nan):.2f}" if not np.isnan(details.get('beta', np.nan)) else "N/A", ""),
        ]
        for col, label, val, sub in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        # Business model thesis
        st.markdown(f"""
        <div class="insight-card" style="margin-top:10px;">
            <div class="insight-label">📋 Business Model Thesis</div>
            <div class="insight-text">"{business_model}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 2: Score Breakdown Bar + Price Chart
    # ─────────────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.plotly_chart(breakdown_bar(result), use_container_width=True, config={"displayModeBar": False})

        # Score detail table
        st.markdown('<div class="section-header">Module Drill-Down</div>', unsafe_allow_html=True)
        modules = [
            ("Quality / 30", result["quality"], 30),
            ("  ↳ CRP", result["scores"]["crp"], 10),
            ("  ↳ OM Trend", result["scores"]["om_trend"], 10),
            ("  ↳ FCF Quality", result["scores"]["fcf_quality"], 10),
            ("Expectations / 15", result["expectations"], 15),
            ("  ↳ Rev CAGR", result["scores"]["rev_cagr"], 7.5),
            ("  ↳ EPS CAGR", result["scores"]["eps_cagr"], 7.5),
            ("Valuation / 15", result["valuation"], 15),
            ("  ↳ FCF Yield", result["scores"]["fcf_yield"], 5),
            ("  ↳ P/E vs Hist", result["scores"]["pe_hist"], 5),
            ("  ↳ PEG", result["scores"]["peg"], 5),
            ("Technicals / 15", result["technicals"], 15),
            ("  ↳ Stage 2", result["scores"]["stage2"], 6),
            ("  ↳ RSI Zone", result["scores"]["rsi"], 5),
            ("  ↳ Volume", result["scores"]["volume"], 4),
            ("7 Powers / 30", result["powers"], 30),
        ]
        rows = []
        for label, val, mx in modules:
            bar_len = int((val / mx) * 10) if mx > 0 else 0
            bar = "█" * bar_len + "░" * (10 - bar_len)
            rows.append({"Module": label, "Score": f"{val:.1f}/{mx}", "Bar": bar})
        df_scores = pd.DataFrame(rows)
        st.dataframe(df_scores, hide_index=True, use_container_width=True,
                     column_config={"Bar": st.column_config.TextColumn("Progress", width="medium")})

    with col_right:
        if not hist.empty:
            st.plotly_chart(price_chart(hist, ticker), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Price chart unavailable — no historical data.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 3: Key Metrics + 7 Powers Radar + OM Trend
    # ─────────────────────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([1.5, 1.2, 1.3])

    with col_a:
        st.markdown('<div class="section-header">Key Financial Metrics</div>', unsafe_allow_html=True)

        crp_val = details.get("crp", np.nan)
        fcf_val = details.get("fcf", np.nan)
        fcf_ratio = details.get("fcf_ratio", np.nan)
        fcf_yield = details.get("fcf_yield", np.nan)
        pe_val = details.get("pe", np.nan)
        peg_val = details.get("peg", np.nan)
        rev_cagr = details.get("rev_cagr", np.nan)
        eps_cagr = details.get("eps_cagr", np.nan)
        rsi_val = details.get("rsi", np.nan)
        atr_pct = details.get("atr_pct", np.nan)

        gross_margin = safe_get(info, "grossMargins", np.nan)
        op_margin = safe_get(info, "operatingMargins", np.nan)
        net_margin = safe_get(info, "profitMargins", np.nan)
        rev_growth = safe_get(info, "revenueGrowth", np.nan)
        debt_equity = safe_get(info, "debtToEquity", np.nan)

        kv_items = [
            ("Capital Return Proxy (CRP)", pct(crp_val), "Net Income / (Equity + Debt). >15% = excellent"),
            ("FCF (Manual)", fmt(fcf_val, prefix="$"), "Operating CF − CapEx"),
            ("FCF / Net Income Ratio", pct(fcf_ratio), "≥80% = high earnings quality"),
            ("FCF Yield", pct(fcf_yield), "vs 4.4% Treasury benchmark"),
            ("Trailing P/E", f"{pe_val:.1f}x" if not np.isnan(pe_val) else "N/A", ""),
            ("PEG Ratio", f"{peg_val:.2f}" if not np.isnan(peg_val) else "N/A (redistributed)", "<1.0 = attractive"),
            ("Rev CAGR (5Y→3Y)", pct(rev_cagr), "Hierarchy: 5Y preferred"),
            ("EPS CAGR (5Y→3Y)", pct(eps_cagr), ""),
            ("Gross Margin", pct(gross_margin), ""),
            ("Operating Margin", pct(op_margin), ""),
            ("Net Margin", pct(net_margin), ""),
            ("D/E Ratio", f"{debt_equity/100:.2f}" if not np.isnan(debt_equity) else "N/A", "<0.5 = conservative"),
            ("RSI (14-day)", f"{rsi_val:.1f}" if not np.isnan(rsi_val) else "N/A", "45–65 = optimal zone"),
            ("ATR %", pct(atr_pct), "<3% = LOW risk"),
        ]
        for label, val, hint in kv_items:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
                {"<div class='metric-sub'>" + hint + "</div>" if hint else ""}
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-header">7 Powers Radar · Helmer (30 pts)</div>', unsafe_allow_html=True)
        st.plotly_chart(radar_chart(powers_selected, all_powers), use_container_width=True,
                        config={"displayModeBar": False})

        # Powers pills
        st.markdown("**Active Powers:**")
        pills_html = ""
        for p in all_powers:
            cls = "active" if p in powers_selected else ""
            pills_html += f'<span class="power-pill {cls}">{p}</span>'
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)

        st.markdown("")
        if powers_selected:
            power_pts = result["powers"]
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-label">Powers Score</div>
                <div class="metric-value" style="color:#3b82f6;">{power_pts:.1f} / 30</div>
                <div class="metric-sub">{len(powers_selected)} of 7 powers identified</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No powers selected. Check applicable powers in the sidebar.")

    with col_c:
        st.markdown('<div class="section-header">Operating Margin Trend</div>', unsafe_allow_html=True)
        om_fig = om_trend_chart(details.get("om_trend", []))
        if om_fig:
            st.plotly_chart(om_fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Operating margin trend unavailable.")

        st.markdown('<div class="section-header">Position Sizing (1% Risk Rule)</div>', unsafe_allow_html=True)

        ps_items = [
            ("Entry Price", f"${entry_price:.2f}" if not np.isnan(entry_price) else "N/A"),
            ("Stop-Loss (2× ATR)", f"${stop_loss:.2f}" if not np.isnan(stop_loss) else "N/A"),
            ("Risk per Share", f"${(entry_price-stop_loss):.2f}" if not np.isnan(stop_loss) else "N/A"),
            ("1% Portfolio Risk ($)", f"${portfolio_size*0.01:,.0f}"),
            ("Shares to Buy", f"{shares_qty:.0f}" if not np.isnan(shares_qty) else "N/A"),
            ("Position Size ($)", f"${position_size:,.0f}" if not np.isnan(position_size) else "N/A"),
            ("% of Portfolio", f"{position_size/portfolio_size*100:.1f}%" if not np.isnan(position_size) else "N/A"),
        ]
        for label, val in ps_items:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 4: Bull / Bear / Daily Insight
    # ─────────────────────────────────────────────────────────────────────────
    col_bull, col_bear = st.columns(2)

    with col_bull:
        st.markdown('<div class="section-header">🟢 Automated Bull Case Signals</div>', unsafe_allow_html=True)
        bull_points = []

        if result["quality"] >= 20:
            bull_points.append("Strong financial health: Quality module scores ≥20/30")
        if not np.isnan(details.get("crp", np.nan)) and details["crp"] > 0.15:
            bull_points.append(f"High Capital Return Proxy: {pct(details['crp'])} (>15% threshold)")
        if details.get("fcf_ratio", np.nan) and not np.isnan(details["fcf_ratio"]) and details["fcf_ratio"] >= 0.80:
            bull_points.append(f"High FCF quality: FCF is {pct(details['fcf_ratio'])} of Net Income")
        if not np.isnan(details.get("rev_cagr", np.nan)) and details["rev_cagr"] > 0.10:
            bull_points.append(f"Strong revenue CAGR: {pct(details['rev_cagr'])}")
        if not np.isnan(details.get("fcf_yield", np.nan)) and details["fcf_yield"] > 0.044:
            bull_points.append(f"FCF Yield {pct(details['fcf_yield'])} beats 4.4% Treasury benchmark")
        if result["scores"].get("stage2", 0) == 12:
            bull_points.append("Stage 2 Uptrend: Price > 50D SMA > 200D SMA (strongest technical signal)")
        if not np.isnan(details.get("rsi", np.nan)) and 45 <= details["rsi"] <= 65:
            bull_points.append(f"RSI {details['rsi']:.1f} in optimal 45–65 trend zone")
        if powers_selected:
            bull_points.append(f"{len(powers_selected)} Helmer Power(s) identified: {', '.join(powers_selected[:3])}{'...' if len(powers_selected) > 3 else ''}")

        if not bull_points:
            bull_points.append("No strong bull signals detected at current levels.")

        for pt in bull_points:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color:#10b981;">
                <div class="insight-text">✅ {pt}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_bear:
        st.markdown('<div class="section-header">🔴 Automated Bear Case / Risk Flags</div>', unsafe_allow_html=True)
        bear_points = []

        if not hist.empty:
            last = hist.iloc[-1]
            sma200 = last.get("SMA200", np.nan)
            close = last["Close"]
            if not np.isnan(sma200) and close < sma200:
                bear_points.append(f"Price ${close:.2f} is BELOW 200D SMA ${sma200:.2f} — AVOID signal triggered")

        if not np.isnan(details.get("rsi", np.nan)) and details["rsi"] > 70:
            bear_points.append(f"RSI {details['rsi']:.1f} is overbought (>70) — momentum may be exhausted")
        if not np.isnan(details.get("rsi", np.nan)) and details["rsi"] < 30:
            bear_points.append(f"RSI {details['rsi']:.1f} is oversold (<30) — potential downtrend")
        if not np.isnan(details.get("atr_pct", np.nan)) and details["atr_pct"] > 0.05:
            bear_points.append(f"HIGH volatility: ATR% is {pct(details['atr_pct'])} (>5% threshold)")
        if not np.isnan(details.get("beta", np.nan)) and details["beta"] > 1.5:
            bear_points.append(f"High Beta ({details['beta']:.2f}) — 50%+ more volatile than market")
        if result["scores"].get("fcf_quality", 0) < 3:
            bear_points.append("Weak FCF quality — earnings may not be converting to real cash")
        if not np.isnan(details.get("peg", np.nan)) and details["peg"] > 2.5:
            bear_points.append(f"Elevated PEG Ratio {details['peg']:.2f} — expensive relative to growth")
        if not np.isnan(details.get("pe", np.nan)) and details["pe"] > 40:
            bear_points.append(f"High P/E {details['pe']:.1f}x — demanding valuation requires execution")
        if result["total"] < 60:
            bear_points.append(f"Composite score {result['total']} is below 60 threshold — AVOID signal")

        if not bear_points:
            bear_points.append("No critical bear flags detected at current levels.")

        for pt in bear_points:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color:#ef4444;">
                <div class="insight-text">⚠️ {pt}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 5: Signal Summary Card
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Final Signal Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    summary_items = [
        (c1, "Signal", signal, signal_color),
        (c2, "Composite Score", f"{result['total']} / 105", signal_color),
        (c3, "Risk Level", risk_level, "#34d399" if risk_level == "LOW" else "#fbbf24" if risk_level == "MEDIUM" else "#f87171"),
        (c4, "7 Powers", f"{len(powers_selected)} / 7  ({result['powers']:.0f}pts)", "#3b82f6"),
        (c5, "Shares (1% Rule)", f"{shares_qty:.0f}" if not np.isnan(shares_qty) else "N/A", "#94a3b8"),
    ]
    for col, label, val, color in summary_items:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}; font-size:1.2rem;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SIGNAL LOGIC EXPLANATION ─────────────────────────────────────────────
    st.markdown("")
    signal_logic = {
        "STRONG BUY": "Score > 75 AND Price > 200D SMA AND RSI 45–65 AND Volume/Price confirmation all met.",
        "BUY": "Score ≥ 60 AND Price > 200D SMA. Consider accumulating on pullbacks.",
        "NEUTRAL": "Score 60–75 but technical conditions not fully met. Monitor for improvement.",
        "AVOID": "Score < 60 OR Price below 200D SMA. Do not enter — wait for evidence of recovery.",
    }
    st.markdown(f"""
    <div class="insight-card" style="border-left-color:{signal_color};">
        <div class="insight-label">Signal Rationale</div>
        <div class="insight-text">{signal_logic.get(signal, '')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; color:#334155; font-size:0.72rem; margin-top:24px; padding-top:12px; border-top: 1px solid #1e2a45;">
        War Room Terminal · Quality(30) + Expectations(15) + Valuation(15) + Technicals(15) + 7 Powers(30) = 105 pts · FUT · Spring 2026 · For Educational Purposes Only — Not Financial Advice
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
