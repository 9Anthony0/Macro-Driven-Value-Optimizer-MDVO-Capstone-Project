# AI Usage Disclosure — MGMT 490 Capstone Project

## Project: Macro-Driven Value Optimizer (MDVO)

### AI Tools Used
- **AI Coding Assistant** (Antigravity / Claude): Used for code generation, architecture design, and debugging

### How AI Was Used

| Task | AI Role | Human Role |
|------|---------|------------|
| Architecture Design | Proposed modular structure (engine.py + app.py) | Defined requirements, validated design decisions |
| DCF Implementation | Generated `calculate_dcf()` and `calculate_wacc()` functions | Verified CAPM formula, validated output ranges |
| Portfolio Optimization | Implemented SciPy SLSQP optimizer | Verified Sharpe ratio calculation, checked weight constraints |
| UI/CSS Styling | Generated Bloomberg-style dark theme CSS | Directed aesthetic preferences, reviewed layout |
| Stock Data | Populated baseline financial metrics | Cross-referenced with public financial data for realism |
| Error Handling | Implemented edge case guards | Identified edge cases (WACC ≤ terminal growth, empty filter) |
| DRIVER Documentation | Assisted with formatting and structure | Authored all analytical content and reflections |

### What I Learned Through This Process
1. **CAPM/WACC Integration:** Understanding how the risk-free rate flows through CAPM into WACC and ultimately affects enterprise valuations
2. **Mean-Variance Optimization:** How expected return vectors and covariance matrices drive portfolio construction
3. **Cross-Component Dependencies:** How assumptions in one stage compound through downstream calculations
4. **Edge Case Thinking:** Why financial models need robust handling for extreme parameter values

### What AI Cannot Replace
- **Judgment on model assumptions** (e.g., appropriate terminal growth rates, reasonable beta estimates)
- **Understanding of limitations** (why a simplified DCF shouldn't be used for actual investment decisions)
- **Domain expertise** (knowing when CAPM breaks down, understanding market microstructure)
- **Critical evaluation** of whether outputs make financial sense

### Verification Steps Taken
1. Manually calculated WACC for AAPL to verify formula implementation
2. Checked that higher Rf → higher WACC → lower intrinsic values (directional correctness)
3. Verified portfolio weights sum to 1.0 across all parameter combinations
4. Tested extreme parameters to ensure app handles edge cases without crashing
