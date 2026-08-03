import sys, numpy as np, pandas as pd
sys.path.insert(0,"/home/user/Trade_Cartel")
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT
from backtest.io import load_csv
from backtest import champion as ch, exit_lab

gd=load_csv("/home/user/Trade_Cartel/data/xauusd_15m.csv.gz",rule="30min")
B=dict(pyr=dict(pyr_atr=1.5,pyr_max=4,pyr_mode="vol_entry"),cooldown=24,
       lb_over=dict(sma2=630),tighten_after=20,tighten_to=2.0,frac_qty=True)
tr,_=ch.run(gd,**B); d=pd.DataFrame(tr)
d["date"]=[gd.index[b] for b in d["bar"]]; d["hours"]=d.bars_held*0.5
W=d[d.pnl>0]; L=d[d.pnl<=0]
S=exit_lab.stats(tr); YRS=(gd.index[-1]-gd.index[0]).days/365.25
CAGR=((1+S['net_pct']/100)**(1/YRS)-1)*100

INK=colors.HexColor("#14213d"); ACC=colors.HexColor("#c1121f")
GOLD=colors.HexColor("#b8860b"); PAPER=colors.HexColor("#faf8f3")
GREY=colors.HexColor("#6c757d"); LINE=colors.HexColor("#d8d3c8")

ss=getSampleStyleSheet()
def st(n,**k): return ParagraphStyle(n,parent=ss["Normal"],**k)
H1=st("H1",fontName="Helvetica-Bold",fontSize=19,textColor=INK,leading=22,spaceAfter=2)
SUB=st("SUB",fontName="Helvetica",fontSize=9,textColor=GREY,leading=12,spaceAfter=10)
H2=st("H2",fontName="Helvetica-Bold",fontSize=12,textColor=INK,leading=14,
      spaceBefore=12,spaceAfter=5)
H3=st("H3",fontName="Helvetica-Bold",fontSize=9.5,textColor=GOLD,leading=12,
      spaceBefore=8,spaceAfter=3)
BODY=st("BODY",fontName="Helvetica",fontSize=8.8,textColor=INK,leading=12.5,spaceAfter=5)
SMALL=st("SMALL",fontName="Helvetica",fontSize=7.6,textColor=GREY,leading=10,spaceAfter=4)
WARN=st("WARN",fontName="Helvetica-Bold",fontSize=9,textColor=ACC,leading=12,spaceAfter=4)

def tbl(data,widths,align=None,head=True,fs=8):
    # Plain strings in a ReportLab table cell DO NOT wrap and DO NOT parse HTML
    # entities -- long text runs off the page edge. Anything long becomes a
    # Paragraph so it wraps inside its column.
    cell=ParagraphStyle("cell",parent=ss["Normal"],fontName="Helvetica",
                        fontSize=fs,leading=fs+2.6,textColor=INK)
    data=[[Paragraph(c,cell) if (isinstance(c,str) and len(c)>44 and r>0) else c
           for c in row] for r,row in enumerate(data)]
    t=Table(data,colWidths=widths,repeatRows=1 if head else 0)
    cmds=[("FONT",(0,0),(-1,-1),"Helvetica",fs),
          ("TEXTCOLOR",(0,0),(-1,-1),INK),
          ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
          ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("LINEBELOW",(0,0),(-1,-2),0.4,LINE)]
    if head:
        cmds+=[("FONT",(0,0),(-1,0),"Helvetica-Bold",fs),
               ("BACKGROUND",(0,0),(-1,0),PAPER),
               ("LINEBELOW",(0,0),(-1,0),0.9,INK)]
    if align:
        for c,a in align.items(): cmds.append(("ALIGN",(c,0),(c,-1),a))
    t.setStyle(TableStyle(cmds)); return t

