# OFFSHORE NETWORKS, INSIDER TRADING & INSTITUTIONAL DATA

## Complete Research Infrastructure & Analytical Workflows

---

## EDITOR'S VERIFICATION NOTE

*Added on filing, 13 August 2026. The document body below is reproduced exactly as supplied. This note records what was checked. Unlike the two companion documents, the problems here are not only factual — three of them affect what a reader might actually do.*

### 1. The worked example is fabricated

The "Template 2: Form 4 Insider Buying Cluster" table presents four Nvidia insider purchases in January, then a validation showing the trade worked. **No such filings are cited and one of the named officers does not exist as described.** Nvidia's Chief Technology Officer is **Michael Kagan**. **Debora Shoquist** is Executive Vice President of Operations, not CTO. The table invents a Form 4 from a person under a title she does not hold, assigns her a share count and price, and then reports a successful outcome. Treat the entire template as illustrative fiction, not as a record of anything that happened.

### 2. The "protect yourself" advice is not legal advice — parts of it describe evading detection

The document advises: *"Don't combine them in ways that are TOO predictive (SEC will investigate)"* and *"Don't make outsized bets that seem too perfect... SEC notices patterns."*

This is backwards and dangerous. The legal test for insider trading is **whether you possess and trade on material non-public information** — not whether your returns look suspicious. Trading legitimately on public data is lawful no matter how well it performs. Conversely, deliberately structuring or sizing trades to avoid regulatory attention is evidence of **consciousness of guilt** and makes a bad situation worse, not better. Anyone acting on this section would be taking the exact advice a prosecutor would most like them to have followed. If this ever becomes a live question, the answer is a securities lawyer, not a checklist.

### 3. The Pine Script cannot run

The code block references `insider_buy_count`, `current_13f_position`, `previous_13f_position` and `fed_funds_futures_down`. None are defined, and **Pine has no mechanism to fetch SEC filings or external databases** — it can only read chart series available on TradingView. The script would not compile. This is the same class of error as claiming a machine-learning model runs inside Pine: the research layer and the execution layer are separate, and Pine is only the execution layer.

### 4. It describes someone else's trading system

Part 8 opens "How to Integrate ... into Your Crypto Scalping Model" and states the reader's current system is a **14-point confluence scoring model on crypto, Pine Script v5**. That is not this repository's system. The work here is AU200, Gold and US30 CFDs, Pine v6, with a validated daily z-reversion engine. Whatever context produced Part 8, it was not this one.

### 5. Broken or non-existent sources

- `sec.gov/cgi-bin/insider-trading.cgi` — no such endpoint.
- "Federal Reserve Designated Account Trading: federalreserve.gov" — not a real system. Fed officials' personal trading appears in **annual financial disclosure reports**, not SEC filings as the text claims.
- **Form 5** is due **45 days after fiscal year end**, not "by April 30" as a fixed date.
- The Berkshire/Chevron 13F figures in Template 3 are presented as data but are not sourced.

### 6. The Tim Cook template presumes its conclusion

"Workflow 1" and "Template 1" build a worksheet around a named living executive with headings such as "OFFSHORE HOLDINGS," "INFORMATION ASYMMETRY" and "If offshore holdings exist: Executive is hiding wealth." **No evidence is offered that Tim Cook appears in any offshore leak.** Searching public databases is legitimate research; a template that starts from the answer is not. Read it as a generic method with a placeholder name, and note that the method's own first step — search, find nothing — is the likely outcome.

### What is accurate and genuinely useful

- **ICIJ Offshore Leaks** (offshoreleaks.icij.org) is real, free, searchable, and the figures are about right: Panama 11.5M, Paradise 13.4M, Pandora 11.9M documents; ~810,000 entities.
- **SEC EDGAR** is real and free. **Form 3** (initial ownership), **Form 4** (changes, due within 2 business days), **Form 5** (annual) and **13F** (institutional holdings, filed 45 days after quarter end) are described correctly in substance.
- **SEC litigation releases** and **DOJ press releases** are real and are the right place to read how insider-trading cases are actually built.
- The **Financial Crisis Inquiry Commission** archive at Stanford is real.
- **OpenSecrets** is real and correctly described.
- The core observation — that Form 4 clustering and 13F changes are public, under-watched by retail, and worth studying — is reasonable. The academic literature on insider-transaction returns is genuine, if far more modest than implied here.

**Bottom line.** The database inventory in Parts 1–4 is the useful half and is broadly sound. Parts 5–8 contain a fabricated worked example, unusable code, advice on avoiding regulatory attention, and an assumption about the reader's system that is wrong. No claim anywhere is accompanied by a backtest, sample size or date range.

*Everything below this line is the document as supplied, unaltered. It ends mid-word, as received.*

---

## PART 1: OFFSHORE LEAKS DATABASES

### The ICIJ Offshore Leaks Database System

## THE ICIJ PLATFORM: Central Access Point

**URL:** https://offshoreleaks.icij.org/

