import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import plotly.graph_objects as go
import pytz

# --- הגדרות עמוד ---
st.set_page_config(page_title="Greek Portfolio Tracker", layout="wide", page_icon="🇬🇷")

# --- CSS ליישור טקסט עברי לימין ---
st.markdown("""
<style>
    /* ========== כללי ========== */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    
    /* יישור כללי לטקסט עברי */
    .stMarkdown, .stText {
        direction: rtl;
        text-align: right;
    }
    
    /* ========== כותרות ========== */
    h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
        direction: rtl !important;
        width: 100%;
    }
    
    .stTitle {
        text-align: center !important;
    }
    
    /* תת-כותרות */
    [data-testid="stHeader"] {
        direction: rtl;
        text-align: center;
    }
    
    /* ========== מדדים (Metrics) ========== */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
    
    [data-testid="stMetricLabel"] {
        direction: rtl !important;
        text-align: right !important;
        justify-content: flex-end !important;
        width: 100%;
        display: flex;
    }
    
    [data-testid="stMetricLabel"] > div {
        text-align: right !important;
        width: 100%;
    }
    
    [data-testid="stMetricValue"] {
        direction: ltr !important;
        text-align: center !important;
        font-family: 'Courier New', monospace;
        width: 100%;
        display: block;
    }
    
    [data-testid="stMetricDelta"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stMetricDelta"] > div {
        text-align: right !important;
    }
    
    /* ========== קפציות (Captions) ========== */
    .stCaption {
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stCaptionContainer"] {
        direction: rtl;
        text-align: right;
    }
    
    /* ========== טבלאות ========== */
    .dataframe {
        direction: rtl;
    }
    
    .dataframe th {
        text-align: right !important;
        direction: rtl;
    }
    
    .dataframe td {
        text-align: right !important;
        direction: rtl;
    }
    
    /* ========== אינפוטים ולייבלים ========== */
    label {
        direction: rtl !important;
        text-align: right !important;
        width: 100%;
    }
    
    .stSelectbox label, 
    .stRadio label, 
    .stCheckbox label,
    .stSlider label,
    .stTextInput label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stRadio [role="radiogroup"] {
        direction: rtl;
    }
    
    /* Checkbox */
    .stCheckbox {
        direction: rtl;
        width: 100%;
    }
    
    .stCheckbox > div {
        width: 100% !important;
    }
    
    .stCheckbox > label {
        direction: rtl !important;
        text-align: right !important;
        display: inline-flex !important;
        flex-direction: row-reverse !important;
        align-items: flex-start !important;
        white-space: nowrap !important;
        gap: 8px;
        width: auto !important;
        max-width: 100% !important;
    }
    
    .stCheckbox > label > div:first-child {
        flex-shrink: 0;
        margin-top: 2px;
    }
    
    .stCheckbox > label > div:last-child {
        flex: 0 1 auto;
    }
    
    @media (max-width: 400px) {
        .stCheckbox > label {
            white-space: normal !important;
        }
    }
    
    /* Toggle */
    [data-testid="stCheckbox"] {
        direction: rtl;
        width: 100%;
    }
    
    [data-testid="stCheckbox"] > div {
        width: 100% !important;
    }
    
    [data-testid="stCheckbox"] label {
        direction: rtl !important;
        text-align: right !important;
        display: inline-flex !important;
        flex-direction: row-reverse !important;
        align-items: flex-start !important;
        gap: 8px;
        width: auto !important;
        max-width: 100% !important;
    }
    
    [data-testid="stCheckbox"] label > div:first-child {
        flex-shrink: 0;
        margin-top: 2px;
        direction: ltr !important;
    }
    
    /* כפתור ה-Toggle עצמו - הפוך כיוון */
    [data-testid="stCheckbox"] label > div:first-child > div {
        direction: ltr !important;
    }
    
    [data-testid="stCheckbox"] label > div:last-child {
        flex: 0 1 auto;
        white-space: nowrap;
    }
    
    @media (max-width: 400px) {
        [data-testid="stCheckbox"] label > div:last-child {
            white-space: normal;
        }
    }
    
    /* Selectbox */
    .stSelectbox {
        direction: rtl;
    }
    
    /* ========== אלרטים ומסגרות מידע ========== */
    .stAlert, 
    [data-testid="stAlert"],
    [data-testid="stNotification"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stInfo, .stSuccess, .stWarning, .stError {
        direction: rtl;
        text-align: right;
    }
    
    /* ========== Sidebar ========== */
    [data-testid="stSidebar"] {
        direction: rtl;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        text-align: center !important;
    }
    
    /* ========== רשימות ========== */
    ul, ol {
        direction: rtl;
        text-align: right;
        padding-right: 20px;
        padding-left: 0;
    }
    
    li {
        direction: rtl;
        text-align: right;
    }
    
    /* ========== Expanders ========== */
    [data-testid="stExpander"] {
        direction: rtl;
    }
    
    [data-testid="stExpander"] summary {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .rtl-box {
        direction: rtl;
        text-align: right;
        line-height: 1.6;
    }
    
    /* ========== Tabs ========== */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        justify-content: flex-end;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl;
    }
    
    /* ========== כפתורים ========== */
    .stButton > button {
        width: 100%;
    }
    
    /* ========== טיימרים מיוחדים ========== */
    .refresh-timer {
        background-color: #e8f4f8;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        text-align: center;
        direction: ltr;
        font-family: 'Courier New', monospace;
    }
    
    .market-closed {
        background-color: #fff3cd;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        text-align: center;
        direction: rtl;
    }
    
    /* ========== Columns ========== */
    [data-testid="column"] {
        direction: rtl;
    }
    
    /* ========== Dividers ========== */
    hr {
        margin: 1rem 0;
    }
    
    /* ========== Tooltips & Help Text ========== */
    [data-testid="stTooltipIcon"] {
        direction: rtl;
        flex-shrink: 0;
        margin-right: 4px;
    }
    
    .stTooltipContent {
        direction: rtl;
        text-align: right;
    }
    
    /* Help icon בתוך checkbox/toggle */
    [data-testid="stCheckbox"] [data-testid="stTooltipIcon"] {
        display: inline-flex;
        vertical-align: middle;
    }
    
    /* ========== Form Submit Button ========== */
    .stFormSubmitButton {
        direction: rtl;
    }
    
    /* ========== Progress & Spinner ========== */
    .stProgress > div {
        direction: ltr;
    }
</style>
""", unsafe_allow_html=True)



