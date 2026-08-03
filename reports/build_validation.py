import sys, json, numpy as np, pandas as pd
sys.path.insert(0,"/home/user/Trade_Cartel")
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)
from backtest.io import load_csv
from backtest import champion as ch, exit_lab
MC=json.load(open("mc.json"))
gd=load_csv("/home/user/Trade_Cartel/data/xauusd_15m.csv.gz",rule="30min")
B=dict(pyr=dict(pyr_atr=1.5,pyr_max=4,pyr_mode="vol_entry"),cooldown=24,
       lb_over=dict(sma2=630),tighten_after=20,tighten_to=2.0,frac_qty=True)
tr,_=ch.run(gd,**B); d=pd.DataFrame(tr); S=exit_lab.stats(tr)

INK=colors.HexColor("#14213d"); ACC=colors.HexColor("#c1121f")
GOLD=colors.HexColor("#b8860b"); PAPER=colors.HexColor("#faf8f3")
GREEN=colors.HexColor("#2d6a4f"); GREY=colors.HexColor("#6c757d")
LINE=colors.HexColor("#d8d3c8")
ss=getSampleStyleSheet()
def st(n,**k): return ParagraphStyle(n,parent=ss["Normal"],**k)
H1=st("H1",fontName="Helvetica-Bold",fontSize=19,textColor=INK,leading=22,spaceAfter=2)
SUB=st("SUB",fontName="Helvetica",fontSize=9,textColor=GREY,leading=12,spaceAfter=10)
H2=st("H2",fontName="Helvetica-Bold",fontSize=12,textColor=INK,leading=14,spaceBefore=11,spaceAfter=5)
H3=st("H3",fontName="Helvetica-Bold",fontSize=9.5,textColor=GOLD,leading=12,spaceBefore=7,spaceAfter=3)
BODY=st("BODY",fontName="Helvetica",fontSize=8.8,textColor=INK,leading=12.5,spaceAfter=5)
SMALL=st("SMALL",fontName="Helvetica",fontSize=7.6,textColor=GREY,leading=10,spaceAfter=4)

def tbl(data,widths,align=None,head=True,fs=8,rowcol=None):
    cell=ParagraphStyle("cell",parent=ss["Normal"],fontName="Helvetica",
                        fontSize=fs,leading=fs+2.6,textColor=INK)
    data=[[Paragraph(c,cell) if (isinstance(c,str) and len(c)>44 and r>0) else c
           for c in row] for r,row in enumerate(data)]
    t=Table(data,colWidths=widths,repeatRows=1 if head else 0)
    cmds=[("FONT",(0,0),(-1,-1),"Helvetica",fs),("TEXTCOLOR",(0,0),(-1,-1),INK),
          ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
          ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("LINEBELOW",(0,0),(-1,-2),0.4,LINE)]
    if head: cmds+=[("FONT",(0,0),(-1,0),"Helvetica-Bold",fs),
                    ("BACKGROUND",(0,0),(-1,0),PAPER),("LINEBELOW",(0,0),(-1,0),0.9,INK)]
    if align:
        for c,a in align.items(): cmds.append(("ALIGN",(c,0),(c,-1),a))
    if rowcol:
        for r,col in rowcol.items(): cmds.append(("TEXTCOLOR",(0,r),(0,r),col))
    t.setStyle(TableStyle(cmds)); return t