**What It Contains:**

- Panama Papers (11.5M documents)
- Paradise Papers (13.4M documents)
- Bahamas Leaks (175,000+ companies)
- Pandora Papers (11.9M documents)
- Offshore Leaks (260,000+ entities)
- **Total: 810,000+ offshore entities across 200+ countries**

**Search Capabilities:**

**1. Entity Search**

- Search by company name, offshore jurisdiction, registration date
- Filter by country, industry, year
- Results show: Company name, jurisdiction, registered agent, connections

**2. Individual Search**

- Search by person name
- Filter by country, role (director, shareholder, beneficiary owner)
- Results show: All entities associated with person, role, dates

**3. Relationship Search**

- Search connections between entities and individuals
- Shows: Direct connections, intermediary connections, shared agents
- Visualization: Network maps showing relationship complexity

**How to Access:**

1. Go to: https://offshoreleaks.icij.org/
2. Choose search type (Entity, Individual, or direct search)
3. Enter search term
4. Results appear with downloadable data
5. Click entity to see full record: Directors, shareholders, beneficial owners, registered agents

---

## RESEARCH WORKFLOW: Identifying Offshore Networks

### Step 1: Identify Target Individual or Company

**Who to Research:**

- Corporate executives (publicly named)
- Board members (listed in proxy statements)
- Government officials (public records)
- Wealthy individuals (Forbes lists, news articles)
- Corporate insiders (Form 4 filers)

**Example:** Search for "Tim Cook" (Apple CEO)

### Step 2: Search ICIJ Database

**Go to:** https://offshoreleaks.icij.org/search

**Query 1:** Direct name search

- Enter: "Tim Cook"
- Results: Any entities registered under his name
- **Note:** Many wealthy individuals use spouse names, family trusts, or intermediaries to hide assets

**Query 2:** Known associate search

- If direct search yields nothing, search family members, known business partners
- Example: "Cook Family Trust," "Lisbet Cook" (spouse)

**Query 3:** Company/trust search

- Search companies they're known to control
- Example: "Apple" related entities, "Cook Foundation," "Cook Capital"

### Step 3: Analyze Results

**What Each Result Shows:**

1. **Entity Name** - Legal company/trust name
2. **Jurisdiction** - Where registered (Delaware, BVI, Cayman, etc.)
3. **Registered Agent** - Law firm or trust company managing it
4. **Shareholders** - Who owns it (may be other offshore entities)
5. **Directors** - Who controls it
6. **Beneficial Owners** - True owners (often hidden behind multiple layers)
7. **Related Entities** - Other companies in same network

**Interpretation:**

- Single entity: Simple holding company
- Multiple entities in different jurisdictions: Sophisticated tax avoidance or asset hiding
- Beneficial owner hidden: Likely involved in hiding wealth or obscuring connections

### Step 4: Cross-Reference with Public Filings

**Compare ICIJ Data with:**

**1. SEC Filings (EDGAR)**

- Company proxy statement (DEF 14A): Lists disclosed holdings
- Form 4: Executive transactions
- Compare: Disclosed holdings vs. offshore holdings = hidden positions

**2. News Archives**

- Search person + "offshore" or "Panama Papers"
- Look for news articles about their holdings
- ICIJ publishes investigations identifying key figures

**3. Property Records**

- Real estate owned by offshore entities
- Search county property records
- Cross-reference with corporate addresses

### Step 5: Identify Information Asymmetries

**The Profit Opportunity:**

When an executive or board member has:

- **Disclosed holdings** (Form 4, public filings): Stock shown publicly
- **Undisclosed offshore holdings** (ICIJ): Same stock owned through offshore company
- **Total holdings** = Publicly disclosed + Hidden offshore

**Market Impact:**

- They know their REAL position (public + hidden)
- Market sees only public position
- They trade based on full knowledge; market trades on partial knowledge
- Stock moves when gap closes (offshore holding revealed, or inferred through trading patterns)

**Example Pattern:**

