"""
engine.py — Core calculations for Macro-Driven Value Optimizer v2
Supports: CAPM/WACC, DCF, multi-strategy portfolio optimization, Monte Carlo sim
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════
# DEFAULT STOCK UNIVERSE
# ═══════════════════════════════════════════════════════════
DEFAULT_STOCKS = {
    "AAPL": {"name":"Apple Inc.","sector":"Technology","fcf":110543,"beta":1.24,
             "debt_ratio":0.36,"cost_of_debt":0.034,"tax_rate":0.21,"base_growth":0.065,
             "terminal_growth":0.025,"shares":15408,"net_debt":49000,"market_price":198.50},
    "MSFT": {"name":"Microsoft Corp.","sector":"Technology","fcf":74071,"beta":1.05,
             "debt_ratio":0.22,"cost_of_debt":0.031,"tax_rate":0.21,"base_growth":0.11,
             "terminal_growth":0.025,"shares":7432,"net_debt":-30000,"market_price":430.20},
    "GOOGL": {"name":"Alphabet Inc.","sector":"Technology","fcf":69495,"beta":1.08,
              "debt_ratio":0.04,"cost_of_debt":0.025,"tax_rate":0.21,"base_growth":0.09,
              "terminal_growth":0.025,"shares":12220,"net_debt":-95000,"market_price":177.80},
    "AMZN": {"name":"Amazon.com","sector":"Consumer Discretionary","fcf":38514,"beta":1.28,
             "debt_ratio":0.28,"cost_of_debt":0.038,"tax_rate":0.21,"base_growth":0.13,
             "terminal_growth":0.025,"shares":10520,"net_debt":18000,"market_price":189.70},
    "PG": {"name":"Procter & Gamble","sector":"Consumer Staples","fcf":14988,"beta":0.52,
            "debt_ratio":0.34,"cost_of_debt":0.032,"tax_rate":0.21,"base_growth":0.035,
            "terminal_growth":0.025,"shares":2358,"net_debt":24000,"market_price":168.40},
    "KO": {"name":"Coca-Cola Co.","sector":"Consumer Staples","fcf":9774,"beta":0.62,
            "debt_ratio":0.45,"cost_of_debt":0.035,"tax_rate":0.21,"base_growth":0.03,
            "terminal_growth":0.025,"shares":4320,"net_debt":28000,"market_price":63.10},
    "XOM": {"name":"Exxon Mobil","sector":"Energy","fcf":33436,"beta":0.87,
            "debt_ratio":0.18,"cost_of_debt":0.040,"tax_rate":0.21,"base_growth":0.015,
            "terminal_growth":0.020,"shares":4188,"net_debt":12000,"market_price":108.30},
    "CVX": {"name":"Chevron Corp.","sector":"Energy","fcf":19760,"beta":0.98,
            "debt_ratio":0.14,"cost_of_debt":0.038,"tax_rate":0.21,"base_growth":0.02,
            "terminal_growth":0.020,"shares":1842,"net_debt":8500,"market_price":152.60},
    "JNJ": {"name":"Johnson & Johnson","sector":"Healthcare","fcf":17944,"beta":0.68,
            "debt_ratio":0.30,"cost_of_debt":0.030,"tax_rate":0.21,"base_growth":0.04,
            "terminal_growth":0.025,"shares":2410,"net_debt":15000,"market_price":162.50},
    "JPM": {"name":"JPMorgan Chase","sector":"Financials","fcf":27500,"beta":1.12,
            "debt_ratio":0.55,"cost_of_debt":0.045,"tax_rate":0.21,"base_growth":0.045,
            "terminal_growth":0.025,"shares":2870,"net_debt":40000,"market_price":208.70},
}

# Scenario presets
SCENARIO_PRESETS = {
    "📈 Bull Market":    {"rf": 3.00, "erp": 4.00, "growth": 1.40, "desc": "Low rates, high growth expectations"},
    "⚖️ Base Case":      {"rf": 4.25, "erp": 5.50, "growth": 1.00, "desc": "Current market consensus"},
    "📉 Recession":      {"rf": 2.00, "erp": 7.00, "growth": 0.60, "desc": "Rate cuts, risk aversion, slow growth"},
    "🔥 Stagflation":    {"rf": 7.00, "erp": 6.50, "growth": 0.50, "desc": "High inflation, weak growth"},
    "🚀 Tech Boom":      {"rf": 3.50, "erp": 4.50, "growth": 1.80, "desc": "AI/innovation-driven expansion"},
}


def fetch_stock_from_yfinance(ticker: str) -> Optional[dict]:
    """Fetch stock data from yfinance. Returns dict or None on failure."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        if not info or info.get("regularMarketPrice") is None:
            return None
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            return None
        beta = info.get("beta") or 1.0
        fcf = info.get("freeCashflow")
        if fcf is None:
            ocf = info.get("operatingCashflow", 0)
            capex = abs(info.get("capitalExpenditures", 0))
            fcf = ocf - capex if ocf else None
        if fcf is None or fcf <= 0:
            fcf = price * (info.get("sharesOutstanding", 1e9)) * 0.05
        shares = (info.get("sharesOutstanding") or 1e9) / 1e6
        total_debt = info.get("totalDebt") or 0
        total_equity = info.get("marketCap") or (price * shares * 1e6)
        debt_ratio = total_debt / (total_debt + total_equity) if (total_debt + total_equity) > 0 else 0.2
        net_debt = total_debt - (info.get("totalCash") or 0)
        rev_growth = info.get("revenueGrowth") or info.get("earningsGrowth") or 0.05
        rev_growth = max(min(rev_growth, 0.25), -0.5)
        if rev_growth < -0.5: rev_growth = 0.02
        return {
            "name": info.get("shortName") or ticker, "sector": info.get("sector", "Other"),
            "fcf": fcf / 1e6, "beta": beta, "debt_ratio": min(debt_ratio, 0.8),
            "cost_of_debt": 0.035, "tax_rate": 0.21, "base_growth": rev_growth,
            "terminal_growth": 0.025, "shares": shares, "net_debt": net_debt / 1e6,
            "market_price": price,
        }
    except Exception:
        return None


