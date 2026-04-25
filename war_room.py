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

def ai_analyze_7_powers(ticker, company_name, sector, industry, description,
                         gross_margin, op_margin, rev_cagr, market_cap, stage):
    """Call Groq API (free) to automatically analyze which of Helmer's 7 Powers apply."""
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

    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                json={"model": "llama-3.3-70b-versatile", "max_tokens": 1000, "temperature": 0.3,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=30
            )
            if response.status_code != 200:
                continue
            raw = response.json()["choices"][0]["message"]["content"].strip()
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else parts[0]
                if raw.startswith("json"): raw = raw[4:]
            raw = raw.strip()
            result = json.loads(raw)
            if all(p in result for p in ALL_POWERS):
                return result
        except Exception:
            continue
    return None


def ai_news_sentiment(ticker, company_name, news_items):
    """Use Groq to analyze sentiment of latest news headlines."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key or not news_items:
            return None

        headlines = "\n".join([f"- {n.get('title','')}" for n in news_items[:5]])

        prompt = f"""You are a financial news analyst. Analyze these {company_name} ({ticker}) headlines and for each one give:
1. SENTIMENT: BULLISH / BEARISH / NEUTRAL
2. ONE LINE: Why it matters for the stock

Headlines:
{headlines}

Respond ONLY in JSON array format, no markdown:
[
  {{"headline": "...", "sentiment": "BULLISH/BEARISH/NEUTRAL", "impact": "one line why it matters"}},
  ...
]"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            json={"model": "llama-3.3-70b-versatile", "max_tokens": 800, "temperature": 0.2,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=20
        )
        raw = response.json()["choices"][0]["message"]["content"]
        raw = raw.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_top5_stocks():
    """Score a curated watchlist and return top 5 — includes AI powers estimate."""
    # Curated list of quality compounders across sectors
    watchlist = [
        "AAPL","MSFT","NVDA","GOOGL","META","AMZN","LLY","V","MA",
        "COST","AVGO","NOW","ADBE","INTU","UNH","JPM","BRK-B","TSLA","AMD","CRM"
    ]
    results = []
    for t in watchlist:
        try:
            tk = yf.Ticker(t)
            info = tk.info or {}
            hist = add_ta(tk.history(period="6mo", auto_adjust=True))
            fin  = tk.financials
            bal  = tk.balance_sheet
            cf   = tk.cashflow
            res  = score(info, hist, fin, bal, cf)

            # Estimate AI powers from sector/margin heuristics (no API call in batch)
            gm = sg(info,"grossMargins",np.nan) or 0
            sector = (sg(info,"sector","") or "").lower()
            industry = (sg(info,"industry","") or "").lower()
            estimated_powers = 0
            if gm > 0.50: estimated_powers += 1          # likely scale/branding
            if "software" in industry or "internet" in sector: estimated_powers += 2
            if "semiconductor" in industry: estimated_powers += 1
            if sg(info,"marketCap",0) > 100e9: estimated_powers += 1  # scale
            if gm > 0.70: estimated_powers += 1           # strong branding/switching costs
            estimated_pw_score = min(20, estimated_powers * (20/7))

            total = round(min(100, res["total"] + estimated_pw_score), 1)
            price_v = get_price(info, hist)
            prev = sg(info,"previousClose",np.nan)
            day_chg = (price_v-prev)/prev if not np.isnan(price_v) and not np.isnan(prev) and prev>0 else np.nan

            results.append({
                "ticker":  t,
                "name":    sg(info,"shortName", t),
                "score":   total,
                "price":   price_v,
                "chg":     day_chg,
                "signal":  get_signal_from_score(total, hist)[0],
                "sector":  sg(info,"sector","—"),
                "gm":      gm,
            })
        except Exception:
            continue
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]


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
    """Get row from financial dataframe — exact match first, then substring."""
    try:
        if df is None or df.empty: return default
        # Try exact match first
        if name in df.index:
            v = df.loc[name].iloc[idx]
            return float(v) if not pd.isna(v) else default
        # Try case-insensitive exact
        for r in df.index:
            if r.lower() == name.lower():
                v = df.loc[r].iloc[idx]
                return float(v) if not pd.isna(v) else default
        # Fallback: substring (least preferred)
        matches = [r for r in df.index if name.lower() in r.lower()]
        # Prefer shorter match (more specific)
        matches.sort(key=lambda x: len(x))
        if not matches: return default
        v = df.loc[matches[0]].iloc[idx]
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
def score(info, hist, fin, bal, cf):
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

    # E. 7 POWERS — score comes from AI analysis AFTER the fact, starts at 0
    # Will be overridden in main() after AI runs. Powers_analysis is empty dict here.
    confirmed = []
    pw_s = 0
    sc["pw"] = pw_s; sc["n_pw"] = 0

    # ── TOTALS
    # New rational weights: Quality(25) + Expectations(20) + Valuation(20) + Technicals(15) + Powers(20) = 100
    # Scale each module to its target max
    q_raw    = sc["crp"] + sc["om_trend"] + sc["fcf_q"]   # raw max = 29
    e_raw    = sc["rc"]  + sc["ec"]                        # raw max = 14
    v_raw    = sc["fy"]  + sc["pe"]  + sc["pg"]            # raw max = 14
    tech_raw = sc["st2"] + sc["rsi"] + sc["vol"]           # raw max = 14

    # Scale to new target weights
    q    = round(min(25, q_raw    * 25 / 29), 1)
    e    = round(min(20, e_raw    * 20 / 14), 1)
    v    = round(min(20, v_raw    * 20 / 14), 1)
    tech = round(min(15, tech_raw * 15 / 14), 1)
    pw   = 0  # filled in by AI after this function

    total = round(min(80, q + e + v + tech), 1)  # max 80 without powers; AI adds up to 20

    return {"total": total, "q": q, "e": e, "v": v,
            "tech": tech, "pw": pw,
            "q_raw": q_raw, "e_raw": e_raw, "v_raw": v_raw, "tech_raw": tech_raw,
            "sc": sc, "det": det, "confirmed": confirmed}

