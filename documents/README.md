# documents/

Material kept in this repository that is **not** part of the trading system.

Nothing here feeds the strategies, playbooks, backtests or Pine code. It is
stored separately so the always-on session-start reading order in `CLAUDE.md`
is unaffected.

| file | what it is |
|------|------------|
| `bill_cooper_porterville_report.md` | Research report on 15 topics from Bill Cooper's 1997 Porterville presentation. Each topic separates documented fact from contested interpretation and lists sources for independent verification. |
| `Bill_Cooper_Porterville_Report.pdf` | Typeset PDF of the above, built with `research/build_report_pdf.py`. |
| `rigorous_research_framework.md` | Self-directed study guide built on four falsifiable frameworks: Mills' power elite, the Chomsky/Herman propaganda model, Kahneman's cognitive biases, and Strauss & Howe's generational cycles. Includes a source-reliability hierarchy and a ~200-hour reading schedule. |
| `Rigorous_Research_Framework.pdf` | Typeset PDF of the above. |
| `institutional_power_and_markets.md` | Document on leaks, insider-trading networks and a proposed pre-announcement trading system. **Carries an Editor's Verification Note recording six failed fact-checks, including one apparently fabricated case.** Body reproduced unaltered. |
| `Institutional_Power_And_Markets.pdf` | Typeset PDF of the above, verification note included. |
| `offshore_networks_and_institutional_data.md` | Guide to ICIJ offshore databases and SEC filing research, plus proposed trading workflows. **Carries an Editor's Verification Note: fabricated worked example, non-functional Pine code, and a section describing how to avoid regulatory attention.** Body reproduced unaltered. |
| `Offshore_Networks_And_Institutional_Data.pdf` | Typeset PDF of the above, verification note included. |
| `msvp_master_trading_system.md` | NQ futures system distilled from Fabio Valentini and Marco Accettone. **Carries an Editor's Verification Note: both traders verified real, but the headline Initial Balance statistic is misreported (sample size and the 82% figure).** Body unaltered. |
| `MSVP_Master_Trading_System.pdf` | Typeset PDF of the above, verification note included. |
| `mspv1_master_strategy_report.md` | "Dialectic Engine" strategy report for XAUUSD/BTCUSD/US30. **Verification note: its core stack (Supertrend 97/3.1 + EMA200 + RSI) is the same one we measured at PF 0.544 on AU200 the same day; its 78-82% accuracy claims carry no source.** Its Pine v6 technical lessons and its fake-data self-correction are sound. |
| `MSPV1_Master_Strategy_Report.pdf` | Typeset PDF of the above, verification note included. |
| `mspv2_dialectic_engine_report.md` | **Read this before MSPV1.** Reports its own negative results with real numbers (22-25%, 30.8% win rates) and concludes 1m has no edge regardless of indicator. Directly contradicts MSPV1 on the 1m timeframe, and is the one with data. |
| `MSPV2_Dialectic_Engine_Report.pdf` | Typeset PDF of the above, verification note included. |
| `msvp_carmine_rosato_source_003.md` | Carmine Rosato (verified real) CLC order-flow model for ES. **Verification note: the "TRIPLE CONFIRMED / CORE LAW" grading rests on a correlated sample — the source is a joint Fabio+Carmine session, and all three traders share one teaching platform.** |
| `MSVP_Carmine_Rosato_Source_003.pdf` | Typeset PDF of the above, verification note included. |
| `msvp4_fabio_valentini_training_manual.md` | Fabio Valentini AMT/order-flow manual. **First uploaded document verifiable against PRIMARY SOURCE held here** (five transcripts). Absorption and CVD corroborated; the 30-NY/20-London contract filter is blurred to "20-30"; contains no fabricated statistics, unlike its companion. |
| `MSVP4_Fabio_Valentini_Training_Manual.pdf` | Typeset PDF of the above, verification note included. |
| `Institutional_Intelligence_OS_Multi_Agent_Architecture.pdf` | 25-page architecture spec for the 8-agent Institutional Intelligence OS. |
| `Institutional_Intelligence_OS_Setup_Guide.pdf` | 38-page setup guide for the Institutional Intelligence OS. Addressed to the "Devesh" stack. |
| `Institutional_Intelligence_OS_Orchestrator_Framework.pdf` | Python orchestration framework coordinating the 8 agents. |
| `Institutional_Intelligence_OS_Executive_Summary.pdf` | Overview of the 7-file Institutional Intelligence OS documentation set. |
| `Devesh_IntelligenceOS_Integration_Summary.pdf` | Integration plan for a stack belonging to "Devesh" (392 skills, 81 agents, 15 MCPs, Hermes) — **not this repository's system**. |
| `Legendary_Trader_Pine_Scripts_Raw_Source.pdf` | Raw open-source Pine for Market Cipher B and similar. Supplied named "Mspv3" but unrelated to the MSPV strategy reports. |
| `Institutional_Intelligence_OS_Quick_Reference.pdf` | Operations manual for a PostgreSQL Form 4 signal pipeline. Supplied as two identical files; one kept. Documents a different system from the MSVP trading system. |

Rebuild the PDF with:

```
python3 research/build_report_pdf.py \
    documents/bill_cooper_porterville_report.md \
    documents/Bill_Cooper_Porterville_Report.pdf \
    "Bill Cooper" "The Porterville Presentation, 1997"
```
