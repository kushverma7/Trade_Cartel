import sys, json, numpy as np, pandas as pd
sys.path.insert(0,"/home/user/Trade_Cartel")
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)
R="/home/user/Trade_Cartel/research/"
INK=colors.HexColor("#14213d"); ACC=colors.HexColor("#c1121f")
GOLD=colors.HexColor("#b8860b"); PAPER=colors.HexColor("#faf8f3")
GRN=colors.HexColor("#2d6a4f"); GREY=colors.HexColor("#6c757d"); LINE=colors.HexColor("#d8d3c8")
ss=getSampleStyleSheet()
def st(n,**k): return ParagraphStyle(n,parent=ss["Normal"],**k)
H1=st("H1",fontName="Helvetica-Bold",fontSize=19,textColor=INK,leading=22,spaceAfter=2)
SUB=st("SUB",fontName="Helvetica",fontSize=9,textColor=GREY,leading=12,spaceAfter=10)
H2=st("H2",fontName="Helvetica-Bold",fontSize=12,textColor=INK,leading=14,spaceBefore=11,spaceAfter=5)
H3=st("H3",fontName="Helvetica-Bold",fontSize=9.5,textColor=GOLD,leading=12,spaceBefore=7,spaceAfter=3)
BODY=st("BODY",fontName="Helvetica",fontSize=8.8,textColor=INK,leading=12.5,spaceAfter=5)
SMALL=st("SMALL",fontName="Helvetica",fontSize=7.6,textColor=GREY,leading=10,spaceAfter=4)
def tbl(data,widths,align=None,head=True,fs=8):
    cell=ParagraphStyle("c",parent=ss["Normal"],fontName="Helvetica",fontSize=fs,
                        leading=fs+2.6,textColor=INK)
    def wrap(c,r):
        # A cell must become a Paragraph if it is long enough to need wrapping
        # OR if it carries markup/entities -- a raw string in a ReportLab table
        # renders "<b>" and "&gt;" literally.
        if isinstance(c,str) and r>0 and (len(c)>44 or "<" in c or "&" in c):
            return Paragraph(c,cell)
        return c
    data=[[wrap(c,r) for c in row] for r,row in enumerate(data)]
    t=Table(data,colWidths=widths,repeatRows=1 if head else 0)
    cm=[("FONT",(0,0),(-1,-1),"Helvetica",fs),("TEXTCOLOR",(0,0),(-1,-1),INK),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),5),
        ("RIGHTPADDING",(0,0),(-1,-1),5),("LINEBELOW",(0,0),(-1,-2),0.4,LINE)]
    if head: cm+=[("FONT",(0,0),(-1,0),"Helvetica-Bold",fs),("BACKGROUND",(0,0),(-1,0),PAPER),
                  ("LINEBELOW",(0,0),(-1,0),0.9,INK)]
    if align:
        for c,a in align.items(): cm.append(("ALIGN",(c,0),(c,-1),a))
    t.setStyle(TableStyle(cm)); return t
