# documents/

Material kept in this repository that is **not** part of the trading system.

Nothing here feeds the strategies, playbooks, backtests or Pine code. It is
stored separately so the always-on session-start reading order in `CLAUDE.md`
is unaffected.

| file | what it is |
|------|------------|
| `bill_cooper_porterville_report.md` | Research report on 15 topics from Bill Cooper's 1997 Porterville presentation. Each topic separates documented fact from contested interpretation and lists sources for independent verification. |
| `Bill_Cooper_Porterville_Report.pdf` | Typeset PDF of the above, built with `research/build_report_pdf.py`. |

Rebuild the PDF with:

```
python3 research/build_report_pdf.py \
    documents/bill_cooper_porterville_report.md \
    documents/Bill_Cooper_Porterville_Report.pdf \
    "Bill Cooper" "The Porterville Presentation, 1997"
```
