"""MDVO v3 — Institutional Tabbed Dashboard"""
import streamlit as st, pandas as pd, numpy as np, plotly.graph_objects as go, copy
from engine import *
from styles import CUSTOM_CSS, CHART_LAYOUT, SECTOR_COLORS

st.set_page_config(page_title="MDVO", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def CL(**kw):
    base = copy.deepcopy(CHART_LAYOUT)
    base.update(kw)
    return base
def sc(t): return SECTOR_COLORS.get(universe.get(t,{}).get("sector",""),"#6b7280")

# ════════════════════════════ SIDEBAR ════════════════════════════
with st.sidebar:
    st.markdown("## ◆ MDVO")
    st.caption("Macro-Driven Value Optimizer")
    st.markdown("---")
    # Scenarios
    preset = st.selectbox("🎬 Scenario Preset", ["Custom"]+list(SCENARIO_PRESETS.keys()))
    if preset != "Custom":
        p=SCENARIO_PRESETS[preset]; st.caption(f"*{p['desc']}*")
        drf,derp,dg = p["rf"],p["erp"],p["growth"]
    else: drf,derp,dg = 4.25,5.50,1.00
    st.markdown("---")
    st.markdown("##### ⚙️ Macro Parameters")
    risk_free = st.slider("Risk-Free Rate (%)",2.0,8.0,drf,0.25)/100
    erp = st.slider("Equity Risk Premium (%)",3.0,8.0,derp,0.25)/100
    sector_mod = st.slider("Sector Growth Modifier",0.50,2.00,dg,0.05)
    overval_thresh = st.slider("Overvaluation Filter (%)",-50,0,-20,5)/100
    st.markdown("---")
    st.markdown("##### 🏗️ Portfolio Strategy")
    strategy = st.radio("Objective:", ["Max Sharpe Ratio","Minimize Risk","Maximize Return","Risk Parity","Equal Weight"], label_visibility="collapsed")
    smap={"Max Sharpe Ratio":"max_sharpe","Minimize Risk":"min_variance","Maximize Return":"max_return","Risk Parity":"risk_parity","Equal Weight":"equal_weight"}
    skey=smap[strategy]
    max_wt = st.slider("Max Position (%)",10,100,40,5)/100
    st.markdown("---")
    st.markdown("##### 📡 Universe")
    use_custom = st.toggle("Custom Tickers",value=False)
    if use_custom:
        ti=st.text_area("Tickers:","AAPL, MSFT, GOOGL, NVDA, AMZN, META, JPM, XOM")
        clist=[t.strip().upper() for t in ti.split(",") if t.strip()]
    else: clist=None
    # Regime
    st.markdown("---")
    reg="🟢 Dovish" if risk_free<0.04 else ("🟡 Neutral" if risk_free<0.06 else "🔴 Hawkish")
    st.markdown(f'<div class="sidebar-card" style="text-align:center"><div style="font-size:.6rem;color:#6b7280;text-transform:uppercase;letter-spacing:.12em">Regime</div><div style="font-size:1.1rem;font-weight:700;margin:4px 0">{reg}</div><div style="font-size:.72rem;color:#4b5563">Rf {risk_free:.2%} · ERP {erp:.2%} · G×{sector_mod:.2f}</div></div>', unsafe_allow_html=True)

# Build universe
if use_custom and clist:
    with st.spinner("Fetching..."): universe,failed=build_universe(clist)
    if failed: st.sidebar.warning(f"Failed: {', '.join(failed)}")
else: universe,_=build_universe()

# Run pipeline
all_df,filtered_df=run_valuation_screen(universe,risk_free,erp,sector_mod,overval_thresh)
has_stocks=len(filtered_df)>0
if has_stocks:
    tickers=filtered_df["Ticker"].tolist()
    exp_rets=filtered_df["Implied Alpha"].values
    cov_matrix=generate_covariance_matrix(tickers,universe)
    weights,stats=optimize_portfolio(exp_rets,cov_matrix,risk_free,skey,max_wt)
else:
    tickers,exp_rets,cov_matrix,weights,stats=[],np.array([]),None,None,{}

# Helper
def fmt(df):
    d=df.copy()
    for c in ["WACC","Cost of Equity","Adj. Growth"]: d[c]=d[c].apply(lambda x:f"{x:.2%}")
    d["Intrinsic Value"]=d["Intrinsic Value"].apply(lambda x:f"${x:,.2f}" if not np.isnan(x) else "—")
    d["Market Price"]=d["Market Price"].apply(lambda x:f"${x:,.2f}")
    d["Implied Alpha"]=d["Implied Alpha"].apply(lambda x:f"{x:+.1%}" if not np.isnan(x) else "—")
    d["Enterprise Value ($M)"]=d["Enterprise Value ($M)"].apply(lambda x:f"${x:,.0f}M" if not np.isnan(x) else "—")
    return d

# ════════════════════════════ HEADER ════════════════════════════
st.markdown("# ◆ Macro-Driven Value Optimizer")
st.caption(f"Pipeline: Macro Scenario Engine → DCF Valuation ({len(universe)} stocks) → {strategy} Portfolio")
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

# ════════════════════════════ TABS ════════════════════════════
tab_dash, tab_val, tab_port, tab_sens = st.tabs([
    "📊 Dashboard Overview", "📈 Valuation Engine", "🎯 Portfolio Construction", "🔗 Pipeline Sensitivity"
])

# ──────────────────── TAB 1: DASHBOARD ────────────────────
with tab_dash:
    st.markdown('<span class="pill p-blue">Executive Summary</span>', unsafe_allow_html=True)

    # Macro panel
    st.markdown("#### Macro Environment")
    mc1,mc2,mc3,mc4=st.columns(4)
    mc1.metric("Risk-Free Rate",f"{risk_free:.2%}")
    mc2.metric("Equity Risk Prem.",f"{erp:.2%}")
    mc3.metric("Growth Modifier",f"{sector_mod:.2f}×")
    mc4.metric("Regime",reg.split(" ",1)[1])

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # Key outputs
    st.markdown("#### Key Outputs")
    ko1,ko2,ko3,ko4=st.columns(4)
    aa=filtered_df["Implied Alpha"].mean() if has_stocks else 0
    ko1.metric("Avg Alpha (Filtered)",f"{aa:.1%}")
    ko2.metric("Avg WACC",f"{all_df['WACC'].mean():.2%}")
    ko3.metric("Stocks Passed",f"{len(filtered_df)} / {len(all_df)}")
    if has_stocks: ko4.metric("Portfolio Sharpe",f"{stats.get('sharpe',0):.2f}")
    else: ko4.metric("Portfolio Sharpe","—")

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # Two panels: table + donut
    dcol,pcol=st.columns([3,2])
    with dcol:
        st.markdown("#### Filtered Stock Universe")
        if has_stocks: st.dataframe(fmt(filtered_df)[["Ticker","Company","Sector","WACC","Intrinsic Value","Market Price","Implied Alpha"]], width="stretch", hide_index=True, height=340)
        else: st.info("No stocks passed the valuation screen.")
    with pcol:
        st.markdown("#### Optimal Allocation")
        if has_stocks:
            wdf=pd.DataFrame({"Ticker":tickers,"Weight":weights})
            wdf=wdf[wdf["Weight"]>0.005].sort_values("Weight",ascending=False)
            fig=go.Figure(go.Pie(labels=wdf["Ticker"],values=wdf["Weight"],
                marker=dict(colors=[sc(t) for t in wdf["Ticker"]],line=dict(color="#181c24",width=2)),
                textinfo="label+percent",textfont=dict(size=11,family="Inter",color="#d1d5db"),
                hole=0.55,hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"))
            fig.update_layout(**CL(height=340,showlegend=False,margin=dict(l=20,r=20,t=20,b=20)),
                annotations=[dict(text=f"<b>{stats['sharpe']:.2f}</b><br><span style='font-size:9px;color:#6b7280'>{strategy.split()[0]}</span>",
                    x=0.5,y=0.5,font=dict(size=18,color="#e4e8ee",family="JetBrains Mono"),showarrow=False)])
            st.plotly_chart(fig, width="stretch")
        else: st.info("Optimize after stocks pass screen.")

# ──────────────────── TAB 2: VALUATION ────────────────────
with tab_val:
    st.markdown('<span class="pill p-green">Step 2 · DCF Valuation Engine</span>', unsafe_allow_html=True)
    st.markdown("#### Intrinsic Value & Implied Alpha")

    vm1,vm2,vm3,vm4=st.columns(4)
    vm1.metric("Universe",f"{len(all_df)}")
    vm2.metric("Passed Screen",f"{len(filtered_df)}")
    vm3.metric("Avg Alpha",f"{aa:.1%}")
    vm4.metric("Avg WACC",f"{all_df['WACC'].mean():.2%}")

    vt1,vt2=st.tabs(["🟢 Filtered","📋 Full Universe"])
    with vt1:
        if has_stocks: st.dataframe(fmt(filtered_df), width="stretch", hide_index=True)
        else: st.warning("No stocks passed. Adjust parameters.")
    with vt2: st.dataframe(fmt(all_df), width="stretch", hide_index=True)

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # Alpha bar chart
    if len(all_df)>0:
        st.markdown("#### Implied Alpha by Stock")
        cdf=all_df.dropna(subset=["Implied Alpha"])
        fig_a=go.Figure(go.Bar(x=cdf["Ticker"],y=cdf["Implied Alpha"]*100,
            marker=dict(color=["#10b981" if a>0 else "#ef4444" for a in cdf["Implied Alpha"]],
                        line=dict(width=0),cornerradius=6),
            text=[f"{a:+.1f}%" for a in cdf["Implied Alpha"]*100],textposition="outside",
            textfont=dict(size=10,family="JetBrains Mono",color="#9ca3af")))
        fig_a.update_layout(**CL(height=340),yaxis_title="Alpha (%)")
        st.plotly_chart(fig_a, width="stretch")

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # WACC Heatmap
    st.markdown("#### WACC Sensitivity Heatmap")
    hm_tk=st.selectbox("Stock for heatmap:",list(universe.keys()),key="hm")
    s_hm=universe[hm_tk]
    rf_vals=np.arange(0.02,0.081,0.005); erp_vals=np.arange(0.03,0.081,0.005)
    grid=wacc_sensitivity_grid(s_hm,erp,sector_mod,rf_vals,erp_vals)
    pivot=grid.pivot(index="ERP",columns="Rf",values="IV")
    fig_hm=go.Figure(go.Heatmap(z=pivot.values,
        x=[f"{r:.1%}" for r in pivot.columns],y=[f"{e:.1%}" for e in pivot.index],
        colorscale=[[0,"#ef4444"],[0.5,"#fbbf24"],[1,"#10b981"]],
        text=[[f"${v:,.0f}" if not np.isnan(v) else "—" for v in row] for row in pivot.values],
        texttemplate="%{text}",textfont=dict(size=7,family="JetBrains Mono"),
        hovertemplate="Rf:%{x}<br>ERP:%{y}<br>IV:%{text}<extra></extra>",
        colorbar=dict(title="IV ($)",tickformat="$,.0f")))
    fig_hm.update_layout(**CL(height=400),xaxis_title="Risk-Free Rate",yaxis_title="Equity Risk Premium",
        title=f"{hm_tk} Intrinsic Value across Rf × ERP")
    st.plotly_chart(fig_hm, width="stretch")

# ──────────────────── TAB 3: PORTFOLIO ────────────────────
with tab_port:
    st.markdown('<span class="pill p-purple">Step 3 · Portfolio Construction</span>', unsafe_allow_html=True)
    st.markdown(f"#### {strategy} Portfolio")

    if not has_stocks:
        st.error("🚫 No stocks passed the valuation screen. Adjust macro parameters.")
    else:
        pm1,pm2,pm3=st.columns(3)
        pm1.metric("Expected Return",f"{stats['return']:.2%}")
        pm2.metric("Volatility",f"{stats['volatility']:.2%}")
        pm3.metric("Sharpe Ratio",f"{stats['sharpe']:.2f}")

        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

        pie_c,ef_c=st.columns(2)
        with pie_c:
            st.markdown("#### Allocation")
            wdf=pd.DataFrame({"Ticker":tickers,"Weight":weights})
            wdf=wdf[wdf["Weight"]>0.005].sort_values("Weight",ascending=False)
            fig_p=go.Figure(go.Pie(labels=wdf["Ticker"],values=wdf["Weight"],
                marker=dict(colors=[sc(t) for t in wdf["Ticker"]],line=dict(color="#181c24",width=2)),
                textinfo="label+percent",textfont=dict(size=11,family="Inter",color="#d1d5db"),
                hole=0.52,hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"))
            fig_p.update_layout(**CL(height=400,showlegend=False,margin=dict(l=20,r=20,t=20,b=20)),
                annotations=[dict(text=f"<b>{stats['sharpe']:.2f}</b><br><span style='font-size:9px;color:#6b7280'>Sharpe</span>",
                    x=0.5,y=0.5,font=dict(size=20,color="#e4e8ee",family="JetBrains Mono"),showarrow=False)])
            st.plotly_chart(fig_p, width="stretch")

        with ef_c:
            st.markdown("#### Efficient Frontier")
            f_vols,f_rets=calculate_efficient_frontier(exp_rets,cov_matrix,risk_free)
            fig_ef=go.Figure()
            if f_vols:
                fig_ef.add_trace(go.Scatter(x=[v*100 for v in f_vols],y=[r*100 for r in f_rets],
                    mode="lines",name="Frontier",line=dict(color="#06b6d4",width=2.5,shape="spline"),
                    fill="tozeroy",fillcolor="rgba(6,182,212,.04)"))
            fig_ef.add_trace(go.Scatter(x=[stats["volatility"]*100],y=[stats["return"]*100],
                mode="markers",name=strategy.split()[-1],
                marker=dict(color="#fbbf24",size=14,symbol="star",line=dict(color="#181c24",width=1.5))))
            avols=[np.sqrt(cov_matrix[i,i])*100 for i in range(len(tickers))]
            fig_ef.add_trace(go.Scatter(x=avols,y=[r*100 for r in exp_rets],
                mode="markers+text",name="Assets",
                marker=dict(color="#8b5cf6",size=7,line=dict(color="#a78bfa",width=1)),
                text=tickers,textposition="top center",textfont=dict(size=8,color="#6b7280")))
            fig_ef.update_layout(**CL(height=400),xaxis_title="Volatility (%)",yaxis_title="Return (%)")
            st.plotly_chart(fig_ef, width="stretch")

        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

        # Weights table
        st.markdown("#### Detailed Weights")
        wt_full=pd.DataFrame({"Ticker":tickers,"Company":[universe[t]["name"] for t in tickers],
            "Sector":[universe[t]["sector"] for t in tickers],
            "Weight":[f"{w:.2%}" for w in weights],"Alpha":[f"{r:+.1%}" for r in exp_rets]})
        st.dataframe(wt_full, width="stretch", hide_index=True)

        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

        # Risk Analytics
        st.markdown('<span class="pill p-red">Risk Analytics</span>', unsafe_allow_html=True)
        ra_c,mc_c=st.columns(2)

        with ra_c:
            st.markdown("#### Risk Contribution")
            rc=risk_contribution(weights,cov_matrix)
            fig_rc=go.Figure(go.Bar(
                x=[t for i,t in enumerate(tickers) if weights[i]>0.005],
                y=[r*100 for i,r in enumerate(rc) if weights[i]>0.005],
                marker=dict(color=[sc(t) for i,t in enumerate(tickers) if weights[i]>0.005],
                            line=dict(width=0),cornerradius=6),
                text=[f"{r:.1f}%" for i,r in enumerate(rc*100) if weights[i]>0.005],
                textposition="outside",textfont=dict(size=9,family="JetBrains Mono",color="#9ca3af")))
            fig_rc.update_layout(**CL(height=320),yaxis_title="Risk Contribution (%)")
            st.plotly_chart(fig_rc, width="stretch")

        with mc_c:
            st.markdown("#### Monte Carlo Simulation")
            mc_y=st.select_slider("Horizon (years)",[1,2,3,5,7,10],value=5,key="mc")
            days,pcts,mcs=monte_carlo_simulation(weights,exp_rets,cov_matrix,risk_free,years=mc_y)
            fig_mc=go.Figure()
            # Fan chart
            fig_mc.add_trace(go.Scatter(x=days,y=pcts["95th"],mode="lines",name="95th",
                line=dict(width=0),showlegend=False))
            fig_mc.add_trace(go.Scatter(x=days,y=pcts["5th"],mode="lines",name="5th–95th",
                line=dict(width=0),fill="tonexty",fillcolor="rgba(59,130,246,.06)"))
            fig_mc.add_trace(go.Scatter(x=days,y=pcts["75th"],mode="lines",name="75th",
                line=dict(width=0),showlegend=False))
            fig_mc.add_trace(go.Scatter(x=days,y=pcts["25th"],mode="lines",name="25th–75th",
                line=dict(width=0),fill="tonexty",fillcolor="rgba(59,130,246,.1)"))
            fig_mc.add_trace(go.Scatter(x=days,y=pcts["Median"],mode="lines",name="Median",
                line=dict(color="#10b981",width=2.5,shape="spline")))
            fig_mc.add_hline(y=100000,line_dash="dot",line_color="#4b5563",opacity=.5)
            mc_layout = CL(height=320)
            mc_layout["yaxis"] = dict(title="Value ($)", tickformat="$,.0f", gridcolor="#1e2229")
            fig_mc.update_layout(**mc_layout, xaxis_title="Years")
            st.plotly_chart(fig_mc, width="stretch")
            sm1,sm2,sm3=st.columns(3)
            sm1.metric("Median",f"${mcs['median_final']:,.0f}")
            sm2.metric("P(Loss)",f"{mcs['prob_loss']:.1%}")
            sm3.metric("Avg Max DD",f"{mcs['max_drawdown']:.1%}")

# ──────────────────── TAB 4: SENSITIVITY ────────────────────
with tab_sens:
    st.markdown('<span class="pill p-amber">Pipeline Sensitivity</span>', unsafe_allow_html=True)
    st.markdown("#### Cross-Component Cascade Analysis")
    st.caption("Trace how Risk-Free Rate changes ripple: **ΔRf → ΔWACC → ΔIV → ΔWeight**")

    base_rf=0.03
    rows=[]
    for tk,s in universe.items():
        ag=s["base_growth"]*sector_mod
        wb,_=calculate_wacc(base_rf,s["beta"],erp,s["debt_ratio"],s["cost_of_debt"],s["tax_rate"])
        wc,_=calculate_wacc(risk_free,s["beta"],erp,s["debt_ratio"],s["cost_of_debt"],s["tax_rate"])
        ivb,_=calculate_dcf(s["fcf"],ag,wb,s["terminal_growth"],s["shares"],s["net_debt"])
        ivc,_=calculate_dcf(s["fcf"],ag,wc,s["terminal_growth"],s["shares"],s["net_debt"])
        rows.append({"Ticker":tk,"Sector":s["sector"],
            "WACC (3%)":f"{wb:.2%}","WACC (Now)":f"{wc:.2%}","ΔWACC":f"{(wc-wb)*100:+.2f}pp",
            "IV (3%)":f"${ivb:,.2f}" if not np.isnan(ivb) else "—",
            "IV (Now)":f"${ivc:,.2f}" if not np.isnan(ivc) else "—",
            "ΔIV":f"{(ivc-ivb)/ivb*100:+.1f}%" if (not np.isnan(ivb) and ivb>0) else "—"})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=360)

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # Drill-down
    st.markdown("#### Single-Stock Cascade Drill-Down")
    dtk=st.selectbox("Select stock:",list(universe.keys()),key="sens_tk")
    s=universe[dtk]; ag=s["base_growth"]*sector_mod
    wb,_=calculate_wacc(base_rf,s["beta"],erp,s["debt_ratio"],s["cost_of_debt"],s["tax_rate"])
    wc,_=calculate_wacc(risk_free,s["beta"],erp,s["debt_ratio"],s["cost_of_debt"],s["tax_rate"])
    ivb,_=calculate_dcf(s["fcf"],ag,wb,s["terminal_growth"],s["shares"],s["net_debt"])
    ivc,_=calculate_dcf(s["fcf"],ag,wc,s["terminal_growth"],s["shares"],s["net_debt"])

    def get_wt(rf):
        _,filt=run_valuation_screen(universe,rf,erp,sector_mod,overval_thresh)
        if len(filt)<1 or dtk not in filt["Ticker"].values: return 0.0
        tl=filt["Ticker"].tolist();er=filt["Implied Alpha"].values
        cv=generate_covariance_matrix(tl,universe); w,_=optimize_portfolio(er,cv,rf,skey,max_wt)
        return w[tl.index(dtk)] if w is not None else 0.0
    wtb,wtc=get_wt(base_rf),get_wt(risk_free)

    st.markdown(f"**{dtk} — {s['name']}** · {s['sector']}")
    d1,d2,d3,d4=st.columns(4)
    d1.metric("Risk-Free",f"{risk_free:.2%}",f"{(risk_free-base_rf)*100:+.2f}pp")
    d2.metric("WACC",f"{wc:.2%}",f"{(wc-wb)*100:+.2f}pp")
    d3.metric("Intrinsic Value",f"${ivc:,.2f}" if not np.isnan(ivc) else "—",
        f"{(ivc-ivb)/ivb*100:+.1f}%" if (not np.isnan(ivb) and ivb>0) else "—")
    d4.metric("Weight",f"{wtc:.1%}",f"{(wtc-wtb)*100:+.1f}pp")

    fig_w=go.Figure(go.Waterfall(
        x=["ΔRf","→ ΔWACC","→ ΔIV%","→ ΔWeight"],
        y=[(risk_free-base_rf)*100,(wc-wb)*100,
           ((ivc-ivb)/ivb*100) if (not np.isnan(ivb) and ivb>0) else 0,(wtc-wtb)*100],
        measure=["relative"]*4,
        connector=dict(line=dict(color="#22272f",width=1.5)),
        increasing=dict(marker=dict(color="#10b981")),
        decreasing=dict(marker=dict(color="#ef4444")),
        textposition="outside",textfont=dict(family="JetBrains Mono",size=11,color="#9ca3af"),
        text=[f"{(risk_free-base_rf)*100:+.2f}pp",f"{(wc-wb)*100:+.2f}pp",
              f"{(ivc-ivb)/ivb*100:+.1f}%" if (not np.isnan(ivb) and ivb>0) else "—",
              f"{(wtc-wtb)*100:+.1f}pp"]))
    fig_w.update_layout(**CL(height=380,showlegend=False),title=f"Sensitivity Cascade: {dtk}",
        yaxis_title="Change (pp / %)")
    st.plotly_chart(fig_w, width="stretch")

# Footer
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#4b5563;font-size:.7rem;padding:12px">◆ MDVO v3 · MGMT 490 Capstone · Educational tool only · Not investment advice</div>', unsafe_allow_html=True)