def callout(txt,color=ACC):
    t=Table([[Paragraph(txt,BODY)]],colWidths=[168*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PAPER),("LINEBEFORE",(0,0),(0,-1),2.5,color),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t
def footer(c,doc):
    c.saveState(); c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(21*mm,14*mm,189*mm,14*mm)
    c.setFont("Helvetica",6.8); c.setFillColor(GREY)
    c.drawString(21*mm,10*mm,"Gold Trend - quantitative research report  |  XAUUSD 30m  |  not investment advice")
    c.drawRightString(189*mm,10*mm,f"page {doc.page}"); c.restoreState()

E=pd.read_csv(R+"signals_mfe_mae.csv"); G=pd.read_csv(R+"tp_sl_grid_extended.csv")
W=pd.read_csv(R+"walkforward.csv"); OPT=pd.read_csv(R+"opt_stage1_train.csv")
TRD=pd.read_csv(R+"trades_shipped.csv")
H=[3,5,10,15,20,30,50]
doc=SimpleDocTemplate("Gold_Trend_Quant_Research.pdf",pagesize=A4,leftMargin=21*mm,
    rightMargin=21*mm,topMargin=18*mm,bottomMargin=20*mm,
    title="Gold Trend - Quantitative Research Report",author="Trade Cartel")
E_=[];A=E_.append

A(Paragraph("Quantitative Research Report",H1))
A(Paragraph("Gold Trend &mdash; Strategy &nbsp;|&nbsp; XAUUSD 30m &nbsp;|&nbsp; 78,695 bars, "
  "1 Dec 2019 &ndash; 30 Jul 2026 &nbsp;|&nbsp; 4,036 raw signals, 737 traded positions",SUB))
v=[["VERDICT","Moderate evidence of a robust edge - with one disqualifying fragility"]]
t=Table(v,colWidths=[26*mm,142*mm])
t.setStyle(TableStyle([("FONT",(0,0),(0,0),"Helvetica-Bold",9),("FONT",(1,0),(1,0),"Helvetica-Bold",11),
    ("TEXTCOLOR",(0,0),(0,0),GREY),("TEXTCOLOR",(1,0),(1,0),INK),("BACKGROUND",(0,0),(-1,-1),PAPER),
    ("LINEABOVE",(0,0),(-1,0),1.5,GOLD),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
    ("LEFTPADDING",(0,0),(-1,-1),8)]))
A(t); A(Spacer(1,8))

A(Paragraph("1. What the entry signal is actually worth",H2))
A(Paragraph("Signal confirms on the close of bar N; entry is the OPEN of bar N+1. No intrabar path "
  "of the signal bar is used and no measurement window reads beyond its own horizon. Longs and "
  "shorts are kept separate throughout.",SMALL))
A(Image("q_mfe.png",width=168*mm,height=57*mm))
r=[["Hold (30m bars)","MFE median (ATR)","MAE median (ATR)","MFE/MAE","Favourable first","Mean return (ATR)"]]
for h in H:
    r.append([f"{h}",f"{E[f'mfe_atr_{h}'].median():.3f}",f"{E[f'mae_atr_{h}'].median():.3f}",
              f"{E[f'mfe_atr_{h}'].median()/E[f'mae_atr_{h}'].median():.2f}",
              f"{100*(E[f'bars_mfe_{h}']<E[f'bars_mae_{h}']).mean():.1f}%",
              f"{(E[f'ret_{h}']/E.atr).mean():+.3f}"])
A(tbl(r,[28*mm,30*mm,30*mm,22*mm,30*mm,28*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT"}))
A(callout("<b>The signal has no short-horizon edge.</b> MFE/MAE is 0.97 at a three-bar hold and the "
  "signal moves favourably before adversely only <b>48.8%</b> of the time &mdash; a coin flip. The ratio "
  "climbs to 1.16 by 50 bars and mean return climbs from 0.039 to 0.764 ATR. <b>The edge accrues to "
  "hold time, not to entry timing.</b> That is the same exponent gap this project measured indirectly, "
  "now measured on the entry signal itself."))
A(PageBreak())

A(Paragraph("2. Target and stop testing &mdash; 103 combinations",H2))
A(Paragraph("Each signal's forward path is walked once and thresholds resolved from it. When a stop "
  "and target are first crossed on the SAME 30-minute bar the true order is unknowable without "
  "lower-timeframe data; those resolve as LOSSES (conservative) and the frequency is reported.",SMALL))
A(Image("q_grid.png",width=112*mm,height=73*mm))
A(Paragraph("Ambiguity frequency and why it does not change the conclusion",H3))
r=[["Setting","Same-bar ambiguity","Effect on the verdict"],
   ["target 0.25 / stop 0.25","44.3%","severe - but this cell loses heavily anyway"],
   ["target 1.00 / stop 1.00","1.7%","negligible"],
   ["target 3.00 / stop 2.00","0.3%","negligible - and this is the region that works"]]
A(tbl(r,[42*mm,34*mm,92*mm]))
A(callout("<b>Every target at or below 2.0 ATR is negative after costs, at every stop tested.</b> Edge "
  "rises monotonically with both target and stop and the optimum sits <b>at the boundary of the grid</b> "
  "even after extending targets to 12 ATR. A boundary optimum that keeps improving is the mathematical "
  "statement of <b>no target at all</b> &mdash; which is precisely the shipped exit. The targets were "
  "never too large; they are always too small.",GRN))

A(Paragraph("3. Optimisation and the three-way split",H2))
nexec=len(OPT); passed=int((OPT.rejected=="").sum())
r=[["Item","Value"],
   ["Combinations actually executed",f"{nexec:,} (row count of opt_stage1_train.csv, not an estimate)"],
   ["Passed the rejection filters",f"{passed:,}"],
   ["Rejected: profit factor &lt; 1.15",f"{int((OPT.rejected=='profit factor < 1.15').sum()):,}"],
   ["Rejected: one month &gt; 40% of profit",f"{int((OPT.rejected=='one month is >40% of profit').sum()):,}"],
   ["Rejected: drawdown &gt; 55%",f"{int((OPT.rejected=='drawdown > 55%').sum()):,}"],
   ["Train / Validation / Test","2019-12 to 2023-11 / 2023-11 to 2025-03 / 2025-03 to 2026-07"]]
A(tbl(r,[62*mm,106*mm]))
A(Spacer(1,3))
r=[["Stage","FROZEN (search-selected)","SHIPPED (untouched original)"],
   ["Train (in-sample, 60%)","PF 1.326 / +561.5%","PF 1.324 / +507.0%"],
   ["Validation (20%)","PF 1.737 / +111.6%","PF 1.484 / +75.0%"],
   ["TEST (untouched, 20%)","PF 2.209 / +269.8% / DD 21.1%","PF 2.016 / +249.0% / DD 20.7%"]]
A(tbl(r,[46*mm,61*mm,61*mm]))
A(Paragraph("Parameters and the selection rule were frozen to disk before the test window was read. "
  "<b>Trail 4.24 appears in all top 15 train configurations and entry 24 in 13 of 15</b> &mdash; the "
  "search re-finds the existing settings. Its total gain over changing nothing is <b>+0.193 profit "
  "factor</b>, which after 4,500 trials and 40 validated finalists is inside selection noise.",BODY))
A(callout("<b>Both configurations improved from train to test rather than degrading.</b> That is not "
  "vindication. The test window (Apr 2025 &ndash; Jul 2026) contains the largest gold trend in the "
  "sample. It is a favourable regime as much as it is evidence, and it should be read that way."))
A(PageBreak())

A(Paragraph("4. Walk-forward &mdash; re-optimising makes it worse",H2))
A(Image("q_wf.png",width=168*mm,height=50*mm))
r=[["Approach","Compounded","Positive windows","Median window PF"],
   ["Re-optimised every quarter (12m train / 3m trade)","+463.6%","14 / 21","1.430"],
   ["<b>Fixed shipped parameters, same 21 windows</b>","+651.7%","14 / 21","1.314"]]
A(tbl(r,[76*mm,30*mm,32*mm,30*mm],{1:"RIGHT",2:"CENTER",3:"RIGHT"}))
A(Paragraph("Fixed parameters beat re-optimised ones in <b>11 of 21</b> windows. Twelve months is too "
  "short to estimate these parameters and the search picks up noise. This is evidence the parameters "
  "are <b>stable rather than fitted</b> &mdash; the opposite of what an overfit system shows.",BODY))

A(Paragraph("5. Statistical edge",H2))
r=[["Measure","Value","Reading"],
   ["Expectancy per trade","+1.451 R","1R = median losing trade"],
   ["Bootstrap 95% CI","[+0.469, +2.592] R","5,000 resamples"],
   ["P(expectancy &lt;= 0)","0.08%","bootstrap, not a normal-theory p-value"],
   ["Win rate / payoff","21.71% / 6.614","low hit rate is by design"],
   ["Break-even win rate","13.13%","cushion of +8.58 points"],
   ["Skew / kurtosis","+7.40 / +78.0","far from normal - trust the bootstrap"],
   ["Trade autocorrelation","&lt;= 0.063 at lags 1-5","trades are effectively independent"]]
A(tbl(r,[46*mm,44*mm,78*mm]))
A(Paragraph("Risk of ruin and drawdown by risk per trade (5,000 bootstrap paths each)",H3))
r=[["Risk / trade","Median DD","95th pct DD","P(DD over 50%)","P(ruin, -80%)","Median net"],
   ["0.50%","19.4%","30.2%","0.0%","0.00%","+835%"],
   ["0.75%","27.7%","42.2%","0.9%","0.00%","+2,309%"],
   ["<b>1.00% (shipped)</b>","35.6%","53.2%","8.3%","0.00%","+5,941%"],
   ["1.50%","49.0%","68.2%","46.0%","0.04%","+27,321%"],
   ["2.00%","60.1%","78.9%","85.5%","0.24%","+91,014%"]]
A(tbl(r,[30*mm,26*mm,28*mm,28*mm,28*mm,28*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT"}))

A(Paragraph("6. Cost sensitivity",H2))
r=[["Slippage per side","Full-sample PF","Full-sample net","Max DD","Test-window PF"],
   ["0.00 pt","1.940","+9,950.9%","28.73%","2.065"],
   ["<b>0.20 pt (shipped)</b>","1.834","+5,921.9%","33.80%","2.016"],
   ["0.50 pt","1.691","+2,675.8%","41.82%","2.006"],
   ["1.00 pt","1.364","+581.7%","66.67%","1.912"],
   ["1.50 pt","1.087","+74.6%","85.84%","1.756"]]
A(tbl(r,[36*mm,30*mm,34*mm,28*mm,30*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"}))
A(Paragraph("Survives a doubling of slippage to 0.40 per side (PF 1.716). Break-even is near 1.6 points. "
  "Execution quality remains the largest single risk and it is larger than any parameter in the system.",BODY))
A(PageBreak())

A(Paragraph("7. The finding that limits everything else",H2))
A(Image("q_frag.png",width=88*mm,height=62*mm))
r=[["Best trades removed","Profit factor","Total P&L"],
   ["0 (as traded)","1.834","+$592,189"],
   ["1","1.668","+$474,198"],
   ["5","1.335","+$238,139"],
   ["<b>10</b>","1.040","+$28,230"],
   ["<b>20</b>","0.712","-$204,468"],
   ["Best single MONTH (Mar 2026)","1.669","+$461,471"]]
A(tbl(r,[56*mm,34*mm,40*mm],{1:"RIGHT",2:"RIGHT"}))
A(callout("<b>Ten trades out of 737 separate this system from break-even. Twenty separate it from a "
  "losing one.</b> Combined with a worst losing streak of 25 consecutive positions and an 8.3% chance "
  "of exceeding a 50% drawdown at 1% risk, this &mdash; not any parameter &mdash; is the constraint "
  "that governs whether the strategy is tradeable. It is inherent to trend following and no "
  "configuration tested removes it."))

A(Paragraph("8. Regime, direction and session",H2))
r=[["Breakdown","Trades","Profit factor","Net P&L"],
   ["Long","484","1.806","+$384,477"],
   ["Short","253","1.891","+$207,712"],
   ["Low volatility (ATR rank &lt; 0.33)","300","1.632","+$214,853"],
   ["Mid volatility","217","1.709","+$147,785"],
   ["High volatility (rank &gt; 0.67)","208","2.403","+$224,563"]]
A(tbl(r,[62*mm,26*mm,32*mm,36*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Paragraph("The short side has the HIGHER profit factor despite a lower win rate. Cutting it was "
  "tested and rejected: it degrades exactly the two calendar years in which gold fell, and it is "
  "harmful on a second instrument.",BODY))
A(Paragraph("Session (reported as a hypothesis, NOT applied)",H3))
r=[["Session (UTC)","Signals","Mean 50-bar return (ATR)","After 0.146 ATR cost"],
   ["London 07-12","915","+1.111","+0.965"],
   ["Asia 00-07","1,015","+0.926","+0.780"],
   ["LDN/NY overlap 12-16","1,181","+0.838","+0.692"],
   ["Late / rollover 21-24","205","+0.509","+0.363"],
   ["<b>New York 16-21</b>","718","+0.041","-0.105 NEGATIVE"]]
A(tbl(r,[46*mm,26*mm,48*mm,44*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Paragraph("New York is the only losing session. <b>It has deliberately NOT been applied as a filter</b> "
  "because it has not been validated out of sample, and adding it now would be exactly the kind of "
  "in-sample fitting the rest of this study is designed to avoid. Timestamps are UTC; a fixed UTC hour "
  "drifts one hour against local session time twice a year and this has not been corrected.",BODY))

A(Paragraph("9. Replication, assumptions and weaknesses",H2))
r=[["Item","Status"],
   ["Repainting","None. No request.security, no varip, no realtime branches; all channel lookbacks [1]-offset."],
   ["Lookahead","None. Signals evaluate on closed bars; entry is the next bar's open."],
   ["Same-bar stop/target","Unresolvable at 30m. Resolved conservatively as losses; frequency reported per cell."],
   ["Pyramid fills","Gap-aware: if a bar opened beyond the add level, the fill is the open, not the level."],
   ["Data","No 5-minute gold data exists in this project. 15-minute data resampled to 30m was used, as directed."],
   ["Test-window regime","The untouched window contains gold's largest trend of the sample. Results are regime-flattered."],
   ["Sample size","737 positions over 6.7 years. Adequate for expectancy, thin for session and regime subgroups."],
   ["Overnight financing","NOT modelled. Average hold is 21 hours, so swap costs are real and would reduce these figures."]]
A(tbl(r,[38*mm,130*mm],fs=7.8))
A(Spacer(1,4))
A(Paragraph("Exported files: signals_mfe_mae.csv (4,034 signals, full excursion detail), "
  "opt_stage1_train.csv (all 4,500 combinations), tp_sl_grid.csv and tp_sl_grid_extended.csv, "
  "stage1_finalists.csv, stage2_validation.csv, walkforward.csv, trades_shipped.csv (737 trades). "
  "Code in research/mfe_mae.py, tp_sl_grid.py, optimise.py, walkforward.py.",SMALL))
A(Paragraph("Generated 3 August 2026. All figures include 0.07 commission and 0.20 points of slippage "
  "per side unless stated. Backtested performance is not a prediction and this document is not proof "
  "of a future edge. Research record, not investment advice.",SMALL))
doc.build(E_,onFirstPage=footer,onLaterPages=footer)
print("built")
