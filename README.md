# Macro-Driven Value Optimizer (MDVO)

A three-stage investment pipeline where one macro assumption flows all the way down to a portfolio. Change the risk-free rate by 25 basis points and you can watch it move every stock's WACC, then its intrinsic value, then which stocks pass the screen, then the final portfolio weights.

<!-- LIVE DEMO: add your Streamlit link here, e.g. **[Try the live app](https://your-app.streamlit.app)** -->

📝 **Write-up:** [Cascading Alpha: Bridging the Gap Between Macro Scenarios and Stock Selection](https://9numbers0.substack.com/p/cascading-alpha-bridging-the-gap)

## The pipeline

```
1. Macro scenario engine  →  2. DCF valuation screener  →  3. Portfolio optimizer
   risk-free rate, ERP,         CAPM WACC, 5-year DCF,         5 strategies, efficient
   growth modifier, presets     implied alpha, screen          frontier, risk, Monte Carlo
```

**Stage 1: Macro.** Five presets (Bull, Base, Recession, Stagflation, Tech Boom) or manual control of the risk-free rate (2–8%), equity risk premium (3–8%) and a sector growth modifier (0.5–2×).

**Stage 2: Valuation.** For each stock: cost of equity = R_f + β × ERP, then WACC, a 5-year FCF projection and a Gordon-growth terminal value at 2.5%. The result is intrinsic value per share and *implied alpha* versus market price. An overvaluation filter decides which stocks move on.

**Stage 3: Portfolio.** Implied alphas, not historical returns, become the optimizer's expected returns. Five strategies are available: max Sharpe, min risk, max return, risk parity and equal weight. Each solves with a position cap via SLSQP.

## Dashboard tabs
| Tab | What's in it |
|-----|--------------|
| Overview | Macro regime, average alpha, stocks passing the screen, portfolio Sharpe, allocation donut |
| Valuation Engine | Filtered and full universe tables, implied-alpha bar chart, R_f × ERP sensitivity heatmap |
| Portfolio Construction | Efficient frontier, weights, risk-contribution breakdown, 1,000-path Monte Carlo (GBM) |
| Pipeline Sensitivity | Baseline vs. current comparison and a waterfall chart of the full cascade for any stock |

Custom tickers can be added and are pulled live through `yfinance`.

## Limitations (on purpose, and documented)
1. Single-stage DCF; terminal value can be 60–70% of intrinsic value.
2. Covariance is built from betas and sector correlations, not historical returns.
3. Single-factor CAPM rather than Fama-French.
4. Errors compound across a sequential pipeline.
5. Point-in-time financials, not a real-time feed.

It's meant as a scenario and screening tool that forces systematic thinking about how assumptions cascade. It doesn't replace fundamental analysis.

## Run it locally
```bash
cd "MGMT490 Capstone project"
pip install -r requirements.txt
streamlit run app.py
```

## Repo contents
```
MGMT490 Capstone project/
├── app.py                    # Streamlit UI (4 tabs)
├── engine.py                 # WACC, DCF, optimizer, risk contribution, Monte Carlo, sensitivity grid
├── styles.py                 # Custom CSS
├── DRIVER_Documentation.md   # Build process and validation
└── AI_Usage_Disclosure.md
MGMT 490 Capstone Project Video.txt   # Demo walkthrough transcript
```

## Tech
Python · pandas · NumPy · SciPy · yfinance · Plotly · Streamlit

---
Built by [Anthony Petrescu](https://www.linkedin.com/in/anthony-petrescu/) as the MGMT 490 capstone at Purdue · Finance + Computer Science '27