def callout(txt,color=ACC):
    t=Table([[Paragraph(txt,BODY)]],colWidths=[168*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PAPER),
        ("LINEBEFORE",(0,0),(0,-1),2.5,color),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

def footer(c,doc):
    c.saveState(); c.setStrokeColor(LINE); c.setLineWidth(0.5)
    c.line(21*mm,14*mm,189*mm,14*mm); c.setFont("Helvetica",6.8); c.setFillColor(GREY)
    c.drawString(21*mm,10*mm,"Gold Trend - Strategy  |  pre-live validation  |  research record, not investment advice")
    c.drawRightString(189*mm,10*mm,f"page {doc.page}"); c.restoreState()

doc=SimpleDocTemplate("Gold_Trend_Validation_Report.pdf",pagesize=A4,
    leftMargin=21*mm,rightMargin=21*mm,topMargin=18*mm,bottomMargin=20*mm,
    title="Gold Trend - Pre-Live Validation",author="Trade Cartel")
E=[];A=E.append

A(Paragraph("Pre-Live Validation Report",H1))
A(Paragraph("Gold Trend &mdash; Strategy &nbsp;|&nbsp; XAUUSD 30m &nbsp;|&nbsp; eight checks run against "
            "the research engine, 3 August 2026",SUB))

sc=[["#","Check","Result","Verdict"],
 ["1","Buy and hold","+5,922% at 33.80% DD vs gold +179.1% at 29.08% (33x)","PASS"],
 ["2","Long vs short","shorts PF 1.891 vs longs 1.806; 35.1% of net profit","PASS"],
 ["3","Per-year / out-of-sample","train PF 1.351, OOS 2024-26 PF 1.976 at 20.80% DD","PASS*"],
 ["4","Parameter robustness","Donchian flat (+/-3%); trail is a sharp ridge (-19%)","MIXED"],
 ["5","Fill realism","already hardcoded in the script","PASS"],
 ["6","Repaint","no security calls, all lookbacks [1]-offset","PASS"],
 ["7","Sanity: capital / leverage","$25,000 minimum at current gold prices","ACTION"],
 ["8","Monte Carlo (added)","actual 33.80% DD is better than the median reshuffle","CAUTION"]]
A(tbl(sc,[8*mm,44*mm,88*mm,20*mm],{3:"CENTER"},fs=8,
      rowcol={4:ACC,7:GOLD,8:ACC}))
A(Paragraph("*The out-of-sample half is the stronger one, which is the right direction. But every "
            "parameter in this build was selected knowing the full sample, so 2024&ndash;26 is not "
            "virgin data. Deflated Sharpe (0.9996) and probability of backtest overfitting (0.099) "
            "are the defences against that and both pass. Forward performance from today is the only "
            "true out-of-sample this project will ever get.",SMALL))

A(Paragraph("1&ndash;2. Does it beat holding gold, and is the short side worth keeping?",H2))
t1=[["","Net return","Max drawdown","Profit factor"],
    ["Strategy",f"+{S['net_pct']:,.0f}%",f"{S['maxdd_pct']:.2f}%",f"{S['pf']:.3f}"],
    ["Buy and hold gold","+179.1%","29.08%","-"],
    ["Outperformance",f"+{S['net_pct']-179.1:,.0f} pp","","33.1x"]]
A(tbl(t1,[42*mm,42*mm,42*mm,42*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Spacer(1,4))
L=d[d.dir>0]; Sh=d[d.dir<0]
t2=[["Side","Trades","Win rate","Profit factor","Net P&L","Share of profit"]]
for nm,g in (("LONG",L),("SHORT",Sh)):
    w=g[g.pnl>0]; l=g[g.pnl<=0]
    t2.append([nm,f"{len(g)}",f"{100*len(w)/len(g):.1f}%",f"{w.pnl.sum()/-l.pnl.sum():.3f}",
               f"${g.pnl.sum():+,.0f}",f"{100*g.pnl.sum()/d.pnl.sum():.1f}%"])
A(tbl(t2,[24*mm,22*mm,24*mm,28*mm,36*mm,34*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT"}))
A(callout("<b>The short side is the BETTER book, not dead weight.</b> It has a higher profit factor "
  "than the long side (1.891 against 1.806) despite a lower win rate, and supplies just over a third "
  "of net profit. Cutting or shrinking it was tested separately and rejected: it degrades performance "
  "in exactly the two years gold fell, and it is harmful on US30.",GREEN))

A(Paragraph("3. Out-of-sample split",H2))
A(Image("v_oos.png",width=168*mm,height=53*mm))
tr_=gd[(gd.index>="2020-01-01")&(gd.index<"2024-01-01")]; te_=gd[gd.index>="2024-01-01"]
t3=[["Window","Trades","Profit factor","Net return","Max drawdown","CAGR"]]
for sub,lab in ((tr_,"TRAIN 2020-01 to 2023-12"),(te_,"OOS 2024-01 to 2026-07"),(gd,"Full sample")):
    t2_,_=ch.run(sub,**B); s2=exit_lab.stats(t2_)
    y=(sub.index[-1]-sub.index[0]).days/365.25
    t3.append([lab,f"{s2['n']}",f"{s2['pf']:.3f}",f"+{s2['net_pct']:,.1f}%",
               f"{s2['maxdd_pct']:.2f}%",f"{((1+s2['net_pct']/100)**(1/y)-1)*100:.1f}%"])
A(tbl(t3,[48*mm,20*mm,26*mm,30*mm,26*mm,18*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT"}))
A(PageBreak())

A(Paragraph("4. Parameter robustness &mdash; and it is not symmetric",H2))
A(Image("v_robust.png",width=168*mm,height=55*mm))
t4=[["Parameter","Range tested","Profit factor range","Spread","Verdict"],
    ["Donchian length","19 - 29 (24 +/- 20%)","1.781 - 1.859","+/- 3%","flat, safe"],
    ["Trail multiple","3.74 - 4.74 (4.24 +/- 0.5)","1.418 - 1.859","-19% / -12%","sharp ridge"]]
A(tbl(t4,[32*mm,42*mm,36*mm,24*mm,34*mm],{3:"CENTER"}))
A(Spacer(1,3))
t5=[["Trail multiple","3.50","3.74","4.00","4.24","4.50","4.74","5.00"],
    ["PF, coupled"]+[f"{v:.3f}" for v in MC["pf_t"]]]
A(tbl(t5,[30*mm,19*mm,19*mm,19*mm,19*mm,19*mm,19*mm,19*mm],
      {1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT",5:"RIGHT",6:"RIGHT",7:"RIGHT"},fs=7.6))
A(Paragraph("Pinning position size while varying only the trail gives the same shape (1.411 / 1.498 / "
  "1.549 / <b>1.834</b> / 1.768 / 1.631 / 1.618), so this is a genuine ridge and not an artifact of the "
  "trail also setting position size. <b>All 15 tested combinations remain profitable and none inverts</b> "
  "&mdash; the strategy degrades off the peak rather than breaking.",BODY))
A(callout("<b>Practical consequence.</b> The entry length can be wrong by 20% and you would barely "
  "notice. The trail cannot. If your broker's ATR differs from OANDA's &mdash; different feed, different "
  "session boundaries, different spread handling &mdash; the effective trail width shifts and this is "
  "the parameter that will feel it. Verify ATR(14) on your own feed against 13.2 points at gold $4,081 "
  "before trusting the shipped 4.24.",ACC))

A(Paragraph("8. Monte Carlo &mdash; the most useful check on the list",H2))
A(Image("v_mc.png",width=168*mm,height=55*mm))
A(Paragraph("Per-trade returns were resampled as a fraction of equity at the time of each trade. "
  "Shuffling raw dollar P&amp;L would be wrong under compounding &mdash; late trades are roughly forty "
  "times larger than early ones, so a dollar shuffle would simply move the big trades around and "
  "flatter the result.",SMALL))
t6=[["Measure","Actual","Median","95th percentile","Worst of 3,000"],
    ["Max drawdown - order shuffled","33.80%",f"{MC['dds_med']:.1f}%",f"{MC['dds_95']:.1f}%",f"{MC['dds_max']:.1f}%"],
    ["Max drawdown - bootstrapped","33.80%",f"{MC['dds_med']:.1f}%",f"{MC['bdd_95']:.1f}%",f"{MC['bdd_max']:.1f}%"]]
A(tbl(t6,[54*mm,24*mm,24*mm,34*mm,32*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"}))
A(Spacer(1,3))
t7=[["Outcome","Frequency"],
    [f"Reorderings exceeding a 50% drawdown",f"{MC['over50']:.1f}%"],
    [f"Reorderings exceeding a 60% drawdown",f"{MC['over60']:.1f}%"],
    ["Bootstrap runs ending negative","1 in 3,000 (0.03%)"],
    ["Bootstrap net return, 5th percentile","+721%"],
    ["Bootstrap net return, median","+5,913%"]]
A(KeepTogether([tbl(t7,[100*mm,68*mm],{1:"RIGHT"}),Spacer(1,4),
  callout("<b>Your 33.80% drawdown was a fortunate ordering, not a ceiling.</b> The median reshuffle "
  "of the very same trades produces 35.5%, the 95th percentile 49.1%, and the worst 71.2%. "
  "<b>Size the account for a 50% drawdown, not for 33.8%.</b> On $25,000 that is a $12,500 loss to sit "
  "through, not $8,450. Nothing would be broken if it happened &mdash; it is inside the normal range of "
  "this trade distribution.")]))

A(Spacer(1,6))
A(Paragraph("5&ndash;6. Fill realism and repaint",H2))
A(Paragraph("Both were audited in the source rather than by eye. The settings the checklist asks you to "
            "toggle are already fixed in the script.",BODY))
t8=[["Setting","Required","In the script"],
    ["Fill orders on bar close","ON","process_orders_on_close = true  (line 177)"],
    ["Recalculate on every tick","OFF","calc_on_every_tick = false  (line 183)"],
    ["Slippage","broker's real spread","200 ticks = 0.20 points (line 176) - CHANGE THIS"],
    ["Commission","broker's real cost","0.07 per contract (line 163)"],
    ["Bar magnifier","your choice","TradingView-side toggle; recommended ON"]]
A(tbl(t8,[46*mm,40*mm,82*mm]))
A(Paragraph("Repaint audit",H3))
t9=[["Construct","Count","Why it matters"],
    ["request.security","0","no higher-timeframe calls, so no lookahead vector exists"],
    ["barstate.isrealtime / varip / timenow","0","no branch behaves differently in real time"],
    ["ta.highest / ta.lowest","4, all [1]-offset","a bar cannot set the trigger it then crosses"],
    ["chandelier anchor","high[1] / low[1]","a bar cannot move its own stop and then hit it"],
    ["bestPx (excursion tracker)","after strategy.exit","the excursion always reads through the previous bar"]]
A(tbl(t9,[54*mm,32*mm,82*mm],fs=7.8))
A(Paragraph("The only textual match for the word &quot;lookahead&quot; in the file is a comment recording "
  "BUG-019, a defect of this exact kind found and fixed earlier in this project. <b>Nothing in this "
  "script can repaint.</b> If the reload test on TradingView does show changed statistics, the cause is "
  "data revision on your broker's feed, not the code.",BODY))

A(Paragraph("7. Sanity &mdash; capital and leverage",H2))
px=4081.11; atr=13.17; stop=4.24*atr
t10=[["Account","Position (oz)","Peak stack","Notional at peak","Verdict"]]
for eq,v in ((5000,"Broken - takes ~9% of signals"),(10000,"Works, leaks ~1/3 of return"),
             (25000,"Recommended minimum"),(50000,"Full fidelity")):
    oz=eq*0.01/stop
    t10.append([f"${eq:,}",f"{oz:.2f}",f"{5*oz:.2f} oz",f"${5*oz*px:,.0f}",v])
A(tbl(t10,[24*mm,26*mm,26*mm,34*mm,58*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT"}))
A(Paragraph("Peak stack is the position after all four adds, about 3.65x account leverage. At 1:100 "
  "broker leverage that requires 3.7% of the account as margin; at 1:20 it requires 18.3%. Margin is "
  "not the binding constraint &mdash; whole-ounce granularity is.",SMALL))

MANUAL_HEAD=Paragraph("What still has to be done manually on TradingView",H2)
t11=[["Step","Why it cannot be answered here"],
 ["Reload the chart and re-add the strategy; confirm signals and statistics do not change",
  "tests TradingView's own data handling and your broker feed, not the script logic"],
 ["Turn the bar magnifier on and re-run",
  "changes how TradingView resolves intrabar fill order; the research engine models this differently"],
 ["Set initial capital and leverage to match your real account",
  "the shipped $10,000 is a research default, not your position sizing"],
 ["Re-run at your broker's real gold spread",
  "the single largest risk to this strategy; break-even is 1.2-1.5 points"]]
A(KeepTogether([MANUAL_HEAD,tbl(t11,[76*mm,92*mm],fs=7.8),Spacer(1,6),
  Paragraph("Generated 3 August 2026 from 78,695 bars of XAUUSD 30-minute data, 737 positions, "
  "1 Dec 2019 to 30 Jul 2026. All figures include 0.07 commission and 0.20 points of slippage per "
  "side. Past backtested performance is not a prediction. Research record, not investment advice.",SMALL)]))
doc.build(E,onFirstPage=footer,onLaterPages=footer)
print("built")
