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
| `Institutional_Intelligence_OS_Quick_Reference.pdf` | Operations manual for a PostgreSQL Form 4 signal pipeline. Supplied as two identical files; one kept. Documents a different system from the MSVP trading system. |

Rebuild the PDF with:

```
python3 research/build_report_pdf.py \
    documents/bill_cooper_porterville_report.md \
    documents/Bill_Cooper_Porterville_Report.pdf \
    "Bill Cooper" "The Porterville Presentation, 1997"
```
