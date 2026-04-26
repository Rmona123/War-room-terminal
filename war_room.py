"""
War Room — Stock Research & Portfolio Tracker
Dynamic scoring: sector-specific weights, macro overlay, stage-aware framework
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

st.set_page_config(page_title="War Room", page_icon="⚔️",
                   layout="wide", initial_sidebar_state="collapsed")

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#070d1a;color:#e2e8f0;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 2rem;max-width:1440px;}
div[data-testid="stSidebar"]{background:#0a1020 !important;border-right:1px solid #1a2540;}
.stTabs [data-baseweb="tab-list"]{background:#0d1525;border-radius:10px;padding:4px;gap:4px;border:1px solid #1a2540;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#64748b;border-radius:8px;font-weight:500;font-size:0.88rem;padding:8px 20px;}
.stTabs [aria-selected="true"]{background:#1e3a5f !important;color:#93c5fd !important;}
.card{background:#0d1525;border:1px solid #1a2540;border-radius:12px;padding:16px 18px;margin-bottom:10px;}
.card-sm{background:#0d1525;border:1px solid #1a2540;border-radius:10px;padding:11px 13px;margin-bottom:7px;}
.mlabel{font-size:0.67rem;color:#475569;text-transform:uppercase;letter-spacing:0.8px;}
.mvalue{font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:600;color:#f1f5f9;margin-top:1px;}
.msub{font-size:0.67rem;color:#64748b;margin-top:1px;}
.slabel{font-size:0.67rem;text-transform:uppercase;letter-spacing:1.5px;color:#334155;margin:14px 0 7px;padding-bottom:4px;border-bottom:1px solid #1a2540;}
.sig{padding:5px 13px;border-radius:8px;font-weight:700;font-size:0.9rem;display:inline-block;}
.sig-sb{background:#052e1c;border:1px solid #10b981;color:#6ee7b7;}
.sig-b{background:#0f2044;border:1px solid #3b82f6;color:#93c5fd;}
.sig-n{background:#1c1a08;border:1px solid #f59e0b;color:#fcd34d;}
.sig-av{background:#2a0a0a;border:1px solid #ef4444;color:#fca5a5;}
.pcard{border-radius:8px;padding:9px 12px;margin:4px 0;border-left:3px solid;}
.pcard-yes{background:#051a10;border-color:#10b981;}
.pcard-part{background:#1a1505;border-color:#f59e0b;}
.pcard-no{background:#0d1525;border-color:#1a2540;}
.macro-good{background:#051a10;border:1px solid #10b981;border-radius:8px;padding:10px 14px;margin:4px 0;}
.macro-warn{background:#1a1505;border:1px solid #f59e0b;border-radius:8px;padding:10px 14px;margin:4px 0;}
.macro-bad{background:#1a0808;border:1px solid #ef4444;border-radius:8px;padding:10px 14px;margin:4px 0;}
.stButton>button{background:#1e3a5f !important;color:#93c5fd !important;border:1px solid #2d5a8e !important;border-radius:8px !important;font-weight:600 !important;}
.stTextInput>div>div>input,.stNumberInput>div>div>input{background:#0d1525 !important;border:1px solid #1a2540 !important;color:#f1f5f9 !important;border-radius:8px !important;}
.stTextArea>div>textarea{background:#0d1525 !important;border:1px solid #1a2540 !important;color:#f1f5f9 !important;border-radius:8px !important;}
.stDataFrame{background:#0d1525 !important;}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def sg(d, k, default=None):
    try: v=d.get(k,default); return v if v is not None else default
    except: return default

def sr(df, name, idx=0, default=np.nan):
    try:
        if df is None or df.empty: return default
        if name in df.index:
            v=df.loc[name].iloc[idx]; return float(v) if not pd.isna(v) else default
        for r in df.index:
            if r.lower()==name.lower():
                v=df.loc[r].iloc[idx]; return float(v) if not pd.isna(v) else default
        m=sorted([r for r in df.index if name.lower() in r.lower()],key=len)
        if not m: return default
        v=df.loc[m[0]].iloc[idx]; return float(v) if not pd.isna(v) else default
    except: return default

def sf(v):
    try: f=float(v); return f if not np.isnan(f) else np.nan
    except: return np.nan

def pct(v,d=1):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "N/A"
    return f"{v*100:.{d}f}%"

def fmtn(v,d=2,pre="",suf=""):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "N/A"
    if abs(v)>=1e12: return f"{pre}{v/1e12:.{d}f}T{suf}"
    if abs(v)>=1e9:  return f"{pre}{v/1e9:.{d}f}B{suf}"
    if abs(v)>=1e6:  return f"{pre}{v/1e6:.{d}f}M{suf}"
    return f"{pre}{v:.{d}f}{suf}"

def m(label,value,sub="",color="#f1f5f9"):
    s=f"<div class='msub'>{sub}</div>" if sub else ""
    return f"<div class='card-sm'><div class='mlabel'>{label}</div><div class='mvalue' style='color:{color};'>{value}</div>{s}</div>"

def sig_badge(signal):
    cls={"STRONG BUY":"sig-sb","BUY":"sig-b","NEUTRAL":"sig-n","AVOID":"sig-av"}.get(signal,"sig-n")
    return f"<span class='sig {cls}'>{signal}</span>"

def cagr(series,yrs):
    try:
        s=[x for x in series if x and not np.isnan(x) and x>0]
        if len(s)<2: return np.nan
        n=min(yrs,len(s)-1)
        return (s[0]/s[n])**(1/n)-1
    except: return np.nan

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load(ticker):
    t=yf.Ticker(ticker)
    info={}; hist=pd.DataFrame(); fin=pd.DataFrame(); bal=pd.DataFrame(); cf=pd.DataFrame()
    try: info=t.info or {}
    except: pass
    try: hist=t.history(period="2y",auto_adjust=True)
    except: pass
    try: fin=t.financials
    except: pass
    try: bal=t.balance_sheet
    except: pass
    try: cf=t.cashflow
    except: pass
    return info,hist,fin,bal,cf

@st.cache_data(ttl=900, show_spinner=False)
def load_macro():
    """Load macro context: rates, sector ETF performance, VIX."""
    macro={}
    try:
        # 10Y Treasury yield proxy via TLT (inverse)
        tlt=yf.Ticker("TLT").history(period="6mo",auto_adjust=True)
        if not tlt.empty:
            tlt_3m=( tlt["Close"].iloc[-1] / tlt["Close"].iloc[-63] - 1 ) if len(tlt)>63 else np.nan
            macro["tlt_3m"]=tlt_3m  # falling TLT = rising rates = bad for growth stocks
    except: pass
    try:
        vix=yf.Ticker("^VIX").history(period="5d",auto_adjust=True)
        if not vix.empty: macro["vix"]=float(vix["Close"].iloc[-1])
    except: pass
    try:
        spy=yf.Ticker("SPY").history(period="6mo",auto_adjust=True)
        if not spy.empty:
            macro["spy_3m"]=(spy["Close"].iloc[-1]/spy["Close"].iloc[-63]-1) if len(spy)>63 else np.nan
            macro["spy_1m"]=(spy["Close"].iloc[-1]/spy["Close"].iloc[-21]-1) if len(spy)>21 else np.nan
    except: pass

    # Sector ETFs
    sector_etfs={"tech":"XLK","semis":"SOXX","biotech":"XBI","energy":"XLE",
                 "financials":"XLF","consumer":"XLY","health":"XLV","industrials":"XLI"}
    macro["sectors"]={}
    for name,etf in sector_etfs.items():
        try:
            h=yf.Ticker(etf).history(period="3mo",auto_adjust=True)
            if not h.empty and len(h)>10:
                ret_1m=(h["Close"].iloc[-1]/h["Close"].iloc[-21]-1) if len(h)>21 else np.nan
                ret_3m=(h["Close"].iloc[-1]/h["Close"].iloc[0]-1)
                macro["sectors"][name]={"1m":ret_1m,"3m":ret_3m,"etf":etf}
        except: pass
    return macro

@st.cache_data(ttl=60, show_spinner=False)
def quick_quote(ticker):
    try:
        t=yf.Ticker(ticker); info=t.info or {}
        hist=t.history(period="5d",auto_adjust=True)
        price=None
        for f in ["currentPrice","regularMarketPrice","previousClose"]:
            v=info.get(f)
            if v:
                try:
                    fv=float(v)
                    if not np.isnan(fv) and fv>0: price=fv; break
                except: pass
        if price is None and not hist.empty: price=float(hist["Close"].iloc[-1])
        prev=sf(info.get("previousClose",np.nan))
        if np.isnan(prev) and not hist.empty and len(hist)>=2: prev=float(hist["Close"].iloc[-2])
        chg=(price-prev)/prev if price and not np.isnan(prev) and prev>0 else np.nan
        return {"price":price or np.nan,"chg":chg,"name":info.get("shortName",ticker),
                "mktcap":sf(info.get("marketCap",np.nan)),"pe":sf(info.get("trailingPE",np.nan)),
                "hi52":sf(info.get("fiftyTwoWeekHigh",np.nan)),"lo52":sf(info.get("fiftyTwoWeekLow",np.nan))}
    except: return {"price":np.nan,"chg":np.nan,"name":ticker,"mktcap":np.nan,"pe":np.nan,"hi52":np.nan,"lo52":np.nan}

def add_ta(hist):
    if hist.empty: return hist
    h=hist.copy()
    try:
        h["SMA50"]=h["Close"].rolling(50).mean()
        h["SMA200"]=h["Close"].rolling(200).mean()
        h["Vol20"]=h["Volume"].rolling(20).mean()
        d=h["Close"].diff()
        g=d.clip(lower=0).rolling(14).mean()
        l=(-d.clip(upper=0)).rolling(14).mean()
        h["RSI"]=100-(100/(1+g/l.replace(0,np.nan)))
        tr=pd.concat([h["High"]-h["Low"],(h["High"]-h["Close"].shift()).abs(),(h["Low"]-h["Close"].shift()).abs()],axis=1).max(axis=1)
        h["ATR"]=tr.rolling(14).mean()
        # Relative strength vs SPY
        try:
            spy=yf.Ticker("SPY").history(period="3mo",auto_adjust=True)
            if not spy.empty and len(spy)>20:
                last_spy=float(spy["Close"].iloc[-1]); spy_63=float(spy["Close"].iloc[max(0,len(spy)-63)])
                last_close=float(h["Close"].iloc[-1]); close_63=float(h["Close"].iloc[max(0,len(h)-63)])
                if spy_63>0 and close_63>0:
                    h_rs=(last_close/close_63-1)-(last_spy/spy_63-1)
                    h["RS_vs_SPY"]=h_rs
        except: pass
    except: pass
    return h

def get_price(info,hist):
    for f in ["currentPrice","regularMarketPrice","previousClose","ask","bid"]:
        v=info.get(f)
        if v:
            try:
                fv=float(v)
                if not np.isnan(fv) and fv>0: return fv
            except: pass
    if not hist.empty: return float(hist["Close"].iloc[-1])
    return np.nan

# ─────────────────────────────────────────────────────────────────────────────
# STAGE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────
def classify(info, fin):
    """
    Returns (stage, sector_type) tuple.
    stage: mature | growth | cyclical | early_stage | biotech
    sector_type: tech | semis | biotech | energy | financial | consumer | industrial | other
    """
    industry=(sg(info,"industry","") or "").lower()
    sector  =(sg(info,"sector","")   or "").lower()
    desc    =(sg(info,"longBusinessSummary","") or "").lower()
    gm      =sf(sg(info,"grossMargins",np.nan)) or 0
    rg      =sf(sg(info,"revenueGrowth",np.nan))
    mktcap  =sf(sg(info,"marketCap",np.nan)) or 0
    rev     =sf(sg(info,"totalRevenue",np.nan)) or 0
    ni      =sr(fin,"Net Income")

    # ── SECTOR TYPE ──────────────────────────────────────────────────────────
    if any(x in industry for x in ["drug","pharma","biotech","biolog"]):
        stype="biotech"
    elif any(x in industry for x in ["semiconductor","chip"]):
        stype="semis"
    elif any(x in industry for x in ["software","saas","cloud","internet","data"]):
        stype="tech"
    elif any(x in industry or x in sector for x in ["oil","gas","petroleum","energy","mining","metal"]):
        stype="energy"
    elif any(x in sector for x in ["financial","bank"]):
        stype="financial"
    elif any(x in sector for x in ["consumer"]):
        stype="consumer"
    elif any(x in sector for x in ["industrial","manufactur"]):
        stype="industrial"
    else:
        stype="other"

    # ── STAGE ────────────────────────────────────────────────────────────────
    # Early-stage biotech: little/no revenue, burning cash, clinical stage
    if stype=="biotech" and rev < 500e6:
        return "early_stage", stype

    # Platform semis (NVDA, AMD, AVGO, QCOM) vs commodity semis (MU, WDC)
    is_platform_semi = stype=="semis" and (
        gm>0.50 or
        any(x in desc for x in ["gpu","ai chip","accelerat","inference","training","neural","architect"]) or
        (mktcap>200e9 and not any(x in desc for x in ["memory","dram","nand","flash"]))
    )

    # Commodity cyclicals
    cyclical_kw=["memory","dram","nand","steel","aluminum","copper","iron","oil","gas",
                 "petroleum","refin","mining","gold","silver","coal","chemical",
                 "fertilizer","airline","shipping","paper","timber"]
    is_cyclical=(any(k in industry or k in desc[:200] for k in cyclical_kw) and not is_platform_semi)
    if is_cyclical: return "cyclical", stype

    # High-growth: fast revenue, may not be profitable yet
    rv_r=[r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"] if not fin.empty else []
    rc_v=np.nan
    if rv_r:
        s=[float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
        rc_v=cagr(s,3)
    fast=(not np.isnan(rc_v) and rc_v>0.15) or (not np.isnan(rg) and rg>0.15)
    if not np.isnan(ni) and ni<0 and (fast or gm>0.35): return "growth", stype
    if np.isnan(sf(sg(info,"trailingPE",np.nan))) and fast: return "growth", stype

    return "mature", stype

# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC WEIGHT TABLE
# ─────────────────────────────────────────────────────────────────────────────
WEIGHTS = {
    # (stage, stype) -> {module: max_pts}
    # Total always = 100 (+ macro overlay ±10)
    ("mature",      "tech"):       {"quality":20,"expectations":20,"valuation":20,"technicals":20,"powers":20},
    ("mature",      "semis"):      {"quality":20,"expectations":20,"valuation":20,"technicals":20,"powers":20},
    ("mature",      "financial"):  {"quality":30,"expectations":15,"valuation":25,"technicals":20,"powers":10},
    ("mature",      "consumer"):   {"quality":25,"expectations":15,"valuation":20,"technicals":20,"powers":20},
    ("mature",      "industrial"): {"quality":25,"expectations":15,"valuation":20,"technicals":20,"powers":20},
    ("mature",      "energy"):     {"quality":20,"expectations":20,"valuation":20,"technicals":25,"powers":15},
    ("mature",      "other"):      {"quality":25,"expectations":15,"valuation":20,"technicals":20,"powers":20},
    ("growth",      "tech"):       {"quality":10,"expectations":25,"valuation":15,"technicals":20,"powers":30},
    ("growth",      "semis"):      {"quality":15,"expectations":25,"valuation":15,"technicals":20,"powers":25},
    ("growth",      "other"):      {"quality":10,"expectations":25,"valuation":15,"technicals":20,"powers":30},
    ("cyclical",    "energy"):     {"quality":15,"expectations":25,"valuation":15,"technicals":30,"powers":15},
    ("cyclical",    "semis"):      {"quality":20,"expectations":20,"valuation":15,"technicals":30,"powers":15},
    ("cyclical",    "other"):      {"quality":15,"expectations":25,"valuation":15,"technicals":30,"powers":15},
    ("early_stage", "biotech"):    {"quality":5, "expectations":20,"valuation":10,"technicals":30,"powers":35},
    ("early_stage", "other"):      {"quality":5, "expectations":20,"valuation":15,"technicals":30,"powers":30},
}

def get_weights(stage, stype):
    key=(stage,stype)
    if key in WEIGHTS: return WEIGHTS[key]
    # Fallback: match on stage only
    for k,v in WEIGHTS.items():
        if k[0]==stage: return v
    return {"quality":20,"expectations":20,"valuation":20,"technicals":20,"powers":20}

# ─────────────────────────────────────────────────────────────────────────────
# MACRO OVERLAY  (±15 pts on top of 100)
# ─────────────────────────────────────────────────────────────────────────────
def macro_overlay(macro, stage, stype, hist):
    """
    Returns (score_delta, factors) where score_delta is between -15 and +15.
    Considers: rate environment, sector momentum, market regime, relative strength.
    """
    if not macro: return 0, []
    delta=0; factors=[]

    vix=macro.get("vix",20)
    spy_3m=macro.get("spy_3m",np.nan)
    spy_1m=macro.get("spy_1m",np.nan)
    tlt_3m=macro.get("tlt_3m",np.nan)  # negative = rates rising
    sectors=macro.get("sectors",{})

    # ── 1. MARKET REGIME ─────────────────────────────────────────────────────
    if not np.isnan(spy_3m):
        if spy_3m > 0.08:
            delta+=3; factors.append(("🟢 Bull market regime","S&P 500 up {:.1f}% in 3M — risk-on environment supports multiples.".format(spy_3m*100)))
        elif spy_3m < -0.08:
            delta-=3; factors.append(("🔴 Bear market regime","S&P 500 down {:.1f}% in 3M — multiple compression, risk-off.".format(abs(spy_3m)*100)))
        elif spy_3m < -0.03:
            delta-=1; factors.append(("🟡 Market under pressure","S&P 500 down {:.1f}% in 3M — cautious environment.".format(abs(spy_3m)*100)))

    # ── 2. VOLATILITY REGIME ─────────────────────────────────────────────────
    if not np.isnan(vix):
        if vix > 30:
            delta-=2; factors.append(("🔴 Elevated fear (VIX {:.0f})".format(vix),"High VIX signals market stress — be selective, position sizing matters."))
        elif vix < 15:
            delta+=1; factors.append(("🟢 Low volatility (VIX {:.0f})".format(vix),"Complacent market — good for momentum but watch for sudden reversals."))

    # ── 3. RATE ENVIRONMENT ───────────────────────────────────────────────────
    if not np.isnan(tlt_3m):
        rate_rising = tlt_3m < -0.03   # TLT falling = rates rising
        rate_falling= tlt_3m > 0.03    # TLT rising = rates falling
        if rate_rising and stage in ["growth","early_stage"]:
            delta-=4; factors.append(("🔴 Rising rates — headwind for {}".format(stage),"TLT down {:.1f}% → rates rising. Growth/long-duration stocks face multiple compression. This is the single biggest macro risk for high-multiple companies.".format(abs(tlt_3m)*100)))
        elif rate_rising and stage=="mature":
            delta-=1; factors.append(("🟡 Rates rising","Mild headwind for mature stocks — rising discount rates compress all multiples."))
        elif rate_falling and stage in ["growth","early_stage"]:
            delta+=4; factors.append(("🟢 Falling rates — tailwind for {}".format(stage),"TLT up {:.1f}% → rates falling. Significant multiple expansion catalyst for growth/long-duration stocks.".format(tlt_3m*100)))
        elif rate_falling:
            delta+=2; factors.append(("🟢 Falling rates","Rate cuts typically expand multiples across sectors — tailwind."))

    # ── 4. SECTOR MOMENTUM ───────────────────────────────────────────────────
    sector_map={"tech":"tech","semis":"semis","biotech":"biotech","energy":"energy",
                "financial":"financials","consumer":"consumer","industrial":"industrials"}
    sect_key=sector_map.get(stype,"tech")
    if sect_key in sectors:
        s1m=sectors[sect_key].get("1m",np.nan)
        s3m=sectors[sect_key].get("3m",np.nan)
        etf=sectors[sect_key].get("etf","")
        if not np.isnan(s3m):
            if s3m > 0.12:
                delta+=3; factors.append(("🟢 {etf} sector in strong uptrend ({r:+.1f}% 3M)".format(etf=etf,r=s3m*100),"Sector momentum is a powerful force — institutional flows are favorable. Trend is your friend."))
            elif s3m > 0.05:
                delta+=1; factors.append(("🟢 {etf} sector momentum positive ({r:+.1f}% 3M)".format(etf=etf,r=s3m*100),"Sector has positive but moderate momentum."))
            elif s3m < -0.10:
                delta-=3; factors.append(("🔴 {etf} sector in downtrend ({r:+.1f}% 3M)".format(etf=etf,r=s3m*100),"Sector-wide selling pressure — even good stocks struggle when the sector is out of favor. Don't fight institutional flows."))
            elif s3m < -0.04:
                delta-=1; factors.append(("🟡 {etf} sector under pressure ({r:+.1f}% 3M)".format(etf=etf,r=s3m*100),"Sector momentum negative — headwind for individual names."))

    # ── 5. RELATIVE STRENGTH ─────────────────────────────────────────────────
    if not hist.empty and "RS_vs_SPY" in hist.columns:
        rs=float(hist["RS_vs_SPY"].iloc[-1]) if not np.isnan(hist["RS_vs_SPY"].iloc[-1]) else np.nan
        if not np.isnan(rs):
            if rs > 0.10:
                delta+=2; factors.append(("🟢 Strong relative strength vs S&P 500","Stock outperforming S&P by {:.1f}% over 3M — institutional accumulation signal.".format(rs*100)))
            elif rs < -0.10:
                delta-=2; factors.append(("🔴 Weak relative strength vs S&P 500","Stock underperforming S&P by {:.1f}% over 3M — distribution or sector rotation away.".format(abs(rs)*100)))

    delta=max(-15, min(15, delta))
    return delta, factors

# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT SCORING FUNCTIONS  (each returns 0–100, then scaled to weight)
# ─────────────────────────────────────────────────────────────────────────────

def score_quality(info, fin, bal, cf, stage, stype):
    """Returns (raw_0_100, details_dict)"""
    det={}
    gm   =sf(sg(info,"grossMargins",np.nan))    or 0
    om   =sf(sg(info,"operatingMargins",np.nan)) or 0
    roe  =sf(sg(info,"returnOnEquity",np.nan))
    roa  =sf(sg(info,"returnOnAssets",np.nan))
    fcf  =sf(sg(info,"freeCashflow",np.nan))
    rev  =sf(sg(info,"totalRevenue",np.nan))     or 1
    ni_ttm=sf(sg(info,"netIncomeToCommon",np.nan))
    cash =sf(sg(info,"totalCash",np.nan))        or 0
    debt =sf(sg(info,"totalDebt",np.nan))        or 0
    cr   =sf(sg(info,"currentRatio",np.nan))

    det["gm"]=gm; det["om"]=om; det["roe"]=roe; det["roa"]=roa
    det["fcf"]=fcf; det["cash"]=cash; det["debt"]=debt

    # FCF ratio
    fcf_ni=np.nan
    if not np.isnan(fcf) and not np.isnan(ni_ttm) and ni_ttm>0:
        fcf_ni=fcf/ni_ttm
    det["fcf_ni"]=fcf_ni

    scores=[]

    if stage=="early_stage":
        # Early stage: survival metrics — cash runway, burn rate, gross margin potential
        burn=sf(sg(info,"operatingCashflow",np.nan))
        if not np.isnan(cash) and not np.isnan(burn) and burn<0:
            runway_months=cash/abs(burn)*12 if burn!=0 else 999
            det["runway_months"]=runway_months
            scores.append(min(100, runway_months/6*100) if runway_months<60 else 100)
        else:
            scores.append(50)  # unknown runway = neutral
        # Gross margin potential
        if not np.isnan(gm):
            scores.append(100 if gm>0.80 else 80 if gm>0.60 else 50 if gm>0.40 else 20)
        scores.append(50)  # don't punish for no NI

    elif stage=="cyclical":
        # Cyclical: through-cycle averages, balance sheet strength (survive the trough)
        ni_rows=[r for r in fin.index if r.lower()=="net income"] if not fin.empty else []
        avg_ni=np.nan
        if ni_rows and fin.shape[1]>=3:
            vals=[float(fin.loc[ni_rows[0]].iloc[i]) for i in range(min(5,fin.shape[1])) if not pd.isna(fin.loc[ni_rows[0]].iloc[i])]
            if vals: avg_ni=np.mean(vals)
        det["avg_ni"]=avg_ni

        # Through-cycle profitability
        if not np.isnan(avg_ni) and rev>0:
            avg_margin=avg_ni/rev
            scores.append(100 if avg_margin>0.15 else 80 if avg_margin>0.08 else 60 if avg_margin>0.02 else 40 if avg_margin>-0.02 else 20)
        else:
            scores.append(50)
        # Balance sheet (survive trough)
        net_debt=(debt-cash)/rev if rev>0 else 0
        scores.append(100 if net_debt<0 else 80 if net_debt<0.5 else 60 if net_debt<1.5 else 40 if net_debt<3 else 20)
        # FCF margin
        if not np.isnan(fcf):
            fcf_m=fcf/rev
            scores.append(100 if fcf_m>0.12 else 80 if fcf_m>0.06 else 60 if fcf_m>0 else 40 if fcf_m>-0.05 else 20)
        else:
            scores.append(50)

    elif stage=="growth":
        # Growth: gross margin (unit economics), FCF trajectory, burn sustainability
        if not np.isnan(gm):
            scores.append(100 if gm>0.75 else 85 if gm>0.60 else 65 if gm>0.45 else 40 if gm>0.25 else 15)
        else: scores.append(50)
        if not np.isnan(fcf):
            scores.append(100 if fcf>0 else 75 if fcf>-1e8 else 50 if fcf>-5e8 else 25)
        else: scores.append(40)
        # Net debt sustainability
        net_debt_abs=debt-cash
        if not np.isnan(ni_ttm) and not np.isnan(fcf) and fcf!=0:
            years_to_insolvency=abs(net_debt_abs)/abs(fcf) if fcf<0 and net_debt_abs>0 else 999
            scores.append(100 if years_to_insolvency>5 else 60 if years_to_insolvency>3 else 20)
        else: scores.append(60)

    else:  # mature
        # Mature: ROE/ROIC quality, FCF/NI quality, balance sheet
        if not np.isnan(roe):
            scores.append(100 if roe>0.25 else 85 if roe>0.15 else 65 if roe>0.08 else 35 if roe>0 else 0)
        elif not np.isnan(gm):
            scores.append(100 if gm>0.60 else 80 if gm>0.40 else 60 if gm>0.25 else 30)
        else: scores.append(50)

        if not np.isnan(fcf_ni):
            scores.append(100 if fcf_ni>=0.90 else 85 if fcf_ni>=0.75 else 65 if fcf_ni>=0.55 else 40 if fcf_ni>=0.35 else 20 if fcf_ni>0 else 0)
        elif not np.isnan(fcf) and fcf>0: scores.append(60)
        else: scores.append(20)

        if not np.isnan(om):
            scores.append(100 if om>0.30 else 80 if om>0.20 else 60 if om>0.12 else 35 if om>0.05 else 10)
        else: scores.append(50)

        # Balance sheet
        if stype!="financial":
            net_debt=(debt-cash)/rev if rev>0 else 0
            scores.append(100 if net_debt<0 else 80 if net_debt<0.5 else 55 if net_debt<1.5 else 30 if net_debt<3 else 10)

    raw=np.mean(scores) if scores else 50
    det["component_scores"]=scores
    return round(raw,1), det


def score_expectations(info, fin, stage, stype):
    """Returns (raw_0_100, details_dict)"""
    det={}

    # Forward estimates — priority order
    trailing_eps=sf(sg(info,"trailingEps",np.nan))
    forward_eps =sf(sg(info,"forwardEps",np.nan))
    fwd_pe      =sf(sg(info,"forwardPE",np.nan))
    trail_pe    =sf(sg(info,"trailingPE",np.nan))
    yh_eg       =sf(sg(info,"earningsGrowth",np.nan))
    yh_rg       =sf(sg(info,"revenueGrowth",np.nan))
    n_analysts  =sf(sg(info,"numberOfAnalystOpinions",np.nan))
    target      =sf(sg(info,"targetMeanPrice",np.nan))
    price       =sf(sg(info,"currentPrice",np.nan)) or sf(sg(info,"regularMarketPrice",np.nan))

    # Implied forward EPS growth
    fwd_eps_growth=np.nan
    if not np.isnan(trailing_eps) and not np.isnan(forward_eps) and trailing_eps!=0:
        fwd_eps_growth=(forward_eps-trailing_eps)/abs(trailing_eps)

    # PE-implied growth
    pe_implied=np.nan
    if not np.isnan(fwd_pe) and not np.isnan(trail_pe) and fwd_pe>0 and trail_pe>0:
        pe_implied=trail_pe/fwd_pe-1

    # Historical CAGR fallback
    rc_hist=np.nan
    if not fin.empty:
        rv_r=[r for r in fin.index if "total revenue" in r.lower() or r.lower()=="revenue"]
        if rv_r:
            s=[float(fin.loc[rv_r[0]].iloc[i]) for i in range(min(6,fin.shape[1])) if not pd.isna(fin.loc[rv_r[0]].iloc[i])]
            rc_hist=cagr(s,3)

    # Best estimates
    best_eg=fwd_eps_growth if not np.isnan(fwd_eps_growth) else \
            pe_implied if (not np.isnan(pe_implied) and pe_implied>-0.5) else \
            yh_eg if not np.isnan(yh_eg) else np.nan

    best_rg=yh_rg if not np.isnan(yh_rg) else rc_hist

    # Analyst price target upside
    upside=np.nan
    if not np.isnan(target) and not np.isnan(price) and price>0:
        upside=target/price-1

    # Analyst count confidence multiplier
    analyst_conf=1.0
    if not np.isnan(n_analysts):
        analyst_conf=1.0 if n_analysts>=5 else 0.8 if n_analysts>=2 else 0.5

    det.update({"eg":best_eg,"rg":best_rg,"upside":upside,
                "n_analysts":n_analysts,"fwd_eps":forward_eps,
                "trailing_eps":trailing_eps,"source":"forward" if not np.isnan(fwd_eps_growth) else "TTM"})

    scores=[]

    # Revenue growth score
    rg_s=0
    if not np.isnan(best_rg):
        if stage in ["growth","early_stage"]:
            rg_s=100 if best_rg>0.40 else 85 if best_rg>0.25 else 65 if best_rg>0.15 else 40 if best_rg>0.05 else 15
        elif stage=="cyclical":
            rg_s=100 if best_rg>0.20 else 75 if best_rg>0.08 else 55 if best_rg>0 else 35 if best_rg>-0.10 else 15
        else:
            rg_s=100 if best_rg>0.20 else 80 if best_rg>0.12 else 60 if best_rg>0.06 else 40 if best_rg>0 else 10
    else: rg_s=40
    scores.append(rg_s)

    # Earnings growth score
    eg_s=0
    if not np.isnan(best_eg):
        if stage in ["growth","early_stage"]:
            eg_s=100 if best_eg>0.40 else 80 if best_eg>0.25 else 60 if best_eg>0.10 else 35 if best_eg>0 else 15
        elif stage=="cyclical":
            eg_s=100 if best_eg>0.25 else 75 if best_eg>0.10 else 55 if best_eg>0 else 40 if best_eg>-0.15 else 15
        else:
            eg_s=100 if best_eg>0.25 else 80 if best_eg>0.15 else 60 if best_eg>0.08 else 40 if best_eg>0 else 10
    else: eg_s=35
    scores.append(eg_s * analyst_conf)

    # Analyst target upside
    if not np.isnan(upside):
        us=100 if upside>0.30 else 80 if upside>0.15 else 60 if upside>0.05 else 40 if upside>-0.05 else 15
        scores.append(us * analyst_conf)
    else:
        scores.append(40)

    raw=np.mean(scores)
    return round(raw,1), det


def score_valuation(info, hist, stage, stype):
    """Returns (raw_0_100, details_dict)"""
    det={}
    pe_t =sf(sg(info,"trailingPE",np.nan))
    pe_f =sf(sg(info,"forwardPE",np.nan))
    ps   =sf(sg(info,"priceToSalesTrailingTwelveMonths",np.nan))
    pb   =sf(sg(info,"priceToBook",np.nan))
    ev_eb=sf(sg(info,"enterpriseToEbitda",np.nan))
    eg   =sf(sg(info,"earningsGrowth",np.nan))
    fcf  =sf(sg(info,"freeCashflow",np.nan))
    mktcap=sf(sg(info,"marketCap",np.nan))
    rg   =sf(sg(info,"revenueGrowth",np.nan))

    # FCF yield
    fcf_yield=np.nan
    if not np.isnan(fcf) and not np.isnan(mktcap) and mktcap>0:
        fcf_yield=fcf/mktcap
    det.update({"pe_t":pe_t,"pe_f":pe_f,"ps":ps,"pb":pb,"ev_eb":ev_eb,"fcf_yield":fcf_yield})

    TREASURY=0.044
    scores=[]

    if stage in ["growth","early_stage"]:
        # Growth: PS ratio + revenue-adjusted EV/S
        if not np.isnan(ps) and not np.isnan(rg) and rg>0:
            # Rule of 40 price: PS divided by growth rate
            ps_adj=ps/((rg*100)/40) if rg>0 else ps  # normalize to 40% growth
            scores.append(100 if ps_adj<3 else 80 if ps_adj<6 else 60 if ps_adj<12 else 35 if ps_adj<20 else 10)
        elif not np.isnan(ps):
            scores.append(100 if ps<5 else 70 if ps<10 else 45 if ps<20 else 20)
        if not np.isnan(pe_f):
            scores.append(100 if pe_f<25 else 75 if pe_f<40 else 50 if pe_f<60 else 25)
        if fcf_yield and not np.isnan(fcf_yield) and fcf_yield>0:
            scores.append(100 if fcf_yield>0.05 else 70 if fcf_yield>0.02 else 50)

    elif stage=="cyclical":
        # Cyclical: EV/EBITDA (cycle-smoothed), PB (asset-based)
        if not np.isnan(ev_eb) and ev_eb>0:
            scores.append(100 if ev_eb<5 else 80 if ev_eb<8 else 55 if ev_eb<12 else 25 if ev_eb<20 else 10)
        if not np.isnan(pb) and pb>0:
            scores.append(100 if pb<1.0 else 80 if pb<2.0 else 55 if pb<3.5 else 30)
        if not np.isnan(fcf_yield):
            scores.append(100 if fcf_yield>TREASURY*3 else 75 if fcf_yield>TREASURY*1.5 else 50 if fcf_yield>TREASURY else 25)

    else:  # mature
        # Mature: FCF yield vs Treasury, forward PE, EV/EBITDA
        if not np.isnan(fcf_yield):
            scores.append(100 if fcf_yield>TREASURY*2.5 else 85 if fcf_yield>TREASURY*1.5 else 65 if fcf_yield>TREASURY else 40 if fcf_yield>TREASURY*0.5 else 15)
        if not np.isnan(pe_f):
            scores.append(100 if pe_f<12 else 80 if pe_f<18 else 60 if pe_f<25 else 35 if pe_f<35 else 10)
        elif not np.isnan(pe_t):
            scores.append(100 if pe_t<12 else 75 if pe_t<18 else 55 if pe_t<25 else 30 if pe_t<35 else 10)
        if not np.isnan(ev_eb) and ev_eb>0:
            scores.append(100 if ev_eb<8 else 80 if ev_eb<12 else 55 if ev_eb<18 else 25)

    # PEG for non-early-stage
    if stage not in ["early_stage","cyclical"] and not np.isnan(pe_t) and not np.isnan(eg) and eg>0:
        peg=pe_t/(eg*100)
        det["peg"]=peg
        scores.append(100 if peg<0.8 else 80 if peg<1.2 else 55 if peg<1.8 else 30 if peg<2.5 else 10)

    raw=np.mean(scores) if scores else 40
    return round(raw,1), det


def score_technicals(hist, info, stage):
    """Returns (raw_0_100, details_dict)"""
    det={}
    if hist.empty: return 40, det

    try:
        last=hist.iloc[-1]; prev=hist.iloc[-2]
        cl=float(last["Close"]); s50=float(last.get("SMA50",np.nan))
        s200=float(last.get("SMA200",np.nan)); rsi=float(last.get("RSI",np.nan))
        atr=float(last.get("ATR",np.nan)); vol=float(last.get("Volume",np.nan))
        v20=float(last.get("Vol20",np.nan)); dchg=cl-float(prev["Close"])
        beta=sf(sg(info,"beta",np.nan))
        rs=float(hist["RS_vs_SPY"].iloc[-1]) if "RS_vs_SPY" in hist.columns and not np.isnan(hist["RS_vs_SPY"].iloc[-1]) else np.nan

        atr_pct=atr/cl if not np.isnan(atr) and cl>0 else np.nan

        det.update({"rsi":rsi,"atr":atr_pct,"beta":beta,"rs_spy":rs,
                    "above_50":cl>s50 if not np.isnan(s50) else None,
                    "above_200":cl>s200 if not np.isnan(s200) else None})

        scores=[]

        # Trend structure (Stage 2 = price > 50D > 200D)
        if not any(np.isnan(x) for x in [cl,s50,s200]):
            if cl>s50>s200:   t_s=100
            elif cl>s200:     t_s=65
            elif cl>s50:      t_s=45
            else:             t_s=20
            scores.append(t_s)

        # RSI — optimal zone varies by stage
        if not np.isnan(rsi):
            if stage=="cyclical":
                # Cyclicals: accept wider range, look for momentum off lows
                r_s=100 if 40<=rsi<=70 else 70 if 30<=rsi<40 or 70<rsi<=80 else 40
            elif stage in ["growth","early_stage"]:
                # Growth: momentum matters more, higher RSI ok
                r_s=100 if 50<=rsi<=75 else 75 if 40<=rsi<50 or 75<rsi<=85 else 40
            else:
                r_s=100 if 45<=rsi<=65 else 70 if 35<=rsi<45 or 65<rsi<=75 else 35
            scores.append(r_s)

        # Volume confirmation
        if not any(np.isnan(x) for x in [vol,v20]):
            if vol>v20 and dchg>0:   v_s=100
            elif vol>v20 and dchg<0: v_s=30  # high vol down = distribution
            elif dchg>0:             v_s=65
            else:                    v_s=40
            scores.append(v_s)

        # Relative strength vs SPY
        if not np.isnan(rs):
            if rs>0.15:   scores.append(100)
            elif rs>0.05: scores.append(80)
            elif rs>-0.05:scores.append(55)
            elif rs>-0.15:scores.append(30)
            else:         scores.append(10)

        raw=np.mean(scores) if scores else 40
        return round(raw,1), det
    except: return 40, det


# ─────────────────────────────────────────────────────────────────────────────
# 7 POWERS  (rule-based, no API)
# ─────────────────────────────────────────────────────────────────────────────
ALL_POWERS=["Scale Economies","Network Economies","Counter-Positioning",
            "Switching Costs","Branding","Cornered Resource","Process Power"]

def score_powers(info, fin, cf, ticker, stage, stype, q_det):
    """Returns (raw_0_100, powers_dict)"""
    industry=(sg(info,"industry","") or "").lower()
    sector  =(sg(info,"sector","")   or "").lower()
    desc    =(sg(info,"longBusinessSummary","") or "").lower()
    gm      =sf(sg(info,"grossMargins",np.nan))    or 0
    om      =sf(sg(info,"operatingMargins",np.nan)) or 0
    rg      =sf(sg(info,"revenueGrowth",np.nan))   or 0
    mktcap  =sf(sg(info,"marketCap",np.nan))       or 0
    rev     =sf(sg(info,"totalRevenue",np.nan))    or 1
    emp     =sf(sg(info,"fullTimeEmployees",np.nan)) or 0
    rd      =sr(fin,"Research And Development") or 0
    if np.isnan(rd): rd=0
    rd_pct  =rd/rev if rev>0 else 0
    sga     =sf(sg(info,"sellingGeneralAdministrative",np.nan)) or 0
    sga_pct =sga/rev if rev>0 and sga>0 else np.nan
    fcf     =sf(sg(info,"freeCashflow",np.nan)) or 0
    fcf_m   =fcf/rev if rev>0 else 0
    rev_per_emp=rev/emp if emp>0 else 0

    is_soft =any(x in industry for x in ["software","saas","cloud","internet","data"])
    is_semi =stype=="semis"
    is_pay  =any(x in industry for x in ["payment","credit","transaction"])
    is_mkt  =any(x in desc for x in ["marketplace","platform","two-sided","exchange"])
    is_cons =any(x in sector for x in ["consumer"])
    is_lux  =any(x in desc for x in ["luxury","premium","heritage","exclusive","iconic"])
    is_pharma=stype=="biotech"
    is_energy=stype=="energy"
    is_large=mktcap>100e9
    is_mega =mktcap>500e9
    has_ai  =any(x in desc for x in ["artificial intelligence","machine learning","foundation model",
                                       "large language","ai research","deep learning","gpu"])

    results={}

    # 1. SCALE ECONOMIES
    if is_mega and gm>0.55 and om>0.25:
        v,r="YES",f"Mega-cap with {gm*100:.0f}%/{om*100:.0f}% gross/op margins — massive fixed-cost base amortized over huge revenue creates structural unit cost advantage."
    elif is_semi and is_large and gm>0.45:
        v,r="YES",f"Semiconductor scale requires $20B+ fabs — only a handful can operate at cost parity. {gm*100:.0f}% gross margins confirm the advantage."
    elif is_energy and is_large:
        v,r="PARTIAL","Large E&P/integrated energy: infrastructure scale (pipelines, refineries) creates real cost advantages vs. smaller operators, but commodity price dominates."
    elif is_large and gm>0.40 and om>0.20:
        v,r="YES",f"Scale evident: {gm*100:.0f}% gross/{om*100:.0f}% op margins at ${mktcap/1e9:.0f}B scale — operational leverage hard for smaller competitors to match."
    elif mktcap>20e9 and gm>0.30 and om>0.12:
        v,r="PARTIAL",f"Some scale ({gm*100:.0f}% gross, {om*100:.0f}% op) but not yet prohibitively hard for a funded entrant to replicate."
    else:
        v,r="NO",f"No meaningful scale-driven cost advantage. GM {gm*100:.0f}%, mktcap ${mktcap/1e9:.0f}B insufficient."
    results["Scale Economies"]={"verdict":v,"reasoning":r}

    # 2. NETWORK ECONOMIES
    if is_pay and is_large:
        v,r="YES","Payments: textbook two-sided network — more merchants → more cardholders → more merchants. Self-reinforcing flywheel nearly impossible to displace."
    elif is_mkt and is_large and gm>0.50:
        v,r="YES",f"Marketplace platform {gm*100:.0f}% GM: each new buyer attracts more sellers and vice versa — network density IS the product."
    elif is_soft and is_large and any(x in desc for x in ["ecosystem","developer","api","integration","network effect"]):
        v,r="YES",f"Large software ecosystem {gm*100:.0f}% GM: indirect network effects from developer/partner integrations increase value for all participants."
    elif is_mkt or (is_soft and any(x in desc for x in ["community","connect","viral","flywheel"])):
        v,r="PARTIAL","Network characteristics present but local/limited in scope — not yet winner-take-most."
    else:
        v,r="NO","No evidence additional users increase value for existing users."
    results["Network Economies"]={"verdict":v,"reasoning":r}

    # 3. COUNTER-POSITIONING
    has_dis=any(x in desc for x in ["disrupt","transform","replace","legacy","traditional","obsolete"])
    if rg>0.25 and stage in ["growth","early_stage"] and gm>0.60 and has_dis:
        v,r="YES",f"Classic setup: {rg*100:.0f}% growth, {gm*100:.0f}% GM, disrupting legacy. Incumbents face cannibalization dilemma — copying destroys their existing business."
    elif rg>0.20 and stage=="growth" and is_soft and gm>0.50:
        v,r="YES",f"Cloud/SaaS displacing on-premise: {rg*100:.0f}% growth, {gm*100:.0f}% GM. Incumbents can't match economics without cannibalizing maintenance/license revenue."
    elif rg>0.12 and has_dis and gm>0.35:
        v,r="PARTIAL",f"Some counter-positioning signals ({rg*100:.0f}% growth, disruptive language). Cannibalization dilemma for incumbents not yet fully confirmed."
    elif stage in ["growth","early_stage"] and rg>0.08:
        v,r="PARTIAL",f"Growth-stage company ({rg*100:.0f}% revenue growth) — may be building counter-positioning but too early to confirm structural barrier."
    else:
        v,r="NO","No evidence of a model incumbents are structurally prevented from copying."
    results["Counter-Positioning"]={"verdict":v,"reasoning":r}

    # 4. SWITCHING COSTS
    nrr_proxy_high=is_soft and rg>0.12 and gm>0.65
    nrr_proxy_mid =is_soft and rg>0.06 and gm>0.55
    if is_soft and is_large and gm>0.65:
        v,r="YES",f"Enterprise software {gm*100:.0f}% GM growing {rg*100:.0f}%: deep workflow integration + data migration pain = NRR likely >110%. Customers expand spend rather than risk switching."
    elif any(x in desc for x in ["terminal","bloomberg","analytics","workflow"]) and is_large:
        v,r="YES","Financial data/analytics embedded into daily workflows — years of custom data, muscle memory, and messaging network create near-insurmountable switching costs."
    elif nrr_proxy_high:
        v,r="YES",f"High-margin software ({gm*100:.0f}% GM) growing {rg*100:.0f}%: NRR proxy strongly suggests >110%, meaning customers expand rather than leave."
    elif nrr_proxy_mid or (is_soft and gm>0.55):
        v,r="PARTIAL",f"Software {gm*100:.0f}% GM with {rg*100:.0f}% growth suggests moderate switching costs. NRR likely 100-110% — sticky but not fully locked in."
    elif any(x in desc for x in ["enterprise","erp","crm","mission-critical"]):
        v,r="PARTIAL","Enterprise/mission-critical software implies switching friction, but depth of lock-in unclear."
    else:
        v,r="NO","Consumer or commodity business — switching costs minimal."
    results["Switching Costs"]={"verdict":v,"reasoning":r}

    # 5. BRANDING
    low_ad=not np.isnan(sga_pct) and sga_pct<0.12 and gm>0.50
    if is_lux and gm>0.60:
        ad_note=f" Low ad spend ({sga_pct*100:.0f}% revenue) confirms brand sells itself — like Ferrari vs. Ford." if not np.isnan(sga_pct) else ""
        v,r="YES",f"Luxury brand {gm*100:.0f}% GM — pricing power from perception not cost.{ad_note}"
    elif is_cons and gm>0.45 and is_large and low_ad:
        v,r="YES",f"Consumer brand {gm*100:.0f}% GM + only {sga_pct*100:.0f}% SGA/revenue: low ad spend + premium margins = brand sells itself (established brand signal)."
    elif is_cons and gm>0.40 and is_large:
        v,r="YES",f"Strong consumer brand {gm*100:.0f}% GM at scale — customers pay premium for the brand specifically."
    elif is_cons and gm>0.30:
        v,r="PARTIAL",f"Some brand premium ({gm*100:.0f}% GM) but not yet clearly dominant over generic alternatives."
    elif low_ad and not is_soft:
        v,r="PARTIAL",f"Low SGA ({sga_pct*100:.0f}% revenue) with {gm*100:.0f}% GM — possible brand effect, but needs verification vs. peers."
    else:
        v,r="NO","B2B or commodity — purchasing driven by specs/price, not brand affinity."
    results["Branding"]={"verdict":v,"reasoning":r}

    # 6. CORNERED RESOURCE
    talent_signal=rev_per_emp>600000 and rd_pct>0.12
    if is_pharma:
        if rd_pct>0.20:
            v,r="YES",f"Pharma {rd_pct*100:.0f}% R&D — patent portfolio + pipeline = legally protected cornered resources."
        else:
            v,r="PARTIAL",f"Biotech/pharma assets likely include IP, but R&D intensity {rd_pct*100:.1f}% is modest — quality of pipeline matters most."
    elif is_semi and rd_pct>0.10:
        v,r="YES",f"Semiconductor IP + {rd_pct*100:.0f}% R&D: proprietary architectures take decades to replicate. Key engineers = cornered human capital."
    elif is_energy:
        v,r="YES" if gm>0.35 else "PARTIAL"
        r=f"Mineral rights, proved reserves, prime acreage — geologically unique assets. Competitors cannot build a better deposit regardless of capital. GM {gm*100:.0f}%."
    elif has_ai and rd_pct>0.10:
        v,r="YES",f"AI/ML research leadership + {rd_pct*100:.0f}% R&D: world-class AI researchers are scarce human capital. Proprietary training data compounds this."
    elif talent_signal:
        v,r="YES",f"${rev_per_emp/1000:.0f}K revenue/employee + {rd_pct*100:.0f}% R&D = concentrated high-value talent. Classic human capital cornered resource."
    elif rd_pct>0.10 and gm>0.55:
        v,r="YES",f"High R&D {rd_pct*100:.0f}% + {gm*100:.0f}% GM suggests proprietary tech/data not easily replicated."
    elif rd_pct>0.05 or any(x in desc for x in ["patent","proprietary","exclusive","license","spectrum","mineral"]):
        v,r="PARTIAL",f"Some proprietary assets (R&D {rd_pct*100:.1f}%), but exclusivity depth and durability unclear."
    else:
        v,r="NO","No clear exclusive access to scarce assets."
    results["Cornered Resource"]={"verdict":v,"reasoning":r}

    # 7. PROCESS POWER
    om_trend_list=q_det.get("om_trend",[]) if q_det else []
    sector_benchmarks={"tech":0.18,"semis":0.18,"financial":0.20,"consumer":0.12,
                       "industrial":0.12,"energy":0.10,"biotech":0.05,"other":0.14}
    benchmark=sector_benchmarks.get(stype,0.14)
    well_above=om>benchmark*1.6

    if om>0.32 and gm>0.50 and is_large and well_above:
        v,r="YES",f"Operating margin {om*100:.0f}% is {om/benchmark:.1f}x sector benchmark — sustained margin superiority vs. same-model peers is the definitive Process Power signal."
    elif any(x in desc for x in ["lean","kaizen","danaher","operational excellence","six sigma","manufacturing system"]):
        v,r="YES",f"Named operational excellence system in business description — embedded culture of continuous improvement like Toyota TPS or Danaher DBS is textbook Process Power."
    elif well_above and om>0.22:
        v,r="YES",f"Operating margin {om*100:.0f}% is ~{om/benchmark:.1f}x sector norm ({benchmark*100:.0f}%). Same business model, higher margins than peers = embedded process superiority."
    elif om>benchmark*1.2 and fcf_m>0.12:
        v,r="PARTIAL",f"Above-sector margins ({om*100:.0f}% vs {benchmark*100:.0f}% norm) + strong FCF conversion. Verify vs. direct competitors to confirm Process Power vs. mix/scale effects."
    elif om>benchmark:
        v,r="NO",f"Margin {om*100:.0f}% modestly above sector average ({benchmark*100:.0f}%) — not sufficient to conclude Process Power. Need consistent superiority vs. direct peers."
    else:
        v,r="NO",f"Operating margin {om*100:.0f}% at or below sector benchmark {benchmark*100:.0f}% — no evidence of embedded process superiority."
    results["Process Power"]={"verdict":v,"reasoning":r}

    # Score
    confirmed=[p for p,d in results.items() if d["verdict"]=="YES"]
    partial  =[p for p,d in results.items() if d["verdict"]=="PARTIAL"]
    raw=min(100,(len(confirmed)+(len(partial)*0.5))*(100/7))
    return round(raw,1), results


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SCORER
# ─────────────────────────────────────────────────────────────────────────────
def master_score(info, hist, fin, bal, cf, macro):
    stage,stype=classify(info,fin)
    weights=get_weights(stage,stype)
    W=sum(weights.values())  # should be 100

    q_raw,  q_det  = score_quality(info,fin,bal,cf,stage,stype)
    e_raw,  e_det  = score_expectations(info,fin,stage,stype)
    v_raw,  v_det  = score_valuation(info,hist,stage,stype)
    t_raw,  t_det  = score_technicals(hist,info,stage)
    p_raw,  p_det  = score_powers(info,fin,cf,"",stage,stype,q_det)

    # Weighted sum (each component is 0-100, weighted)
    base = (
        q_raw * weights["quality"]      / 100 +
        e_raw * weights["expectations"] / 100 +
        v_raw * weights["valuation"]    / 100 +
        t_raw * weights["technicals"]   / 100 +
        p_raw * weights["powers"]       / 100
    )
    base=round(min(100,base),1)

    # Macro overlay
    macro_delta, macro_factors = macro_overlay(macro,stage,stype,hist)

    total=round(min(100,max(0,base+macro_delta)),1)

    return {
        "total":total,"base":base,"macro_delta":macro_delta,
        "stage":stage,"stype":stype,"weights":weights,
        "q":round(q_raw,1),"e":round(e_raw,1),"v":round(v_raw,1),
        "t":round(t_raw,1),"p":round(p_raw,1),
        "q_det":q_det,"e_det":e_det,"v_det":v_det,
        "t_det":t_det,"p_det":p_det,
        "macro_factors":macro_factors,
    }

def get_signal(score,hist):
    s200_ok=rsi_ok=False
    try:
        if not hist.empty:
            last=hist.iloc[-1]; cl=float(last["Close"])
            s200=float(last.get("SMA200",np.nan)); rsi=float(last.get("RSI",np.nan))
            s200_ok=not np.isnan(s200) and cl>s200
            rsi_ok=not np.isnan(rsi) and 40<=rsi<=75
    except: pass
    if score>78 and s200_ok and rsi_ok: return "STRONG BUY","#10b981"
    if score>=65 and s200_ok:           return "BUY","#3b82f6"
    if score>=50:                        return "NEUTRAL","#f59e0b"
    return "AVOID","#ef4444"

def risk_label(t_det,stage):
    a=t_det.get("atr",np.nan) or 0.04; b=t_det.get("beta",np.nan) or 1.0
    if stage in ["early_stage","growth"]: return "HIGH" if a>0.08 or b>2.5 else "MEDIUM"
    return "LOW" if a<0.03 and b<1.0 else "HIGH" if a>0.05 or b>1.5 else "MEDIUM"

# ── CHARTS ────────────────────────────────────────────────────────────────────
def price_chart(hist):
    if hist.empty: return go.Figure()
    fig=make_subplots(rows=3,cols=1,shared_xaxes=True,row_heights=[0.60,0.20,0.20],vertical_spacing=0.015)
    fig.add_trace(go.Candlestick(x=hist.index,open=hist["Open"],high=hist["High"],low=hist["Low"],close=hist["Close"],
        increasing=dict(line=dict(color="#00d4aa",width=1),fillcolor="#00d4aa"),
        decreasing=dict(line=dict(color="#ff4757",width=1),fillcolor="#ff4757"),
        name="Price",showlegend=False),row=1,col=1)
    for col_n,color,nm in [("SMA50","#fbbf24","SMA50"),("SMA200","#a78bfa","SMA200")]:
        if col_n in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index,y=hist[col_n],name=nm,line=dict(color=color,width=1.8),opacity=0.9),row=1,col=1)
    up=hist["Close"]>=hist["Open"]
    fig.add_trace(go.Bar(x=hist.index[up],y=hist["Volume"][up],marker_color="rgba(0,212,170,0.35)",showlegend=False),row=2,col=1)
    fig.add_trace(go.Bar(x=hist.index[~up],y=hist["Volume"][~up],marker_color="rgba(255,71,87,0.35)",showlegend=False),row=2,col=1)
    if "Vol20" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["Vol20"],name="Vol MA",line=dict(color="#fbbf24",width=1.2,dash="dot"),opacity=0.7),row=2,col=1)
    if "RSI" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["RSI"],name="RSI",line=dict(color="#60a5fa",width=1.8)),row=3,col=1)
        fig.add_hrect(y0=70,y1=100,row=3,col=1,fillcolor="rgba(239,68,68,0.07)",line_width=0)
        fig.add_hrect(y0=0,y1=30,row=3,col=1,fillcolor="rgba(239,68,68,0.07)",line_width=0)
        fig.add_hrect(y0=45,y1=65,row=3,col=1,fillcolor="rgba(16,185,129,0.05)",line_width=0)
        for lvl,lc in [(70,"rgba(239,68,68,0.5)"),(30,"rgba(239,68,68,0.5)"),(50,"rgba(100,116,139,0.4)")]:
            fig.add_hline(y=lvl,row=3,col=1,line=dict(color=lc,width=0.8,dash="dot"))
    ax=dict(gridcolor="rgba(26,37,64,0.9)",linecolor="#1a2540",showgrid=True,zeroline=False,tickfont=dict(color="#64748b",size=10))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#070d1a",font=dict(color="#94a3b8",family="Inter",size=10),
        height=500,showlegend=True,barmode="overlay",
        legend=dict(orientation="h",y=1.02,x=0,font=dict(color="#94a3b8",size=10),bgcolor="rgba(7,13,26,0.8)",bordercolor="#1a2540",borderwidth=1),
        hovermode="x unified",xaxis_rangeslider_visible=False,margin=dict(l=55,r=20,t=10,b=20))
    for i in range(1,4):
        fig.update_xaxes(row=i,col=1,**ax); fig.update_yaxes(row=i,col=1,**ax)
    fig.update_yaxes(tickprefix="$",row=1,col=1); fig.update_yaxes(title_text="RSI",row=3,col=1,range=[0,100])
    return fig

def gauge(score):
    color="#10b981" if score>=75 else "#3b82f6" if score>=60 else "#f59e0b" if score>=48 else "#ef4444"
    fig=go.Figure(go.Indicator(mode="gauge+number",value=score,
        number={"font":{"color":color,"size":40,"family":"JetBrains Mono"}},
        gauge={"axis":{"range":[0,100],"tickcolor":"#334155","tickfont":{"color":"#334155","size":9}},
               "bar":{"color":color,"thickness":0.22},"bgcolor":"#070d1a","borderwidth":0,
               "steps":[{"range":[0,50],"color":"#120808"},{"range":[50,65],"color":"#0d1020"},{"range":[65,100],"color":"#081510"}],
               "threshold":{"line":{"color":color,"width":2},"thickness":0.75,"value":score}}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=20,r=20,t=10,b=10),height=175)
    return fig

def spider(p_det):
    confirmed=[p for p,d in p_det.items() if d["verdict"]=="YES"]
    partial  =[p for p,d in p_det.items() if d["verdict"]=="PARTIAL"]
    vals=[1.0 if p in confirmed else 0.5 if p in partial else 0.0 for p in ALL_POWERS]
    vals_c=vals+[vals[0]]; cats_c=ALL_POWERS+[ALL_POWERS[0]]
    fig=go.Figure(go.Scatterpolar(r=vals_c,theta=cats_c,fill="toself",fillcolor="rgba(59,130,246,0.12)",
        line=dict(color="#3b82f6",width=2),marker=dict(size=7,color=["#10b981" if v==1 else "#f59e0b" if v==0.5 else "#1a2540" for v in vals_c])))
    fig.update_layout(polar=dict(bgcolor="#070d1a",radialaxis=dict(visible=False,range=[0,1]),
        angularaxis=dict(tickfont=dict(color="#94a3b8",size=10),linecolor="#1a2540",gridcolor="#1a2540")),
        paper_bgcolor="rgba(0,0,0,0)",showlegend=False,margin=dict(l=30,r=30,t=20,b=20),height=250)
    return fig

def breakdown_chart(res):
    W=res["weights"]
    # Show actual points earned vs max available
    cats=["Quality","Expectations","Valuation","Technicals","7 Powers"]
    maxv=[W["quality"],W["expectations"],W["valuation"],W["technicals"],W["powers"]]
    # Convert 0-100 component scores to weighted points
    earned=[round(res["q"]*W["quality"]/100,1),round(res["e"]*W["expectations"]/100,1),
            round(res["v"]*W["valuation"]/100,1),round(res["t"]*W["technicals"]/100,1),
            round(res["p"]*W["powers"]/100,1)]
    colors=["#10b981" if e/mx>=0.75 else "#3b82f6" if e/mx>=0.55 else "#f59e0b" if e/mx>=0.35 else "#ef4444"
            for e,mx in zip(earned,maxv)]
    fig=go.Figure()
    fig.add_trace(go.Bar(x=cats,y=maxv,marker_color="rgba(26,37,64,0.6)",marker_line=dict(color="#1a2540",width=1),showlegend=False))
    fig.add_trace(go.Bar(x=cats,y=earned,marker_color=colors,
        text=[f"{e:.0f}" for e in earned],textposition="inside",textfont=dict(color="white",size=11,family="JetBrains Mono"),showlegend=False))
    fig.update_layout(barmode="overlay",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#070d1a",
        font=dict(color="#64748b",family="Inter",size=10),height=175,margin=dict(l=5,r=5,t=5,b=5),
        xaxis=dict(tickfont=dict(color="#94a3b8",size=10),gridcolor="rgba(26,37,64,0.5)",linecolor="#1a2540"),
        yaxis=dict(tickfont=dict(color="#64748b",size=9),gridcolor="rgba(26,37,64,0.5)",linecolor="#1a2540"))
    return fig

def mini_chart(prices,color="#3b82f6"):
    fig=go.Figure(go.Scatter(x=list(range(len(prices))),y=prices,mode="lines",
        line=dict(color=color,width=1.5),fill="tozeroy",fillcolor=f"rgba(59,130,246,0.06)"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=45,showlegend=False,
        margin=dict(l=0,r=0,t=0,b=0),xaxis=dict(visible=False),yaxis=dict(visible=False))
    return fig

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state.watchlist=["AAPL","MSFT","NVDA","GOOGL","V"]

# ── HEADER ────────────────────────────────────────────────────────────────────
h1,h2=st.columns([3,1])
with h1:
    st.markdown('<div style="padding:8px 0 18px;"><div style="font-size:1.75rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.5px;">⚔️ War Room</div><div style="font-size:0.8rem;color:#475569;margin-top:2px;">Dynamic Scoring · Macro Overlay · Sector-Aware Weights · 7 Powers</div></div>',unsafe_allow_html=True)
with h2:
    ticker_input=st.text_input("",placeholder="Ticker (e.g. NVDA)",label_visibility="collapsed")

tab_r,tab_w,tab_c=st.tabs(["🔍 Research","📋 Watchlist","⚖️ Compare"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ═══════════════════════════════════════════════════════════════════════════
with tab_r:
    ticker=(ticker_input or "AAPL").strip().upper()

    with st.spinner(f"Loading {ticker}..."):
        info,hist_raw,fin,bal,cf=load(ticker)
        hist=add_ta(hist_raw)
        macro=load_macro()

    if not info and hist.empty:
        st.error(f"No data for **{ticker}**"); st.stop()

    # ETF check
    qt=(sg(info,"quoteType","") or "").upper()
    if qt in ["ETF","MUTUALFUND"]:
        name=sg(info,"longName",ticker); cat=sg(info,"category","—"); ff=sg(info,"fundFamily","—")
        price=get_price(info,hist); prev=sf(sg(info,"previousClose",np.nan))
        chg=(price-prev)/prev if not np.isnan(price) and not np.isnan(prev) and prev>0 else np.nan
        chg_c="#10b981" if not np.isnan(chg) and chg>=0 else "#ef4444"
        st.markdown(f'<div style="background:#0d1525;border:1px solid #1a2540;border-radius:12px;padding:20px 26px;margin-bottom:18px;"><div style="font-size:1.6rem;font-weight:700;color:#f1f5f9;">{name}</div><div style="font-size:0.8rem;color:#64748b;margin-top:4px;">📊 ETF · {cat} · {ff}</div></div>',unsafe_allow_html=True)
        c1,c2,c3,c4,c5,c6=st.columns(6)
        for col,(lbl,val) in zip([c1,c2,c3,c4,c5,c6],[
            ("Price",f"${price:.2f}" if not np.isnan(price) else "N/A"),
            ("Day Chg",f'<span style="color:{chg_c}">{pct(chg)}</span>'),
            ("52W High",f"${sf(sg(info,'fiftyTwoWeekHigh',np.nan)):.2f}" if not np.isnan(sf(sg(info,'fiftyTwoWeekHigh',np.nan))) else "N/A"),
            ("52W Low",f"${sf(sg(info,'fiftyTwoWeekLow',np.nan)):.2f}" if not np.isnan(sf(sg(info,'fiftyTwoWeekLow',np.nan))) else "N/A"),
            ("Expense Ratio",pct(sf(sg(info,"annualReportExpenseRatio",np.nan)))),
            ("AUM",fmtn(sf(sg(info,"totalAssets",np.nan)),pre="$")),
        ]):
            with col: st.markdown(m(lbl,val),unsafe_allow_html=True)
        if not hist.empty: st.plotly_chart(price_chart(hist),use_container_width=True,config={"displayModeBar":False})
        st.info("ETF — scoring model applies to individual stocks only.")
    else:
        # STOCK
        with st.spinner("Analyzing..."):
            res=master_score(info,hist,fin,bal,cf,macro)

        stage=res["stage"]; stype=res["stype"]
        signal,sig_color=get_signal(res["total"],hist)
        rl=risk_label(res["t_det"],stage)
        price=get_price(info,hist)
        prev=sf(sg(info,"previousClose",np.nan))
        if np.isnan(prev) and not hist.empty and len(hist)>=2: prev=float(hist["Close"].iloc[-2])
        day_chg=(price-prev)/prev if not np.isnan(price) and not np.isnan(prev) and prev>0 else np.nan
        name=sg(info,"longName",ticker); sector=sg(info,"sector","—"); industry=sg(info,"industry","—")

        # ── ROW 1: Header ────────────────────────────────────────────────────
        c_name,c_score,c_gauge=st.columns([2.5,1,1.2])

        with c_name:
            chg_c="#10b981" if not np.isnan(day_chg) and day_chg>=0 else "#ef4444"
            mktcap=sf(sg(info,"marketCap",np.nan))
            w52h=sf(sg(info,"fiftyTwoWeekHigh",np.nan)); w52l=sf(sg(info,"fiftyTwoWeekLow",np.nan))
            rl_c={"LOW":"#10b981","MEDIUM":"#f59e0b","HIGH":"#ef4444"}.get(rl,"#f59e0b")
            stage_c={"growth":"#f59e0b","cyclical":"#60a5fa","early_stage":"#a78bfa","mature":"#64748b"}.get(stage,"#64748b")
            macro_c="#10b981" if res["macro_delta"]>0 else "#ef4444" if res["macro_delta"]<0 else "#64748b"

            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <div style="font-size:1.6rem;font-weight:700;color:#f1f5f9;line-height:1.2;">{name}</div>
                <div style="font-size:0.78rem;color:#475569;margin-top:3px;">{ticker} · {sector} · {industry}</div>
                <div style="margin-top:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:1.9rem;font-weight:700;color:#f1f5f9;">${price:.2f}</span>
                    <span style="font-size:0.95rem;color:{chg_c};font-weight:600;">{pct(day_chg)} today</span>
                    {sig_badge(signal)}
                </div>
            </div>
            """,unsafe_allow_html=True)

            c1,c2,c3,c4,c5=st.columns(5)
            for col,(lbl,val,vc) in zip([c1,c2,c3,c4,c5],[
                ("Mkt Cap",    fmtn(mktcap,pre="$"),   "#f1f5f9"),
                ("Stage",      stage.replace("_"," ").upper(), stage_c),
                ("Sector Type",stype.upper(),          "#94a3b8"),
                ("Risk",       rl,                     rl_c),
                ("Macro",      f"{res['macro_delta']:+.0f} pts",macro_c),
            ]):
                with col: st.markdown(m(lbl,val,color=vc),unsafe_allow_html=True)

        with c_score:
            W=res["weights"]
            st.markdown(f"""
            <div style="background:#0d1525;border:1px solid #1a2540;border-radius:14px;padding:16px;text-align:center;">
                <div style="font-size:0.67rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">Total Score</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:3.2rem;font-weight:700;color:{sig_color};line-height:1;">{res["total"]}</div>
                <div style="font-size:0.67rem;color:#334155;margin-top:2px;">base {res["base"]} + macro {res["macro_delta"]:+.0f}</div>
                <div style="margin-top:10px;font-size:0.68rem;color:#475569;line-height:1.8;">
                    Q:{res["q"]:.0f} ({W["quality"]}wt) · E:{res["e"]:.0f} ({W["expectations"]}wt)<br>
                    V:{res["v"]:.0f} ({W["valuation"]}wt) · T:{res["t"]:.0f} ({W["technicals"]}wt)<br>
                    7P:{res["p"]:.0f} ({W["powers"]}wt)
                </div>
            </div>
            """,unsafe_allow_html=True)

        with c_gauge:
            st.plotly_chart(gauge(res["total"]),use_container_width=True,config={"displayModeBar":False})

        st.markdown("---")

        # ── ROW 2: Chart + Financials ────────────────────────────────────────
        c_ch,c_fi=st.columns([2.2,1])
        with c_ch:
            st.plotly_chart(price_chart(hist),use_container_width=True,config={"displayModeBar":False})
        with c_fi:
            st.markdown('<div class="slabel">Financials · Yahoo Finance</div>',unsafe_allow_html=True)
            gm_=sf(sg(info,"grossMargins",np.nan)); om_=sf(sg(info,"operatingMargins",np.nan))
            nm_=sf(sg(info,"profitMargins",np.nan)); roe_=sf(sg(info,"returnOnEquity",np.nan))
            roa_=sf(sg(info,"returnOnAssets",np.nan)); rev_=sf(sg(info,"totalRevenue",np.nan))
            ni_=sf(sg(info,"netIncomeToCommon",np.nan)); fcf_=sf(sg(info,"freeCashflow",np.nan))
            ebitda_=sf(sg(info,"ebitda",np.nan)); pe_t=res["v_det"].get("pe_t",np.nan)
            pe_f=res["v_det"].get("pe_f",np.nan); ps_=sf(sg(info,"priceToSalesTrailingTwelveMonths",np.nan))
            pb_=sf(sg(info,"priceToBook",np.nan)); ev_eb_=sf(sg(info,"enterpriseToEbitda",np.nan))
            de_=sf(sg(info,"debtToEquity",np.nan)); cr_=sf(sg(info,"currentRatio",np.nan))
            dy_=sf(sg(info,"dividendYield",np.nan)); cash_=sf(sg(info,"totalCash",np.nan))
            debt_=sf(sg(info,"totalDebt",np.nan))

            e_det=res["e_det"]
            for grp,items in [
                ("MARGINS",[("Gross Margin",pct(gm_)),("Operating Margin",pct(om_)),("Net Margin",pct(nm_))]),
                ("RETURNS",[("ROE",pct(roe_)),("ROA",pct(roa_))]),
                ("INCOME TTM",[("Revenue",fmtn(rev_,pre="$")),("Net Income",fmtn(ni_,pre="$")),("FCF",fmtn(fcf_,pre="$")),("EBITDA",fmtn(ebitda_,pre="$"))]),
                (f"EXPECTATIONS ({e_det.get('source','').upper()})",[
                    ("Revenue Growth",pct(e_det.get("rg",np.nan))),
                    ("Earnings Growth",pct(e_det.get("eg",np.nan))),
                    ("Forward EPS",f"${e_det.get('fwd_eps',np.nan):.2f}" if not np.isnan(e_det.get("fwd_eps",np.nan)) else "N/A"),
                    ("Trailing EPS",f"${e_det.get('trailing_eps',np.nan):.2f}" if not np.isnan(e_det.get("trailing_eps",np.nan)) else "N/A"),
                    ("Analyst Target Upside",pct(e_det.get("upside",np.nan))),
                ]),
                ("VALUATION",[("Trailing P/E",f"{pe_t:.1f}x" if not np.isnan(pe_t) else "N/A"),
                    ("Forward P/E",f"{pe_f:.1f}x" if not np.isnan(pe_f) else "N/A"),
                    ("P/S",f"{ps_:.2f}x" if not np.isnan(ps_) else "N/A"),
                    ("P/B",f"{pb_:.2f}x" if not np.isnan(pb_) else "N/A"),
                    ("EV/EBITDA",f"{ev_eb_:.1f}x" if not np.isnan(ev_eb_) else "N/A"),
                    ("FCF Yield",pct(res["v_det"].get("fcf_yield",np.nan)))]),
                ("BALANCE SHEET",[("Cash",fmtn(cash_,pre="$")),("Total Debt",fmtn(debt_,pre="$")),
                    ("D/E",f"{de_/100:.2f}" if not np.isnan(de_) else "N/A"),
                    ("Current Ratio",f"{cr_:.2f}" if not np.isnan(cr_) else "N/A"),
                    ("Dividend Yield",pct(dy_) if not np.isnan(dy_) else "None")]),
                ("TECHNICALS",[("RSI (14D)",f"{res['t_det'].get('rsi',np.nan):.1f}" if not np.isnan(res['t_det'].get('rsi',np.nan)) else "N/A"),
                    ("ATR %",pct(res["t_det"].get("atr",np.nan))),
                    ("Beta",f"{res['t_det'].get('beta',np.nan):.2f}" if not np.isnan(res['t_det'].get('beta',np.nan)) else "N/A"),
                    ("RS vs S&P500",pct(res["t_det"].get("rs_spy",np.nan)))]),
            ]:
                st.markdown(f'<div class="slabel">{grp}</div>',unsafe_allow_html=True)
                for lbl,val in items: st.markdown(m(lbl,val),unsafe_allow_html=True)

        st.markdown("---")

        # ── ROW 3: Score Breakdown + 7 Powers ───────────────────────────────
        c_bd,c_7p=st.columns([1,1.6])
        with c_bd:
            st.markdown('<div class="slabel">Score Breakdown (weighted pts)</div>',unsafe_allow_html=True)
            st.plotly_chart(breakdown_chart(res),use_container_width=True,config={"displayModeBar":False})

            W=res["weights"]
            st.markdown(f"""
            <div style="background:#0d1525;border:1px solid #1a2540;border-radius:8px;padding:10px 14px;font-size:0.75rem;color:#64748b;line-height:1.9;">
                <div style="color:#94a3b8;font-weight:600;margin-bottom:4px;">Weight Distribution — {stage.upper()} / {stype.upper()}</div>
                Quality <b style="color:#f1f5f9">{W["quality"]}pts</b> &nbsp;·&nbsp;
                Expectations <b style="color:#f1f5f9">{W["expectations"]}pts</b> &nbsp;·&nbsp;
                Valuation <b style="color:#f1f5f9">{W["valuation"]}pts</b><br>
                Technicals <b style="color:#f1f5f9">{W["technicals"]}pts</b> &nbsp;·&nbsp;
                7 Powers <b style="color:#f1f5f9">{W["powers"]}pts</b>
            </div>
            """,unsafe_allow_html=True)

            # Stage explanation
            stage_explain={
                "mature":"Balanced framework. Quality and valuation carry equal weight.",
                "growth":"Expectations & 7 Powers dominate (55pts). Quality de-emphasized — unprofitability is normal.",
                "cyclical":"Technicals & momentum highest (25-30pts). Valuation on normalized earnings, not peak/trough.",
                "early_stage":"7 Powers dominate (35pts). Survival & pipeline matter. Financial metrics largely irrelevant.",
            }
            st.markdown(f'<div style="font-size:0.75rem;color:#475569;margin-top:8px;padding:8px 12px;background:#070d1a;border-radius:6px;border:1px solid #1a2540;">📌 {stage_explain.get(stage,"")}</div>',unsafe_allow_html=True)

        with c_7p:
            st.markdown('<div class="slabel">7 Powers — Helmer Framework</div>',unsafe_allow_html=True)
            p_det=res["p_det"]
            confirmed=[p for p,d in p_det.items() if d["verdict"]=="YES"]
            partial  =[p for p,d in p_det.items() if d["verdict"]=="PARTIAL"]
            pw_c="#10b981" if len(confirmed)>=3 else "#f59e0b" if len(confirmed)>=1 else "#ef4444"

            cp,cp2=st.columns([1,1.5])
            with cp:
                st.plotly_chart(spider(p_det),use_container_width=True,config={"displayModeBar":False})
                st.markdown(f"""
                <div style="text-align:center;background:#0d1525;border:1px solid #1a2540;border-radius:10px;padding:10px;">
                    <div style="font-size:0.67rem;color:#475569;text-transform:uppercase;">Powers (wt: {W["powers"]}pts)</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:700;color:{pw_c};">{res["p"]:.0f}/100</div>
                    <div style="font-size:0.7rem;color:#64748b;">✅ {len(confirmed)} confirmed · ⚡ {len(partial)} partial</div>
                </div>
                """,unsafe_allow_html=True)
            with cp2:
                for p in ALL_POWERS:
                    pd_=p_det.get(p,{}); v=pd_.get("verdict","NO"); r=pd_.get("reasoning","")
                    cls="pcard-yes" if v=="YES" else "pcard-part" if v=="PARTIAL" else "pcard-no"
                    icon="✅" if v=="YES" else "⚡" if v=="PARTIAL" else "❌"
                    st.markdown(f'<div class="pcard {cls}"><div style="font-size:0.78rem;font-weight:600;color:#e2e8f0;">{icon} {p}</div><div style="font-size:0.72rem;color:#64748b;margin-top:2px;line-height:1.4;">{r}</div></div>',unsafe_allow_html=True)

        st.markdown("---")

        # ── ROW 4: Macro Overlay ─────────────────────────────────────────────
        st.markdown('<div class="slabel">🌍 Macro Overlay & Sector Context</div>',unsafe_allow_html=True)

        if res["macro_factors"]:
            macro_cols=st.columns(min(3,len(res["macro_factors"])))
            for i,(title,body) in enumerate(res["macro_factors"]):
                col=macro_cols[i%len(macro_cols)]
                cls="macro-good" if "🟢" in title else "macro-bad" if "🔴" in title else "macro-warn"
                with col:
                    st.markdown(f'<div class="{cls}"><div style="font-size:0.78rem;font-weight:600;color:#e2e8f0;">{title}</div><div style="font-size:0.72rem;color:#94a3b8;margin-top:3px;line-height:1.5;">{body}</div></div>',unsafe_allow_html=True)

            macro_sum=res["macro_delta"]
            mc="#10b981" if macro_sum>0 else "#ef4444" if macro_sum<0 else "#64748b"
            st.markdown(f'<div style="margin-top:10px;font-size:0.8rem;color:{mc};font-weight:600;">Macro adjustment: {macro_sum:+.0f} pts → base {res["base"]:.0f} → final {res["total"]:.0f}</div>',unsafe_allow_html=True)
        else:
            st.info("Macro data loading...")

        # Sector ETF context
        smap={"tech":"tech","semis":"semis","biotech":"biotech","energy":"energy","financial":"financials","consumer":"consumer","industrial":"industrials"}
        sk=smap.get(stype)
        if sk and sk in macro.get("sectors",{}):
            sd=macro["sectors"][sk]
            s1m=sd.get("1m",np.nan); s3m=sd.get("3m",np.nan); etf=sd.get("etf","")
            c1,c2,c3=st.columns(3)
            with c1: st.markdown(m(f"{etf} 1M Return",f'<span style="color:{"#10b981" if not np.isnan(s1m) and s1m>=0 else "#ef4444"}">{pct(s1m)}</span>'),unsafe_allow_html=True)
            with c2: st.markdown(m(f"{etf} 3M Return",f'<span style="color:{"#10b981" if not np.isnan(s3m) and s3m>=0 else "#ef4444"}">{pct(s3m)}</span>'),unsafe_allow_html=True)
            with c3: st.markdown(m("Market (SPY) 3M",f'<span style="color:{"#10b981" if not np.isnan(macro.get("spy_3m",np.nan)) and macro.get("spy_3m",0)>=0 else "#ef4444"}">{pct(macro.get("spy_3m",np.nan))}</span>'),unsafe_allow_html=True)

        st.markdown("---")

        # ── ROW 5: Bull/Bear + Analyst ───────────────────────────────────────
        c_bull,c_bear,c_an=st.columns([1,1,0.8])

        with c_bull:
            st.markdown('<div class="slabel">🟢 Bull Case</div>',unsafe_allow_html=True)
            bulls=[]
            if res["q"]>70: bulls.append(f"Strong quality score: {res['q']:.0f}/100 on quality")
            if not np.isnan(res["e_det"].get("eg",np.nan)) and res["e_det"]["eg"]>0.15: bulls.append(f"Earnings growth: {pct(res['e_det']['eg'])} ({res['e_det'].get('source','')})")
            if not np.isnan(res["e_det"].get("upside",np.nan)) and res["e_det"]["upside"]>0.15: bulls.append(f"Analyst target {pct(res['e_det']['upside'])} upside")
            if res["t_det"].get("above_200"): bulls.append("Price above 200D SMA — trend intact")
            if res["p"]>60: bulls.append(f"{len(confirmed)} Helmer power(s): {', '.join(confirmed[:2])}{'…' if len(confirmed)>2 else ''}")
            for t,_ in res["macro_factors"]:
                if "🟢" in t: bulls.append(t.replace("🟢 ",""))
            fcf_=sf(sg(info,"freeCashflow",np.nan))
            if not np.isnan(fcf_) and fcf_>0: bulls.append(f"Positive FCF: {fmtn(fcf_,pre='$')}")
            if not bulls: bulls.append("No strong bull signals at current levels.")
            for b in bulls: st.markdown(f'<div style="background:#051a0e;border-left:3px solid #10b981;border-radius:0 6px 6px 0;padding:7px 11px;margin:4px 0;font-size:0.8rem;color:#cbd5e1;">✅ {b}</div>',unsafe_allow_html=True)

        with c_bear:
            st.markdown('<div class="slabel">🔴 Bear Case</div>',unsafe_allow_html=True)
            bears=[]
            if not res["t_det"].get("above_200",True): bears.append("Price below 200D SMA — trend broken")
            rsi_v=res["t_det"].get("rsi",np.nan)
            if not np.isnan(rsi_v):
                if rsi_v>78: bears.append(f"RSI {rsi_v:.0f} overbought")
                if rsi_v<25: bears.append(f"RSI {rsi_v:.0f} deeply oversold")
            for t,_ in res["macro_factors"]:
                if "🔴" in t: bears.append(t.replace("🔴 ",""))
            beta_v=res["t_det"].get("beta",np.nan)
            if not np.isnan(beta_v) and beta_v>2: bears.append(f"High beta {beta_v:.1f} — amplified drawdowns")
            if res["total"]<50: bears.append(f"Score {res['total']}/100 below AVOID threshold")
            if not confirmed and p_det: bears.append("No Helmer powers confirmed — moat unproven")
            if res["v"]<35: bears.append(f"Weak valuation score {res['v']:.0f}/100")
            if not bears: bears.append("No major red flags.")
            for b in bears: st.markdown(f'<div style="background:#1a0808;border-left:3px solid #ef4444;border-radius:0 6px 6px 0;padding:7px 11px;margin:4px 0;font-size:0.8rem;color:#cbd5e1;">⚠️ {b}</div>',unsafe_allow_html=True)

        with c_an:
            st.markdown('<div class="slabel">Analyst Consensus</div>',unsafe_allow_html=True)
            rec=sg(info,"recommendationKey",""); target=sf(sg(info,"targetMeanPrice",np.nan))
            n_an=sf(sg(info,"numberOfAnalystOpinions",np.nan))
            rc_c={"buy":"#10b981","strongbuy":"#10b981","hold":"#f59e0b","sell":"#ef4444","underperform":"#ef4444"}.get((rec or "").lower().replace(" ",""),"#94a3b8")
            for lbl,val,vc in [("Recommendation",rec.upper() if rec else "N/A",rc_c),
                ("Price Target",f"${target:.2f}" if not np.isnan(target) else "N/A","#f1f5f9"),
                ("# Analysts",str(int(n_an)) if not np.isnan(n_an) else "N/A","#f1f5f9"),
                ("Upside to Target",pct(res["e_det"].get("upside",np.nan)),"#10b981" if not np.isnan(res["e_det"].get("upside",np.nan)) and res["e_det"]["upside"]>0 else "#ef4444")]:
                st.markdown(m(lbl,val,color=vc),unsafe_allow_html=True)

            st.markdown('<div class="slabel">Signal</div>',unsafe_allow_html=True)
            logic={"STRONG BUY":"Score>78 + Above 200D SMA + RSI 40-75 + Positive momentum.","BUY":"Score≥65 + Price above 200D SMA.","NEUTRAL":"Score 50-65. Monitor.","AVOID":"Score<50."}
            st.markdown(f'<div style="background:#0d1525;border:1px solid {sig_color};border-radius:10px;padding:12px;"><div style="font-size:1rem;font-weight:700;color:{sig_color};margin-bottom:5px;">{signal}</div><div style="font-size:0.75rem;color:#64748b;">{logic.get(signal,"")}</div></div>',unsafe_allow_html=True)

        # Company description
        desc_=sg(info,"longBusinessSummary","")
        if desc_:
            st.markdown("---")
            st.markdown(f'<div class="slabel">About</div>',unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.8rem;color:#94a3b8;line-height:1.7;background:#0d1525;border:1px solid #1a2540;border-radius:10px;padding:14px;">{desc_[:600]}{"..." if len(desc_)>600 else ""}</div>',unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;color:#1e2a45;font-size:0.67rem;margin-top:20px;padding-top:8px;border-top:1px solid #0f1525;">War Room · Educational purposes only · Not financial advice</div>',unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — WATCHLIST
# ═══════════════════════════════════════════════════════════════════════════
with tab_w:
    st.markdown('<div class="slabel">Your Watchlist</div>',unsafe_allow_html=True)
    ca,cb=st.columns([3,1])
    with ca: new_t=st.text_input("",placeholder="Add ticker",key="wl_add",label_visibility="collapsed")
    with cb:
        if st.button("＋ Add"):
            t=new_t.strip().upper()
            if t and t not in st.session_state.watchlist:
                st.session_state.watchlist.append(t); st.rerun()
    if not st.session_state.watchlist:
        st.info("Watchlist empty. Add a ticker above.")
    else:
        with st.spinner("Loading..."):
            wl=[{"ticker":t,**quick_quote(t)} for t in st.session_state.watchlist]
        cols=st.columns([1.2,2,1.2,1.2,1.2,1.2,1.2,0.8])
        for col,hdr in zip(cols,["Ticker","Name","Price","Change","Mkt Cap","P/E","52W Range",""]):
            with col: st.markdown(f'<div style="font-size:0.67rem;color:#334155;text-transform:uppercase;letter-spacing:0.8px;padding:4px 0;">{hdr}</div>',unsafe_allow_html=True)
        for row in wl:
            chg_c="#10b981" if not np.isnan(row["chg"]) and row["chg"]>=0 else "#ef4444"
            lo,hi,pr=row["lo52"],row["hi52"],row["price"]
            if not any(np.isnan(x) for x in [lo,hi,pr]) and hi>lo:
                pct_r=(pr-lo)/(hi-lo)*100
                rbar=f'<div style="font-size:0.67rem;color:#475569;">${lo:.0f}</div><div style="background:#1a2540;border-radius:3px;height:4px;margin:3px 0;"><div style="background:#3b82f6;width:{pct_r:.0f}%;height:4px;border-radius:3px;"></div></div><div style="font-size:0.67rem;color:#475569;">${hi:.0f}</div>'
            else: rbar='<div style="color:#334155;">—</div>'
            rcols=st.columns([1.2,2,1.2,1.2,1.2,1.2,1.2,0.8])
            with rcols[0]: st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.92rem;font-weight:700;color:#93c5fd;padding:10px 0;">{row["ticker"]}</div>',unsafe_allow_html=True)
            with rcols[1]: st.markdown(f'<div style="font-size:0.8rem;color:#94a3b8;padding:10px 0;white-space:nowrap;overflow:hidden;">{row["name"][:22]}</div>',unsafe_allow_html=True)
            with rcols[2]: st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.9rem;color:#f1f5f9;padding:10px 0;">${row["price"]:.2f}" if not np.isnan(row["price"]) else "N/A"</div>',unsafe_allow_html=True)
            with rcols[3]: st.markdown(f'<div style="font-size:0.88rem;color:{chg_c};font-weight:600;padding:10px 0;">{row["chg"]*100:+.2f}%" if not np.isnan(row["chg"]) else "—"</div>',unsafe_allow_html=True)
            with rcols[4]: st.markdown(f'<div style="font-size:0.8rem;color:#94a3b8;padding:10px 0;">{fmtn(row["mktcap"],pre="$")}</div>',unsafe_allow_html=True)
            with rcols[5]: st.markdown(f'<div style="font-size:0.8rem;color:#94a3b8;padding:10px 0;">{f"{row["pe"]:.1f}x" if not np.isnan(row["pe"]) else "—"}</div>',unsafe_allow_html=True)
            with rcols[6]: st.markdown(rbar,unsafe_allow_html=True)
            with rcols[7]:
                if st.button("✕",key=f"rm_{row['ticker']}"):
                    st.session_state.watchlist.remove(row["ticker"]); st.rerun()
        if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPARE
# ═══════════════════════════════════════════════════════════════════════════
with tab_c:
    st.markdown('<div class="slabel">Compare up to 4 stocks</div>',unsafe_allow_html=True)
    ci=st.columns(4)
    defaults=["AAPL","MSFT","NVDA","GOOGL"]
    ctickers=[col.text_input(f"Stock {i+1}",value=defaults[i],key=f"cmp_{i}").strip().upper() for i,col in enumerate(ci)]
    ctickers=[t for t in ctickers if t]
    if st.button("⚡ Compare"):
        macro_=load_macro()
        with st.spinner("Analyzing..."):
            cres=[]
            for t in ctickers:
                try:
                    inf,his,fn,bl,cashflow=load(t)
                    his=add_ta(his); r=master_score(inf,his,fn,bl,cashflow,macro_)
                    pr=get_price(inf,his); pv=sf(sg(inf,"previousClose",np.nan))
                    chg=(pr-pv)/pv if not np.isnan(pr) and not np.isnan(pv) and pv>0 else np.nan
                    sig,sc=get_signal(r["total"],his)
                    cres.append({"Ticker":t,"Name":sg(inf,"shortName",t),"Score":r["total"],
                        "Signal":sig,"Stage":r["stage"].upper(),"Weights":f'Q{r["weights"]["quality"]}/E{r["weights"]["expectations"]}/V{r["weights"]["valuation"]}/T{r["weights"]["technicals"]}/7P{r["weights"]["powers"]}',
                        "Quality":f'{r["q"]:.0f}','Expectations':f'{r["e"]:.0f}','Valuation':f'{r["v"]:.0f}',
                        "Technicals":f'{r["t"]:.0f}','7 Powers':f'{r["p"]:.0f}',"Macro":f'{r["macro_delta"]:+.0f}',
                        "GM":pct(sf(sg(inf,"grossMargins",np.nan))),"FCF":fmtn(sf(sg(inf,"freeCashflow",np.nan)),pre="$"),
                        "Fwd P/E":f'{r["v_det"].get("pe_f",np.nan):.1f}x' if not np.isnan(r["v_det"].get("pe_f",np.nan)) else "N/A",
                        "Price":f"${pr:.2f}" if not np.isnan(pr) else "N/A",
                        "Chg":f"{chg*100:+.1f}%" if not np.isnan(chg) else "—",
                        "_hist":his,"_r":r})
                except: pass
        if cres:
            fig=go.Figure()
            for cr,color in zip(cres,["#3b82f6","#10b981","#f59e0b","#a78bfa"]):
                fig.add_trace(go.Bar(name=cr["Ticker"],x=["Quality","Expectations","Valuation","Technicals","7 Powers"],
                    y=[float(cr["Quality"]),float(cr["Expectations"]),float(cr["Valuation"]),float(cr["Technicals"]),float(cr["7 Powers"])],
                    marker_color=color,opacity=0.85))
            fig.update_layout(barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#070d1a",
                font=dict(color="#94a3b8",family="Inter",size=11),height=260,margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(font=dict(color="#94a3b8"),bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#1a2540",tickfont=dict(color="#94a3b8")),
                yaxis=dict(gridcolor="#1a2540",tickfont=dict(color="#64748b")))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            disp=["Ticker","Name","Score","Signal","Stage","Weights","Quality","Expectations","Valuation","Technicals","7 Powers","Macro","GM","FCF","Fwd P/E","Price","Chg"]
            df=pd.DataFrame([{k:r[k] for k in disp} for r in cres])
            st.dataframe(df,hide_index=True,use_container_width=True,
                column_config={"Score":st.column_config.ProgressColumn("Score",max_value=100,format="%f")})
            mcols=st.columns(len(cres))
            for col,cr,color in zip(mcols,cres,["#3b82f6","#10b981","#f59e0b","#a78bfa"]):
                with col:
                    if not cr["_hist"].empty:
                        st.markdown(f'<div style="font-size:0.8rem;font-weight:600;color:#94a3b8;text-align:center;margin-bottom:3px;">{cr["Ticker"]} ({cr["Signal"]})</div>',unsafe_allow_html=True)
                        prices=cr["_hist"]["Close"].tolist()
                        st.plotly_chart(mini_chart(prices,color),use_container_width=True,config={"displayModeBar":False})
                        chg_t=(prices[-1]-prices[0])/prices[0]*100 if len(prices)>1 else 0
                        cc="#10b981" if chg_t>=0 else "#ef4444"
                        st.markdown(f'<div style="text-align:center;font-size:0.78rem;color:{cc};font-weight:600;">{chg_t:+.1f}% 2Y</div>',unsafe_allow_html=True)