def get_signal_from_score(total, hist):
    s200_ok=rsi_ok=vol_ok=False
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

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.02,
        subplot_titles=("", "Volume", "RSI")
    )

    # ── Candlestick with wider candles ──
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        name="Price",
        increasing=dict(line=dict(color="#00d4aa", width=1), fillcolor="#00d4aa"),
        decreasing=dict(line=dict(color="#ff4757", width=1), fillcolor="#ff4757"),
        whiskerwidth=0.5,
    ), row=1, col=1)

    # ── SMAs with gradient style ──
    if "SMA50" in hist.columns:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["SMA50"], name="SMA 50",
            line=dict(color="#ffa502", width=2),
            opacity=0.9, hovertemplate="%{y:.2f}"
        ), row=1, col=1)

    if "SMA200" in hist.columns:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["SMA200"], name="SMA 200",
            line=dict(color="#a855f7", width=2),
            opacity=0.9, hovertemplate="%{y:.2f}"
        ), row=1, col=1)

    # ── Volume bars colored by up/down ──
    if "Volume" in hist.columns:
        up_mask   = hist["Close"] >= hist["Open"]
        down_mask = ~up_mask
        fig.add_trace(go.Bar(
            x=hist.index[up_mask], y=hist["Volume"][up_mask],
            name="Vol Up", marker_color="rgba(0,212,170,0.4)",
            showlegend=False
        ), row=2, col=1)
        fig.add_trace(go.Bar(
            x=hist.index[down_mask], y=hist["Volume"][down_mask],
            name="Vol Down", marker_color="rgba(255,71,87,0.4)",
            showlegend=False
        ), row=2, col=1)
        if "Vol20" in hist.columns:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Vol20"], name="Vol MA20",
                line=dict(color="#ffa502", width=1.2, dash="dot"),
                opacity=0.7
            ), row=2, col=1)

    # ── RSI with zones ──
    if "RSI" in hist.columns:
        rsi = hist["RSI"]
        fig.add_trace(go.Scatter(
            x=hist.index, y=rsi, name="RSI",
            line=dict(color="#60a5fa", width=2),
            fill=None
        ), row=3, col=1)
        # Color zones
        fig.add_hrect(y0=70, y1=100, row=3, col=1,
                      fillcolor="rgba(255,71,87,0.08)", line_width=0)
        fig.add_hrect(y0=0,  y1=30,  row=3, col=1,
                      fillcolor="rgba(255,71,87,0.08)", line_width=0)
        fig.add_hrect(y0=45, y1=65,  row=3, col=1,
                      fillcolor="rgba(0,212,170,0.06)", line_width=0)
        for lvl, clr, lbl in [
            (70, "rgba(255,71,87,0.6)",   "OB"),
            (30, "rgba(255,71,87,0.6)",   "OS"),
            (50, "rgba(100,116,139,0.4)", ""),
        ]:
            fig.add_hline(y=lvl, row=3, col=1,
                          line=dict(color=clr, width=1, dash="dot"),
                          annotation_text=lbl,
                          annotation_position="right",
                          annotation=dict(font=dict(size=9, color=clr)))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1220",
        font=dict(color="#94a3b8", family="Inter", size=11),
        height=560,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        margin=dict(l=60, r=30, t=30, b=30),
    )
    # Grid styling per row
    for i in range(1, 4):
        fig.update_xaxes(
            row=i, col=1,
            gridcolor="rgba(30,42,69,0.8)",
            linecolor="#2d3a5e",
            showgrid=True,
            zeroline=False,
        )
        fig.update_yaxes(
            row=i, col=1,
            gridcolor="rgba(30,42,69,0.8)",
            linecolor="#2d3a5e",
            showgrid=True,
            zeroline=False,
        )
    fig.update_yaxes(title_text="Price", row=1, col=1,
                     title_font=dict(size=10), tickprefix="$")
    fig.update_yaxes(title_text="Vol",   row=2, col=1,
                     title_font=dict(size=10))
    fig.update_yaxes(title_text="RSI",   row=3, col=1,
                     title_font=dict(size=10), range=[0, 100])
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

