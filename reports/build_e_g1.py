import sys, json, numpy as np
sys.path.insert(0,"/home/user/Trade_Cartel")
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, KeepTogether)
O=json.load(open("both.json"))
INK=colors.HexColor("#14213d"); ACC=colors.HexColor("#c1121f"); GOLD=colors.HexColor("#b8860b")
PAPER=colors.HexColor("#faf8f3"); GRN=colors.HexColor("#2d6a4f"); BLU=colors.HexColor("#1d4e89")
GREY=colors.HexColor("#6c757d"); LINE=colors.HexColor("#d8d3c8")
ss=getSampleStyleSheet()
def st(n,**k): return ParagraphStyle(n,parent=ss["Normal"],**k)
H1=st("H1",fontName="Helvetica-Bold",fontSize=19,textColor=INK,leading=22,spaceAfter=2)
SUB=st("SUB",fontName="Helvetica",fontSize=9,textColor=GREY,leading=12,spaceAfter=10)
H2=st("H2",fontName="Helvetica-Bold",fontSize=12,textColor=INK,leading=14,spaceBefore=11,spaceAfter=5)
H3=st("H3",fontName="Helvetica-Bold",fontSize=9.5,textColor=GOLD,leading=12,spaceBefore=7,spaceAfter=3)
BODY=st("BODY",fontName="Helvetica",fontSize=8.8,textColor=INK,leading=12.5,spaceAfter=5)
SMALL=st("SMALL",fontName="Helvetica",fontSize=7.6,textColor=GREY,leading=10,spaceAfter=4)
def tbl(data,widths,align=None,head=True,fs=8):
    cell=ParagraphStyle("c",parent=ss["Normal"],fontName="Helvetica",fontSize=fs,leading=fs+2.6,textColor=INK)
    def wrap(x,r):
        if isinstance(x,str) and r>0 and (len(x)>44 or "<" in x or "&" in x): return Paragraph(x,cell)
        return x
    data=[[wrap(x,r) for x in row] for r,row in enumerate(data)]
    t=Table(data,colWidths=widths,repeatRows=1 if head else 0)
    cm=[("FONT",(0,0),(-1,-1),"Helvetica",fs),("TEXTCOLOR",(0,0),(-1,-1),INK),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),5),
        ("RIGHTPADDING",(0,0),(-1,-1),5),("LINEBELOW",(0,0),(-1,-2),0.4,LINE)]
    if head: cm+=[("FONT",(0,0),(-1,0),"Helvetica-Bold",fs),("BACKGROUND",(0,0),(-1,0),PAPER),
                  ("LINEBELOW",(0,0),(-1,0),0.9,INK)]
    if align:
        for k,a in align.items(): cm.append(("ALIGN",(k,0),(k,-1),a))
    t.setStyle(TableStyle(cm)); return t
