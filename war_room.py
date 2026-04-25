"""
War Room Research Terminal
Full-Stack Equity Research + 7 Powers Scoring Engine
Based on Hamilton Helmer's 7 Powers Framework
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

st.set_page_config(page_title="War Room | Equity Research Terminal", page_icon="⚔️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
  html,body,[class*="css"]{font-family:'Inter',sans-serif;}
  .stApp{background-color:#0a0e1a;color:#e2e8f0;}
  .war-header{background:linear-gradient(135deg,#1a1f35,#0f1525);border:1px solid #2d3a5e;border-radius:12px;padding:24px 32px;margin-bottom:24px;}
  .war-header h1{font-size:2rem;font-weight:700;color:#f8fafc;margin:0;}
  .war-header p{color:#94a3b8;margin:6px 0 0;font-size:0.88rem;}
  .score-card{background:linear-gradient(135deg,#1e2540,#151c30);border:1px solid #2d3a5e;border-radius:16px;padding:20px;text-align:center;}
  .score-giant{font-family:'JetBrains Mono',monospace;font-size:4rem;font-weight:700;line-height:1;}
  .score-label{font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}
  .signal-STRONG_BUY{background:linear-gradient(135deg,#064e3b,#065f46);border:1px solid #10b981;color:#6ee7b7;padding:12px 24px;border-radius:10px;font-weight:700;font-size:1.1rem;text-align:center;}
  .signal-BUY{background:linear-gradient(135deg,#1e3a5f,#1e40af);border:1px solid #3b82f6;color:#93c5fd;padding:12px 24px;border-radius:10px;font-weight:700;font-size:1.1rem;text-align:center;}
  .signal-NEUTRAL{background:linear-gradient(135deg,#2d2a1a,#3d3510);border:1px solid #f59e0b;color:#fcd34d;padding:12px 24px;border-radius:10px;font-weight:700;font-size:1.1rem;text-align:center;}
  .signal-AVOID{background:linear-gradient(135deg,#450a0a,#7f1d1d);border:1px solid #ef4444;color:#fca5a5;padding:12px 24px;border-radius:10px;font-weight:700;font-size:1.1rem;text-align:center;}
  .metric-card{background:#151c30;border:1px solid #1e2a45;border-radius:10px;padding:12px 14px;margin:3px 0;}
  .metric-label{font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;}
  .metric-value{font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:600;color:#f1f5f9;}
  .metric-sub{font-size:0.7rem;color:#94a3b8;margin-top:2px;}
  .section-header{font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;color:#475569;margin:18px 0 8px;padding-bottom:5px;border-bottom:1px solid #1e2a45;}
  .insight-card{background:#0f1525;border-left:3px solid #3b82f6;border-radius:0 8px 8px 0;padding:10px 14px;margin:6px 0;}
  .insight-label{font-size:0.68rem;color:#3b82f6;text-transform:uppercase;letter-spacing:1px;font-weight:600;}
  .insight-text{color:#cbd5e1;font-size:0.85rem;margin-top:3px;line-height:1.5;}
  .news-card{background:#0f1525;border:1px solid #1e2a45;border-radius:8px;padding:12px 14px;margin:6px 0;}
  .news-title{color:#e2e8f0;font-size:0.88rem;font-weight:600;line-height:1.4;}
  .news-meta{color:#475569;font-size:0.72rem;margin-top:4px;}
  .power-card{background:#0f1525;border:1px solid #1e2a45;border-radius:8px;padding:10px 14px;margin:5px 0;}
  .power-card.active{border-color:#3b82f6;background:#0d1929;}
  .power-name{font-size:0.82rem;font-weight:600;color:#93c5fd;}
  .power-verdict{font-size:0.78rem;color:#94a3b8;margin-top:3px;line-height:1.4;}
  .power-verdict.filled{color:#cbd5e1;}
  .comp-card{background:#0f1525;border:1px solid #1e2a45;border-radius:8px;padding:10px 14px;margin:4px 0;}
  .part-card{background:#0a1a14;border:1px solid #1e3a2e;border-radius:8px;padding:10px 14px;margin:4px 0;}
  .risk-LOW{color:#34d399;font-weight:600;}
  .risk-MEDIUM{color:#fbbf24;font-weight:600;}
  .risk-HIGH{color:#f87171;font-weight:600;}
  div[data-testid="stSidebar"]{background:#0d1220 !important;border-right:1px solid #1e2a45;}
  .stTextInput>div>div>input{background:#151c30 !important;border:1px solid #2d3a5e !important;color:#f1f5f9 !important;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:1.1rem;}
  .stTextArea>div>textarea{background:#151c30 !important;border:1px solid #2d3a5e !important;color:#f1f5f9 !important;border-radius:8px;font-size:0.85rem;}
  .stButton>button{background:linear-gradient(135deg,#1e40af,#4f46e5) !important;color:white !important;border:none !important;border-radius:8px !important;font-weight:600 !important;padding:10px 28px !important;width:100%;}
  .stNumberInput>div>div>input{background:#151c30 !important;border:1px solid #2d3a5e !important;color:#f1f5f9 !important;border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
ALL_POWERS = ["Scale Economies","Network Economies","Counter-Positioning",
              "Switching Costs","Branding","Cornered Resource","Process Power"]
POWER_GUIDE = {
    "Scale Economies":     "Does unit cost fall meaningfully as volume grows? Is competitor scale prohibitively expensive to replicate?",
    "Network Economies":   "Does each new user make the product more valuable for all others? Direct, indirect, or data network effect?",
    "Counter-Positioning": "Does the company use a superior model that the incumbent won't copy without cannibalizing itself?",
    "Switching Costs":     "Would a customer incur significant financial, procedural, or data-migration pain to switch suppliers?",
    "Branding":            "Can it charge a measurable premium over an objectively identical competitor? Would customers pay 20% more?",
    "Cornered Resource":   "Does the company have exclusive access to a scarce asset — talent, IP, data, license, or natural resource?",
    "Process Power":       "Has it built embedded operational processes that consistently outperform peers and resist imitation?",
}
INDUSTRY_PEERS = {
    "consumer electronics":      ["Samsung (005930.KS)","Sony (SONY)","Microsoft (MSFT)","Xiaomi (1810.HK)","Google (GOOGL)"],
    "semiconductors":            ["NVIDIA (NVDA)","AMD (AMD)","Intel (INTC)","Qualcomm (QCOM)","Broadcom (AVGO)"],
    "software":                  ["Microsoft (MSFT)","Salesforce (CRM)","Oracle (ORCL)","SAP (SAP)","ServiceNow (NOW)"],
    "internet":                  ["Meta (META)","Alphabet (GOOGL)","Amazon (AMZN)","Snap (SNAP)","Pinterest (PINS)"],
    "drug":                      ["Johnson & Johnson (JNJ)","Pfizer (PFE)","AbbVie (ABBV)","Merck (MRK)","Eli Lilly (LLY)"],
    "retail":                    ["Amazon (AMZN)","Walmart (WMT)","Target (TGT)","Costco (COST)","Home Depot (HD)"],
    "bank":                      ["JPMorgan (JPM)","Bank of America (BAC)","Wells Fargo (WFC)","Citigroup (C)","Goldman Sachs (GS)"],
    "auto":                      ["Tesla (TSLA)","Toyota (TM)","Ford (F)","GM (GM)","Stellantis (STLA)"],
    "oil":                       ["ExxonMobil (XOM)","Chevron (CVX)","Shell (SHEL)","BP (BP)","ConocoPhillips (COP)"],
    "aerospace":                 ["Boeing (BA)","Lockheed Martin (LMT)","Raytheon (RTX)","Northrop (NOC)","L3Harris (LHX)"],
    "telecom":                   ["AT&T (T)","Verizon (VZ)","T-Mobile (TMUS)","Comcast (CMCSA)","Charter (CHTR)"],
    "cloud":                     ["AWS / Amazon (AMZN)","Microsoft Azure (MSFT)","Google Cloud (GOOGL)","Oracle (ORCL)","IBM (IBM)"],
}
INDUSTRY_PARTNERS = {
    "consumer electronics":      ["TSMC (chip manufacturing)","Samsung (displays & memory)","Foxconn (assembly)","Corning (glass)","Broadcom (wireless chips)"],
    "semiconductors":            ["TSMC (foundry)","ASML (EUV lithography)","ARM (IP licensing)","Applied Materials (equipment)","Cloud hyperscalers (customers)"],
    "software":                  ["AWS / Azure / GCP (cloud infra)","Major SIs: Accenture, Deloitte","Reseller / VAR channel partners","ISV ecosystem"],
    "internet":                  ["Major advertisers (revenue)","Content creators (supply-side)","Cloud providers (infra)","Telecom carriers (distribution)"],
    "drug":                      ["CROs (clinical trials)","CMOs (contract manufacturing)","McKesson / AmerisourceBergen (distribution)","Hospital systems"],
    "bank":                      ["Federal Reserve (regulatory)","Visa / Mastercard (card networks)","Fintech partners","Institutional clients"],
    "auto":                      ["CATL / Panasonic (batteries)","NVIDIA / Mobileye (ADAS chips)","Dealership networks","Steel & aluminum suppliers"],
    "oil":                       ["OPEC+ (supply coordination)","Pipeline operators","Refiners","Engineering firms: Halliburton, SLB"],
    "aerospace":                 ["US DoD / NATO (primary customers)","Tier-1 suppliers: Spirit AeroSystems, Safran","Engine makers: GE, Rolls-Royce","FAA (regulatory)"],
    "telecom":                   ["Nokia / Ericsson / Samsung (network equipment)","Handset makers (Apple, Samsung)","Content providers (streaming)","Tower REITs"],
}

# ── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker):
    t = yf.Ticker(ticker)
    info, hist, fin, bal, cf, news = {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []
    try: info = t.info or {}
    except Exception: pass
    try: hist = t.history(period="2y", auto_adjust=True)
    except Exception: pass
    try: fin  = t.financials
    except Exception: pass
    try: bal  = t.balance_sheet
    except Exception: pass
    try: cf   = t.cashflow
    except Exception: pass
    try: news = t.news or []
    except Exception: pass
    return info, hist, fin, bal, cf, news

@st.cache_data(ttl=600, show_spinner=False)
def ai_analyze_7_powers(ticker, company_name, sector, industry, description,
                         gross_margin, op_margin, rev_cagr, market_cap, stage):
    """Call Groq API (free) to automatically analyze which of Helmer's 7 Powers apply."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return None

        prompt = f"""You are an expert equity analyst trained in Hamilton Helmer's 7 Powers framework.

Analyze this company and determine which of the 7 Powers apply. Be specific, concise, and honest — if a power does NOT apply, say so clearly.

COMPANY: {company_name} ({ticker})
SECTOR: {sector}
INDUSTRY: {industry}
STAGE: {stage}
GROSS MARGIN: {gross_margin}
OPERATING MARGIN: {op_margin}
REVENUE CAGR: {rev_cagr}
MARKET CAP: {market_cap}
BUSINESS DESCRIPTION: {description[:600] if description else 'N/A'}

For each of the 7 Powers below, provide:
1. VERDICT: "YES - confirmed" / "PARTIAL - weak/emerging" / "NO - does not apply"
2. REASONING: 1-2 sentences max explaining why

Respond ONLY in this exact JSON format, no markdown, no extra text:
{{
  "Scale Economies": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Network Economies": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Counter-Positioning": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Switching Costs": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Branding": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Cornered Resource": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}},
  "Process Power": {{"verdict": "YES/PARTIAL/NO", "reasoning": "..."}}
}}"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 1000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = response.json()
        raw = data["choices"][0]["message"]["content"]
        raw = raw.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception:
        return None


def get_price(info, hist):
    for f in ["currentPrice","regularMarketPrice","previousClose","ask","bid"]:
        v = info.get(f)
        if v:
            try:
                fv = float(v)
                if not np.isnan(fv) and fv > 0: return fv
            except Exception: pass
    if not hist.empty: return float(hist["Close"].iloc[-1])
    return np.nan

def sg(d, k, default=None):
    try: v = d.get(k, default); return v if v is not None else default
    except: return default

def sr(df, name, idx=0, default=np.nan):
    try:
        if df is None or df.empty: return default
        m = [r for r in df.index if name.lower() in r.lower()]
        if not m: return default
        v = df.loc[m[0]].iloc[idx]
        return float(v) if not pd.isna(v) else default
    except: return default

def cagr(series, yrs):
    try:
        s = [x for x in series if x and not np.isnan(x) and x > 0]
        if len(s) < 2: return np.nan
        n = min(yrs, len(s)-1)
        return (s[0]/s[n])**(1/n) - 1
    except: return np.nan

def add_ta(hist):
    if hist.empty: return hist
    h = hist.copy()
    try:
        h["SMA50"]  = h["Close"].rolling(50).mean()
        h["SMA200"] = h["Close"].rolling(200).mean()
        h["SMA20"]  = h["Close"].rolling(20).mean()
        h["Vol20"]  = h["Volume"].rolling(20).mean()
        d = h["Close"].diff()
        g = d.clip(lower=0).rolling(14).mean()
        l = (-d.clip(upper=0)).rolling(14).mean()
        h["RSI"] = 100 - (100/(1 + g/l.replace(0,np.nan)))
        tr = pd.concat([h["High"]-h["Low"],(h["High"]-h["Close"].shift()).abs(),(h["Low"]-h["Close"].shift()).abs()],axis=1).max(axis=1)
        h["ATR"] = tr.rolling(14).mean()
    except: pass
    return h

def detect_stage(info, fin):
    """Detect GROWTH vs MATURE. Growth = unprofitable but fast revenue/good gross margins."""
    try:
        ni = sr(fin, "Net Income")
        gm = sg(info, "grossMargins", np.nan)
        rev_growth = sg(info, "revenueGrowth", np.nan)
        rv_r = [r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"] if not fin.empty else []
        rc_v = np.nan
        if rv_r:
            series = [float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
            rc_v = cagr(series, 3)
        is_unprofitable = not np.isnan(ni) and ni < 0
        fast_rev = (not np.isnan(rc_v) and rc_v > 0.15) or (not np.isnan(rev_growth) and rev_growth > 0.15)
        decent_gm = not np.isnan(gm) and gm > 0.35
        if is_unprofitable and (fast_rev or decent_gm):
            return "growth"
        pe_v = sg(info, "trailingPE", np.nan)
        if np.isnan(pe_v) and fast_rev:
            return "growth"
    except:
        pass
    return "mature"

def pct(v, d=1):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "N/A"
    return f"{v*100:.{d}f}%"

def fmt(v, d=2, pre="", suf=""):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "N/A"
    if abs(v)>=1e12: return f"{pre}{v/1e12:.{d}f}T{suf}"
    if abs(v)>=1e9:  return f"{pre}{v/1e9:.{d}f}B{suf}"
    if abs(v)>=1e6:  return f"{pre}{v/1e6:.{d}f}M{suf}"
    return f"{pre}{v:.{d}f}{suf}"

# ── SCORING  (100 pts: Q29 + E14 + V14 + T14 + P29) ─────────────────────────
def score(info, hist, fin, bal, cf, powers_analysis):
    sc, det = {}, {}
    stage = detect_stage(info, fin)
    det["stage"] = stage

    # A. QUALITY (29 pts)
    # CRP — for growth companies, replace with gross margin score if CRP is negative
    crp_v = np.nan; crp_s = 0
    try:
        ni = sr(fin,"Net Income"); eq = sr(bal,"Stockholders Equity")
        if np.isnan(eq): eq = sr(bal,"Total Stockholders Equity")
        td = sr(bal,"Total Debt")
        if np.isnan(td): td = sr(bal,"Long Term Debt",default=0)
        denom = eq + (td if not np.isnan(td) else 0)
        if not any(np.isnan(x) for x in [ni,eq]) and denom!=0:
            crp_v = ni/denom
            if stage == "growth":
                # For growth companies: use gross margin as quality proxy instead
                gm = sg(info,"grossMargins",np.nan)
                if not np.isnan(gm):
                    crp_s = 10 if gm>0.60 else 8 if gm>0.45 else 6 if gm>0.30 else 4 if gm>0.15 else 2
                else:
                    crp_s = 3  # neutral — not penalized for negative NI
            else:
                crp_s = 10 if crp_v>0.20 else 8 if crp_v>0.15 else 5 if crp_v>0.10 else 3 if crp_v>0.05 else 1
        elif stage == "growth":
            # No equity data but growth company — neutral score
            crp_s = 3
    except: pass
    sc["crp"]=crp_s; det["crp"]=crp_v

    om_s=0; om_trend=[]
    try:
        if not fin.empty and fin.shape[1]>=2:
            op_r = [r for r in fin.index if "operating" in r.lower() and "income" in r.lower()]
            rv_r = [r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"]
            if op_r and rv_r:
                for i in range(min(5,fin.shape[1])):
                    try:
                        op=float(fin.loc[op_r[0]].iloc[i]); rv=float(fin.loc[rv_r[0]].iloc[i])
                        if rv>0: om_trend.append(op/rv)
                    except: pass
                if len(om_trend)>=2:
                    delta=om_trend[0]-om_trend[-1]
                    if stage == "growth":
                        # For growth: reward trend improvement, but don't penalize for still-negative margins
                        # If margins are improving (less negative or turning positive) = good
                        om_s = 10 if delta>0.05 else 7 if delta>0.02 else 5 if delta>0 else 3 if delta>-0.03 else 1
                    else:
                        om_s = 10 if delta>0.03 else 7 if delta>0 else 4 if delta>-0.02 else 1
    except: pass
    sc["om_trend"]=om_s; det["om_trend"]=om_trend

    fcf_s=0; fcf_v=np.nan; fcf_r=np.nan
    try:
        opcf=sr(cf,"Operating Cash Flow")
        if np.isnan(opcf): opcf=sr(cf,"Total Cash From Operating Activities")
        cap=sr(cf,"Capital Expenditure")
        if np.isnan(cap): cap=sr(cf,"Capital Expenditures")
        ni2=sr(fin,"Net Income")
        if not np.isnan(opcf):
            fcf_v=opcf-(abs(cap) if not np.isnan(cap) else 0)
            if stage == "growth":
                # For growth: reward positive FCF even without NI; penalize only burning cash with no path
                if fcf_v > 0:
                    fcf_s = 9  # generating real cash despite losses = powerful signal
                elif fcf_v > -1e8:
                    fcf_s = 5  # small burn, manageable
                elif fcf_v > -5e8:
                    fcf_s = 3  # moderate burn
                else:
                    fcf_s = 1  # heavy burn — flag but don't destroy score
            else:
                if not np.isnan(ni2) and ni2>0:
                    fcf_r=fcf_v/ni2
                    fcf_s = 9 if fcf_r>=0.80 else 6 if fcf_r>=0.60 else 3 if fcf_r>=0.40 else 1 if fcf_r>0 else 0
                elif fcf_v>0: fcf_s=4
    except: pass
    sc["fcf_q"]=fcf_s; det["fcf"]=fcf_v; det["fcf_r"]=fcf_r

    # B. EXPECTATIONS (14 pts)
    rc_s=0; rc_v=np.nan
    try:
        if not fin.empty:
            rv_r=[r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"]
            if rv_r:
                series=[float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
                rc_v=cagr(series,5)
                if np.isnan(rc_v): rc_v=cagr(series,3)
                if not np.isnan(rc_v): rc_s=7 if rc_v>0.20 else 5 if rc_v>0.10 else 3 if rc_v>0.05 else 1 if rc_v>0 else 0
    except: pass
    sc["rc"]=rc_s; det["rc"]=rc_v

    ec_s=0; ec_v=np.nan
    try:
        shares=sg(info,"sharesOutstanding",np.nan)
        ni_r=[r for r in fin.index if "net income" in r.lower()] if not fin.empty else []
        if ni_r and not np.isnan(shares) and shares>0:
            eps=[float(fin.loc[ni_r[0]].iloc[i])/shares for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[ni_r[0]].iloc[i])]
            eps=[x for x in eps if x>0]
            ec_v=cagr(eps,5)
            if np.isnan(ec_v): ec_v=cagr(eps,3)
        if not np.isnan(ec_v): ec_s=7 if ec_v>0.20 else 5 if ec_v>0.10 else 3 if ec_v>0.05 else 1 if ec_v>0 else 0
    except: pass
    sc["ec"]=ec_s; det["ec"]=ec_v

    # C. VALUATION (14 pts)
    fy_s=0; pe_s=0; pg_s=0; pg_ok=False; fy_v=np.nan; pg_v=np.nan
    pe_v=sg(info,"trailingPE",np.nan)
    try:
        price=get_price(info,hist); shares=sg(info,"sharesOutstanding",np.nan)
        if not any(np.isnan(x) for x in [fcf_v,price,shares]) and price>0 and shares>0:
            fy_v=(fcf_v/shares)/price
            T=0.044
            if stage == "growth":
                # FCF yield can be negative for growth — reward positive FCF; use PS ratio instead for valuation
                ps = sg(info,"priceToSalesTrailingTwelveMonths",np.nan)
                rev_growth_v = sg(info,"revenueGrowth",np.nan)
                if fcf_v > 0:
                    fy_s = 5  # positive FCF for a growth company = excellent
                elif not np.isnan(ps) and not np.isnan(rc_v):
                    # Rule of 40: revenue growth rate + FCF margin > 40% = healthy growth company
                    fcf_margin = sg(info,"freeCashflow",np.nan)
                    rev_total  = sg(info,"totalRevenue",np.nan)
                    r40 = np.nan
                    if not np.isnan(fcf_margin) and not np.isnan(rev_total) and rev_total>0:
                        r40 = (rc_v*100) + (fcf_margin/rev_total*100)
                    if not np.isnan(r40):
                        fy_s = 5 if r40>60 else 4 if r40>40 else 2 if r40>20 else 1
                    elif not np.isnan(ps) and not np.isnan(rev_growth_v):
                        # Low PS + high growth = attractive
                        fy_s = 5 if ps<5 and rev_growth_v>0.30 else 4 if ps<10 and rev_growth_v>0.20 else 2 if ps<20 else 1
                    else:
                        fy_s = 2
            else:
                fy_s=5 if fy_v>T*2 else 4 if fy_v>T else 2 if fy_v>T*0.5 else 1 if fy_v>0 else 0
    except: pass

    try:
        if stage == "growth":
            # For growth: P/E is meaningless (no earnings). Use PS ratio instead.
            ps2 = sg(info,"priceToSalesTrailingTwelveMonths",np.nan)
            rev_g = sg(info,"revenueGrowth",np.nan)
            if not np.isnan(ps2):
                # Lower PS + strong growth = better; high PS OK if growth is very fast
                if not np.isnan(rev_g) and rev_g > 0.30:
                    pe_s = 5 if ps2<10 else 4 if ps2<20 else 3 if ps2<40 else 2
                else:
                    pe_s = 5 if ps2<5 else 3 if ps2<15 else 1
            else:
                pe_s = 2  # neutral
        else:
            if not np.isnan(pe_v): pe_s=5 if pe_v<15 else 4 if pe_v<25 else 2 if pe_v<35 else 1 if pe_v<50 else 0
    except: pass

    try:
        if stage != "growth":
            g=sg(info,"earningsGrowth",np.nan)
            if np.isnan(g) or g<=0: g=ec_v
            if not np.isnan(g) and not np.isnan(pe_v) and g>0:
                pg_v=pe_v/(g*100); pg_ok=True
                pg_s=4 if pg_v<1.0 else 3 if pg_v<1.5 else 2 if pg_v<2.0 else 1 if pg_v<3.0 else 0
        else:
            # For growth: use EV/Revenue growth ratio instead of PEG
            ev_rev = sg(info,"enterpriseToRevenue",np.nan)
            rev_g2 = sg(info,"revenueGrowth",np.nan)
            if not np.isnan(ev_rev) and not np.isnan(rev_g2) and rev_g2>0:
                # EV/Rev divided by growth — lower is better (like PEG but for growth)
                ev_peg = ev_rev / (rev_g2*100)
                pg_ok = True; pg_v = ev_peg
                pg_s = 4 if ev_peg<0.1 else 3 if ev_peg<0.2 else 2 if ev_peg<0.5 else 1
    except: pass

    if not pg_ok and stage != "growth":
        tot=fy_s+pe_s
        if tot>0: fy_s=min(5,fy_s*14/9); pe_s=min(5,pe_s*14/9)
    sc["fy"]=fy_s; sc["pe"]=pe_s; sc["pg"]=pg_s
    det["fy"]=fy_v; det["pe"]=pe_v; det["pg"]=pg_v

    # D. TECHNICALS (14 pts)
    st2_s=0; rsi_s=0; vol_s=0; rsi_v=np.nan; atr_p=np.nan
    beta=sg(info,"beta",np.nan)
    try:
        if not hist.empty and len(hist)>5:
            last=hist.iloc[-1]; prev=hist.iloc[-2]
            cl=float(last["Close"]); s50=float(last.get("SMA50",np.nan))
            s200=float(last.get("SMA200",np.nan)); rsi_v=float(last.get("RSI",np.nan))
            atr=float(last.get("ATR",np.nan)); vol=float(last.get("Volume",np.nan))
            v20=float(last.get("Vol20",np.nan)); dchg=cl-float(prev["Close"])
            if not np.isnan(atr) and cl>0: atr_p=atr/cl
            if not any(np.isnan(x) for x in [cl,s50,s200]):
                if cl>s50>s200: st2_s=6
                elif cl>s200:   st2_s=3
                elif cl>s50:    st2_s=2
            if not np.isnan(rsi_v):
                if 45<=rsi_v<=65: rsi_s=5
                elif 35<=rsi_v<45 or 65<rsi_v<=75: rsi_s=3
                else: rsi_s=1
            if not any(np.isnan(x) for x in [vol,v20]):
                if vol>v20 and dchg>0: vol_s=3
                elif vol>v20 or dchg>0: vol_s=1
    except: pass
    sc["st2"]=st2_s; sc["rsi"]=rsi_s; sc["vol"]=vol_s
    det["rsi"]=rsi_v; det["atr"]=atr_p; det["beta"]=beta

    # E. 7 POWERS (29 pts) — only counts if analyst wrote justification
    confirmed=[p for p,t in powers_analysis.items() if t and len(t.strip())>10]
    pw_s=min(29, len(confirmed)*(29/7))
    sc["pw"]=pw_s; sc["n_pw"]=len(confirmed)

    # TOTALS
    q = sc["crp"]+sc["om_trend"]+sc["fcf_q"]
    e = sc["rc"]+sc["ec"]
    v = sc["fy"]+sc["pe"]+sc["pg"]
    tech = min(14, sc["st2"]+sc["rsi"]+sc["vol"])
    pw = sc["pw"]
    total = min(100, q+e+v+tech+pw)

    return {"total":round(total,1),"q":round(q,1),"e":round(e,1),"v":round(v,1),
            "tech":round(tech,1),"pw":round(pw,1),"sc":sc,"det":det,"confirmed":confirmed}

def get_signal(res, hist):
    total=res["total"]; s200_ok=rsi_ok=vol_ok=False
    try:
        if not hist.empty:
            last=hist.iloc[-1]; prev=hist.iloc[-2]
            cl=float(last["Close"]); s200=float(last.get("SMA200",np.nan))
            rsi=float(last.get("RSI",np.nan)); vol=float(last.get("Volume",np.nan))
            v20=float(last.get("Vol20",np.nan))
            s200_ok=not np.isnan(s200) and cl>s200
            rsi_ok=not np.isnan(rsi) and 45<=rsi<=65
            vol_ok=not any(np.isnan(x) for x in [vol,v20]) and vol>v20 and cl>float(prev["Close"])
    except: pass
    if total>75 and s200_ok and rsi_ok and vol_ok: return "STRONG BUY","#10b981"
    elif total>=65 and s200_ok:                    return "BUY","#3b82f6"
    elif total>=50:                                return "NEUTRAL","#f59e0b"
    else:                                          return "AVOID","#ef4444"

def risk_level(det):
    a=det.get("atr",np.nan) or 0.04; b=det.get("beta",np.nan) or 1.0
    stage=det.get("stage","mature")
    # Growth companies are inherently more volatile — adjust thresholds
    if stage == "growth":
        if a<0.05 and b<1.5: return "MEDIUM"  # normal for growth
        elif a>0.08 or b>2.5: return "HIGH"
        else: return "MEDIUM"
    else:
        if a<0.03 and b<1.0: return "LOW"
        elif a>0.05 or b>1.5: return "HIGH"
        else: return "MEDIUM"

# ── CHARTS ───────────────────────────────────────────────────────────────────
CL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(10,14,26,0.8)",
          font=dict(color="#94a3b8",family="Inter"),
          xaxis=dict(gridcolor="#1e2a45",showgrid=True,linecolor="#2d3a5e"),
          yaxis=dict(gridcolor="#1e2a45",showgrid=True,linecolor="#2d3a5e"),
          margin=dict(l=50,r=20,t=30,b=40))

def price_chart(hist, ticker):
    if hist.empty: return go.Figure()
    fig=make_subplots(rows=3,cols=1,shared_xaxes=True,row_heights=[0.55,0.25,0.20],vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=hist.index,open=hist["Open"],high=hist["High"],low=hist["Low"],close=hist["Close"],
        name="Price",increasing_line_color="#10b981",decreasing_line_color="#ef4444",
        increasing_fillcolor="#10b981",decreasing_fillcolor="#ef4444"),row=1,col=1)
    for sma,col,nm in [("SMA50","#f59e0b","50D"),("SMA200","#8b5cf6","200D")]:
        if sma in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index,y=hist[sma],name=nm,
                line=dict(color=col,width=1.5,dash="dot"),opacity=0.8),row=1,col=1)
    colors=["#10b981" if c>=o else "#ef4444" for c,o in zip(hist["Close"],hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index,y=hist["Volume"],name="Vol",marker_color=colors,opacity=0.5),row=2,col=1)
    if "Vol20" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["Vol20"],name="Vol20",
            line=dict(color="#f59e0b",width=1),opacity=0.7),row=2,col=1)
    if "RSI" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["RSI"],name="RSI",
            line=dict(color="#3b82f6",width=1.5)),row=3,col=1)
        fig.add_hrect(y0=45,y1=65,row=3,col=1,fillcolor="rgba(59,130,246,0.08)",line_width=0)
        for lv,lc in [(30,"#ef4444"),(70,"#ef4444"),(50,"#64748b")]:
            fig.add_hline(y=lv,row=3,col=1,line=dict(color=lc,width=0.8,dash="dot"))
    fig.update_layout(title=f"{ticker} — Price · Volume · RSI",**CL,height=510,showlegend=True,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font=dict(size=10)),
        xaxis_rangeslider_visible=False)
    return fig

def gauge_chart(s):
    col="#10b981" if s>=75 else "#3b82f6" if s>=60 else "#f59e0b" if s>=45 else "#ef4444"
    fig=go.Figure(go.Indicator(mode="gauge+number",value=s,
        number={"font":{"color":col,"size":48,"family":"JetBrains Mono"}},
        gauge={"axis":{"range":[0,100],"tickcolor":"#475569","tickfont":{"color":"#475569","size":10}},
               "bar":{"color":col,"thickness":0.25},"bgcolor":"#0a0e1a","borderwidth":0,
               "steps":[{"range":[0,50],"color":"#1a0a0a"},{"range":[50,65],"color":"#151515"},{"range":[65,100],"color":"#0a1510"}],
               "threshold":{"line":{"color":col,"width":3},"thickness":0.8,"value":s}}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=20,r=20,t=20,b=20),height=200)
    return fig

def breakdown_chart(res):
    cats=["Quality\n(29)","Expectations\n(14)","Valuation\n(14)","Technicals\n(14)","7 Powers\n(29)"]
    maxes=[29,14,14,14,29]; vals=[res["q"],res["e"],res["v"],res["tech"],res["pw"]]
    colors=["#10b981" if v/m>=0.75 else "#3b82f6" if v/m>=0.5 else "#f59e0b" if v/m>=0.25 else "#ef4444"
            for v,m in zip(vals,maxes)]
    fig=go.Figure()
    fig.add_trace(go.Bar(x=cats,y=maxes,marker_color="rgba(30,42,69,0.5)",
        marker_line=dict(color="#2d3a5e",width=1),name="Max",showlegend=False))
    fig.add_trace(go.Bar(x=cats,y=vals,marker_color=colors,name="Score",
        text=[f"{v:.1f}" for v in vals],textposition="inside",
        textfont=dict(color="white",size=12,family="JetBrains Mono"),showlegend=False))
    fig.update_layout(barmode="overlay",**CL,height=210,title="Score Breakdown (/ 100)",
        yaxis_title="Points",xaxis_tickfont=dict(size=10))
    return fig

def radar_chart(confirmed):
    vals=[1 if p in confirmed else 0 for p in ALL_POWERS]+[1 if ALL_POWERS[0] in confirmed else 0]
    cats=ALL_POWERS+[ALL_POWERS[0]]
    fig=go.Figure(go.Scatterpolar(r=vals,theta=cats,fill="toself",
        fillcolor="rgba(59,130,246,0.15)",line=dict(color="#3b82f6",width=2),
        marker=dict(color=["#3b82f6" if v else "#1e2a45" for v in vals],size=8)))
    fig.update_layout(polar=dict(bgcolor="rgba(10,14,26,0.8)",
        radialaxis=dict(visible=False,range=[0,1]),
        angularaxis=dict(tickfont=dict(color="#94a3b8",size=10),linecolor="#2d3a5e",gridcolor="#1e2a45")),
        paper_bgcolor="rgba(0,0,0,0)",showlegend=False,margin=dict(l=40,r=40,t=20,b=20),height=280)
    return fig

def om_chart(trend):
    if not trend or len(trend)<2: return None
    n=len(trend); labels=[f"FY-{n-1-i}" if i<n-1 else "Latest" for i in range(n)]
    fig=go.Figure(go.Scatter(x=labels,y=[v*100 for v in trend],mode="lines+markers",
        line=dict(color="#8b5cf6",width=2),marker=dict(color="#8b5cf6",size=8),
        fill="tozeroy",fillcolor="rgba(139,92,246,0.08)"))
    fig.update_layout(**CL,height=170,title="Operating Margin Trend (%)",yaxis_ticksuffix="%")
    return fig

# ── HELPERS ──────────────────────────────────────────────────────────────────
def mc(label, val, hint=""):
    h = f"<div class='metric-sub'>{hint}</div>" if hint else ""
    return f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div>{h}</div>"

def ic(text, color="#3b82f6", label=""):
    l = f"<div class='insight-label'>{label}</div>" if label else ""
    return f"<div class='insight-card' style='border-left-color:{color};'>{l}<div class='insight-text'>{text}</div></div>"

def get_peers(industry):
    ind = industry.lower()
    for key, peers in INDUSTRY_PEERS.items():
        if key in ind or ind in key: return peers
    return []

def get_partners(industry):
    ind = industry.lower()
    for key, partners in INDUSTRY_PARTNERS.items():
        if key in ind or ind in key: return partners
    return []

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="war-header">
        <h1>⚔️ War Room Research Terminal</h1>
        <p>Equity Research · Quality(29) + Expectations(14) + Valuation(14) + Technicals(14) + 7 Powers(29) = 100 pts</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🎯 Target Stock")
        ticker = st.text_input("", value="AAPL", placeholder="e.g. NVDA", label_visibility="collapsed").strip().upper()

        st.markdown('<div class="section-header">Investment Thesis (optional)</div>', unsafe_allow_html=True)
        thesis = st.text_area("", placeholder="e.g. Apple sells premium hardware and earns recurring revenue through its services ecosystem.",
                              height=60, label_visibility="collapsed")

        st.markdown('<div class="section-header">Position Sizing (optional)</div>', unsafe_allow_html=True)
        use_pos = st.checkbox("Enable position sizing", value=False)
        port_size = 100000; entry_in = 0.0
        if use_pos:
            port_size = st.number_input("Portfolio Size ($)", min_value=0, value=100000, step=1000)
            entry_in  = st.number_input("Entry Price ($) — 0 = use last close", min_value=0.0, value=0.0, step=0.01)

        run_btn = st.button("⚡ Run War Room Analysis")

    if not run_btn:
        st.markdown("""<div style="text-align:center;padding:80px 20px;">
            <div style="font-size:4rem;margin-bottom:16px;">⚔️</div>
            <div style="font-size:1.3rem;color:#64748b;font-weight:600;">Enter a ticker and click Run</div>
            <div style="font-size:0.88rem;margin-top:10px;color:#334155;">Quality · Expectations · Valuation · Technicals · 7 Powers</div>
        </div>""", unsafe_allow_html=True)
        return

    # 7 Powers scored on the dashboard — no user input needed, starts at 0
    powers_analysis = {p: "" for p in ALL_POWERS}

    with st.spinner(f"Loading {ticker}..."):
        try:
            info, hist_raw, fin, bal, cf, news = fetch_data(ticker)
            hist = add_ta(hist_raw)
        except Exception as e:
            st.error(f"Failed to load {ticker}: {e}"); return

    if not info and hist.empty:
        st.error(f"No data for {ticker}."); return

    res = score(info, hist, fin, bal, cf, powers_analysis)
    signal, sig_color = get_signal(res, hist)
    rl   = risk_level(res["det"])
    det  = res["det"]
    confirmed = res["confirmed"]

    # Price — always last available (handles closed market)
    price = get_price(info, hist)
    prev  = sg(info, "previousClose", np.nan)
    if np.isnan(prev) and not hist.empty and len(hist)>=2:
        prev = float(hist["Close"].iloc[-2])
    day_chg = (price-prev)/prev if not np.isnan(price) and not np.isnan(prev) and prev>0 else np.nan

    # Position sizing
    entry = entry_in if (use_pos and entry_in>0) else price
    pos_size = stop_loss = shares_qty = np.nan
    if use_pos and not np.isnan(entry):
        try:
            atr_v = float(hist["ATR"].iloc[-1]) if not hist.empty and "ATR" in hist.columns else np.nan
            if not np.isnan(atr_v) and atr_v>0:
                stop_loss = entry - 2*atr_v
                rps = entry - stop_loss
                if rps>0:
                    shares_qty = (port_size*0.01)/rps
                    pos_size   = shares_qty*entry
        except: pass

    # ── ROW 1: Signal · Score · Header ──────────────────────────────────────
    c1,c2,c3 = st.columns([1.2,1.4,2.4])

    with c1:
        st.markdown(f'<div class="signal-{signal.replace(" ","_")}">{signal}</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="score-card"><div class="score-giant" style="color:{sig_color};">{res["total"]}</div><div class="score-label">Score / 100</div></div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div class="metric-label">Risk Level</div><div class="metric-value risk-{rl}" style="font-size:1.3rem;">{rl}</div></div>', unsafe_allow_html=True)
        stage_badge_color = "#f59e0b" if det.get("stage")=="growth" else "#64748b"
        stage_label = "GROWTH STAGE" if det.get("stage")=="growth" else "MATURE"
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div class="metric-label">Company Stage</div><div class="metric-value" style="font-size:0.9rem;color:{stage_badge_color};">{stage_label}</div></div>', unsafe_allow_html=True)

    with c2:
        st.plotly_chart(gauge_chart(res["total"]), use_container_width=True, config={"displayModeBar":False})

    with c3:
        name     = sg(info,"longName",ticker)
        sector   = sg(info,"sector","—")
        industry = sg(info,"industry","—")
        mktcap   = sg(info,"marketCap",np.nan)
        beta_v   = det.get("beta",np.nan)
        w52h     = sg(info,"fiftyTwoWeekHigh",np.nan)
        w52l     = sg(info,"fiftyTwoWeekLow",np.nan)
        st.markdown(f'<div style="font-size:1.45rem;font-weight:700;color:#f1f5f9;">{name}</div><div style="font-size:0.8rem;color:#64748b;">{sector} · {industry}</div>', unsafe_allow_html=True)
        st.markdown("")
        chg_c="#10b981" if (isinstance(day_chg,float) and not np.isnan(day_chg) and day_chg>=0) else "#ef4444"
        cols = st.columns(6)
        for col,(lbl,val) in zip(cols,[
            ("Last Price",  f"${price:.2f}" if not np.isnan(price) else "N/A"),
            ("Day Chg",     f'<span style="color:{chg_c}">{pct(day_chg)}</span>'),
            ("Mkt Cap",     fmt(mktcap,pre="$")),
            ("Beta",        f"{beta_v:.2f}" if not np.isnan(beta_v) else "N/A"),
            ("52W High",    f"${w52h:.2f}" if not np.isnan(w52h) else "N/A"),
            ("52W Low",     f"${w52l:.2f}" if not np.isnan(w52l) else "N/A"),
        ]):
            with col:
                st.markdown(mc(lbl,val), unsafe_allow_html=True)
        if thesis.strip():
            st.markdown(ic(f'"{thesis}"',label="📋 Investment Thesis"), unsafe_allow_html=True)
        desc = sg(info,"longBusinessSummary","")
        if desc:
            st.markdown(f'<div style="font-size:0.77rem;color:#64748b;margin-top:8px;line-height:1.5;">{desc[:300]}{"..." if len(desc)>300 else ""}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 2: Score Breakdown + Price Chart ─────────────────────────────────
    cl, cr = st.columns([1,2])
    with cl:
        st.plotly_chart(breakdown_chart(res), use_container_width=True, config={"displayModeBar":False})
        if det.get("stage") == "growth":
            st.markdown(ic("🚀 <b>Growth Stage Mode</b> — Scoring adapted: CRP replaced by Gross Margin, FCF Quality rewards positive FCF not FCF/NI ratio, Valuation uses P/S + Rule of 40 instead of P/E + PEG. High ATR/Beta thresholds relaxed.", "#f59e0b"), unsafe_allow_html=True)
        st.markdown('<div class="section-header">Module Drill-Down</div>', unsafe_allow_html=True)
        modules=[
            ("Quality / 29",      res["q"],           29),
            ("  ↳ CRP",           res["sc"]["crp"],   10),
            ("  ↳ OM Trend",      res["sc"]["om_trend"],10),
            ("  ↳ FCF Quality",   res["sc"]["fcf_q"],  9),
            ("Expectations / 14", res["e"],           14),
            ("  ↳ Rev CAGR",      res["sc"]["rc"],     7),
            ("  ↳ EPS CAGR",      res["sc"]["ec"],     7),
            ("Valuation / 14",    res["v"],           14),
            ("  ↳ FCF Yield",     res["sc"]["fy"],     5),
            ("  ↳ P/E",           res["sc"]["pe"],     5),
            ("  ↳ PEG",           res["sc"]["pg"],     4),
            ("Technicals / 14",   res["tech"],        14),
            ("  ↳ Stage 2",       res["sc"]["st2"],    6),
            ("  ↳ RSI Zone",      res["sc"]["rsi"],    5),
            ("  ↳ Volume",        res["sc"]["vol"],    3),
            ("7 Powers / 29",     res["pw"],          29),
        ]
        rows=[{"Module":l,"Score":f"{v:.1f}/{m}","▓":"█"*int((v/m)*10)+"░"*(10-int((v/m)*10))} for l,v,m in modules]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                     column_config={"▓":st.column_config.TextColumn("Progress",width="medium")})
    with cr:
        if not hist.empty:
            st.plotly_chart(price_chart(hist,ticker), use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Price chart unavailable.")

    st.markdown("---")

    # ── ROW 3: AI-Powered 7 Powers Analysis ──────────────────────────────────
    st.markdown('<div class="section-header">⚡ 7 Powers Analysis — Auto-Analyzed by AI (Helmer Framework)</div>', unsafe_allow_html=True)

    with st.spinner("🤖 Analyzing 7 Powers with AI..."):
        powers_ai = ai_analyze_7_powers(
            ticker       = ticker,
            company_name = name,
            sector       = sector,
            industry     = industry,
            description  = sg(info, "longBusinessSummary", ""),
            gross_margin = pct(sg(info,"grossMargins",np.nan)),
            op_margin    = pct(sg(info,"operatingMargins",np.nan)),
            rev_cagr     = pct(det.get("rc", np.nan)),
            market_cap   = fmt(sg(info,"marketCap",np.nan), pre="$"),
            stage        = det.get("stage","mature")
        )

    # Determine confirmed powers from AI verdict
    if powers_ai:
        ai_confirmed = [p for p, v in powers_ai.items() if v.get("verdict","NO").startswith("YES")]
        ai_partial   = [p for p, v in powers_ai.items() if v.get("verdict","NO").startswith("PARTIAL")]
        # Score: YES = full weight, PARTIAL = half weight
        ai_pw_score  = min(29, (len(ai_confirmed) + len(ai_partial)*0.5) * (29/7))
    else:
        ai_confirmed = []; ai_partial = []; ai_pw_score = res["pw"]

    # Update the score display with AI result
    cp, pp = st.columns([1, 2])

    with cp:
        st.plotly_chart(radar_chart(ai_confirmed), use_container_width=True, config={"displayModeBar":False})
        confirmed_count = len(ai_confirmed)
        partial_count   = len(ai_partial)
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="metric-label">AI Powers Score</div>
            <div class="metric-value" style="color:#3b82f6;font-size:2rem;">{ai_pw_score:.1f} / 29</div>
            <div class="metric-sub">✅ {confirmed_count} confirmed &nbsp;·&nbsp; ⚡ {partial_count} partial</div>
        </div>
        """, unsafe_allow_html=True)

        if powers_ai:
            st.markdown("")
            verdict_summary = []
            for p in ALL_POWERS:
                v = powers_ai.get(p, {}).get("verdict","NO")
                icon = "✅" if v.startswith("YES") else "⚡" if v.startswith("PARTIAL") else "❌"
                verdict_summary.append(f"{icon} {p}")
            st.markdown('<div style="font-size:0.78rem;line-height:1.9;color:#94a3b8;">' + "<br>".join(verdict_summary) + '</div>', unsafe_allow_html=True)
        else:
            st.markdown(ic("⚠️ AI analysis unavailable. Check API connection.", "#f59e0b"), unsafe_allow_html=True)

    with pp:
        if powers_ai:
            for p in ALL_POWERS:
                pdata   = powers_ai.get(p, {})
                verdict = pdata.get("verdict", "NO")
                reason  = pdata.get("reasoning", "No analysis available.")
                if verdict.startswith("YES"):
                    border = "#10b981"; icon = "✅"; badge = "CONFIRMED"
                    badge_color = "#10b981"; card_bg = "#0a1a0f"
                elif verdict.startswith("PARTIAL"):
                    border = "#f59e0b"; icon = "⚡"; badge = "PARTIAL"
                    badge_color = "#f59e0b"; card_bg = "#1a1505"
                else:
                    border = "#1e2a45"; icon = "❌"; badge = "NOT APPLICABLE"
                    badge_color = "#475569"; card_bg = "#0f1525"

                st.markdown(f"""
                <div style="background:{card_bg};border:1px solid {border};border-radius:8px;padding:12px 14px;margin:5px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">{icon} {p}</div>
                        <div style="font-size:0.68rem;font-weight:700;color:{badge_color};background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:10px;">{badge}</div>
                    </div>
                    <div style="font-size:0.8rem;color:#94a3b8;line-height:1.5;">{reason}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            for p in ALL_POWERS:
                st.markdown(f"""
                <div class="power-card">
                    <div class="power-name">⬜ {p}</div>
                    <div class="power-verdict"><em style="color:#475569">{POWER_GUIDE[p]}</em></div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 4: Metrics · OM Trend · Position Sizing ───────────────────────────
    ca, cb, cc = st.columns([1.5,1.2,1.3])

    with ca:
        st.markdown('<div class="section-header">Key Financial Metrics</div>', unsafe_allow_html=True)
        gm  = sg(info,"grossMargins",np.nan)
        om_ = sg(info,"operatingMargins",np.nan)
        nm  = sg(info,"profitMargins",np.nan)
        roe = sg(info,"returnOnEquity",np.nan)
        de  = sg(info,"debtToEquity",np.nan)
        for lbl,val,hint in [
            ("Capital Return Proxy (CRP)", pct(det.get("crp",np.nan)),   "Net Income/(Equity+Debt). >15%=excellent"),
            ("FCF (Op CF − CapEx)",        fmt(det.get("fcf",np.nan),pre="$"), "Manual calculation"),
            ("FCF / Net Income",           pct(det.get("fcf_r",np.nan)), "≥80%=high earnings quality"),
            ("FCF Yield",                  pct(det.get("fy",np.nan)),    "vs 4.4% Treasury benchmark"),
            ("Trailing P/E",               f"{det.get('pe',np.nan):.1f}x" if not np.isnan(det.get("pe",np.nan)) else "N/A", ""),
            ("PEG Ratio",                  f"{det.get('pg',np.nan):.2f}" if not np.isnan(det.get("pg",np.nan)) else "N/A", "<1.0=attractive"),
            ("Rev CAGR (5Y→3Y fallback)",  pct(det.get("rc",np.nan)),   ""),
            ("EPS CAGR (5Y→3Y fallback)",  pct(det.get("ec",np.nan)),   ""),
            ("Gross Margin",               pct(gm),  ""),
            ("Operating Margin",           pct(om_), ""),
            ("Net Margin",                 pct(nm),  ""),
            ("Return on Equity",           pct(roe), ">15%=strong"),
            ("Debt / Equity",              f"{de/100:.2f}" if not np.isnan(de) else "N/A", "<0.5=conservative"),
            ("RSI (14-day)",               f"{det.get('rsi',np.nan):.1f}" if not np.isnan(det.get("rsi",np.nan)) else "N/A", "45–65=optimal"),
            ("ATR %",                      pct(det.get("atr",np.nan)),   "<3%=LOW volatility"),
        ]:
            st.markdown(mc(lbl,val,hint), unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="section-header">Operating Margin Trend</div>', unsafe_allow_html=True)
        omf = om_chart(det.get("om_trend",[]))
        if omf: st.plotly_chart(omf, use_container_width=True, config={"displayModeBar":False})
        else:   st.info("OM trend unavailable.")

        st.markdown('<div class="section-header">Valuation Multiples</div>', unsafe_allow_html=True)
        for lbl,val in [
            ("Forward P/E",   f"{sg(info,'forwardPE',np.nan):.1f}x"       if not np.isnan(sg(info,'forwardPE',np.nan)) else "N/A"),
            ("Price/Sales",   f"{sg(info,'priceToSalesTrailingTwelveMonths',np.nan):.2f}x" if not np.isnan(sg(info,'priceToSalesTrailingTwelveMonths',np.nan)) else "N/A"),
            ("Price/Book",    f"{sg(info,'priceToBook',np.nan):.2f}x"      if not np.isnan(sg(info,'priceToBook',np.nan)) else "N/A"),
            ("EV/Revenue",    f"{sg(info,'enterpriseToRevenue',np.nan):.2f}x" if not np.isnan(sg(info,'enterpriseToRevenue',np.nan)) else "N/A"),
            ("EV/EBITDA",     f"{sg(info,'enterpriseToEbitda',np.nan):.2f}x"  if not np.isnan(sg(info,'enterpriseToEbitda',np.nan)) else "N/A"),
        ]:
            st.markdown(mc(lbl,val), unsafe_allow_html=True)

        st.markdown('<div class="section-header">Dividends</div>', unsafe_allow_html=True)
        dy=sg(info,"dividendYield",np.nan); dr=sg(info,"dividendRate",np.nan); pr=sg(info,"payoutRatio",np.nan)
        for lbl,val in [
            ("Dividend Yield",  pct(dy) if not np.isnan(dy) else "No dividend"),
            ("Annual Dividend", f"${dr:.2f}" if dr and not np.isnan(dr) else "—"),
            ("Payout Ratio",    pct(pr) if not np.isnan(pr) else "—"),
        ]:
            st.markdown(mc(lbl,val), unsafe_allow_html=True)

    with cc:
        st.markdown('<div class="section-header">Position Sizing (1% Risk Rule)</div>', unsafe_allow_html=True)
        if use_pos:
            for lbl,val in [
                ("Entry Price",        f"${entry:.2f}" if not np.isnan(entry) else "N/A"),
                ("Stop-Loss (2× ATR)", f"${stop_loss:.2f}" if not np.isnan(stop_loss) else "N/A"),
                ("Risk per Share",     f"${entry-stop_loss:.2f}" if not np.isnan(stop_loss) else "N/A"),
                ("1% Portfolio Risk",  f"${port_size*0.01:,.0f}"),
                ("Shares to Buy",      f"{shares_qty:.0f}" if not np.isnan(shares_qty) else "N/A"),
                ("Position Size ($)",  f"${pos_size:,.0f}" if not np.isnan(pos_size) else "N/A"),
                ("% of Portfolio",     f"{pos_size/port_size*100:.1f}%" if not np.isnan(pos_size) and port_size>0 else "N/A"),
            ]:
                st.markdown(mc(lbl,val), unsafe_allow_html=True)
        else:
            st.info("Enable position sizing in the sidebar.")

        st.markdown('<div class="section-header">Analyst Consensus</div>', unsafe_allow_html=True)
        rec    = sg(info,"recommendationKey","")
        target = sg(info,"targetMeanPrice",np.nan)
        n_anal = sg(info,"numberOfAnalystOpinions",np.nan)
        rc = {"buy":"#10b981","strongbuy":"#10b981","hold":"#f59e0b","sell":"#ef4444","underperform":"#ef4444"}.get((rec or "").lower().replace(" ",""),"#94a3b8")
        upside = (target/price-1)*100 if not np.isnan(target) and not np.isnan(price) and price>0 else np.nan
        for lbl,val in [
            ("Consensus",       f'<span style="color:{rc};font-weight:700;">{rec.upper() if rec else "N/A"}</span>'),
            ("Price Target",    f"${target:.2f}" if not np.isnan(target) else "N/A"),
            ("# of Analysts",   str(int(n_anal)) if not np.isnan(n_anal) else "N/A"),
            ("Upside to Target",f"{upside:.1f}%" if not np.isnan(upside) else "N/A"),
        ]:
            st.markdown(mc(lbl,val), unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 5: Competitors & Partners ────────────────────────────────────────
    st.markdown('<div class="section-header">🏆 Competitive Landscape & Partners</div>', unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)

    with cc1:
        st.markdown("**Key Competitors**")
        peers = [p for p in get_peers(industry) if ticker not in p]
        if peers:
            for p in peers[:5]:
                st.markdown(f'<div class="comp-card"><div style="font-size:0.88rem;color:#e2e8f0;font-weight:500;">⚔️ {p}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="comp-card"><div style="font-size:0.82rem;color:#94a3b8;">Industry: <b style="color:#e2e8f0;">{industry}</b> · Sector: <b style="color:#e2e8f0;">{sector}</b><br><span style="color:#475569;font-size:0.74rem;">Peer list not mapped for this industry. Use finviz.com → Screener → similar sector for manual comparison.</span></div></div>', unsafe_allow_html=True)

        st.markdown("")
        st.markdown("**Company Profile**")
        emp  = sg(info,"fullTimeEmployees",None)
        web  = sg(info,"website",None)
        ctry = sg(info,"country","—")
        for lbl,val in [
            ("Country",   ctry),
            ("Employees", f"{emp:,}" if emp else "N/A"),
            ("Website",   f'<a href="{web}" target="_blank" style="color:#3b82f6;">{web}</a>' if web else "N/A"),
        ]:
            st.markdown(mc(lbl,val), unsafe_allow_html=True)

    with cc2:
        st.markdown("**Key Partners & Supply Chain**")
        partners = get_partners(industry)
        if partners:
            for p in partners:
                st.markdown(f'<div class="part-card"><div style="font-size:0.85rem;color:#86efac;font-weight:500;">🤝 {p}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="part-card"><div style="font-size:0.82rem;color:#94a3b8;">Partners not mapped for <b style="color:#e2e8f0;">{industry}</b>.<br><span style="color:#475569;font-size:0.74rem;">Check the company\'s 10-K annual report (Customers and Suppliers sections) for official partnership details.</span></div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 6: News ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📰 Latest News</div>', unsafe_allow_html=True)
    if news:
        n1, n2 = st.columns(2)
        for i, item in enumerate(news[:8]):
            try:
                title = item.get("title","No title")
                pub   = item.get("publisher","Unknown")
                link  = item.get("link","#")
                ts    = item.get("providerPublishTime",None)
                date  = datetime.fromtimestamp(ts).strftime("%b %d, %Y  %H:%M") if ts else "—"
                html  = f'<div class="news-card"><a href="{link}" target="_blank" style="text-decoration:none;"><div class="news-title">{title}</div></a><div class="news-meta">📰 {pub} &nbsp;·&nbsp; 🕐 {date}</div></div>'
                (n1 if i%2==0 else n2).markdown(html, unsafe_allow_html=True)
            except: continue
    else:
        st.info("No recent news available.")

    st.markdown("---")

    # ── ROW 7: Bull / Bear ───────────────────────────────────────────────────
    cb1, cb2 = st.columns(2)
    with cb1:
        st.markdown('<div class="section-header">🟢 Bull Case Signals</div>', unsafe_allow_html=True)
        bull = []
        if res["q"] >= 20:          bull.append(f"Strong financial health — Quality score {res['q']:.1f}/29")
        if not np.isnan(det.get("crp",np.nan)) and det["crp"]>0.15: bull.append(f"High CRP {pct(det['crp'])} (>15% threshold)")
        if not np.isnan(det.get("fcf_r",np.nan)) and det["fcf_r"]>=0.80: bull.append(f"Excellent FCF quality: {pct(det['fcf_r'])} of net income")
        if not np.isnan(det.get("rc",np.nan)) and det["rc"]>0.10: bull.append(f"Strong revenue CAGR: {pct(det['rc'])}")
        if not np.isnan(det.get("fy",np.nan)) and det["fy"]>0.044: bull.append(f"FCF Yield {pct(det['fy'])} beats 4.4% Treasury")
        if res["sc"].get("st2",0)>=6: bull.append("Stage 2 Uptrend: Price > 50D SMA > 200D SMA")
        if not np.isnan(det.get("rsi",np.nan)) and 45<=det["rsi"]<=65: bull.append(f"RSI {det['rsi']:.1f} in optimal 45–65 zone")
        if ai_confirmed: bull.append(f"{len(ai_confirmed)} Helmer Power(s) confirmed by AI: {', '.join(ai_confirmed[:3])}{'…' if len(ai_confirmed)>3 else ''}")
        if not np.isnan(sg(info,"targetMeanPrice",np.nan)) and not np.isnan(price) and price>0:
            up=(sg(info,"targetMeanPrice",np.nan)/price-1)*100
            if up>15: bull.append(f"Analyst consensus implies {up:.1f}% upside")
        if not bull: bull.append("No strong bull signals at current levels.")
        for pt in bull: st.markdown(ic(f"✅ {pt}","#10b981"), unsafe_allow_html=True)

    with cb2:
        st.markdown('<div class="section-header">🔴 Bear Case / Risk Flags</div>', unsafe_allow_html=True)
        bear = []
        stage = det.get("stage","mature")
        if not hist.empty:
            try:
                last=hist.iloc[-1]; cl=float(last["Close"]); s200=float(last.get("SMA200",np.nan))
                if not np.isnan(s200) and cl<s200: bear.append(f"Price ${cl:.2f} below 200D SMA ${s200:.2f} — bearish trend")
            except: pass
        rsi_v=det.get("rsi",np.nan)
        if not np.isnan(rsi_v):
            if rsi_v>70: bear.append(f"RSI {rsi_v:.1f} overbought — momentum may be exhausted")
            if rsi_v<30: bear.append(f"RSI {rsi_v:.1f} oversold — potential downtrend")
        # ATR flag: only warn for MATURE companies; growth companies are expected to be volatile
        if stage == "mature":
            if not np.isnan(det.get("atr",np.nan)) and det["atr"]>0.05:
                bear.append(f"High volatility: ATR {pct(det['atr'])} > 5%")
        else:
            if not np.isnan(det.get("atr",np.nan)) and det["atr"]>0.10:
                bear.append(f"Extreme volatility for growth stage: ATR {pct(det['atr'])} > 10%")
        if not np.isnan(det.get("beta",np.nan)) and det["beta"]>2.5:
            bear.append(f"Very high Beta {det['beta']:.2f} — extreme market sensitivity")
        # FCF flag: only penalize growth company if cash burn is very heavy
        if stage == "mature":
            if res["sc"].get("fcf_q",0)<3: bear.append("Weak FCF quality — earnings not converting to cash")
        else:
            if not np.isnan(det.get("fcf",np.nan)) and det["fcf"] < -5e8:
                bear.append(f"Heavy cash burn: FCF {fmt(det['fcf'],pre='$')} — monitor cash runway")
        # CRP / profitability flags — skip for growth companies
        if stage == "mature":
            if not np.isnan(det.get("pg",np.nan)) and det["pg"]>2.5:
                bear.append(f"Elevated PEG {det['pg']:.2f} — expensive vs. growth")
            if not np.isnan(det.get("pe",np.nan)) and det["pe"]>40:
                bear.append(f"High P/E {det['pe']:.1f}x — demanding valuation")
        else:
            # For growth: flag high PS ratio without growth to back it up
            ps_v = sg(info,"priceToSalesTrailingTwelveMonths",np.nan)
            rev_g = sg(info,"revenueGrowth",np.nan)
            if not np.isnan(ps_v) and not np.isnan(rev_g) and ps_v>20 and rev_g<0.20:
                bear.append(f"High P/S {ps_v:.1f}x with only {pct(rev_g)} revenue growth — valuation requires acceleration")
        if res["total"]<50: bear.append(f"Score {res['total']}/100 below 50 — AVOID threshold")
        if not ai_confirmed: bear.append("No Helmer Powers confirmed by AI — moat not established")
        if not bear: bear.append("No critical bear flags at current levels.")
        for pt in bear: st.markdown(ic(f"⚠️ {pt}","#ef4444"), unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 8: Final Summary ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Final Signal</div>', unsafe_allow_html=True)
    target_p = sg(info,"targetMeanPrice",np.nan)
    cols5 = st.columns(5)
    for col,(lbl,val,color) in zip(cols5,[
        ("Signal",        signal,                     sig_color),
        ("Score / 100",   str(res["total"]),          sig_color),
        ("Risk Level",    rl,                         "#34d399" if rl=="LOW" else "#fbbf24" if rl=="MEDIUM" else "#f87171"),
        ("AI Powers",     f"{len(ai_confirmed)}/7 confirmed", "#3b82f6"),
        ("Analyst Target",f"${target_p:.2f}" if not np.isnan(target_p) else "N/A","#94a3b8"),
    ]):
        with col:
            st.markdown(f'<div class="metric-card" style="text-align:center;"><div class="metric-label">{lbl}</div><div class="metric-value" style="color:{color};">{val}</div></div>', unsafe_allow_html=True)

    logic={"STRONG BUY":"Score>75 AND Price>200D SMA AND RSI 45–65 AND Volume confirmation.",
           "BUY":"Score≥65 AND Price>200D SMA.",
           "NEUTRAL":"Score 50–65. Monitor for improvement.",
           "AVOID":"Score<50. Do not enter."}
    st.markdown(ic(logic.get(signal,""),sig_color,"Signal Rationale"), unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;color:#334155;font-size:0.7rem;margin-top:20px;padding-top:10px;border-top:1px solid #1e2a45;">War Room Terminal · For educational purposes only — Not financial advice</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