def build_universe(custom_tickers: List[str] = None):
    """Build stock universe from custom tickers or defaults."""
    if not custom_tickers:
        return DEFAULT_STOCKS.copy(), []
    universe, failed = {}, []
    for ticker in custom_tickers:
        ticker = ticker.strip().upper()
        if not ticker: continue
        data = fetch_stock_from_yfinance(ticker)
        if data:
            universe[ticker] = data
        elif ticker in DEFAULT_STOCKS:
            universe[ticker] = DEFAULT_STOCKS[ticker].copy()
        else:
            failed.append(ticker)
    return universe, failed


# ═══════════════════════════════════════════════════════════
# CORE VALUATION FUNCTIONS
# ═══════════════════════════════════════════════════════════

def calculate_wacc(rf, beta, erp, debt_ratio, cost_of_debt, tax_rate):
    ke = rf + beta * erp
    wacc = ke * (1 - debt_ratio) + cost_of_debt * (1 - tax_rate) * debt_ratio
    return wacc, ke


def calculate_dcf(fcf, growth, wacc, terminal_growth, shares, net_debt, years=5):
    if wacc <= terminal_growth or wacc <= 0:
        return np.nan, np.nan
    pv_fcfs = sum(fcf * (1 + growth)**t / (1 + wacc)**t for t in range(1, years+1))
    terminal_fcf = fcf * (1 + growth)**years * (1 + terminal_growth)
    pv_terminal = (terminal_fcf / (wacc - terminal_growth)) / (1 + wacc)**years
    ev = pv_fcfs + pv_terminal
    equity = ev - net_debt
    return max(equity / shares, 0), ev


def run_valuation_screen(universe, rf, erp, sector_mod, threshold=-0.20):
    rows = []
    for tk, s in universe.items():
        ag = s["base_growth"] * sector_mod
        wacc, ke = calculate_wacc(rf, s["beta"], erp, s["debt_ratio"], s["cost_of_debt"], s["tax_rate"])
        iv, ev = calculate_dcf(s["fcf"], ag, wacc, s["terminal_growth"], s["shares"], s["net_debt"])
        alpha = (iv - s["market_price"]) / s["market_price"] if not np.isnan(iv) else np.nan
        rows.append({"Ticker":tk,"Company":s["name"],"Sector":s["sector"],"Beta":s["beta"],
                      "WACC":wacc,"Cost of Equity":ke,"Adj. Growth":ag,
                      "Intrinsic Value":iv,"Market Price":s["market_price"],
                      "Implied Alpha":alpha,"Enterprise Value ($M)":ev})
    df = pd.DataFrame(rows)
    filt = df[df["Implied Alpha"].notna() & (df["Implied Alpha"] > threshold)].copy()
    return df, filt


# ═══════════════════════════════════════════════════════════
# COVARIANCE & PORTFOLIO OPTIMIZATION
# ═══════════════════════════════════════════════════════════

def generate_covariance_matrix(tickers, universe, market_vol=0.16):
    n = len(tickers)
    sectors = [universe[t]["sector"] for t in tickers]
    betas = np.array([universe[t]["beta"] for t in tickers])
    vols = betas * market_vol
    corr = np.eye(n)
    for i in range(n):
        for j in range(i+1, n):
            corr[i,j] = corr[j,i] = 0.60 if sectors[i] == sectors[j] else 0.25
    return np.outer(vols, vols) * corr


def _portfolio_stats(w, exp_rets, cov, rf):
    pr = w @ exp_rets
    pv = np.sqrt(w @ cov @ w)
    sr = (pr - rf) / pv if pv > 1e-10 else 0
    return pr, pv, sr


