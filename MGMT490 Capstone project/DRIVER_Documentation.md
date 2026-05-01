# DRIVER Documentation — Macro-Driven Value Optimizer (MDVO) v2

## D — DISCOVER & DEFINE

**Problem:** Build an integrated investment pipeline connecting macroeconomic scenario analysis, DCF valuation, and portfolio optimization with full cross-component sensitivity and multiple optimization strategies.

**Success Criteria:**
- App runs without crashing under all parameter combinations
- Three components integrated with data flow: Macro → Valuation → Portfolio
- 5 portfolio construction strategies available
- Cross-component sensitivity clearly demonstrated
- Professional, institutional-quality UI with premium aesthetics
- Monte Carlo simulation and risk analytics included

---

## R — REPRESENT

```
SIDEBAR INPUTS                    MAIN DASHBOARD
┌──────────────────┐              ┌────────────────────────────────────┐
│ Scenario Presets │              │  HERO: Pipeline Overview           │
│ (Bull/Bear/etc.) │              ├────────────────────────────────────┤
│                  │──────────────│  STEP 2: DCF Valuation Screener    │
│ Macro Parameters │              │  • WACC = Rf + β×ERP (CAPM)        │
│ • Risk-Free Rate │              │  • Intrinsic Value per share       │
│ • Equity Risk Pr.│              │  • Implied Alpha bar chart         │
│ • Growth Modifier│              ├────────────────────────────────────┤
│                  │              │  STEP 3: Portfolio Construction    │
│ Portfolio Strategy│             │  • 5 strategies: Max Sharpe, Min   │
│ • Max Sharpe     │              │    Risk, Max Return, Risk Parity,  │
│ • Min Risk       │              │    Equal Weight                    │
│ • Max Return     │              │  • Pie chart + Efficient Frontier  │
│ • Risk Parity    │              ├────────────────────────────────────┤
│ • Equal Weight   │              │  RISK ANALYTICS                    │
│                  │              │  • Risk contribution breakdown     │
│ Max Position Size│              │  • Monte Carlo simulation          │
│                  │              ├────────────────────────────────────┤
│ Stock Universe   │              │  PIPELINE SENSITIVITY              │
│ • Default 10     │              │  • Baseline vs. Current comparison │
│ • Custom (yfinance)│            │  • Waterfall cascade chart         │
└──────────────────┘              │  • WACC Sensitivity Heatmap        │
                                  └────────────────────────────────────┘
```

---

## I — IMPLEMENT

**Files:** `engine.py` (calculations), `styles.py` (CSS), `app.py` (UI)

**Key Functions:**
- `calculate_wacc()` / `calculate_dcf()` — CAPM-based valuation
- `optimize_portfolio()` — 5-strategy optimizer (SLSQP)
- `risk_contribution()` — marginal risk decomposition
- `monte_carlo_simulation()` — 1,000-path GBM simulation
- `wacc_sensitivity_grid()` — Rf × ERP heatmap data
- `fetch_stock_from_yfinance()` — live data integration

---

## V — VALIDATE

✅ App launches without errors on all tested parameter combinations
✅ All 5 portfolio strategies produce valid weights summing to 100%
✅ Extreme Rf (8%) correctly filters most stocks — graceful warning shown
✅ Monte Carlo simulation produces reasonable value distributions
✅ WACC heatmap correctly shows inverse Rf-IV relationship
✅ Custom tickers via yfinance fetch and display correctly
✅ Scenario presets correctly update all downstream calculations

---

## E — EVOLVE

**v1 → v2 Enhancements:**
1. 5 portfolio strategies (was: Max Sharpe only)
2. Monte Carlo simulation with configurable horizon
3. Risk contribution decomposition
4. WACC sensitivity heatmap (Rf × ERP)
5. Scenario presets (Bull, Recession, Stagflation, Tech Boom)
6. Custom ticker input via yfinance
7. Adjustable max position size
8. Premium gradient UI with glassmorphism

---

## R — REFLECT

**Limitations:**
1. Simplified single-stage DCF (real models use multi-stage growth)
2. Sector-based synthetic covariance (not historical correlations)
3. Single-factor CAPM (professionals use Fama-French multi-factor)
4. No transaction costs or tax-loss harvesting
5. Static financial data (not real-time feeds)
6. Assumption errors compound across pipeline stages

**Professional Use Case:**
Scenario analysis and screening tool for portfolio managers — quickly visualize how rate environments affect valuations and optimal allocations. Supplements (not replaces) fundamental analysis. Key value: forces systematic thinking about how assumptions cascade through investment decisions.