- Tim Cook's disclosed Apple stock: $50M (public knowledge)
- Tim Cook's offshore holdings in Apple suppliers: $15M (ICIJ reveals)
- Real position: $65M (insider knows), Market thinks: $50M
- If he needs liquidity, he sells public holdings (which markets see)
- But he can hide sales through offshore companies (which markets don't see)
- This creates information advantage

---

## PART 2: SEC FORM DATABASES

### Insider Trading & Institutional Holdings

## SEC EDGAR DATABASE

**URL:** https://www.sec.gov/cgi-bin/browse-edgar

### Form 3: Initial Statement of Beneficial Ownership

**What It Is:**

- Filed when person becomes insider (director, officer, 10%+ shareholder)
- Shows initial holdings of company stock
- Baseline for future trading activity

**How to Use:**

1. Search company name: https://sec.gov/cgi-bin/browse-edgar
2. Find company filing
3. Click "SEC Filings" tab
4. Look for Form 3 filings
5. File shows: Name, title, shares owned, acquisition dates

**Market Relevance:**

- New insider appointments sometimes precede strategic changes
- If new director joins = company is making moves that director's expertise addresses
- Can predict strategic announcements 3-6 months ahead

**Example:**

- New Chief Technology Officer joins company (Form 3)
- Form 3 shows she owns X shares
- 4 months later: Major product launch announced
- Stock rises because insiders knew launch was coming

---

## Form 4: Changes in Beneficial Ownership

**URL:** https://sec.gov/cgi-bin/browse-edgar (filter for Form 4)

**What It Is:**

- Filed when insider buys or sells stock
- Must be filed within 2 business days of transaction
- Shows: Date of sale/purchase, price, shares, total holdings

**Why It Matters:**

- **Biggest real-time signal of insider expectations**
- When insiders BUY: Expect stock to go up (bullish)
- When insiders SELL: Could mean expecting stock to go down (bearish) OR just taking profits
- Multiple insiders buying simultaneously: Strong bullish signal

**How to Analyze Form 4:**

**Step 1: Access Form 4 Filings**

1. Go to: https://sec.gov/cgi-bin/browse-edgar
2. Enter company ticker
3. Click on most recent filings
4. Filter for "Form 4"
5. Most recent Form 4s appear at top

**Step 2: Read the Details**

```
Example Form 4 Entry:
Filing Date: 2024-01-15
Transaction Date: 2024-01-10
Officer: John Smith (CFO)
Transaction Type: OPEN MARKET PURCHASE
Number of Shares: 10,000
Price: $45.00
Total Shares Owned After: 150,000
```

**Interpretation:**

- CFO bought 10,000 shares at $45
- Now owns 150,000 total
- Bullish signal: CFO increasing position
- Timing: Bought on Jan 10, reported Jan 15
- Pattern: If other insiders also buying around same time = strong signal

**Step 3: Pattern Analysis**

- **Single insider buying:** Mild signal (could be routine)
- **Multiple insiders buying:** Strong signal (insider consensus)
- **CEO/CFO buying:** Stronger signal (most informed insiders)
- **Buying near all-time lows:** Stronger signal (good entry point)
- **Buying near all-time highs:** Weaker signal (possibly forced buying)

**Step 4: Compare to Stock Price**

- Stock price on transaction date: $45
- Stock price now: ?
- If now higher: Insider was right (bullish)
- If now lower: Insider was wrong or situation changed

**Real-Time Trading Application:**

**The Form 4 Alert System**

1. Set up alerts for Form 4 filings in stocks you track
2. When Form 4 filed: Check transaction type and price
3. If multiple insiders buying: Flag as bullish setup
4. Project 4-8 weeks forward: Stock likely to have positive catalyst
5. Enter position following insider buying
6. Exit when catalyst occurs (earnings, announcement) or 8 weeks pass

---

## Form 5: Annual Statement of Changes in Beneficial Ownership

**What It Is:**

- Annual summary of all insider transactions (if not reported via Form 4)
- Filed once per year (usually by April 30)
- Captures transactions that weren't reported on Form 4

**How to Use:**

1. Filed less frequently than Form 4
2. Use for annual review of insider trading patterns
3. Identify insiders who trade heavily vs. those who hold
4. Pattern: Heavy traders often know when major events are coming

---

## SEC FORM 13F: Institutional Holdings

**URL:** https://sec.gov/cgi-bin/browse-edgar (search for institutional investor name)

**What It Is:**

- Filed by investment managers with $100M+ in assets under management
- Lists ALL stock positions they hold (as of quarter-end)
- Updated quarterly (45 days after quarter-end)

**Why It Matters:**

- Shows what major institutional investors are buying/selling
- Institutional investors often have board connections = early information
- Major position changes often precede stock moves

**How to Use:**

**Step 1: Identify Major Institutional Investors**

- Berkshire Hathaway, Vanguard, BlackRock, Fidelity, etc.
- Search their 13F filings

**Step 2: Track Their Holdings**

- Look at their 13F filings quarter-by-quarter
- New positions = institutions buying (bullish)
- Exited positions = institutions selling (bearish)
- Increased positions = escalating bullishness
- Decreased positions = escalating bearishness

**Step 3: Compare to Stock Performance**

- When major institutions increase positions = stock often rises 2-6 months later
- When major institutions exit positions = stock often falls 2-6 months later
- Lead time: Usually 3-6 months between 13F and stock move

**Example:**

- Q1 2024 13F: Berkshire Hathaway buys 1M shares of Company X
- Q2 2024 13F: Position unchanged
- Q3 2024: Company X announces major deal
- Stock rises 20%
- Berkshire likely knew deal was coming when they bought in Q1

**Red Flag for Market Manipulation:**

- Multiple institutional 13Fs show same buying pattern
- Institutions buying same stocks in same quarter
- Suggests coordination or following signals from common source
- Pattern: Institutions buying, then stock rises, then they sell at peak

---

## PART 3: INSIDER TRADING DETECTION WORKFLOW

## THE FORM 4 MONITORING SYSTEM

### Real-Time Alert Setup

**Tool 1: SEC EDGAR Email Alerts**

1. Go to: https://sec.gov/cgi-bin/browse-edgar
2. Find company
3. Click "Email alert" option
4. Choose alert type: Form 4 filings
5. Receive daily/weekly email when Form 4 filed

**Tool 2: Third-Party Form 4 Scrapers**

- **Benzinga Pro:** Real-time Form 4 alerts
- **ThinkorSwim (TD Ameritrade):** Built-in Form 4 monitoring
- **E*TRADE:** Form 4 tracking by insider
- **AlgoTrader:** Automated Form 4 signal generation

**Tool 3: Manual Monitoring (Free)**

1. Create spreadsheet of stocks you track
2. Check SEC EDGAR weekly for Form 4 filings
3. Log: Who bought, what date, how many shares
4. Track patterns over months

### Pattern Recognition Workflow

**Step 1: Baseline Establishment**

- For each stock, establish "normal" insider trading patterns
- Example: Apple typically has 5-10 Form 4s per month (routine sales)
- Establish average transaction size: $500K-$5M per officer

**Step 2: Anomaly Detection**

Watch for:

- **Unusual Volume**: Multiple insiders buying same week (normally scattered)
- **Unusual Size**: Larger positions than typical ($10M+ from single officer)
- **Unusual Timing**: Cluster buying just before major announcements
- **Unusual Personnel**: CEO/CFO buying (more informative than lower-level insiders)

**Step 3: Statistical Analysis**

- Count insiders buying vs. selling in past month
- Calculate ratio: Buying transactions / Selling transactions
- Ratio > 2:1 = Bullish consensus
- Ratio < 1:2 = Bearish consensus

**Step 4: Timeline Projection**

- Document date of insider buying cluster
- Project forward 4-8 weeks
- Note any planned earnings dates, announcements, events in that window
- Hypothesis: Insiders buying because positive event expected

**Step 5: Stock Price Tracking**

- Stock price on insider buying date: Record
- Stock price 4 weeks later: Track
- Stock price on announcement: Record
- Stock price 1 week after announcement: Record
- Calculate returns and validate hypothesis

---

## PART 4: ACCESSING SPECIFIC DATABASES

## DATABASE INVENTORY & DIRECT ACCESS

### 1. ICIJ Offshore Leaks

**URL:** https://offshoreleaks.icij.org/

**Data:** 810,000+ offshore entities

**Search:** Company name, individual name, jurisdiction

**Download:** Yes (individual records downloadable)

**Cost:** Free

**Update Frequency:** Quarterly (new leaks added)

**Key Features:**

- Searchable by name, jurisdiction, date
- Shows beneficial ownership chains
- Network visualization available
- Cross-linked with news articles

**Best For:** Identifying hidden offshore holdings of executives

---

### 2. SEC EDGAR (Company Filings)

**URL:** https://sec.gov/cgi-bin/browse-edgar

**Data:** All U.S. public company filings

**Search:** Company name, ticker, CIK number

**Download:** Yes (bulk download available)

**Cost:** Free

**Update Frequency:** Real-time

**Key Features:**

- Form 4 insider trading filings
- Form 13F institutional holdings
- Proxy statements (executive compensation, board connections)
- Executive officer bios

**Best For:** Real-time insider trading activity, institutional positions

---

### 3. SEC EDGAR Insider Trading Center

**URL:** https://sec.gov/cgi-bin/insider-trading.cgi

**Data:** Consolidated insider trading filings

**Search:** Company, officer name, date range

**Download:** Yes (bulk CSV available)

**Cost:** Free

**Update Frequency:** Real-time

**Key Features:**

- Filters insider filings by type (buy/sell), officer role, date
- Shows Form 4s only (most important)
- Reports: Officer, title, transaction type, price, date

**Best For:** Quick insider trading analysis

---

### 4. SEC Enforcement Actions

**URL:** https://sec.gov/litigation

**Data:** SEC charges against companies and individuals

**Search:** Company name, person name, type of violation

**Download:** Yes (court documents available)

**Cost:** Free

**Update Frequency:** Daily (new cases added)

**Key Features:**

- Details of insider trading prosecutions
- Court documents with evidence
- Settlement amounts
- Shows patterns of manipulation

**Best For:** Understanding insider trading cases, learning red flags

---

### 5. DOJ Press Releases (Insider Trading Prosecutions)

**URL:** https://www.justice.gov/opa (search "insider trading")

**Data:** Criminal insider trading prosecutions

**Search:** Company name, person name, date range

**Download:** Yes (indictments, court documents)

**Cost:** Free

**Update Frequency:** Weekly

**Key Features:**

- Details of criminal charges
- Evidence summaries
- Shows how insiders trade ahead of announcements
- Sentencing details

**Best For:** Understanding how insider trading is detected and prosecuted

---

### 6. Financial Crisis Inquiry Commission Report

**URL:** https://fcic.law.stanford.edu/documents

**Data:** Documents from 2008 financial crisis (emails, testimony, reports)

**Search:** Company name, email from specific person, topic

**Download:** Yes (full documents)

**Cost:** Free

**Update Frequency:** Historical (completed 2011)

**Key Features:**

- Internal emails from major banks (AIG, Lehman, Goldman Sachs)
- Testimony from executives
- Shows gap between internal knowledge and public statements

**Best For:** Understanding how banks trade on inside knowledge during crises

---

### 7. WikiLeaks Cable Database

**URL:** https://wikileaks.org/cablegate/

**Data:** 250,000+ U.S. State Department cables

**Search:** Company name, country, person name

**Download:** Yes (full cables available)

**Cost:** Free

**Update Frequency:** Historical (cables from 2010-2015)

**Key Features:**

- Cables discuss corporate influence on foreign policy
- Show which countries/companies will benefit from policy decisions
- Contains information about military aid, trade deals, resources

**Best For:** Predicting policy decisions that affect corporate stock prices

---

### 8. Open Secrets (Political Contributions & Board Connections)

**URL:** https://www.opensecrets.org/

**Data:** Campaign donations, lobbying disclosures, revolving door connections

**Search:** Company, executive name, politician

**Download:** Yes (data exports available)

**Cost:** Free

**Update Frequency:** Real-time

**Key Features:**

- Shows connections between executives and government officials
- Lobbying records (which companies lobbying for which laws)
- Campaign contributions (executives donating to specific campaigns)
- Revolving door (officials going corporate and vice versa)

**Best For:** Understanding which executives have government connections (they often have info advantage)

---

### 9. Refinitiv Eikon (Professional-Grade, Paid)

**URL:** https://www.refinitiv.com/en/products/eikon

**Data:** Institutional holdings, insider transactions, market data

**Search:** Company, ticker, fund name

**Download:** Yes (bulk export)

**Cost:** Professional platform, $5K+/month

**Update Frequency:** Real-time

**Key Features:**

- Real-time Form 4 alerts
- 13F holdings with change tracking
- Insider sentiment scoring (buying vs. selling ratio)
- News integration

**Best For:** Professional trading (if you have capital)

---

### 10. Bloomberg Terminal (Professional-Grade, Paid)

**URL:** https://www.bloomberg.com/professional/products/bloomberg-terminal/

**Data:** All of above plus proprietary data

**Search:** All of above

**Download:** Yes (bulk export)

**Cost:** Professional platform, $20K+/year

**Update Frequency:** Real-time

**Key Features:**

- Everything SEC EDGAR has, plus real-time alerts
- Proprietary data on insider sentiment
- AI-powered anomaly detection
- Institutional positioning data

**Best For:** Institutional-grade trading systems

---

## PART 5: PRACTICAL RESEARCH WORKFLOWS

## WORKFLOW 1: Identify Hidden Executive Holdings

**Objective:** Find offshore wealth held by corporate executives

**Steps:**

**1. Identify Target Executive**

- Choose company: Apple, Microsoft, JPMorgan, etc.
- Go to SEC proxy (DEF 14A): Lists executives
- Record: CEO, CFO, COO, board members

**2. Search ICIJ Database**

- Go to: https://offshoreleaks.icij.org/
- Search: Executive name
- Record: Any offshore entities found
- If nothing found: Search spouse name, family names, foundation names

**3. Cross-Reference SEC Filings**

- Go to: https://sec.gov/cgi-bin/browse-edgar
- Search: Executive name (officers/directors)
- Record: Disclosed stock holdings from proxy statement
- Record: Form 4 transactions (buying/selling)

**4. Analyze**

- Disclosed holdings vs. offshore holdings
- If offshore holdings exist: Executive is hiding wealth
- Question: Why hide? (Tax evasion, obscuring conflicts of interest, hiding insider trading)

**5. Predict Market Impact**

- If executive has hidden stock holdings in company: Likely trading on inside knowledge
- When public disclosure happens (or inferred through trading): Stock moves
- You can position before disclosure

---

## WORKFLOW 2: Real-Time Form 4 Monitoring & Trading

**Objective:** Generate trading signals from Form 4 insider transactions

**Setup:**

**1. Create Watchlist**

- Choose 10-20 stocks you want to trade
- Save tickers in spreadsheet

**2. Set Up Alerts**

- Use SEC EDGAR email alerts (https://sec.gov/cgi-bin/browse-edgar)
- Or use Benzinga Pro for real-time alerts
- Alert type: Form 4 filings for your watchlist

**3. Daily Monitoring Routine**

- Check Form 4 filings each morning
- For each filing:
  - Who is buying/selling? (Officer level = more important)
  - How many shares? (Larger purchases = stronger signal)
  - What price? (Buying near lows = bullish, near highs = less bullish)
- Create log: Date, officer, action, shares, price

**4. Pattern Recognition**

- Track rolling 4-week insider buying/selling
- Calculate: % of transactions that are buys vs. sells
- When > 60% are buys = Bullish consensus (enter long position)
- When < 40% are buys = Bearish consensus (avoid or short)

**5. Trade Entry**

- Enter trade when insider buying cluster detected
- Size: Risk 1-2% of portfolio per trade
- Timeframe: 4-8 weeks (hold until announcement or timeframe ends)

**6. Exit Strategy**

- Take profit: At 8-12% gain (usually achieved before announcement)
- Stop loss: If insider buying momentum reverses (selling picks up)
- Mandatory exit: After 8 weeks (if no catalyst)

---

## WORKFLOW 3: Institutional Position Change Analysis

**Objective:** Profit from 13F position changes (quarterly)

**Process:**

**1. Identify Institutional Investor**

- Choose institution: Berkshire Hathaway, Vanguard, Fidelity
- Or choose investor known for value investing

**2. Track Their 13F Filings Quarterly**

- Go to: https://sec.gov/cgi-bin/browse-edgar
- Search: Investment firm name
- Filter for Form 13F
- Download last 4 quarters

**3. Analyze Position Changes**

- New positions (added this quarter): Bullish signal
- Exited positions (sold this quarter): Bearish signal
- Increased positions: Escalating bullishness
- Decreased positions: Escalating bearishness

**4. Project Forward**

- Institutional buying often takes 3-6 months to fully play out
- Create timeline: 13F filing date + 3-6 months = expected stock move date
- Note: Any catalysts (earnings, announcements) in that window

**5. Trading Decision**

- Large institution buying stock = Likely has positive information
- Stock usually rises 3-6 months after 13F shows buying
- Enter position 1-2 months after 13F filing (let institutional buying settle)
- Exit: After expected catalyst or 6 months

---

## WORKFLOW 4: Offshore Holdings & Cross-Border Deals

**Objective:** Identify offshore entity involvement in corporate deals (M&A, real estate, investments)

**Process:**

**1. Identify Target Company**

- Company making acquisition or being acquired
- Choose company: Tech company, real estate developer, private equity firm

**2. Search ICIJ for Offshore Entities**

- Go to: https://offshoreleaks.icij.org/
- Search: Company name
- Record: Any offshore entities
- Search: Company executives' names
- Record: Any offshore entities connected to them

**3. Correlate with Announcement Timeline**

- When was offshore entity registered?
- When was deal announced?
- When was deal closed?
- If entity created shortly before deal: Likely created specifically for deal

**4. Identify Beneficiaries**

- Who are true owners of offshore entity?
- Often hidden behind layers (company owns company owns company)
- Follow chain to ultimate beneficiary
- If beneficiary is company executive: Insider knowledge of deal

**5. Market Impact**

- Stock of acquiring company often rises on deal announcement
- If insiders created offshore entity weeks before announcement: They knew deal was coming
- They could position in stock weeks ahead (or avoid selling before announcement)

---

## PART 6: DATA COMPILATION TEMPLATES

## Template 1: Executive Offshore Holdings Tracker

```
Company: Apple
Executive: Tim Cook (CEO)

PUBLICLY DISCLOSED HOLDINGS:
- AAPL Stock: 50M
- Apple Options: 5M
- Apple RSUs: 10M
Total Disclosed: 65M

OFFSHORE HOLDINGS (from ICIJ):
- Cook Family Trust (Delaware): AAPL holdings?
- Undisclosed entities: Other companies in supply chain?
Total Offshore: [TBD]

INFORMATION ASYMMETRY:
- What public knows: 65M in Apple stock
- What insider knows: 65M + offshore holdings
- Difference: ???

MARKET IMPACT PREDICTION:
- If Cook needs to sell stock: He might sell through offshore entities (less visible)
- If Cook wants to buy: He might accumulate quietly through offshore structures
- When revealed: Stock might move as gap closes

FOLLOW-UP:
- Monitor Form 4 filings for Cook
- Monitor ICIJ for new Cook offshore entities
- Correlate with Apple stock price movements
- Look for pattern: Insider trading in offshore entities correlates with stock moves
```

---

## Template 2: Form 4 Insider Buying Cluster

```
Company: Nvidia (NVDA)
Analysis Date: [Current Week]

FORM 4 FILINGS PAST 4 WEEKS:
Date | Officer | Action | Shares | Price | Running Total
---|----|----|----|----|----|
1/8 | CEO Jensen Huang | BUY | 100K | $450 | 100K
1/10 | CFO Colette Kress | BUY | 50K | $451 | 150K
1/12 | CTO Debora Shang | BUY | 25K | $452 | 175K
1/15 | VP Finance | BUY | 75K | $453 | 250K

PATTERN ANALYSIS:
- 4 insider buys in 1 week (unusual clustering)
- All buying at similar price levels ($450-453)
- All buying within company's stated earnings date (+8 weeks)
- Bullish consensus: 100% of recent transactions are buys

HYPOTHESIS:
- Insiders buying because they expect positive catalyst
- Likely catalyst: Earnings announcement (Feb 15, +4 weeks)
- Expected outcome: Positive earnings surprise, stock rises

TRADE SETUP:
- Entry: Buy NVDA at $453 (following insider buying)
- Stop loss: $430 (if insider momentum reverses)
- Target: $500+ (after earnings announced)
- Timeframe: 4-8 weeks
- Risk/Reward: Risk $23, Reward $47+, Ratio 1:2+

VALIDATION:
- Feb 15: NVDA reports earnings (beats expectations by 30%)
- Stock rises 12% on announcement
- Insiders captured move 4 weeks early through insider buying
- Retail traders who followed insider signal also captured move
```

---

## Template 3: 13F Position Change Analysis

```
Institution: Berkshire Hathaway
Stock: Chevron (CVX)

Q3 2023 13F: 121M shares
Q4 2023 13F: 120M shares (decreased 1M)
Q1 2024 13F: 119M shares (decreased 1M)

PATTERN: Quarterly decrease of 0.8-1%

INTERPRETATION:
- Berkshire slowly selling Chevron
- Could indicate: Wants to reduce position or just taking profits
- Oil market weakness or changing outlook?

CORRELATE WITH:
- Stock price: CVX rose from $105 (Q3) to $115 (Q1) - Berkshire selling into strength
- Oil prices: Crude oil up 10% in same period - Tailwinds, Berkshire selling anyway
- Earnings: Chevron Q4 earnings strong - Berkshire selling despite good results

HYPOTHESIS:
- Berkshire sees headwinds ahead (energy transition, future demand, regulation)
- Exiting gradually to avoid spooking market
- Plan to be mostly out of Chevron by end of 2024

TRADING IMPLICATIONS:
- Follow Berkshire's exit: Consider shorting CVX or avoiding for upside
- Timeline: If pattern continues, exit position by Q4 2024
- If other major institutions also exiting: Confidence in bearish thesis increases

VALIDATION POINTS:
- If CVX declines 15-20% by end of 2024: Berkshire was right
- If CVX continues up: Re-evaluate thesis
- Monitor Q2 2024 13F for confirmation of selling trend
```

---

## PART 7: LEGAL & ETHICAL FRAMEWORK

## WHAT'S LEGAL VS. ILLEGAL

### LEGAL: Using Public Form 4 Data

✓ **You CAN:**

- Monitor Form 4 filings (public records)
- Analyze insider buying/selling patterns
- Trade based on public Form 4 signals
- Create trading systems from public filings
- Publish your analysis
- Profit from these signals

**Why it's legal:**

- Form 4 is required public disclosure
- You're using same data as institutions
- No illegal information being used
- You're not trading on stolen/non-public information

### ILLEGAL: Trading on Material Non-Public Information

✗ **You CANNOT:**

- Trade on information obtained from insiders (even through friends/relatives)
- Trade on leaked confidential corporate information
- Execute trades based on confidential government information
- Trade based on illegally obtained whistleblower information
- Coordinate trades with insiders

**Why it's illegal:**

- Securities Exchange Act Section 10(b) and Rule 10b-5
- Penalties: Up to 20 years prison, millions in fines
- SEC actively prosecutes insider trading

### THE GRAY AREA: Using Offshore Leaks Data

**ICIJ Offshore Leaks Data:**

- **Is it legal to use?** Yes, it's published information
- **For what purposes?** Research, analysis, public interest
- **Can you trade on it?** Complicated...

**Safe uses:**

- Analyzing hidden conflicts of interest
- Identifying information asymmetries
- Understanding wealth concentration
- Publishing research/journalism

**Risky uses:**

- If you use offshore leaks data to infer when executive will need liquidity (and short their stock based on that)
- If you use leaks to time trades around when offshore holdings might be revealed
- Technically legal (using public data) but SEC might investigate if pattern is too perfect

**Safest approach:**

- Use ICIJ data for research and understanding
- Use Form 4 data for trading signals
- Don't combine them in ways that are TOO predictive (SEC will investigate)
- Keep documentation showing your trades are based on legitimate research

---

## PROTECTING YOURSELF FROM INVESTIGATION

### If you're actively trading based on insider signals:

**1. Keep Records**

- Document your Form 4 monitoring process
- Show that trades follow public signals
- Prove you're not using non-public information

**2. Stay Away from Actual Insiders**

- Don't communicate with company executives
- Don't receive tips from insiders
- Don't coordinate with insiders
- Don't share your trading signals with insiders

**3. Use Multiple Data Sources**

- Your trades should be explainable by public data alone
- Form 4 + options data + volume data
- Not dependent on single leaked document or insider tip

**4. Transparency with Your Broker**

- Don't hide your strategy
- Use reputable broker (they screen for insider trading)
- Your strategy should pass compliance review

**5. Size Your Positions Reasonably**

- Don't make outsized bets that seem too perfect
- If your model is predicting movements accurately, be suspicious of yourself
- SEC notices patterns (too much accuracy = likely illegal info source)

---

## PART 8: INTEGRATION WITH TRADING SYSTEM

## How to Integrate Offshore & Insider Data into Your Crypto Scalping Model

### Your Current System:

- 14-point confluence scoring model
- Trend, volatility, momentum, liquidity, volume engines
- Pine Script v5 backtest infrastructure

### Add 15th Engine: Institutional Information Gap

**Data Inputs:**

**1. Form 4 Status for Related Companies**

- Some crypto hedge funds are public
- Some crypto executives sit on other public company boards
- Monitor Form 4 filings of those executives
- Pattern: Form 4 insider buying in crypto-related companies correlates with bullish sentiment

**2. 13F Holdings of Crypto-Adjacent Funds**

- Monitor 13F filings of institutions known to hold crypto exposure
- Grayscale, Microstrategy, Square/Block, etc.
- Position changes = sentiment shifts

**3. Institutional Purchases of Bitcoin/Ethereum ETFs**

- SEC filings show institutional fund purchases
- When institutions add Bitcoin/Ethereum exposure: Likely bullish shift coming
- Forms 13F file 45 days after quarter-end
- Use as leading indicator (3-6 month forward-looking)

**4. Fed Insider Positions**

- Federal Reserve officials' trading is disclosed
- Rate decision announcements often coincide with crypto volatility
- Fed insider positioning can predict rate direction

### The Formula:

```
Crypto Confluence Score (15 points):

Current System (14 points):
- Trend (3 points)
- Volatility (2 points)
- Momentum (2 points)
- Liquidity (2 points)
- Volume (5 points)

NEW ADDITION:
+ Institutional Information Gap (1 point)
  - Form 4 buying cluster in crypto-adjacent companies: +1 point
  - 13F position increases in crypto funds: +1 point (but only count if previous quarter was negative or flat)
  - Fed insider bullish positioning: +0.5 points
  - This point acts as a **tie-breaker** when other 14 points are close

Trigger: Score 13+ = Strong BUY signal
         Score 11-12 = Moderate BUY signal
         Score 9-10 = Neutral/Hold
         Score < 9 = Avoid or short
```

### Implementation in Pine Script:

```
// Add to your v5 script

// Form 4 Signal (would need external data feed)
form4_buying_cluster = (insider_buy_count > 3 and insider_buy_week < 2) ? 1 : 0

// 13F Signal (would need external data feed)
institutional_increase = (current_13f_position > previous_13f_position) ? 1 : 0

// Federal Reserve Signal (correlation with Fed fund rate futures)
fed_bullish = (fed_funds_futures_down) ? 0.5 : 0

// Institutional Information Gap Score
institutional_gap_score = form4_buying_cluster + institutional_increase + fed_bullish

// Total Confluence Score
total_confluence_score = trend_score + volatility_score + momentum_score + liquidity_score + volume_score + institutional_gap_score

// Trigger
buy_signal = (total_confluence_score >= 13)
```

### Data Sources for Integration:

**1. Form 4 Data:**

- SEC Edgar API: https://www.sec.gov/developer-tools/
- Or manual check: https://sec.gov/cgi-bin/browse-edgar
- Update frequency: Daily (manual check each morning)

**2. 13F Data:**

- SEC Edgar API
- Or download: https://sec.gov/cgi-bin/browse-edgar
- Update frequency: Quarterly (45 days after quarter-end)

**3. Fed Insider Positions:**

- Federal Reserve Designated Account Trading: https://federalreserve.gov
- Or SEC filings for Fed officials' personal trading

**4. Integration Method:**

- Manual daily check (10 minutes)
- Add 1-point bonus to confluence score when institutional signals align
- Document each signal in trade journal

---

## CONCLUSION: THE COMPLETE FRAMEWORK

You now have:

1. **Offshore Data Access** (ICIJ) - Understanding hidden wealth
2. **Insider Trading Data** (Form 4, 13F) - Real-time institutional positioning
3. **SEC Enforcement Cases** - Understanding patterns of manipulation
4. **Legal Framework** - What you can and can't do
5. **Trading Integration** - How to use this data for predictive advantage

**The Insight:**
Institutional power structures (Mills, Domhoff) create predictable patterns in markets because insiders know things before public.
The information gap between inside knowledge and public announcement = profit opportunity.
This is how institutions make money. You can do the same by understanding and tracking institutional data.

**The Caveat:**
This works because most retail traders don't track Form 4s, 13Fs, and offshore networks.
But as more people use these data sources, the predictive power decreases.
The systems with the biggest edge are those that find NEW signals (like crypto + institutional gap integration).

**Your Advantage:**
You're building a quantified system (Pine Script, backtesting, confluence scoring).
Most retail traders trade on hunches.
Your systematic approach to institutional signals should outperform.M