def breakdown_chart(res, ai_pw_score=0):
    cats=["Quality\n(25)","Expectations\n(20)","Valuation\n(20)","Technicals\n(15)","7 Powers\n(20)"]
    maxes=[25,20,20,15,20]
    vals=[res["q"],res["e"],res["v"],res["tech"],ai_pw_score]
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
        <p>Fundamental · Technical · AI-Powered 7 Powers Analysis</p>
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

    # ── ETF DETECTION ─────────────────────────────────────────────────────────
    quote_type = sg(info, "quoteType", "")
    is_etf = quote_type in ["ETF", "MUTUALFUND"] or sg(info, "fundFamily", None) is not None

    if is_etf:
        etf_website = sg(info,"website","")
        etf_logo = ""
        if etf_website:
            try:
                domain = etf_website.replace("https://","").replace("http://","").replace("www.","").split("/")[0]
                etf_logo = f'<img src="https://logo.clearbit.com/{domain}" style="height:38px;width:38px;border-radius:6px;object-fit:contain;background:#fff;padding:3px;margin-right:10px;vertical-align:middle;" onerror="this.style.display=\'none\'">'
            except: pass
        st.markdown(f"""
        <div style="background:#1a1f35;border:1px solid #2d3a5e;border-radius:12px;padding:20px 24px;margin-bottom:16px;display:flex;align-items:center;">
            {etf_logo}
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;">{sg(info,'longName',ticker)}</div>
                <div style="font-size:0.8rem;color:#64748b;margin-top:4px;">📊 ETF / Fund · {sg(info,'category','—')} · {sg(info,'fundFamily','—')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        price_etf = get_price(info, hist)
        prev_etf  = sg(info,"previousClose",np.nan)
        if np.isnan(prev_etf) and not hist.empty and len(hist)>=2:
            prev_etf = float(hist["Close"].iloc[-2])
        chg_etf = (price_etf-prev_etf)/prev_etf if not np.isnan(price_etf) and not np.isnan(prev_etf) and prev_etf>0 else np.nan
        chg_c_etf = "#10b981" if (isinstance(chg_etf,float) and not np.isnan(chg_etf) and chg_etf>=0) else "#ef4444"

        e1,e2,e3,e4,e5,e6 = st.columns(6)
        for col,(lbl,val) in zip([e1,e2,e3,e4,e5,e6],[
            ("Price",       f"${price_etf:.2f}" if not np.isnan(price_etf) else "N/A"),
            ("Day Chg",     f'<span style="color:{chg_c_etf}">{pct(chg_etf)}</span>'),
            ("52W High",    f"${sg(info,'fiftyTwoWeekHigh',np.nan):.2f}" if not np.isnan(sg(info,'fiftyTwoWeekHigh',np.nan)) else "N/A"),
            ("52W Low",     f"${sg(info,'fiftyTwoWeekLow',np.nan):.2f}"  if not np.isnan(sg(info,'fiftyTwoWeekLow',np.nan))  else "N/A"),
            ("Expense Ratio",pct(sg(info,'annualReportExpenseRatio',np.nan))),
            ("AUM",         fmt(sg(info,'totalAssets',np.nan),pre="$")),
        ]):
            with col: st.markdown(mc(lbl,val), unsafe_allow_html=True)

        st.markdown("---")
        col_p, col_n = st.columns([1,1])
        with col_p:
            if not hist.empty:
                st.plotly_chart(price_chart(hist, ticker), use_container_width=True, config={"displayModeBar":False})
        with col_n:
            st.markdown('<div class="section-header">📰 Latest News</div>', unsafe_allow_html=True)
            sorted_news = sorted([n for n in news if n.get("providerPublishTime")],
                                  key=lambda x: x.get("providerPublishTime",0), reverse=True)[:5]
            for item in (sorted_news or news[:5]):
                try:
                    title=item.get("title",""); pub=item.get("publisher",""); link=item.get("link","#")
                    ts=item.get("providerPublishTime",None)
                    date=datetime.fromtimestamp(ts).strftime("%b %d, %Y") if ts else "—"
                    st.markdown(f'<div class="news-card"><a href="{link}" target="_blank" style="text-decoration:none;"><div class="news-title">{title}</div></a><div class="news-meta">📰 {pub} · {date}</div></div>', unsafe_allow_html=True)
                except: continue

        st.info("⚠️ ETF detected — the full scoring model (Quality, Valuation, 7 Powers) is designed for individual stocks and does not apply to ETFs. Showing price chart and news only.")
        return

    res = score(info, hist, fin, bal, cf)
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

    # ── Run AI 7 Powers BEFORE rendering so signal/score are ready ───────────
    name     = sg(info,"longName",ticker)
    sector   = sg(info,"sector","—")
    industry = sg(info,"industry","—")

    with st.spinner("🤖 Analyzing 7 Powers with AI..."):
        powers_ai = ai_analyze_7_powers(
            ticker=ticker, company_name=name, sector=sector, industry=industry,
            description=sg(info,"longBusinessSummary",""),
            gross_margin=pct(sg(info,"grossMargins",np.nan)),
            op_margin=pct(sg(info,"operatingMargins",np.nan)),
            rev_cagr=pct(det.get("rc",np.nan)),
            market_cap=fmt(sg(info,"marketCap",np.nan),pre="$"),
            stage=det.get("stage","mature")
        )

    if powers_ai:
        ai_confirmed = [p for p,v in powers_ai.items() if v.get("verdict","NO").startswith("YES")]
        ai_partial   = [p for p,v in powers_ai.items() if v.get("verdict","NO").startswith("PARTIAL")]
        ai_pw_score  = round(min(20,(len(ai_confirmed)+len(ai_partial)*0.5)*(20/7)),1)
    else:
        ai_confirmed = []; ai_partial = []; ai_pw_score = 0

    final_total = round(min(100, res["total"] + ai_pw_score), 1)
    signal, sig_color = get_signal_from_score(final_total, hist)

    # ── ROW 1: Signal · Score · Header ──────────────────────────────────────
    c1,c2,c3 = st.columns([1.2,1.4,2.4])

    with c1:
        st.markdown(f'<div class="signal-{signal.replace(" ","_")}">{signal}</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="score-card"><div class="score-giant" style="color:{sig_color};">{final_total}</div><div class="score-label">Score / 100</div></div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div class="metric-label">Risk Level</div><div class="metric-value risk-{rl}" style="font-size:1.3rem;">{rl}</div></div>', unsafe_allow_html=True)
        stage_badge_color = "#f59e0b" if det.get("stage")=="growth" else "#64748b"
        stage_label = "GROWTH STAGE" if det.get("stage")=="growth" else "MATURE"
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div class="metric-label">Company Stage</div><div class="metric-value" style="font-size:0.9rem;color:{stage_badge_color};">{stage_label}</div></div>', unsafe_allow_html=True)

    with c2:
        st.plotly_chart(gauge_chart(final_total), use_container_width=True, config={"displayModeBar":False})

    with c3:
        mktcap   = sg(info,"marketCap",np.nan)
        beta_v   = det.get("beta",np.nan)
        w52h     = sg(info,"fiftyTwoWeekHigh",np.nan)
        w52l     = sg(info,"fiftyTwoWeekLow",np.nan)
        website  = sg(info,"website","")

        # Company logo via Clearbit (free, no API key needed)
        logo_html = ""
        if website:
            try:
                domain = website.replace("https://","").replace("http://","").replace("www.","").split("/")[0]
                logo_url = f"https://logo.clearbit.com/{domain}"
                logo_html = f'<img src="{logo_url}" style="height:42px;width:42px;border-radius:8px;object-fit:contain;background:#fff;padding:3px;margin-right:12px;vertical-align:middle;" onerror="this.style.display=\'none\'">'
            except: pass

        st.markdown(f'''
        <div style="display:flex;align-items:center;margin-bottom:8px;">
            {logo_html}
            <div>
                <div style="font-size:1.45rem;font-weight:700;color:#f1f5f9;line-height:1.2;">{name}</div>
                <div style="font-size:0.8rem;color:#64748b;">{ticker} · {sector} · {industry}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

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
        st.plotly_chart(breakdown_chart(res, ai_pw_score), use_container_width=True, config={"displayModeBar":False})
        if det.get("stage") == "growth":
            st.markdown(ic("🚀 <b>Growth Stage Mode</b> — CRP replaced by Gross Margin, Valuation uses P/S + Rule of 40.", "#f59e0b"), unsafe_allow_html=True)
        st.markdown('<div class="section-header">Module Drill-Down</div>', unsafe_allow_html=True)
        modules=[
            ("Quality / 25",      res["q"],              25),
            ("  ↳ CRP / GM",      res["sc"]["crp"],      10),
            ("  ↳ OM Trend",      res["sc"]["om_trend"], 10),
            ("  ↳ FCF Quality",   res["sc"]["fcf_q"],     9),
            ("Expectations / 20", res["e"],              20),
            ("  ↳ Rev CAGR",      res["sc"]["rc"],        7),
            ("  ↳ EPS CAGR",      res["sc"]["ec"],        7),
            ("Valuation / 20",    res["v"],              20),
            ("  ↳ FCF Yield",     res["sc"]["fy"],        5),
            ("  ↳ P/E or P/S",    res["sc"]["pe"],        5),
            ("  ↳ PEG / EV-Rev",  res["sc"]["pg"],        4),
            ("Technicals / 15",   res["tech"],           15),
            ("  ↳ Stage 2",       res["sc"]["st2"],       6),
            ("  ↳ RSI Zone",      res["sc"]["rsi"],       5),
            ("  ↳ Volume",        res["sc"]["vol"],       3),
            ("7 Powers / 20",     ai_pw_score,           20),
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

    # Update the score display with AI result
    cp, pp = st.columns([1, 2])

    with cp:
        st.plotly_chart(radar_chart(ai_confirmed), use_container_width=True, config={"displayModeBar":False})
        confirmed_count = len(ai_confirmed)
        partial_count   = len(ai_partial)
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="metric-label">AI Powers Score</div>
            <div class="metric-value" style="color:#3b82f6;font-size:2rem;">{ai_pw_score:.1f} / 20</div>
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
        st.markdown('<div class="section-header">Key Financial Metrics — Source: Yahoo Finance</div>', unsafe_allow_html=True)
        gm   = sg(info,"grossMargins",np.nan)
        om_  = sg(info,"operatingMargins",np.nan)
        nm   = sg(info,"profitMargins",np.nan)
        roe  = sg(info,"returnOnEquity",np.nan)
        roa  = sg(info,"returnOnAssets",np.nan)
        de   = sg(info,"debtToEquity",np.nan)
        cr   = sg(info,"currentRatio",np.nan)
        qr   = sg(info,"quickRatio",np.nan)
        # Use Yahoo's pre-calculated FCF — much more accurate than manual calc
        fcf_yahoo    = sg(info,"freeCashflow",np.nan)
        opcf_yahoo   = sg(info,"operatingCashflow",np.nan)
        rev_ttm      = sg(info,"totalRevenue",np.nan)
        ni_ttm       = sg(info,"netIncomeToCommon",np.nan)
        ebitda_yahoo = sg(info,"ebitda",np.nan)
        eps_ttm      = sg(info,"trailingEps",np.nan)
        eps_fwd      = sg(info,"forwardEps",np.nan)
        shares       = sg(info,"sharesOutstanding",np.nan)

        # FCF yield from Yahoo's FCF
        fcf_yield_display = np.nan
        if not np.isnan(fcf_yahoo) and not np.isnan(price) and not np.isnan(shares) and price>0 and shares>0:
            fcf_yield_display = (fcf_yahoo / shares) / price

        # FCF / NI ratio from Yahoo
        fcf_ni_display = np.nan
        if not np.isnan(fcf_yahoo) and not np.isnan(ni_ttm) and ni_ttm>0:
            fcf_ni_display = fcf_yahoo / ni_ttm

        for lbl,val,hint in [
            ("── PROFITABILITY ──",           "", ""),
            ("Gross Margin",                  pct(gm),   "Yahoo Finance TTM"),
            ("Operating Margin",              pct(om_),  "Yahoo Finance TTM"),
            ("Net Profit Margin",             pct(nm),   "Yahoo Finance TTM"),
            ("Return on Equity (ROE)",        pct(roe),  ">15% = strong"),
            ("Return on Assets (ROA)",        pct(roa),  ">5% = decent"),
            ("── CASH FLOW ──",               "", ""),
            ("Free Cash Flow (Yahoo)",        fmt(fcf_yahoo,pre="$"),   "Yahoo pre-calculated FCF"),
            ("Operating Cash Flow",           fmt(opcf_yahoo,pre="$"),  "Yahoo TTM"),
            ("FCF Yield",                     pct(fcf_yield_display),   "vs 4.4% Treasury benchmark"),
            ("FCF / Net Income",              pct(fcf_ni_display),      "≥80% = high earnings quality"),
            ("── INCOME ──",                  "", ""),
            ("Revenue (TTM)",                 fmt(rev_ttm,pre="$"),     "Yahoo TTM"),
            ("Net Income (TTM)",              fmt(ni_ttm,pre="$"),      "Yahoo TTM"),
            ("EBITDA",                        fmt(ebitda_yahoo,pre="$"),"Yahoo TTM"),
            ("EPS Trailing",                  f"${eps_ttm:.2f}" if eps_ttm and not np.isnan(eps_ttm) else "N/A", ""),
            ("EPS Forward",                   f"${eps_fwd:.2f}" if eps_fwd and not np.isnan(eps_fwd) else "N/A", ""),
            ("── BALANCE SHEET ──",           "", ""),
            ("Debt / Equity",                 f"{de/100:.2f}" if not np.isnan(de) else "N/A", "<0.5=conservative"),
            ("Current Ratio",                 f"{cr:.2f}" if not np.isnan(cr) else "N/A",    ">1.5=healthy"),
            ("Quick Ratio",                   f"{qr:.2f}" if not np.isnan(qr) else "N/A",    ">1.0=healthy"),
            ("── SCORING INPUTS ──",          "", ""),
            ("Capital Return Proxy (CRP)",    pct(det.get("crp",np.nan)), "Net Income/(Equity+Debt). >15%=excellent"),
            ("Rev CAGR (5Y→3Y fallback)",     pct(det.get("rc",np.nan)), "From annual financials"),
            ("EPS CAGR (5Y→3Y fallback)",     pct(det.get("ec",np.nan)), "From annual financials"),
            ("── TECHNICALS ──",              "", ""),
            ("RSI (14-day)",                  f"{det.get('rsi',np.nan):.1f}" if not np.isnan(det.get("rsi",np.nan)) else "N/A", "45–65=optimal"),
            ("ATR %",                         pct(det.get("atr",np.nan)), "<3%=LOW volatility"),
            ("Beta",                          f"{det.get('beta',np.nan):.2f}" if not np.isnan(det.get("beta",np.nan)) else "N/A", "vs S&P 500"),
        ]:
            if val == "" and hint == "":
                st.markdown(f'<div style="font-size:0.68rem;color:#3b82f6;text-transform:uppercase;letter-spacing:1px;margin:10px 0 4px;padding-top:6px;border-top:1px solid #1e2a45;">{lbl}</div>', unsafe_allow_html=True)
            else:
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

    # ── ROW 6: News + AI Sentiment ───────────────────────────────────────────
    st.markdown('<div class="section-header">📰 Latest News + AI Sentiment</div>', unsafe_allow_html=True)

    sorted_news = []
    if news:
        sorted_news = sorted([n for n in news if n.get("providerPublishTime")],
                             key=lambda x: x.get("providerPublishTime",0), reverse=True)[:5]
        if not sorted_news: sorted_news = news[:5]

    if sorted_news:
        with st.spinner("🤖 Analyzing news sentiment..."):
            sentiments = ai_news_sentiment(ticker, name, sorted_news)

        sent_map = {}
        if sentiments:
            for item in sentiments:
                key = item.get("headline","")[:40]
                sent_map[key] = item

        for i, item in enumerate(sorted_news):
            try:
                title = item.get("title","No title")
                pub   = item.get("publisher","Unknown")
                link  = item.get("link","#")
                ts    = item.get("providerPublishTime",None)
                date  = datetime.fromtimestamp(ts).strftime("%b %d, %Y") if ts else "—"

                # Match sentiment
                sent_data = None
                for key, val in sent_map.items():
                    if key.lower() in title.lower() or title.lower()[:40] in key.lower():
                        sent_data = val
                        break
                if not sent_data and sentiments and i < len(sentiments):
                    sent_data = sentiments[i]

                sent_label = sent_data.get("sentiment","NEUTRAL") if sent_data else "NEUTRAL"
                sent_impact = sent_data.get("impact","") if sent_data else ""
                sent_color = "#10b981" if sent_label=="BULLISH" else "#ef4444" if sent_label=="BEARISH" else "#f59e0b"
                sent_icon  = "🟢" if sent_label=="BULLISH" else "🔴" if sent_label=="BEARISH" else "🟡"

                st.markdown(f"""
                <div class="news-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                        <a href="{link}" target="_blank" style="text-decoration:none;flex:1;">
                            <div class="news-title">{title}</div>
                        </a>
                        <span style="font-size:0.72rem;font-weight:700;color:{sent_color};white-space:nowrap;padding:2px 8px;background:rgba(0,0,0,0.3);border-radius:8px;border:1px solid {sent_color};">{sent_icon} {sent_label}</span>
                    </div>
                    <div class="news-meta">📰 {pub} &nbsp;·&nbsp; 🕐 {date}</div>
                    {"<div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>💡 " + sent_impact + "</div>" if sent_impact else ""}
                </div>
                """, unsafe_allow_html=True)
            except: continue
    else:
        st.info("No recent news available for this ticker.")

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
        if final_total<50: bear.append(f"Score {final_total}/100 below 50 — AVOID threshold")
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
        ("Score / 100",   str(final_total),          sig_color),
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

    st.markdown("---")

    # ── TOP 5 STOCKS OF THE DAY ──────────────────────────────────────────────
    st.markdown('<div class="section-header">🏅 Top 5 Stocks Today — Ranked by War Room Score</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.78rem;color:#64748b;margin-bottom:10px;">Screened from a quality watchlist · Scored by our 100-pt model · Updates every hour</div>', unsafe_allow_html=True)

    with st.spinner("Scoring top stocks..."):
        top5 = get_top5_stocks()

    if top5:
        cols_top = st.columns(5)
        for col, stock in zip(cols_top, top5):
            sig_c = {"STRONG BUY":"#10b981","BUY":"#3b82f6","NEUTRAL":"#f59e0b","AVOID":"#ef4444"}.get(stock["signal"],"#94a3b8")
            chg_c = "#10b981" if not np.isnan(stock["chg"]) and stock["chg"]>=0 else "#ef4444"
            chg_str = f"{stock['chg']*100:+.1f}%" if not np.isnan(stock["chg"]) else "N/A"
            price_str = f"${stock['price']:.2f}" if not np.isnan(stock["price"]) else "N/A"
            with col:
                st.markdown(f"""
                <div style="background:#151c30;border:1px solid {sig_c};border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#f1f5f9;">{stock['ticker']}</div>
                    <div style="font-size:0.7rem;color:#64748b;margin:2px 0 6px;">{stock['name'][:18]}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:{sig_c};">{stock['score']:.0f}</div>
                    <div style="font-size:0.65rem;color:#475569;">Score / 100</div>
                    <div style="margin-top:6px;font-size:0.82rem;color:#e2e8f0;">{price_str}</div>
                    <div style="font-size:0.78rem;color:{chg_c};">{chg_str}</div>
                    <div style="margin-top:6px;font-size:0.68rem;font-weight:700;color:{sig_c};background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:6px;">{stock['signal']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Unable to load top stocks at this time.")

    st.markdown('<div style="text-align:center;color:#334155;font-size:0.7rem;margin-top:20px;padding-top:10px;border-top:1px solid #1e2a45;">War Room Terminal · For educational purposes only — Not financial advice</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