def callout(txt,color=ACC):
    t=Table([[Paragraph(txt,BODY)]],colWidths=[168*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PAPER),("LINEBEFORE",(0,0),(0,-1),2.5,color),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t
def footer(c,doc):
    c.saveState(); c.setStrokeColor(LINE); c.setLineWidth(.5); c.line(21*mm,14*mm,189*mm,14*mm)
    c.setFont("Helvetica",6.8); c.setFillColor(GREY)
    c.drawString(21*mm,10*mm,"Gold Trend  |  Config E and Config G1  |  XAUUSD 30m  |  not investment advice")
    c.drawRightString(189*mm,10*mm,f"page {doc.page}"); c.restoreState()
doc=SimpleDocTemplate("Gold_Trend_E_and_G1.pdf",pagesize=A4,leftMargin=21*mm,rightMargin=21*mm,
    topMargin=18*mm,bottomMargin=20*mm,title="Gold Trend - Config E and G1",author="Trade Cartel")
E=[];A=E.append
def f(k,x,d=2,pct=False,sign=False):
    v=O[k][x]
    s=f"{v:+,.{d}f}" if sign else f"{v:,.{d}f}"
    return s+("%" if pct else "")

A(Paragraph("Config E and Config G1",H1))
A(Paragraph("Gold Trend &mdash; two shipped strategies &nbsp;|&nbsp; XAUUSD 30-minute &nbsp;|&nbsp; "
  "tested 1 Dec 2019 &ndash; 30 Jul 2026, 711 positions each",SUB))
A(Paragraph("Headline numbers",H2))
r=[["","E  25% budget","E  20% budget","G1  25% budget","G1  20% budget"],
   ["Risk per trade","0.705%","0.553%","0.723%","0.567%"],
   ["Profit factor",f("E25","pf",3),f("E20","pf",3),f("G125","pf",3),f("G120","pf",3)],
   ["Total return",f("E25","net",0,True,True),f("E20","net",0,True,True),f("G125","net",0,True,True),f("G120","net",0,True,True)],
   ["Max drawdown",f("E25","dd",2,True),f("E20","dd",2,True),f("G125","dd",2,True),f("G120","dd",2,True)],
   ["CAGR",f("E25","cagr",1,True),f("E20","cagr",1,True),f("G125","cagr",1,True),f("G120","cagr",1,True)],
   ["MAR (CAGR/DD)",f("E25","mar"),f("E20","mar"),f("G125","mar"),f("G120","mar")],
   ["Win rate",f("E25","wr",1,True),f("E20","wr",1,True),f("G125","wr",1,True),f("G120","wr",1,True)],
   ["Trades",str(O["E25"]["n"]),str(O["E20"]["n"]),str(O["G125"]["n"]),str(O["G120"]["n"])],
   ["Monte Carlo median DD",f("E25","mc_med",1,True),f("E20","mc_med",1,True),f("G125","mc_med",1,True),f("G120","mc_med",1,True)],
   ["P(drawdown over 30%)",f("E25","p30",1,True),f("E20","p30",1,True),f("G125","p30",1,True),f("G120","p30",1,True)]]
A(tbl(r,[38*mm,32*mm,32*mm,32*mm,32*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"}))
A(Paragraph("Risk per trade is not a preference dial. <b>The drawdown budget is the input and the risk "
  "percentage is the solved output</b> &mdash; whatever value makes the historical maximum drawdown land "
  "on 25% or 20%.",SMALL))
A(Spacer(1,4))
A(Image("b_eq.png",width=168*mm,height=79*mm))
A(PageBreak())

A(Paragraph("Winners versus losers",H2))
A(Image("b_wl.png",width=82*mm,height=58*mm))
r=[["Measure","Config E","Config G1"],
   ["Winning trades",f"{O['E25']['nwin']} ({O['E25']['wr']:.1f}%)",f"{O['G125']['nwin']} ({O['G125']['wr']:.1f}%)"],
   ["Losing trades",str(O["E25"]["nloss"]),str(O["G125"]["nloss"])],
   ["Average WIN",f"+{O['E25']['win_pts']:.1f} pts",f"+{O['G125']['win_pts']:.1f} pts"],
   ["Average LOSS",f"{O['E25']['loss_pts']:.1f} pts",f"{O['G125']['loss_pts']:.1f} pts"],
   ["Win : loss ratio (points)",f"{abs(O['E25']['win_pts']/O['E25']['loss_pts']):.2f} : 1",f"{abs(O['G125']['win_pts']/O['G125']['loss_pts']):.2f} : 1"],
   ["Median win / median loss",f"+{O['E25']['win_med']:.1f} / {O['E25']['loss_med']:.1f} pts",f"+{O['G125']['win_med']:.1f} / {O['G125']['loss_med']:.1f} pts"],
   ["Largest win",f"+{O['E25']['best_pts']:.0f} pts  (${O['E25']['best_usd']:,.0f})",f"+{O['G125']['best_pts']:.0f} pts  (${O['G125']['best_usd']:,.0f})"],
   ["Largest loss",f"{O['E25']['worst_pts']:.0f} pts  (${O['E25']['worst_usd']:,.0f})",f"{O['G125']['worst_pts']:.0f} pts  (${O['G125']['worst_usd']:,.0f})"],
   ["Average hold",f"{O['E25']['hold']:.0f} h",f"{O['G125']['hold']:.0f} h"],
   ["Hold: winners / losers",f"{O['E25']['hold_w']:.0f} h / {O['E25']['hold_l']:.0f} h",f"{O['G125']['hold_w']:.0f} h / {O['G125']['hold_l']:.0f} h"],
   ["Longest losing streak",f"{O['E25']['streak']} trades",f"{O['G125']['streak']} trades"],
   ["Top 10 trades = share of profit",f"{O['E25']['top10']:.1f}%",f"{O['G125']['top10']:.1f}%"]]
A(tbl(r,[56*mm,56*mm,56*mm],{1:"RIGHT",2:"RIGHT"}))
A(callout("<b>You lose roughly four trades out of five.</b> The system works because the average winner is "
  "about 2.4 times the average loser in points, and because position size concentrates in the winners "
  "through pyramiding. <b>Traded at a fixed lot size it loses money</b> &mdash; the adds are not an "
  "enhancement, they are the edge."))
A(PageBreak())
A(Paragraph("Performance by calendar year",H2))
A(Image("b_yr.png",width=168*mm,height=48*mm))
r=[["Year","E profit factor","E net P&L","G1 profit factor","G1 net P&L"]]
for y in sorted(O["E25"]["years"],key=lambda z:int(z)):
    r.append([str(y),f"{O['E25']['years'][y]:.2f}",f"${O['E25']['years_usd'][y]:+,.0f}",
              f"{O['G125']['years'][y]:.2f}",f"${O['G125']['years_usd'][y]:+,.0f}"])
A(tbl(r,[22*mm,36*mm,36*mm,36*mm,36*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"}))
A(Paragraph("2021 is the difficult year for both. At the 20% budget config E returns a flat 0.94 and G1 "
  "0.89 &mdash; neither loses meaningfully, but neither makes money in a year gold fell 4.3%.",SMALL))
A(PageBreak())

A(Paragraph("What each script is, and what changed",H2))
r=[["Component","Setting","Why"],
   ["Entry","Close breaks the 24-bar (12-hour) Donchian extreme, with 21-day EMA, 8-day SMA and 13-day SMA all agreeing. Shorts also need a falling EMA.","unchanged - the entry is worth almost nothing on its own and was never the edge"],
   ["Initial stop","4.24 x ATR(14) - deliberately wide","a tighter stop sits inside the noise the market generates"],
   ["Exit","Chandelier trailing stop, ratchets one way only. No target.","20 target configurations were tested; every one reduced returns"],
   ["Trail tightening","After a 15 ATR favourable run the trail tightens to 2.0 ATR","IMPROVEMENT - cuts give-back on the biggest winners"],
   ["Pyramiding","4 adds, every 1.5 ATR, each sized on the ATR AT ENTRY","IMPROVEMENT - current-ATR sizing shrank the adds exactly when the trade was working"],
   ["Cooldown","30 bars (15 hours) flat after any exit","IMPROVEMENT - a longer wait removes below-average trades"],
   ["Slow SMA","13 days (was 21)","IMPROVEMENT - found on a 6x6 grid where all 36 cells beat the old value"]]
A(tbl(r,[30*mm,74*mm,64*mm],fs=7.6))
A(Paragraph("Config G1 &mdash; the one difference",H3))
A(Paragraph("G1 is config E with a single addition: the risk on a <b>new entry</b> is multiplied by how "
  "far price sits from its regime mean and whether volatility is expanding.",BODY))
r=[["Condition","Multiplier"],
   ["|close &minus; regime EMA| / ATR is above 6.0","x 1.4, else x 0.8"],
   ["SMA(ATR,20) / SMA(ATR,200) is above 1.05","x 1.4, else x 0.6"],
   ["Product, clipped to the range 0.5 to 2.0","the final entry multiplier"],
   ["Pyramid adds","NOT scaled - they stay at base risk"]]
A(tbl(r,[100*mm,68*mm]))
A(Paragraph("Press when the market is both far from its mean and expanding; shrink when it is neither. "
  "The adds are deliberately left unscaled because that is the version that was measured.",SMALL))
A(Spacer(1,3))
A(Image("b_mc.png",width=82*mm,height=58*mm))
A(callout("<b>G1 beats E on every gold metric at both budgets</b> - profit factor, return, MAR, and both "
  "the Monte Carlo median and tail. The effect appears through three unrelated definitions and is a "
  "plateau, not a spike.<br/><br/><b>The qualifier, stated plainly.</b> On US30 with settings unchanged "
  "G1 scores 1.472 against E's 1.469 &mdash; NEUTRAL, not confirmed. Every earlier adopted change showed "
  "a clear gain on the second instrument; this one does not. About 85 configurations were searched to "
  "find a 3% profit-factor gain, close to what noise alone produces at that search count. "
  "<b>Trade E for the settled version; trade G1 if you accept a thinner evidence base.</b>",GOLD))
A(PageBreak())

A(Paragraph("Lot size and account requirements",H2))
px=4081.11; atr=13.17; stop=4.24*atr
A(Paragraph(f"Position size = <b>equity &times; risk% &divide; (4.24 &times; ATR)</b>. At gold ${px:,.0f} "
  f"with a 30-minute ATR of {atr:.2f} points the stop distance is <b>{stop:.1f} points</b>. "
  f"One standard lot is 100 ounces, so 0.01 lots = 1 ounce.",BODY))
r=[["Account","E 0.705%","G1 0.723%","E 20% bud.","Peak stack (4 adds)","Verdict"]]
for eq in (5000,10000,25000,50000,100000):
    e=eq*0.00705/stop; g=eq*0.00723/stop; e20=eq*0.00553/stop
    v=("cannot trade" if e<1 else "works, leaks to rounding" if e<3 else
       "recommended minimum" if eq==25000 else "full fidelity")
    r.append([f"${eq:,}",f"{e:.2f} oz ({e/100:.3f} lot)",f"{g:.2f} oz ({g/100:.3f} lot)",
              f"{e20:.2f} oz",f"{5*e:.1f} oz = ${5*e*px:,.0f}",v])
A(tbl(r,[20*mm,30*mm,30*mm,30*mm,32*mm,26*mm],{1:"RIGHT",2:"RIGHT",3:"RIGHT",4:"RIGHT"},fs=7.3))
A(callout("<b>$25,000 is the recommended minimum</b> and the reason is granularity, not risk. Gold has "
  "tripled since 2019, so a sub-1% risk budget now buys few whole ounces. Tested from today's price "
  "levels: at $5,000 the system takes a small fraction of its signals and loses money; at $25,000 it "
  "takes them all and performs within 2 points of ideal. <b>If your broker supports 0.001 lots or "
  "micro-gold contracts, $10,000 behaves like $50,000</b> and this constraint disappears - check your "
  "broker's minimum trade size before funding more.",GOLD))
A(Paragraph("Margin is not the constraint: the full four-add stack is about 3.65x account leverage, "
  "needing 3.7% of the account at 1:100 or 18.3% at 1:20.",SMALL))

A(Paragraph("How to trade it",H2))
r=[["#","Step"],
   ["1","Chart XAUUSD on the 30-minute. Leave every input at default and pick your drawdown budget. Auto-scale derives all lookbacks from the timeframe."],
   ["2","Set slippage to your broker's REAL gold spread before trusting any figure. The shipped value is 0.20 points per side and break-even is about 1.6 points."],
   ["3","Take every signal. 26.7% of positions produce all of the profit and you cannot know in advance which - skipping trades destroys the system."],
   ["4","Never move the stop closer or take profit manually. The trailing stop is the only exit and the entire edge is in letting winners run."],
   ["5","Let the adds happen. If you cannot pyramid, do not trade this at a fixed lot size - the point average per trade is NEGATIVE without the adds."],
   ["6","Expect to be wrong about four times out of five, and expect a losing run of 20-25 trades at some point. Neither means anything is broken."],
   ["7","Log every trade. After about 50 trades compare your realised win rate and average win/loss against the tables in this document."]]
A(tbl(r,[10*mm,158*mm],fs=8))

A(Paragraph("Risks you must accept",H2))
r=[["Risk","The number"],
   ["Profit concentration",f"The top 10 trades are {O['E25']['top10']:.0f}% of net profit. Removing 20 of 737 trades turns the system into a loser."],
   ["Long losing runs",f"Longest run in the sample: {O['E25']['streak']} consecutive losing positions, at a {O['E25']['wr']:.1f}% win rate."],
   ["Drawdown is understated","A backtest drawdown is a single lucky path. Size for the Monte Carlo median, which is about 1 point worse."],
   ["Execution sensitivity","At 0.50 pt slippage returns fall sharply; at 1.50 pt the system is dead. This is the largest single risk."],
   ["Overnight financing","NOT modelled. Average hold is about 21 hours, so swap costs are real and would reduce every figure here by an estimated 2-8% of equity a year."],
   ["Regime dependence","Gold rose from $1,450 to $4,100 across the test. The system made money in gold's down years, but has never seen a multi-year bear market."],
   ["G1 specifically","Neutral rather than confirmed on a second instrument, and marginally worse in 2021 than config E."]]
A(tbl(r,[38*mm,130*mm],fs=7.8))
A(Spacer(1,5))
A(Paragraph("Generated 4 August 2026 from 78,695 bars of XAUUSD 30-minute data. All figures include "
  "0.07 commission and 0.20 points of slippage per side. Backtested performance is not a prediction. "
  "Research record, not investment advice.",SMALL))
doc.build(E,onFirstPage=footer,onLaterPages=footer)
print("built")
