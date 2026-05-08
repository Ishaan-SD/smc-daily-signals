from data_fetcher import DataFetcher
from signal_processor import SignalProcessor
from notifier import WhatsAppNotifier
from email_notifier import EmailNotifier

# NIFTY 50 Indian Stocks (NSE Format)
NSE_TICKERS = [
    # --- Column 1 ---
    "3BBLACKBIO.NS",    # 3B BLACKBIO
    "ADANIPORTS.NS", # ADANI PORT
    "BAJAJHLDNG.NS", # BAJAJ HOLDING
    "BHARTIARTL.NS", # AIRTEL
    "BLS.NS",        # BLS INTL
    "BSE.NS",        # BSE LTD
    "CAPLIPOINT.NS", # CAPLIN POINT
    "CONCORDBIO.NS", # CONCORD BIOTECK
    "DABUR.NS",      # DABUR
    "DRREDDY.NS",    # DR REDDY
    "ECLERX.NS",     # ECLERX
    "GANESHBE.NS",   # GANESH BENZOPLAST
    "HAL.NS",        # HAL
    "HDFCBANK.NS",   # HDFC BANK
    "INDIAMART.NS",  # INDIA MART
    "INFY.NS",       # INFOSYS
    "ITBEES.NS",     # ITBEES (ETF)
    "ITC.NS",        # ITC
    "JIOFIN.NS",     # JIO FIN
    "CDSL.NS",       # CDSL
    "CLEAN.NS",      # CLEAN SCIENCE
    "CRISIL.NS",     # CRISIL
    "DEEPINDS.NS",   # DEEP IND
    "DIXON.NS",      # DIXON
    "GANESHHOU.NS",  # GANESH HOUSING
    "HDFCAMC.NS",    # HDFCAMC
    "HLEGLAS.NS",    # HLEGLAS
    "HOMEFIRST.NS",  # HOMEFIRST
    "HUDCO.NS",      # HUDCO
    "IEX.NS",        # IEX
    "INDRAMEDCO.NS", # INDRAMEDCO
    "JENBURPH.BO",   # JENBURPH (Primarily trades on BSE)
    "JUSTDIAL.NS",   # JUST DIAL
    "KFINTECH.NS",   # KFINTECH
    "KNRCON.NS",     # KNRCONST
    "JYOTIRES.BO",   # JYOTI RESIN (Primarily trades on BSE)
    "JYOTHYLAB.NS",  # JYOTI LAB
    "LAOPALA.NS",    # LA OPALA
    "LT.NS",         # LT (Larsen & Toubro)
    "MAPMYINDIA.NS", # MAPMYINDIA
    "MAXHEALTH.NS",  # MAXHEALTH
    "MGL.NS",        # MGL
    "NESCO.NS",      # NESCO
    "OBEROIRLTY.NS", # OBEROI REALITY
    "OFSS.NS",       # OFSS
    "PFC.NS",        # PFC
    "POLYCAB.NS",    # POLYCAB
    "RECLTD.NS",     # RECLTD
    "SANGHVIMOV.NS", # SANGHVI MOVERS
    "SUNTV.NS",      # SUN TV
    "SUPRIYA.NS",    # SUPRIYA LIFE
    "TCS.NS",        # TCS
    "VBL.NS",        # VBL
    "ZYDUSLIFE.NS",  # ZYDUS LIFE
    "ADVENZYMES.NS", # ADVANCE EZMY
    "BCG.NS",        # BCG
    "ZENTEC.NS",     # ZEN TECH
    "LIKHITHA.NS",   # LIKHITHA
    "MAHSEAMLES.NS", # MAHARASHTRA SEAMLESS
    "MANBA.NS",      # MANBA
    "MANYAVAR.NS",   # MANYAVAR
    "MISHTANN.BO",   # MISHTANN
    "MSTCLTD.NS",    # MSTCLTD
    "NAVA.NS",       # NAVA
    "NEWGEN.NS",     # NEWGEN
    "OIL.NS",        # OIL INDIA
    "ORIENTCEM.NS",  # ORIENTCEMENT
    "RAJOOENG.NS",   # RAJOO ENGG
    "REPCOHOME.NS",  # REPCO HOME
    "SAREGAMA.NS",   # SAREGAMA
    "SHAREINDIA.NS", # SHAREINDIA
    "SJS.NS",        # SJS
    "SUYOG.NS",      # SUYOG
    "TIMKEN.NS",     # TIMKEN
    "UNIDT.NS",      # UNIDT
    "WHIRLPOOL.NS",  # WHIRLPOOL
    "WSTCSTPAPR.NS", # WSTCSTPAPR
    "YATHARTH.NS",   # YATHARTH
    "ANTHEM.NS",     #ANTEHM BIOSCIENCES
    "CRAMC.NS",      #CANARA ROBECO ASSET MANAGEMENT
    "CPCAP.NS",      #CP CAPITAL
    "CPEDU.NS",      #CAREER POINT EDUTECH
    "EUROPRATIK.NS", #EURO PRATIK SALES
    "IGIL.NS",       #INTERNATIONAL GEMOLOGICAL INSTITUTE
    "IKS.NS"         #INVENTURUS KNOWLEDGE SOLUTIONS

]

ALL_TICKERS = NSE_TICKERS

def run_daily_market_scan():
    print(f"Initiating Daily Scan for {len(ALL_TICKERS)} Assets...")
    
    # 1. Fetch Data
    fetcher = DataFetcher(tickers=ALL_TICKERS)
    market_data = fetcher.fetch_data(period="1y", interval="1d")
    
    # 2. Process Signals
    processor = SignalProcessor()
    active_signals = processor.generate_signals(market_data)
    
    # Initialize the notifier early so we can use it in both scenarios
    notifier = EmailNotifier() # Swap to WhatsAppNotifier() if preferred
    
    # 3. Dispatch Alerts
    if not active_signals:
        print("[INFO] No Smart Money Concept signals detected today. Sending heartbeat notification...")
        # Pass the empty list so your notifier sends an "All Clear" email
        notifier.send_summary(signals=[], interval="1d")
        return

    print(f"[INFO] Found {len(active_signals)} signals! Dispatching consolidated message...")
    notifier.send_summary(signals=active_signals, interval="1d")

if __name__ == "__main__":
    run_daily_market_scan()