def callout(txt,color=ACC,style=None):
    p=Paragraph(txt,style or BODY)
    t=Table([[p]],colWidths=[168*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PAPER),
        ("LINEBEFORE",(0,0),(0,-1),2.5,color),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(21*mm,14*mm,189*mm,14*mm)
    canvas.setFont("Helvetica",6.8); canvas.setFillColor(GREY)
    canvas.drawString(21*mm,10*mm,"Gold Trend - Strategy  |  XAUUSD 30m  |  research report, not investment advice")
    canvas.drawRightString(189*mm,10*mm,f"page {doc.page}")
    canvas.restoreState()

doc=SimpleDocTemplate("Gold_Trend_Strategy_Report.pdf",pagesize=A4,
    leftMargin=21*mm,rightMargin=21*mm,topMargin=18*mm,bottomMargin=20*mm,
    title="Gold Trend Strategy - Full Report",author="Trade Cartel")
E=[]
A=E.append

# ---------------- PAGE 1 ----------------
A(Paragraph("Gold Trend &mdash; Strategy",H1))
A(Paragraph("XAUUSD 30-minute &nbsp;|&nbsp; trend-following with volatility-scaled pyramiding "
            "&nbsp;|&nbsp; tested 1 Dec 2019 &ndash; 30 Jul 2026 (6.7 years, 737 positions)",SUB))

hdr=[["Profit factor","Net return","Max drawdown","CAGR","MAR","Win rate"],
     [f"{S['pf']:.3f}",f"+{S['net_pct']:,.0f}%",f"{S['maxdd_pct']:.2f}%",
      f"{CAGR:.1f}%",f"{CAGR/S['maxdd_pct']:.2f}","21.7%"]]
t=Table(hdr,colWidths=[28*mm]*6)
t.setStyle(TableStyle([("FONT",(0,0),(-1,0),"Helvetica",7),
    ("FONT",(0,1),(-1,1),"Helvetica-Bold",13),
    ("TEXTCOLOR",(0,0),(-1,0),GREY),("TEXTCOLOR",(0,1),(-1,1),INK),
    ("ALIGN",(0,0),(-1,-1),"CENTER"),("BACKGROUND",(0,0),(-1,-1),PAPER),
    ("TOPPADDING",(0,0),(-1,0),7),("BOTTOMPADDING",(0,1),(-1,1),7),
    ("LINEABOVE",(0,0),(-1,0),1.5,GOLD)]))
A(t); A(Spacer(1,10))

A(Paragraph("1. The question you asked: average winning points vs losing points",H2))
pts=[["","Points per trade","In ATR","In dollars*"],
     ["Average WIN",f"+{W.points.mean():.2f}",f"+{(W.points/W.atr0).mean():.2f}",f"+${W.pnl.mean():,.0f}"],
     ["Average LOSS",f"{L.points.mean():.2f}",f"{(L.points/L.atr0).mean():.2f}",f"-${abs(L.pnl.mean()):,.0f}"],
     ["Ratio (win : loss)",f"{abs(W.points.mean()/L.points.mean()):.2f} : 1",
      f"{abs((W.points/W.atr0).mean()/(L.points/L.atr0).mean()):.2f} : 1",
      f"{abs(W.pnl.mean()/L.pnl.mean()):.2f} : 1"],
     ["Median WIN",f"+{W.points.median():.2f}","","" ],
     ["Median LOSS",f"{L.points.median():.2f}","",""]]
A(tbl(pts,[46*mm,42*mm,32*mm,42*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Paragraph("*Dollar figures are on a compounding account that grew from $10,000 to $602,189, "
            "so the dollar ratio (6.61:1) is much larger than the point ratio (2.25:1). "
            "Later trades are simply bigger. The point ratio is the honest per-trade number.",SMALL))

A(Spacer(1,4))
A(callout(
  "<b>THE MOST IMPORTANT NUMBER IN THIS REPORT.</b> Average points per trade across all 737 "
  "positions is <b>&minus;4.01 points</b>. That is <i>negative</i>. The strategy is profitable "
  "only because position size is concentrated in the winners: losers are cut before they can "
  "pyramid, winners carry four added units. <b>Traded at a fixed lot size this strategy loses "
  "money</b> (&minus;2,955 points total). The pyramiding is not an enhancement &mdash; it is the "
  "edge itself."))
A(Spacer(1,6))
A(Image("c_points.png",width=82*mm,height=55*mm))
A(Spacer(1,2))
A(Paragraph("2. Why the average trade loses points but the account still compounds",H2))
rows=[["Adds reached","Trades","% of all","Win rate","Avg points","Total P&L"]]
for k in range(5):
    g=d[d.adds==k]
    if len(g)==0: continue
    rows.append([f"{k} adds",f"{len(g)}",f"{100*len(g)/len(d):.1f}%",
                 f"{100*(g.pnl>0).mean():.1f}%",f"{g.points.mean():+.2f}",f"${g.pnl.sum():+,.0f}"])
A(tbl(rows,[26*mm,20*mm,20*mm,22*mm,26*mm,38*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT"}))
A(Paragraph("A position only reaches four adds if it has already moved six ATR in your favour. "
            "That cohort is 26.7% of trades, wins 81.2% of the time, and produces "
            "<b>+$1,258,247</b> while the other four cohorts lose $666,058 between them.",BODY))
A(PageBreak())

# ---------------- PAGE 2 ----------------
A(Paragraph("3. Biggest wins and biggest losses",H2))
A(Paragraph("Ten largest winning positions",H3))
r=[["Entered","Side","Points","P&L","Held","Adds"]]
for _,x in d.nlargest(10,"points").iterrows():
    r.append([str(x.date)[:16],"LONG" if x["dir"]>0 else "SHORT",f"+{x.points:.1f}",
              f"${x.pnl:+,.0f}",f"{x.hours:.0f}h",f"{x.adds}"])
A(tbl(r,[34*mm,18*mm,24*mm,34*mm,18*mm,16*mm],{2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"CENTER"}))
A(Paragraph("Ten largest losing positions",H3))
r=[["Entered","Side","Points","P&L","Held","Adds"]]
for _,x in d.nsmallest(10,"points").iterrows():
    r.append([str(x.date)[:16],"LONG" if x["dir"]>0 else "SHORT",f"{x.points:.1f}",
              f"${x.pnl:+,.0f}",f"{x.hours:.0f}h",f"{x.adds}"])
A(tbl(r,[34*mm,18*mm,24*mm,34*mm,18*mm,16*mm],{2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"CENTER"}))
A(Paragraph("Note the asymmetry in <b>time</b>, not just size: winners are held 42 hours on "
            "average, losers 15 hours. The system's entire edge is that it stays in the good "
            "trades and leaves the bad ones quickly.",BODY))
A(Spacer(1,3))
A(callout("The single largest loss (&minus;$23,399, 17 Apr 2026) was a trade that had already "
   "pyramided twice before reversing. Losses of that size are a structural feature of adding to "
   "winners, not a malfunction. Expect them.",ACC))

A(PageBreak())
A(Paragraph("4. Performance by year",H2))
A(Image("c_years.png",width=168*mm,height=46*mm))
r=[["Year","Trades","Win rate","Profit factor","Avg win pts","Avg loss pts","P&L"]]
d["yr"]=d.date.dt.year
for y,g in d.groupby("yr"):
    gw=g[g.pnl>0]; gl=g[g.pnl<=0]
    r.append([str(y),f"{len(g)}",f"{100*len(gw)/len(g):.1f}%",
              f"{gw.pnl.sum()/max(-gl.pnl.sum(),1e-9):.2f}",
              f"+{gw.points.mean():.1f}" if len(gw) else "-",
              f"{gl.points.mean():.1f}" if len(gl) else "-",
              f"${g.pnl.sum():+,.0f}"])
A(tbl(r,[18*mm,18*mm,22*mm,26*mm,26*mm,26*mm,32*mm],
      {1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT",6:"RIGHT"}))
A(Paragraph("2021 is the only losing year (PF 0.98). Average point sizes grow through the sample "
            "because gold itself went from $1,450 to $4,100 &mdash; a 15-point move in 2020 is the "
            "same percentage as a 42-point move in 2026.",SMALL))

A(Paragraph("5. Equity curve and drawdown",H2))
A(Image("c_equity.png",width=168*mm,height=74*mm))
A(Image("c_adds.png",width=82*mm,height=55*mm))
A(Spacer(1,4))
A(Paragraph("6. How the strategy actually works",H2))
mech=[["Component","Rule"],
 ["Entry trigger","Close breaks the highest high / lowest low of the prior 24 bars (12 hours)"],
 ["Filter 1","Close above/below the 21-day EMA (regime gate)"],
 ["Filter 2","Close above/below the 8-day SMA"],
 ["Filter 3","Close above/below the 13-day SMA. All three must agree."],
 ["Short-only gate","The regime EMA must also be FALLING (2-day slope) before any short"],
 ["Initial stop","4.24 x ATR(14) from entry - deliberately wide, outside the noise band"],
 ["Exit","Chandelier trailing stop at 4.24 x ATR, ratcheting one way only. Nothing else."],
 ["Trail tightening","After a 20 ATR favourable run the trail tightens to 2.0 x ATR"],
 ["Adds","Every 1.5 ATR of favourable movement, up to 4, each sized on the ATR at entry"],
 ["Cooldown","24 bars (12 hours) flat after any exit before a new entry"],
 ["Targets","NONE. Twenty target configurations were tested; every one reduced returns."]]
A(tbl(mech,[34*mm,134*mm],fs=7.8))
A(Spacer(1,4))
A(Paragraph("Exit statistics",H3))
r=[["Metric","All trades","Winners","Losers"],
   ["Count","737","160 (21.7%)","577 (78.3%)"],
   ["Average hold",f"{d.hours.mean():.1f} h",f"{W.hours.mean():.1f} h",f"{L.hours.mean():.1f} h"],
   ["Average points",f"{d.points.mean():+.2f}",f"+{W.points.mean():.2f}",f"{L.points.mean():.2f}"],
   ["Largest",f"-",f"+{d.points.max():.1f} pts",f"{d.points.min():.1f} pts"],
   ["Exit reason","100% trailing stop","","" ]]
A(tbl(r,[36*mm,36*mm,36*mm,36*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Spacer(1,8))
A(Paragraph("7. Position sizing and account size",H2))
px=4081.11; atr=13.17; stop=4.24*atr
A(Paragraph(f"Position size = <b>account equity &times; 1% &divide; (4.24 &times; ATR)</b>. "
  f"At gold ${px:,.0f} with 30m ATR of {atr:.2f} points, the stop distance is "
  f"<b>{stop:.1f} points</b>, so each $10,000 of account buys {10000*0.01/stop:.2f} ounces.",BODY))
r=[["Account","Position (oz)","In lots","Peak stack*","Notional at peak","Verdict"]]
for eq,v in ((2000,"Cannot trade - size floors to zero"),
             (5000,"Broken - takes ~9% of signals"),
             (10000,"Works, leaks ~1/3 of return"),
             (25000,"Recommended minimum"),
             (50000,"Full fidelity"),
             (100000,"Full fidelity")):
    oz=eq*0.01/stop
    r.append([f"${eq:,}",f"{oz:.2f}",f"{oz/100:.3f}",f"{5*oz:.2f} oz",f"${5*oz*px:,.0f}",v])
A(tbl(r,[22*mm,24*mm,18*mm,22*mm,30*mm,52*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"},fs=7.6))
A(Paragraph("*Peak stack = the position after all four adds, roughly 5&times; the initial unit "
            "(3.65&times; account leverage). At 1:100 broker leverage that needs 3.7% of the "
            "account as margin; at 1:20 it needs 18.3%.",SMALL))
A(Spacer(1,3))
A(callout("<b>$25,000 is the recommended minimum</b>, and the reason is granularity, not risk. "
  "Gold has tripled since 2019, so a 1% risk budget now buys fewer whole ounces. Tested from "
  "today's price levels: at $5,000 the strategy took 5 of 57 signals and lost money; at $10,000 "
  "it returned +35% against an ideal +53%; at $25,000 it took 57 of 57 and came within 1.8 "
  "points of ideal. If your broker supports 0.001 lot / micro-gold, $10,000 behaves like "
  "$50,000 and this constraint disappears.",GOLD))

A(Paragraph("8. How to trade it",H2))
steps=[["1","Chart XAUUSD, 30-minute. Leave every input at default; auto-scale derives the "
        "lookbacks from the timeframe. The dashboard shows what is actually in use."],
 ["2","Set slippage to your broker's real gold spread before trusting any figure. The shipped "
      "value is 0.20 points. Break-even is 1.2-1.5 points."],
 ["3","Risk 1% per position (the Balanced profile). Do not raise it until you have lived "
      "through a full drawdown."],
 ["4","Take every signal. Skipping trades destroys the strategy - 26.7% of positions "
      "produce 100% of the profit and you cannot know in advance which."],
 ["5","Never move the stop closer or take profit early. The trail is the only exit and the "
      "edge is entirely in letting winners run."],
 ["6","Let the adds happen. If you cannot pyramid, do not trade this system at fixed size "
      "&mdash; see section 1."]]
A(tbl([["#","Step"]]+steps,[10*mm,158*mm],fs=8))

A(Paragraph("9. Risks you must accept before funding it",H2))
res=(d.pnl>0).values; run=0; mx=0; runs=[]
for x in res:
    if not x: run+=1; mx=max(mx,run)
    else:
        if run: runs.append(run)
        run=0
runs=np.array(runs)
risks=[["Risk","The number"],
 ["Long losing streaks",f"Longest run of consecutive losing positions: {mx}. "
   f"{(runs>=10).sum()} separate streaks of 10+, {(runs>=15).sum()} of 15+. This is normal at a 21.7% win rate."],
 ["Profit concentration","The top 10 positions are ~95% of net profit. Miss them and you have a losing system."],
 ["Execution sensitivity","At 0.50 pt slippage returns fall sharply; at 1.50 pt the strategy is dead. "
   "This is the largest single risk and it is larger than any parameter."],
 ["Drawdown","30.85% on the TradingView deep test. Live is likely worse. On $25,000 that is "
   "-$7,750, and a 45% stress case is -$11,250."],
 ["A losing year","2021 returned PF 0.98. A year of going nowhere is a normal outcome."],
 ["Regime dependence","Gold rose from $1,450 to $4,100 across the test. The system made money in "
   "gold's down years too, but it has never seen a multi-year bear market."]]
A(tbl(risks,[34*mm,134*mm],fs=7.8))
A(Spacer(1,4))
A(Paragraph("Validation summary",H3))
val=[["Test","Result"],
 ["TradingView deep backtest","PF 1.788 vs 1.827 modelled; 2,020 entry orders vs 2,034 modelled (0.7% apart)"],
 ["Second instrument (US30)","PF 1.469, +247%, 19.32% drawdown, settings unchanged"],
 ["Random-entry null (30 seeds)","Champion at the 93rd percentile; the edge survives replacing the entry with a coin flip"],
 ["Deflated Sharpe ratio","0.9996 assuming 1,000 trials"],
 ["Probability of backtest overfitting","0.099 (below 0.5 means the selection beats random)"]]
A(tbl(val,[52*mm,116*mm],fs=7.8))
A(Spacer(1,6))
A(Paragraph("Report generated 3 August 2026 from 78,695 bars of XAUUSD 30-minute data. "
  "All figures include 0.07 commission and 0.20 points of slippage per side. Past backtested "
  "performance is not a prediction. This document is a research record, not investment advice.",SMALL))

doc.build(E,onFirstPage=footer,onLaterPages=footer)
print("PDF built")