# --- ניהול הגדרות משתמש ---
SETTINGS_FILE = "user_settings.json"

def load_settings():
    """טוען את הגדרות המשתמש מהקובץ"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_settings(residency_idx, withdrawal_strategy, auto_refresh):
    """שומר את הגדרות המשתמש לקובץ"""
    data = {
        "residency_idx": residency_idx,
        "withdrawal_strategy": withdrawal_strategy,
        "auto_refresh": auto_refresh,
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

# --- אתחול session state ---
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# טעינת הגדרות משתמש מקובץ JSON
saved_settings = load_settings()
if saved_settings:
    if 'residency_idx' not in st.session_state:
        st.session_state.residency_idx = saved_settings.get("residency_idx", 1)
    if 'withdrawal_strategy' not in st.session_state:
        st.session_state.withdrawal_strategy = saved_settings.get("withdrawal_strategy", 0)
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = saved_settings.get("auto_refresh", False)
else:
    # ברירות מחדל אם אין קובץ
    if 'residency_idx' not in st.session_state:
        st.session_state.residency_idx = 1  # יוון
    if 'withdrawal_strategy' not in st.session_state:
        st.session_state.withdrawal_strategy = 0  # צבירה
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False

# --- פונקציות לניהול קובץ המעקב החודשי ---
META_FILE = "portfolio_meta.json"
HISTORY_FILE = "income_history.json"

def load_monthly_reference():
    """טוען את נתוני הייחוס החודשי מהקובץ"""
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_monthly_reference(value_eur):
    """שומר ערך ייחוס חדש עם החודש הנוכחי"""
    now = datetime.now()
    data = {
        "reference_month": now.strftime("%Y-%m"),
        "reference_value_eur": round(value_eur, 2),
        "last_updated": now.strftime("%Y-%m-%dT%H:%M:%S")
    }
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

def check_and_update_monthly_reference(current_value_eur):
    """
    בדיקה אם צריך לעדכן את הייחוס החודשי.
    מחזיר: (reference_value, is_new_month)
    """
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    meta = load_monthly_reference()
    
    # אם אין קובץ או עברנו לחודש חדש
    if meta is None or meta.get("reference_month") != current_month:
        new_meta = save_monthly_reference(current_value_eur)
        return new_meta["reference_value_eur"], True
    
    # אותו חודש - מחזירים את הערך השמור
    return meta["reference_value_eur"], False

# --- מערכת היסטוריית הכנסות ---
def load_income_history():
    """טוען את היסטוריית ההכנסות מהקובץ"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_income_history(history):
    """שומר את היסטוריית ההכנסות"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def calculate_month_income(month_date, portfolio, market, eur_ils, withdrawal_strategy=0):
    """
    מחשב את ההכנסות עבור חודש ספציפי.
    
    Parameters:
    - withdrawal_strategy: 0 = צבירה, 1 = רווחים בלבד, 2 = 4% קבוע
    
    מחזיר: (base_eur, efrn_eur, greek_eur, ibci_withdrawal_eur)
    """
    base_eur = 0
    efrn_eur = 0
    greek_eur = 0
    ibci_withdrawal_eur = 0
    
    # VECP - חודשי
    vecp_row = portfolio[portfolio['Ticker'] == 'VECP']
    if not vecp_row.empty:
        qty = vecp_row.iloc[0]['Quantity']
        price = market.get('VECP', vecp_row.iloc[0]['AvgPrice'])
        yrate = vecp_row.iloc[0]['YieldRate']
        base_eur += (qty * price * yrate) / 12
    
    # נכסים ישראליים
    deposit_row = portfolio[portfolio['Ticker'] == 'DEPOSIT_IL']
    if not deposit_row.empty:
        qty = deposit_row.iloc[0]['Quantity']
        yrate = deposit_row.iloc[0]['YieldRate']
        base_eur += (qty * yrate / 12) / eur_ils
    
    bond_il_row = portfolio[portfolio['Ticker'] == 'BOND_IL']
    if not bond_il_row.empty and month_date.month in [6, 12]:
        qty = bond_il_row.iloc[0]['Quantity']
        yrate = bond_il_row.iloc[0]['YieldRate']
        base_eur += (qty * yrate / 2) / eur_ils
    
    # EFRN - רבעוני
    efrn_row = portfolio[portfolio['Ticker'] == 'EFRN']
    if not efrn_row.empty and month_date.month in [3, 6, 9, 12]:
        qty = efrn_row.iloc[0]['Quantity']
        price = market.get('EFRN', efrn_row.iloc[0]['AvgPrice'])
        yrate = efrn_row.iloc[0]['YieldRate']
        efrn_eur = qty * price * yrate
    
    # Greek Bond - שנתי (יולי)
    if month_date.month == 7:
        bond_gr_row = portfolio[portfolio['Ticker'] == 'BOND_GR']
        if not bond_gr_row.empty:
            qty = bond_gr_row.iloc[0]['Quantity']
            bond_gr_annual = qty * (100/100) * 0.03375
            
            purchase_date = datetime.strptime(bond_gr_row.iloc[0]['PurchaseDate'], "%Y-%m-%d")
            
            if month_date.year == purchase_date.year:
                months_active = 7 - purchase_date.month + 1
                if months_active < 0:
                    months_active = 0
            else:
                months_active = 12
            
            greek_eur = bond_gr_annual * (months_active / 12)
    
    # *** IBCI - משיכה לפי אסטרטגיה ***
    if withdrawal_strategy > 0:  # לא צבירה
        ibci_row = portfolio[portfolio['Ticker'] == 'IBCI']
        if not ibci_row.empty:
            qty = ibci_row.iloc[0]['Quantity']
            price = market.get('IBCI', ibci_row.iloc[0]['AvgPrice'])
            current_value = qty * price
            
            # תשואה משוערת של IBCI (אינפלציה)
            expected_annual_return = 0.025
            monthly_growth = current_value * expected_annual_return / 12
            
            if withdrawal_strategy == 1:
                # רווחים בלבד - משיכה = הצמיחה החודשית
                ibci_withdrawal_eur = monthly_growth
            
            elif withdrawal_strategy == 2:
                # 4% קבוע - משיכה קבועה
                ibci_withdrawal_eur = current_value * 0.04 / 12
    
    return base_eur, efrn_eur, greek_eur, ibci_withdrawal_eur

def lock_previous_months(portfolio, market, eur_ils, withdrawal_strategy=0):
    """
    נועל חודשים שעברו (לא כולל החודש הנוכחי).
    פועל אוטומטית בכל ריצה - אם חודש שעבר לא נעול, נועל אותו.
    """
    history = load_income_history()
    now = datetime.now()
    current_month_key = now.strftime("%Y-%m")
    
    # בדיקה אם יש חודשים שצריך לנעול
    start_date_str = portfolio["PurchaseDate"].min()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # עובר על כל החודשים מתחילת התיק ועד החודש הקודם
    check_date = start_date
    months_locked = 0
    
    while check_date < now.replace(day=1):  # עד תחילת החודש הנוכחי
        month_key = check_date.strftime("%Y-%m")
        
        # אם החודש הזה לא נעול עדיין
        if month_key not in history:
            # חישוב ההכנסות לחודש הזה עם האסטרטגיה הנוכחית
            base_eur, efrn_eur, greek_eur, ibci_eur = calculate_month_income(
                check_date, portfolio, market, eur_ils, withdrawal_strategy
            )
            
            # שמירה
            history[month_key] = {
                "base_income": round(base_eur, 2),
                "efrn_bonus": round(efrn_eur, 2),
                "greek_bond": round(greek_eur, 2),
                "ibci_withdrawal": round(ibci_eur, 2),
                "withdrawal_strategy": withdrawal_strategy,
                "total": round(base_eur + efrn_eur + greek_eur + ibci_eur, 2),
                "locked_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
            months_locked += 1
        
        # מעבר לחודש הבא
        check_date = check_date + relativedelta(months=1)
    
    # שמירת השינויים
    if months_locked > 0:
        save_income_history(history)
    
    return history, months_locked

# --- פונקציה לבדיקת שעות מסחר ---
def is_market_open():
    """בודק אם השווקים האירופאים פתוחים (09:30-17:30 CET, ימי חול)"""
    cet = pytz.timezone('Europe/Athens')
    now_cet = datetime.now(cet)
    
    # בדיקת סוף שבוע
    if now_cet.weekday() >= 5:  # שבת (5) או ראשון (6)
        return False
    
    # בדיקת שעות (09:30-17:30)
    market_open_time = now_cet.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now_cet.replace(hour=17, minute=30, second=0, microsecond=0)
    
    return market_open_time <= now_cet <= market_close_time

# --- סגנון CSS ---
st.markdown("""
<style>
    /* יישור כותרות לימין */
    h1 {
        text-align: right !important;
    }
    
    /* צמצום המרווח העליון */
    .block-container {
        padding-top: 1rem !important;
    }
    
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #0066cc;}
    div[data-testid="stMetricValue"] {font-size: 26px; font-weight: bold;}
    .stExpander {border: none; box-shadow: none; background-color: #fff; border-radius: 8px; margin-bottom: 10px; border: 1px solid #eee;}
    
    .streamlit-expanderHeader {
        direction: rtl; 
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .rtl-box {
        direction: rtl;
        text-align: right;
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #0066cc;
        color: #0c5460;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    .rtl-box ul {
        margin-right: 20px;
        padding: 0;
        list-style-position: inside;
    }
    .refresh-timer {
        background-color: #f0f9ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #0066cc;
        margin: 10px 0;
    }
    .market-closed {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #ffc107;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# --- מילון תיאורים ---
descriptions = {
    "BOND_GR": """<strong>🏆 אג"ח ממשלתי יוון 2034</strong>
    <ul>
        <li>תשואה קבועה 3.375%.</li>
        <li>פטור ממס לתושבי יוון (0%).</li>
        <li>נכס הבסיס לויזת הזהב.</li>
    </ul>""",
    
    "IBCI": """<strong>📈 IBCI (צמוד אינפלציה אירופה)</strong>
    <ul>
        <li>קרן 'צוברת' (Accumulating).</li>
        <li>לא מחלקת דיבידנד למזומן אלא צוברת אותו פנימה.</li>
        <li>הגנה מעולה משחיקת הכסף.</li>
    </ul>""",
    
    "EFRN": """<strong>💧 EFRN (ריבית משתנה)</strong>
    <ul>
        <li>משקיעה באג"ח קונצרני בריבית משתנה.</li>
        <li>כשהריבית עולה - התשואה עולה.</li>
        <li>מחלקת דיבידנד רבעוני.</li>
    </ul>""",
    
    "VECP": """<strong>🏢 VECP (אג"ח חברות)</strong>
    <ul>
        <li>פיזור רחב של חברות אירופאיות.</li>
        <li>תשואה שוטפת גבוהה יותר מאג"ח מדינה.</li>
        <li>מחלקת דיבידנד חודשי/רבעוני.</li>
    </ul>""",
    
    "DEPOSIT_IL": """<strong>🏦 פיקדון שקלי (ישראל)</strong>
    <ul>
        <li>פיקדון נזיל בבנק ישראלי.</li>
        <li>חייב במס 15% לתושבי יוון (במקום 25%).</li>
    </ul>""",
    
    "BOND_IL": """<strong>🇮🇱 אג"ח ממשלתי ישראלי</strong>
    <ul>
        <li>נכס בטוח בשקלים (שחר/גליל).</li>
        <li>חייב במס 15% לתושבי יוון.</li>
    </ul>"""
}

# --- חישוב מס מדויק לפי נכס ותושבות ---
def get_net_income(ticker, gross_amount, income_type, residency, cost_basis=None):
    """
    מחשב הכנסה נטו אחרי מס בצורה מדויקת
    
    Parameters:
    - ticker: סימול הנכס (BOND_GR, VECP, EFRN, IBCI, DEPOSIT_IL, BOND_IL)
    - gross_amount: סכום ברוטו
    - income_type: 'dividend', 'interest', 'coupon', 'capital_gain'
    - residency: 'ישראל 🇮🇱' או 'יוון 🇬🇷'
    - cost_basis: בסיס עלות (למס רווחי הון בלבד)
    
    Returns:
    - tuple: (net_amount, tax_paid, effective_tax_rate)
    """
    
    if residency == "ישראל 🇮🇱":
        # תושב ישראל - 25% על הכל
        if income_type == "capital_gain" and cost_basis is not None:
            # מס רווחי הון
            gain = gross_amount - cost_basis
            tax = gain * 0.25
            net = gross_amount - tax
            return net, tax, 0.25
        else:
            # דיבידנד/ריבית/קופון
            tax = gross_amount * 0.25
            net = gross_amount - tax
            return net, tax, 0.25
    
    else:  # תושב יוון 🇬🇷
        
        if income_type == "capital_gain":
            # רווחי הון ביוון - פטור מלא!
            return gross_amount, 0, 0.0
        
        # דיבידנדים וריבית - לפי נכס
        if ticker == "BOND_GR":
            # אג"ח יווני - פטור מלא
            return gross_amount, 0, 0.0
        
        elif ticker == "VECP":
            # דיבידנד הולנדי
            # ניכוי במקור בהולנד: 15%
            # מס ביוון: 5%
            # משלמים את הגבוה = 15%
            tax = gross_amount * 0.15
            net = gross_amount - tax
            return net, tax, 0.15
        
        elif ticker in ["EFRN", "IBCI"]:
            # דיבידנד מאירלנד/לוקסמבורג
            # ניכוי במקור: 0%
            # מס ביוון: 5%
            tax = gross_amount * 0.05
            net = gross_amount - tax
            return net, tax, 0.05
        
        elif ticker in ["DEPOSIT_IL", "BOND_IL"]:
            # ריבית מישראל
            # ניכוי במקור: 15% (תושב חוץ)
            # מס ביוון: 15%
            # משלמים 15% בישראל + זיכוי ביוון = 15% סה"כ
            tax = gross_amount * 0.15
            net = gross_amount - tax
            return net, tax, 0.15
        
        else:
            # ברירת מחדל - 5% ביוון
            tax = gross_amount * 0.05
            net = gross_amount - tax
            return net, tax, 0.05

# --- משיכת נתונים ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_market_data():
    tickers = {"IBCI": "IBCI.DE", "EFRN": "EFRN.DE", "VECP": "VECP.AS", "EUR_ILS": "EURILS=X"}
    data = {"BOND_GR": 101.50, "DEPOSIT_IL": 1.0, "BOND_IL": 1.0}
    backup = {"IBCI": 102.50, "EFRN": 100.20, "VECP": 52.10, "EUR_ILS": 3.67}

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"})
        for k, v in tickers.items():
            try:
                hist = yf.Ticker(v, session=session).history(period="1d")
                if not hist.empty:
                    val = float(hist['Close'].iloc[-1])
                    if k == "EUR_ILS": data["EUR_ILS"] = val
                    else: data[k] = val
            except: pass
    except: pass
    
    for k, v in backup.items():
        if k not in data: data[k] = v
    return data

market = get_market_data()
eur_ils = market.get("EUR_ILS", 3.67)

# --- יצירת תיק ---
if not os.path.exists("holdings.csv"):
    today = datetime.now().strftime("%Y-%m-%d")
    
    targets = {
        "BOND_GR": 500000,
        "IBCI": 150000,
        "EFRN": 100000,
        "VECP": 50000,
        "DEPOSIT_IL": 50000 * eur_ils,
        "BOND_IL": 150000 * eur_ils
    }
    
    data = {
        "Ticker": ["BOND_GR", "IBCI", "EFRN", "VECP", "DEPOSIT_IL", "BOND_IL"],
        "Name": ["Greek Govt Bond '34", "IBCI (Inflation)", "EFRN (Floating)", "VECP (Corporate)", "Deposit Israel", "Bond Israel"],
        "Quantity": [
            int(targets["BOND_GR"] / (market["BOND_GR"]/100)),
            int(targets["IBCI"] / market["IBCI"]),
            int(targets["EFRN"] / market["EFRN"]),
            int(targets["VECP"] / market["VECP"]),
            int(targets["DEPOSIT_IL"]),
            int(targets["BOND_IL"])
        ],
        "AvgPrice": [market["BOND_GR"], market["IBCI"], market["EFRN"], market["VECP"], 1.0, 1.0], 
        "Currency": ["EUR", "EUR", "EUR", "EUR", "ILS", "ILS"],
        "YieldType": ["Coupon", "Capital", "Dividend", "Dividend", "Interest", "Coupon"],
        "YieldRate": [0.03375, 0.025, 0.038, 0.040, 0.030, 0.046],
        "PurchaseDate": [today, today, today, today, today, today]
    }
    pd.DataFrame(data).to_csv("holdings.csv", index=False)

portfolio = pd.read_csv("holdings.csv")

if "PurchaseDate" not in portfolio.columns:
    portfolio["PurchaseDate"] = datetime.now().strftime("%Y-%m-%d")
    portfolio.to_csv("holdings.csv", index=False)

portfolio_start_date = portfolio["PurchaseDate"].min()

# --- נעילת היסטוריה אוטומטית ---
income_history, months_locked = lock_previous_months(portfolio, market, eur_ils, st.session_state.withdrawal_strategy)

# הצגת הודעה אם נעלו חודשים חדשים
if months_locked > 0:
    st.toast(f"🔒 {months_locked} חודשים נעלו בהיסטוריה", icon="✅")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ הגדרות")
    residency_options = ["ישראל 🇮🇱", "יוון 🇬🇷"]
    residency = st.radio("תושבות מס:", residency_options, index=st.session_state.residency_idx)
    new_idx = residency_options.index(residency)
    if new_idx != st.session_state.residency_idx:
        st.session_state.residency_idx = new_idx
        save_settings(st.session_state.residency_idx, 
                     st.session_state.withdrawal_strategy, 
                     st.session_state.auto_refresh)
    
    st.divider()
    
    # --- אסטרטגיית משיכה ---
    st.markdown("### 📉 אסטרטגיית משיכה מ-IBCI")
    
    withdrawal_options = [
        "🔒 צבירה (ללא משיכה)",
        "💰 משוך רווחים בלבד (2.5%)",
        "⚠️ משוך 4% קבוע (כלל קלאסי)"
    ]
    
    withdrawal_strategy = st.radio(
        "בחר מצב:",
        withdrawal_options,
        index=st.session_state.withdrawal_strategy,
        help="""
        🔒 **צבירה**: IBCI צובר ערך פנימית, לא מופיע בתזרים המזומנים
        
        💰 **רווחים בלבד**: משיכה של 2.5% שנתי (תשואה משוערת) - הקרן נשארת קבועה ✅
        
        ⚠️ **4% קבוע**: משיכה של 4% שנתי לפי הכלל הקלאסי - הקרן עשויה להתכווץ אם התשואה נמוכה מ-4%
        """
    )
    
    new_strategy_idx = withdrawal_options.index(withdrawal_strategy)
    if new_strategy_idx != st.session_state.withdrawal_strategy:
        st.session_state.withdrawal_strategy = new_strategy_idx
        save_settings(st.session_state.residency_idx, 
                     new_strategy_idx,
                     st.session_state.auto_refresh)
        st.rerun()
    
    # חישוב משתנים לשימוש
    include_withdrawal = (new_strategy_idx > 0)
    conservative_mode = (new_strategy_idx == 1)
    
    # אזהרה למצב 4% קבוע
    if new_strategy_idx == 2:
        ibci_row = portfolio[portfolio['Ticker'] == 'IBCI']
        if not ibci_row.empty:
            qty = ibci_row.iloc[0]['Quantity']
            price = market.get('IBCI', ibci_row.iloc[0]['AvgPrice'])
            current_value = qty * price
            
            annual_withdrawal = current_value * 0.04
            annual_growth = current_value * 0.025
            annual_decay = annual_withdrawal - annual_growth
            decay_pct = (annual_decay / current_value) * 100
            
            st.warning(f"⚠️ **שים לב**: במצב זה הקרן תתכווץ בכ-€{annual_decay:,.0f} בשנה ({decay_pct:.1f}%)")
    
    # תצוגת מידע על IBCI
    ibci_row = portfolio[portfolio['Ticker'] == 'IBCI']
    if not ibci_row.empty:
        qty = ibci_row.iloc[0]['Quantity']
        price = market.get('IBCI', ibci_row.iloc[0]['AvgPrice'])
        current_value = qty * price
        
        st.info(f"""
        📊 **מצב IBCI נוכחי**
        
        שווי: €{current_value:,.0f}
        
        תשואה משוערת: 2.5% שנתי
        צמיחה חודשית: €{(current_value * 0.025 / 12):,.0f}
        משיכה (4%): €{(current_value * 0.04 / 12):,.0f}
        """)
    
    st.divider()
    
    # --- רענון אוטומטי ---
    st.markdown("### 🔄 רענון אוטומטי")
    
    auto_refresh = st.checkbox("הפעל רענון אוטומטי", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        save_settings(st.session_state.residency_idx, 
                     st.session_state.withdrawal_strategy, 
                     st.session_state.auto_refresh)
    
    # אופציות רענון
    refresh_options = {
        "כל שעה": 3600,
        "כל 4 שעות": 14400,
        "כל יום": 86400,
        "כל שבוע": 604800
    }
    
    refresh_choice = st.selectbox(
        "תדירות רענון:",
        options=list(refresh_options.keys()),
        index=0,
        disabled=not auto_refresh
    )
    
    refresh_interval = refresh_options[refresh_choice]
    
    if auto_refresh and is_market_open():
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= refresh_interval:
            st.session_state.last_refresh = datetime.now()
            get_market_data.clear()
            st.rerun()
        
        time_until_refresh = max(0, refresh_interval - time_since_refresh)
        
        # המרה לפורמט נוח
        hours = int(time_until_refresh // 3600)
        minutes = int((time_until_refresh % 3600) // 60)
        seconds = int(time_until_refresh % 60)
        
        if hours > 0:
            time_display = f"{hours}h {minutes}m"
        elif minutes > 0:
            time_display = f"{minutes}m {seconds}s"
        else:
            time_display = f"{seconds}s"
        
        st.markdown(
            f'<div class="refresh-timer">⏱️ רענון הבא בעוד: <b>{time_display}</b></div>',
            unsafe_allow_html=True
        )
    elif auto_refresh and not is_market_open():
        st.markdown(
            '<div class="market-closed">⚠️ השווקים סגורים - רענון אוטומטי מושהה</div>',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # --- רענון מחירים ידני ---
    st.markdown("### 💹 מחירי שוק")
    
    col_refresh1, col_refresh2 = st.columns([2, 1])
    with col_refresh1:
        if st.button("🔄 רענן מחירים", use_container_width=True, help="משוך מחירים עדכניים מהשוק"):
            get_market_data.clear()
            st.rerun()
    
    with col_refresh2:
        now = datetime.now()
        st.caption(f"🕐 {now.strftime('%H:%M')}")
    
    st.divider()
    
    # --- כפתור איפוס ייחוס חודשי ---
    st.markdown("### 🔄 מעקב חודשי")
    
    meta_info = load_monthly_reference()
    if meta_info:
        st.info(f"📅 ייחוס נוכחי: {meta_info['reference_month']}\n\n💰 ערך בסיס: €{meta_info['reference_value_eur']:,.2f}")
    
    if st.button("🔄 אפס מדידה חודשית", help="קובע את השווי הנוכחי כנקודת התחלה חדשה"):
        # נחשב את השווי הנוכחי
        totalvaleur_temp = 0
        for _, row in portfolio.iterrows():
            qty, curr = row["Quantity"], row["Currency"]
            if curr == "EUR":
                price = market.get(row["Ticker"], row["AvgPrice"])
                if row["Ticker"] == "BOND_GR":
                    totalvaleur_temp += qty * (price / 100)
                else:
                    totalvaleur_temp += qty * price
            else:
                price = market.get(row["Ticker"], 1.0)
                totalvaleur_temp += (qty * price) / eur_ils
        
        save_monthly_reference(totalvaleur_temp)
        st.success("✅ הייחוס החודשי אופס!")
        time.sleep(1)
        st.rerun()
    
    st.divider()
    
    # --- מידע על היסטוריה ---
    st.markdown("### 📚 היסטוריית הכנסות")
    
    locked_months_count = len(income_history)
    if locked_months_count > 0:
        st.info(f"🔒 {locked_months_count} חודשים נעולים")
        
        # הצגת החודשים האחרונים שנעלו
        sorted_months = sorted(income_history.keys(), reverse=True)[:3]
        if sorted_months:
            st.caption("חודשים אחרונים:")
            for month in sorted_months:
                month_data = income_history[month]
                st.caption(f"• {month}: €{month_data['total']:,.0f}")
    else:
        st.caption("טרם נעלו חודשים")
    
    st.divider()
    st.caption(f"📈 יורו/שקל: {eur_ils:.4f}")
    st.caption(f"🕐 עדכון אחרון: {datetime.now().strftime('%H:%M:%S')}")

# --- חישובים ---
totalvaleur, totalvalue, monthlycasheur, yearlycasheur, monthlycashils, table_rows = 0, 0, 0, 0, 0, []

# משתנים נפרדים ליוון וישראל (ברוטו + נטו)
monthly_greece_eur_gross = 0   # הכנסה חודשית מיוון - ברוטו
monthly_greece_eur = 0         # הכנסה חודשית מיוון - נטו
monthly_israel_ils_gross = 0   # הכנסה חודשית מישראל - ברוטו
monthly_israel_ils = 0         # הכנסה חודשית מישראל - נטו

# חישוב רווח/הפסד כולל
total_cost_eur = 0  # עלות כוללת
total_pnl_eur = 0   # רווח/הפסד כולל ביורו
total_pnl_ils = 0   # רווח/הפסד כולל בשקלים

# חישוב נכסים צוברים (לפי כלל ה-4%)
accumulating_value_eur = 0  # שווי נכסים צוברים ביורו

for _, row in portfolio.iterrows():
    qty, avg, curr, ytype, yrate = row["Quantity"], row["AvgPrice"], row["Currency"], row["YieldType"], row["YieldRate"]
    ticker = row["Ticker"]
    
    if curr == "EUR":
        price = market.get(ticker, avg)
        if ticker == "BOND_GR":
            value_eur = qty * (price / 100)
            cost_eur = qty * (avg / 100)
        else:
            value_eur = qty * price
            cost_eur = qty * avg
        
        value_ils = value_eur * eur_ils
        totalvaleur += value_eur
        totalvalue += value_ils
        
        # צבירת עלות ורווח/הפסד
        total_cost_eur += cost_eur
        
        if ytype in ["Coupon", "Dividend"]:
            if ticker == "BOND_GR":
                annual_gross_eur = qty * (100 / 100) * yrate
                income_type = "coupon"
            else:
                annual_gross_eur = qty * price * yrate
                income_type = "dividend"
            
            # חישוב נטו מדויק לפי תושבות
            monthly_gross_eur = annual_gross_eur / 12
            monthly_net_eur, monthly_tax, tax_rate = get_net_income(
                ticker, monthly_gross_eur, income_type, residency
            )
            
            yearlycasheur += annual_gross_eur
            monthly_greece_eur_gross += monthly_gross_eur  # ברוטו
            monthly_greece_eur += monthly_net_eur          # נטו
        
        # זיהוי נכסים צוברים (Capital/Accumulating)
        if ytype == "Capital":
            accumulating_value_eur += value_eur
        
        pnl_eur = value_eur - cost_eur
        pnl_pct = ((value_eur / cost_eur) - 1) * 100 if cost_eur > 0 else 0
        
        total_pnl_eur += pnl_eur  # צבירה
        
        table_rows.append({
            "קבוצה": "יוון 🇬🇷",
            "Ticker": ticker,
            "נכס": row["Name"],
            "תאריך רכישה": row["PurchaseDate"],
            "שווי": f"€{value_eur:,.0f}",
            "רווח": f"€{pnl_eur:,.0f}",
            "שינוי (%)": pnl_pct,
            "נוכחי": f"€{price:.2f}"
        })
    
    else:
        price = market.get(ticker, 1.0)
        value_ils = qty * price
        cost_ils = qty * avg
        value_eur = value_ils / eur_ils
        
        totalvaleur += value_eur
        totalvalue += value_ils
        
        # צבירת עלות ורווח/הפסד
        total_cost_eur += cost_ils / eur_ils
        
        if ytype in ["Coupon", "Interest"]:
            annual_gross_ils = qty * yrate
            monthly_gross_ils = annual_gross_ils / 12
            
            # חישוב נטו מדויק לפי תושבות
            income_type = "interest" if ytype == "Interest" else "coupon"
            monthly_net_ils, monthly_tax_ils, tax_rate = get_net_income(
                ticker, monthly_gross_ils, income_type, residency
            )
            
            monthly_israel_ils_gross += monthly_gross_ils  # ברוטו
            monthly_israel_ils += monthly_net_ils          # נטו
        
        pnl_ils = value_ils - cost_ils
        pnl_pct = ((value_ils / cost_ils) - 1) * 100 if cost_ils > 0 else 0
        
        total_pnl_eur += pnl_ils / eur_ils  # צבירה ביורו
        total_pnl_ils += pnl_ils            # צבירה בשקלים
        
        table_rows.append({
            "קבוצה": "ישראל 🇮🇱",
            "Ticker": ticker,
            "נכס": row["Name"],
            "תאריך רכישה": row["PurchaseDate"],
            "שווי": f"₪{value_ils:,.0f}",
            "רווח": f"₪{pnl_ils:,.0f}",
            "שינוי (%)": pnl_pct,
            "נוכחי": f"₪{price:.2f}"
        })

# --- בדיקה ועדכון אוטומטי של הייחוס החודשי ---
monthly_reference_value, is_new_month = check_and_update_monthly_reference(totalvaleur)

# חישוב שינוי חודשי
monthly_change_eur = totalvaleur - monthly_reference_value
monthly_change_pct = ((totalvaleur / monthly_reference_value) - 1) * 100 if monthly_reference_value > 0 else 0

# --- חישוב משיכה מנכסים צוברים ---
withdrawal_monthly_eur = 0
withdrawal_monthly_gross_eur = 0
withdrawal_tax_eur = 0

if include_withdrawal and accumulating_value_eur > 0:
    ibci_row = portfolio[portfolio['Ticker'] == 'IBCI']
    if not ibci_row.empty:
        qty = ibci_row.iloc[0]['Quantity']
        price = market.get('IBCI', ibci_row.iloc[0]['AvgPrice'])
        current_value = qty * price
        
        expected_annual_return = 0.025
        monthly_growth = current_value * expected_annual_return / 12
        
        if conservative_mode:
            # רווחים בלבד
            withdrawal_monthly_eur = monthly_growth
            withdrawal_monthly_gross_eur = monthly_growth
        else:
            # 4% קבוע
            withdrawal_monthly_gross_eur = current_value * 0.04 / 12
            
            # מס רווחי הון (אם רלוונטי)
            cost_basis_monthly = withdrawal_monthly_gross_eur * 0.9
            withdrawal_monthly_eur, withdrawal_tax_eur, tax_rate = get_net_income(
                "IBCI",
                withdrawal_monthly_gross_eur,
                "capital_gain",
                residency,
                cost_basis=cost_basis_monthly
            )
        
        # הוספה להכנסה חודשית
        monthly_greece_eur_gross += withdrawal_monthly_gross_eur
        monthly_greece_eur += withdrawal_monthly_eur

# --- כותרת ---
st.title("📊 Greek Portfolio Tracker")

# --- מדדים עליונים ---
c1, c2, c3, c4 = st.columns(4)

# monthly_greece_eur ו-monthly_israel_ils כבר נטו!
net_greece_eur = monthly_greece_eur
net_israel_ils = monthly_israel_ils
net_israel_eur = net_israel_ils / eur_ils

# נטו גלובלי
netcasheur_global = net_greece_eur + net_israel_eur
netcashils_global = netcasheur_global * eur_ils

# חישוב אחוז רווח/הפסד כולל
total_pnl_pct = ((totalvaleur / total_cost_eur) - 1) * 100 if total_cost_eur > 0 else 0

with c1:
    if monthly_change_eur == 0:
        delta_color = "off"
    elif monthly_change_eur > 0:
        delta_color = "normal"
    else:
        delta_color = "inverse"
    
    if monthly_change_eur >= 0:
        delta_text = f"+€{monthly_change_eur:,.0f} (+{monthly_change_pct:.2f}%) מתחילת החודש"
    else:
        delta_text = f"€{monthly_change_eur:,.0f} ({monthly_change_pct:.2f}%) מתחילת החודש"
    
    st.metric(
        "💼 שווי תיק כולל", 
        f"€{totalvaleur:,.0f}",
        delta_text,
        delta_color=delta_color
    )

with c2:
    greece_label = "🇬🇷 הכנסה מנכסי יוון"
    if include_withdrawal and withdrawal_monthly_eur > 0:
        greece_label += " 📉"
    
    st.metric(
        greece_label,
        f"€{monthly_greece_eur_gross:,.0f}",
        f"נטו: €{monthly_greece_eur:,.0f}"
    )

with c3:
    st.metric(
        "🇮🇱 הכנסה מנכסי ישראל", 
        f"₪{monthly_israel_ils_gross:,.0f}",
        f"נטו: ₪{monthly_israel_ils:,.0f}"
    )

with c4:
    global_label = "🌍 סך הכנסה פסיבית נטו"
    if include_withdrawal and withdrawal_monthly_eur > 0:
        global_label += " 📉"
    
    st.metric(
        global_label,
        f"€{netcasheur_global:,.0f}",
        f"₪{netcashils_global:,.0f}"
    )

# אינדיקטור משיכה
if include_withdrawal and withdrawal_monthly_eur > 0:
    if conservative_mode:
        st.success(f"💰 משיכת רווחים: €{withdrawal_monthly_eur:,.0f}/חודש (2.5% שנתי) | הקרן נשארת קבועה ב-€{accumulating_value_eur:,.0f} ✅")
    else:
        if residency == "ישראל 🇮🇱":
            st.info(f"📉 משיכה חודשית: €{withdrawal_monthly_gross_eur:,.0f} ברוטו → מס: €{withdrawal_tax_eur:,.0f} → נטו: €{withdrawal_monthly_eur:,.0f} (4% שנתי מנכסים צוברים: €{accumulating_value_eur:,.0f})")
        else:
            st.success(f"📉 משיכה חודשית: €{withdrawal_monthly_eur:,.0f} (4% שנתי מנכסים צוברים: €{accumulating_value_eur:,.0f}) | 🎉 פטור ממס רווחי הון ביוון!")

if is_new_month:
    st.info("🆕 חודש חדש זוהה! נקודת הייחוס עודכנה אוטומטית.")

st.divider()

# --- Continue with tabs and chart (keeping the existing code) ---
# Due to character limit, I'll continue in the remaining parts...

# [Rest of the code continues with the chart building section...]
