# Research Tool — Build Brief

> Test a trading idea honestly, in an afternoon.
> Clean data, a realistic backtest, and results that tell you whether the edge is real or luck.

---

## 1. The problem (start here, not with code)

Most backtests lie, and the person running them rarely knows.

Not deliberately. They lie because the defaults are generous: no trading costs, the strategy is tuned and judged on the same data, dozens of variations are tried and only the best is kept, and the result is shown as one confident number with no sense of how much of it is luck.

So people trade ideas that only ever worked on paper. Independent traders lose money. Students learn the wrong lessons. Competition entrants overfit.

The tools that do this properly are either expensive, built for funds, or so complex that only specialists can use them.

**This tool makes the honest backtest the easy one.**

---

## 2. Who it's for

Useful if even one of these people finds it valuable:

- **Independent and prop traders** with a systematic idea who want to know if it's real before risking money.
- **Students and aspiring quants** who want to research properly, not just run tutorials.
- **Competition participants** (WorldQuant BRAIN, Numerai, Kaggle-style) who need to check ideas for overfitting.
- **Me** — as the research engine behind my own ideas and Proof's risk features.

Not for: live trading, signals, or anyone wanting a strategy handed to them.

---

## 3. Principles

1. **Honest by default.** Costs, slippage and out-of-sample testing are on unless you deliberately turn them off — and the report says when you did.
2. **Every number comes with its uncertainty.** Ranges, not single points. Small samples are called small.
3. **Count the attempts.** The tool tracks how many variations you tried, because trying fifty and keeping the best one changes what the result means.
4. **Reproducible.** The same data snapshot, code version and settings always produce the same result.
5. **Correct before clever.** Every metric is tested against known reference values.
6. **Simple to start, deep when needed.** One command for a first result; a full Python API for serious work.
7. **Say "we don't know".** If the evidence can't separate skill from luck, the report says so plainly.

---

## 4. What it does (v1)

### A. Get clean data
- Download daily prices from free sources (yfinance, Stooq), macro series (FRED) and crypto (via CCXT).
- Store everything as **versioned snapshots** (Parquet) so research can always be re-run on exactly the same data.
- Check data quality on the way in: missing days, suspicious jumps, adjusted vs unadjusted prices — and report problems instead of hiding them.

### B. Define a strategy simply
- A strategy is a small Python function: data in, target positions out.
- Clear, minimal interface so users write ideas, not plumbing.
- Include a few reference strategies (moving-average trend, mean reversion, pairs) as working examples.

### C. Backtest realistically
- Costs, slippage and position limits applied by default, configurable per market.
- No look-ahead: signals only use information available at the time.
- **Walk-forward testing:** tune on one period, test on the next, roll forward.
- **Purged cross-validation** for strategies using machine learning, so information doesn't leak from the future.

### D. Judge the result honestly
- Standard metrics: return, volatility, Sharpe, Sortino, maximum drawdown, win rate, expectancy, turnover.
- **Confidence ranges** on key metrics via bootstrapping.
- **Overfitting checks:** the number of variations tried, the deflated Sharpe ratio, and in-sample vs out-of-sample comparison.
- **Monte Carlo on the strategy's own returns:** the likely range of drawdowns and losing streaks to expect.
- A plain-language verdict: *"Likely real," "Can't tell yet," or "Probably luck"* — with the reasons.

### E. Report
- A one-page **tearsheet** (HTML) per run: equity curve, drawdowns, metric ranges, overfitting checks, the verdict, and the exact settings and data snapshot used.
- Every run saved with its configuration, so results can be compared and reproduced.

### F. Risk and portfolio tools (from the existing `quantrisk` package)
- VaR and CVaR (historical, parametric, Cornish-Fisher for fat tails), volatility models (GARCH), portfolio optimisation, options pricing, Monte Carlo simulation — kept, tested and made available through the same API.

---

## 5. How people use it

```bash
qr data pull SPY QQQ --from 2010-01-01          # snapshot data
qr backtest strategies/trend.py --walk-forward   # honest backtest
qr report runs/2026-10-14-trend                  # open the tearsheet
```

Or in Python / notebooks for deeper work. The command line gives a first honest answer in minutes; the API supports serious research.

---

## 6. Architecture

```
src/quantrisk/
├── data/        sources, quality checks, versioned Parquet snapshots (DuckDB/Polars for queries)
├── strategy/    the strategy interface and reference strategies
├── backtest/    vectorised engine: costs, slippage, limits, walk-forward, purged CV
├── evaluate/    metrics, bootstrapped ranges, overfitting checks, Monte Carlo, verdict
├── risk/        VaR/CVaR, volatility models
├── portfolio/   optimisation
├── options/     pricing and Greeks
├── report/      HTML tearsheets
└── cli.py       the `qr` command
```

- **Engine choice:** a fast **vectorised** backtester of our own for v1 (simple, transparent, testable). Study NautilusTrader for an event-driven engine later; do not copy GPL/LGPL code into this project.
- **Polars** for data work, **NumPy/SciPy/statsmodels/arch** for maths.
- The existing Streamlit app becomes optional — a viewer, not the core.

---

## 7. Engineering standards (non-negotiable)

- **Atomic commits**, `type: description` format, one logical change per commit. **No AI attribution** anywhere in git history.
- **Typed code** (type hints throughout), formatted and linted in CI.
- **Tests against reference values** for every metric and model (known textbook and published examples), plus property tests where useful (e.g. no look-ahead).
- **Reproducibility:** pinned dependencies (`uv`), data snapshots, run configs saved with every result.
- **CI on every pull request:** lint, type-check, tests.
- **Docs:** a clear README, a quickstart that works on a fresh machine, and a short guide to each verdict and metric in plain language.
- **Reuse before you build:** use proven libraries where they fit; check every licence. Prefer MIT/BSD/Apache. Never copy GPL/LGPL code in.
- **Licence:** MIT for this project (add a LICENSE file).

---

## 8. Scope

**v1 in:** data snapshots and quality checks, the strategy interface with reference strategies, the realistic vectorised backtester with walk-forward, honest evaluation with ranges, overfitting checks and Monte Carlo, the HTML tearsheet, the `qr` CLI, the existing risk/portfolio/options tools tested and exposed through the API.

**Later:** event-driven engine, intraday data, more data sources (including African markets where data allows), a hosted version, alpha research helpers for competition platforms.

**Never:** live trading, trade signals, or claims that a strategy will make money.

---

## 9. Build order

1. Project foundations — package layout, `uv`, CI, linting, type-checking, LICENSE.
2. Tests for the existing analytics against reference values; fix anything wrong.
3. Data layer — sources, quality checks, versioned snapshots.
4. Strategy interface and reference strategies.
5. Backtester — costs, slippage, limits, no look-ahead (with tests proving it).
6. Walk-forward and purged cross-validation.
7. Evaluation — metrics, bootstrapped ranges, overfitting checks, Monte Carlo, the verdict.
8. Tearsheet report and saved runs.
9. The `qr` CLI and quickstart docs.

## Definition of done for v1

Someone on a fresh machine can install the tool, pull data, run a walk-forward backtest of a reference strategy with costs on, and open a tearsheet that shows the results with uncertainty ranges, the overfitting checks and a plain verdict — and running it again produces exactly the same result. Every metric passes its reference tests.