def optimize_portfolio(exp_rets, cov, rf, strategy="max_sharpe", max_weight=0.40):
    """Multi-strategy portfolio optimization."""
    n = len(exp_rets)
    if n == 0: return None, {}
    if n == 1:
        vol = np.sqrt(cov[0,0])
        return np.array([1.0]), {"return":exp_rets[0],"volatility":vol,
                                  "sharpe":(exp_rets[0]-rf)/vol if vol>0 else 0}

    bounds = [(0, max_weight)] * n
    constraints = [{"type":"eq","fun":lambda w: np.sum(w)-1.0}]
    x0 = np.ones(n)/n

    if strategy == "max_sharpe":
        obj = lambda w: -(w@exp_rets - rf) / np.sqrt(w@cov@w) if np.sqrt(w@cov@w)>1e-10 else 1e6
    elif strategy == "min_variance":
        obj = lambda w: w @ cov @ w
    elif strategy == "max_return":
        obj = lambda w: -(w @ exp_rets)
    elif strategy == "risk_parity":
        def obj(w):
            port_vol = np.sqrt(w @ cov @ w)
            if port_vol < 1e-10: return 1e6
            mrc = (cov @ w) / port_vol
            rc = w * mrc
            target = port_vol / n
            return np.sum((rc - target)**2)
    elif strategy == "equal_weight":
        return np.ones(n)/n, dict(zip(["return","volatility","sharpe"],
                                       _portfolio_stats(np.ones(n)/n, exp_rets, cov, rf)))
    else:
        obj = lambda w: -(w@exp_rets - rf) / np.sqrt(w@cov@w) if np.sqrt(w@cov@w)>1e-10 else 1e6

    res = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=constraints,
                   options={"maxiter":1000,"ftol":1e-12})
    weights = res.x if res.success else x0
    pr, pv, sr = _portfolio_stats(weights, exp_rets, cov, rf)
    return weights, {"return":pr,"volatility":pv,"sharpe":sr}


def calculate_efficient_frontier(exp_rets, cov, rf, n_points=60):
    n = len(exp_rets)
    if n < 2: return [], []
    targets = np.linspace(max(exp_rets.min(), -0.5), exp_rets.max(), n_points)
    vols, rets = [], []
    for t in targets:
        res = minimize(lambda w: np.sqrt(w@cov@w), np.ones(n)/n, method="SLSQP",
                       bounds=[(0,0.40)]*n,
                       constraints=[{"type":"eq","fun":lambda w:np.sum(w)-1},
                                    {"type":"eq","fun":lambda w,t=t:w@exp_rets-t}],
                       options={"maxiter":500})
        if res.success:
            vols.append(np.sqrt(res.x@cov@res.x))
            rets.append(t)
    return vols, rets


def risk_contribution(weights, cov):
    """Calculate each asset's contribution to total portfolio risk."""
    port_vol = np.sqrt(weights @ cov @ weights)
    if port_vol < 1e-10:
        return np.zeros(len(weights))
    mrc = (cov @ weights) / port_vol  # marginal risk contribution
    rc = weights * mrc                 # risk contribution
    return rc / rc.sum()               # percentage contribution


def monte_carlo_simulation(weights, exp_rets, cov, rf, initial=100000,
                           years=5, n_sims=1000):
    """Monte Carlo simulation of portfolio value over time."""
    port_ret = weights @ exp_rets
    port_vol = np.sqrt(weights @ cov @ weights)
    dt = 1/252  # daily steps
    n_steps = int(years * 252)
    np.random.seed(42)
    paths = np.zeros((n_sims, n_steps+1))
    paths[:, 0] = initial
    for i in range(n_steps):
        z = np.random.standard_normal(n_sims)
        paths[:, i+1] = paths[:, i] * np.exp((port_ret - 0.5*port_vol**2)*dt + port_vol*np.sqrt(dt)*z)

    percentiles = {
        "5th": np.percentile(paths, 5, axis=0),
        "25th": np.percentile(paths, 25, axis=0),
        "Median": np.percentile(paths, 50, axis=0),
        "75th": np.percentile(paths, 75, axis=0),
        "95th": np.percentile(paths, 95, axis=0),
    }
    final_values = paths[:, -1]
    stats = {
        "mean_final": np.mean(final_values),
        "median_final": np.median(final_values),
        "p5_final": np.percentile(final_values, 5),
        "p95_final": np.percentile(final_values, 95),
        "prob_loss": np.mean(final_values < initial),
        "max_drawdown": np.mean(np.min(paths / np.maximum.accumulate(paths, axis=1), axis=1) - 1),
    }
    days = np.arange(n_steps+1) / 252  # convert to years
    return days, percentiles, stats


def wacc_sensitivity_grid(stock, erp, sector_mod, rf_range, erp_range=None):
    """Generate WACC and IV grid for a single stock across Rf values."""
    if erp_range is None:
        erp_range = [erp]
    results = []
    for rf in rf_range:
        for e in erp_range:
            ag = stock["base_growth"] * sector_mod
            wacc, _ = calculate_wacc(rf, stock["beta"], e, stock["debt_ratio"],
                                     stock["cost_of_debt"], stock["tax_rate"])
            iv, _ = calculate_dcf(stock["fcf"], ag, wacc, stock["terminal_growth"],
                                  stock["shares"], stock["net_debt"])
            results.append({"Rf": rf, "ERP": e, "WACC": wacc, "IV": iv})
    return pd.DataFrame(results)
