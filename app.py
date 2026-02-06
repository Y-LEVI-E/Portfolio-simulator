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

def save_settings(residency_idx, include_withdrawal, auto_refresh):
    """שומר את הגדרות המשתמש לקובץ"""
    data = {
        "residency_idx": residency_idx,
        "include_withdrawal": include_withdrawal,
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
    if 'include_withdrawal' not in st.session_state:
        st.session_state.include_withdrawal = saved_settings.get("include_withdrawal", False)
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = saved_settings.get("auto_refresh", False)
else:
    # ברירות מחדל אם אין קובץ
    if 'residency_idx' not in st.session_state:
        st.session_state.residency_idx = 1  # יוון
    if 'include_withdrawal' not in st.session_state:
        st.session_state.include_withdrawal = False
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

def lock_previous_months(portfolio, market, eur_ils):
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
            # חישוב ההכנסות לחודש הזה
            base_eur, efrn_eur, greek_eur = calculate_month_income(
                check_date, portfolio, market, eur_ils
            )
            
            # שמירה
            history[month_key] = {
                "base_income": round(base_eur, 2),
                "efrn_bonus": round(efrn_eur, 2),
                "greek_bond": round(greek_eur, 2),
                "total": round(base_eur + efrn_eur + greek_eur, 2),
                "locked_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
            months_locked += 1
        
        # מעבר לחודש הבא
        check_date = check_date + relativedelta(months=1)
    
    # שמירת השינויים
    if months_locked > 0:
        save_income_history(history)
    
    return history, months_locked

def calculate_month_income(month_date, portfolio, market, eur_ils):
    """
    מחשב את ההכנסות עבור חודש ספציפי.
    מחזיר: (base_eur, efrn_eur, greek_eur)
    """
    base_eur = 0
    efrn_eur = 0
    greek_eur = 0
    
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
    
    return base_eur, efrn_eur, greek_eur

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
income_history, months_locked = lock_previous_months(portfolio, market, eur_ils)

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
                     st.session_state.include_withdrawal, 
                     st.session_state.auto_refresh)
    
    st.divider()
    
    # --- משיכה מנכסים צוברים ---
    st.markdown("### 📉 נכסים צוברים")
    include_withdrawal = st.toggle(
        "כלול משיכה מנכסים צוברים (4%)",
        value=st.session_state.include_withdrawal,
        help="משיכה חודשית של 4% שנתי מנכסים צוברים (IBCI) - לפי כלל ה-4% Rule הידוע בקהילת FIRE"
    )
    if include_withdrawal != st.session_state.include_withdrawal:
        st.session_state.include_withdrawal = include_withdrawal
        save_settings(st.session_state.residency_idx, 
                     st.session_state.include_withdrawal, 
                     st.session_state.auto_refresh)
    
    st.divider()
    
    # --- רענון אוטומטי ---
    st.markdown("### 🔄 רענון אוטומטי")
    
    auto_refresh = st.checkbox("הפעל רענון אוטומטי", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        save_settings(st.session_state.residency_idx, 
                     st.session_state.include_withdrawal, 
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

# --- חישוב משיכה מנכסים צוברים (4% Rule) ---
withdrawal_monthly_eur = 0
withdrawal_monthly_gross_eur = 0
withdrawal_tax_eur = 0

if include_withdrawal and accumulating_value_eur > 0:
    # 4% שנתי / 12 חודשים = משיכה חודשית
    withdrawal_annual_eur = accumulating_value_eur * 0.04
    withdrawal_monthly_gross_eur = withdrawal_annual_eur / 12
    
    # הנחה: עלות רכישה = 90% משווי נוכחי (רווח של 10%)
    # זה שמרני - ברוב המקרים הרווח יהיה יותר גבוה
    cost_basis_monthly = withdrawal_monthly_gross_eur * 0.9
    
    # חישוב נטו אחרי מס רווחי הון
    withdrawal_monthly_eur, withdrawal_tax_eur, tax_rate = get_net_income(
        "IBCI",  # נכס צובר = IBCI
        withdrawal_monthly_gross_eur,
        "capital_gain",
        residency,
        cost_basis=cost_basis_monthly
    )
    
    # הוספה להכנסה חודשית (רק ליוון - IBCI הוא נכס יווני)
    monthly_greece_eur_gross += withdrawal_monthly_gross_eur  # ברוטו
    monthly_greece_eur += withdrawal_monthly_eur              # נטו

# --- כותרת ---
st.title("📊 Greek Portfolio Tracker")

# --- מדדים עליונים ---
c1, c2, c3, c4 = st.columns(4)

# monthly_greece_eur ו-monthly_israel_ils כבר נטו! (מחושבים בפונקציה get_net_income)
net_greece_eur = monthly_greece_eur
net_israel_ils = monthly_israel_ils
net_israel_eur = net_israel_ils / eur_ils

# נטו גלובלי
netcasheur_global = net_greece_eur + net_israel_eur
netcashils_global = netcasheur_global * eur_ils

# חישוב אחוז רווח/הפסד כולל (מתחילת ההשקעה)
total_pnl_pct = ((totalvaleur / total_cost_eur) - 1) * 100 if total_cost_eur > 0 else 0

with c1:
    # הצגת שינוי מתחילת החודש
    # תיקון: כשאין שינוי (0), לא מראים חץ
        # תיקון: כשאין שינוי (0), לא מראים חץ
        if monthly_change_eur == 0:
            delta_color = "off"
        elif monthly_change_eur > 0:
            delta_color = "normal"
        else:
            delta_color = "inverse"

    
        # פורמט נכון עם הסימן לפני סמל המטבע
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
    # בניית הכותרת עם אינדיקטור למשיכה
    greece_label = "🇬🇷 הכנסה מנכסי יוון"
    if include_withdrawal and withdrawal_monthly_eur > 0:
        greece_label += " 📉"  # אייקון משיכה
    
    # בניית הדלתא - הצגת נטו
    st.metric(
        greece_label,
        f"€{monthly_greece_eur_gross:,.0f}",  # ברוטו
        f"נטו: €{monthly_greece_eur:,.0f}"    # נטו
    )

with c3:
    st.metric(
        "🇮🇱 הכנסה מנכסי ישראל", 
        f"₪{monthly_israel_ils_gross:,.0f}",  # ברוטו
        f"נטו: ₪{monthly_israel_ils:,.0f}"    # נטו
    )

with c4:
    # בניית הכותרת עם אינדיקטור למשיכה
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
    if residency == "ישראל 🇮🇱":
        # תושב ישראל - יש מס רווחי הון
        st.info(f"📉 משיכה חודשית: €{withdrawal_monthly_gross_eur:,.0f} ברוטו → מס: €{withdrawal_tax_eur:,.0f} → נטו: €{withdrawal_monthly_eur:,.0f} (4% שנתי מנכסים צוברים: €{accumulating_value_eur:,.0f})")
    else:
        # תושב יוון - פטור ממס רווחי הון!
        st.success(f"📉 משיכה חודשית: €{withdrawal_monthly_eur:,.0f} (4% שנתי מנכסים צוברים: €{accumulating_value_eur:,.0f}) | 🎉 פטור ממס רווחי הון ביוון!")

# אזהרה אם זה חודש חדש
if is_new_month:
    st.info("🆕 חודש חדש זוהה! נקודת הייחוס עודכנה אוטומטית.")

st.divider()

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 סקירה כללית", "⚙️ ניהול תיק"])

with tab1:
    # גרף בשורה מלאה
    st.subheader("תזרים מזומנים חודשי")
    
    # שורה עליונה: כפתורי תקופה + ניווט
    col_nav_left, col_ranges, col_nav_right = st.columns([1, 8, 1])
    
    with col_nav_left:
        if st.button("◄ אחורה", use_container_width=True, help="הזז 3 חודשים אחורה"):
            if 'range_offset' not in st.session_state:
                st.session_state.range_offset = 0
            st.session_state.range_offset = max(-18, st.session_state.range_offset - 3)
            st.rerun()
    
    with col_ranges:
        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        
        current_period = st.session_state.get('view_period', 12)
        
        with col_r1:
            if st.button("📅 6 חודשים", use_container_width=True, key="range_6", type="primary" if current_period == 6 else "secondary"):
                st.session_state.view_period = 6
                st.rerun()
        
        with col_r2:
            if st.button("📅 12 חודשים", use_container_width=True, key="range_12", type="primary" if current_period == 12 else "secondary"):
                st.session_state.view_period = 12
                st.rerun()
        
        with col_r3:
            if st.button("📅 18 חודשים", use_container_width=True, key="range_18", type="primary" if current_period == 18 else "secondary"):
                st.session_state.view_period = 18
                st.rerun()
        
        with col_r4:
            if st.button("📅 24 חודשים", use_container_width=True, key="range_24", type="primary" if current_period == 24 else "secondary"):
                st.session_state.view_period = 24
                st.rerun()
        
        with col_r5:
            if st.button("📅 הכל (36)", use_container_width=True, key="range_36", type="primary" if current_period == 36 else "secondary"):
                st.session_state.view_period = 36
                st.session_state.range_offset = 0  # איפוס offset
                st.rerun()
    
    with col_nav_right:
        if st.button("קדימה ►", use_container_width=True, help="הזז 3 חודשים קדימה"):
            if 'range_offset' not in st.session_state:
                st.session_state.range_offset = 0
            st.session_state.range_offset = min(18, st.session_state.range_offset + 3)
            st.rerun()
    
    # שימוש בערך השמור או ברירת מחדל
    if 'view_period' not in st.session_state:
        st.session_state.view_period = 12
    if 'range_offset' not in st.session_state:
        st.session_state.range_offset = 0
    
    view_period = st.session_state.view_period
    range_offset = st.session_state.range_offset
    
    total_months = 36
    start_date = datetime.strptime(portfolio_start_date, "%Y-%m-%d")
    
    # מבנה נתונים לגרף מפולח
    base_income_data = []  # שכבה 1: הכנסה בסיסית
    efrn_income_data = []  # שכבה 2: EFRN רבעוני
    greek_income_data = []  # שכבה 3: Greek Bond שנתי
    
    for i in range(total_months):
        month_date = start_date + relativedelta(months=i)
        month_name = month_date.strftime("%b %y")
        month_key = month_date.strftime("%Y-%m")
        is_current_month = (month_date.year == datetime.now().year and month_date.month == datetime.now().month)
        is_future = month_date > datetime.now()
        is_past = month_date < datetime.now().replace(day=1)  # לפני החודש הנוכחי
        
        # ========== בדיקה אם יש נתון נעול להיסטוריה ==========
        if month_key in income_history:
            # שימוש בנתונים ההיסטוריים הנעולים
            hist_data = income_history[month_key]
            base_eur = hist_data["base_income"]
            efrn_eur = hist_data["efrn_bonus"]
            greek_eur = hist_data["greek_bond"]
            data_source = "🔒 נעול"
        else:
            # חישוב דינמי (חודש נוכחי + עתיד)
            base_eur, efrn_eur, greek_eur = calculate_month_income(month_date, portfolio, market, eur_ils)
            data_source = "📊 חישוב דינמי"
        
        # ========== בניית פירוט לפי מקור הנתונים ==========
        base_breakdown = []
        efrn_breakdown = []
        greek_breakdown = []
        
        if base_eur > 0:
            base_breakdown.append(f"💰 הכנסה בסיסית: €{base_eur:,.0f}")
        
        if efrn_eur > 0:
            quarter_num = {3: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}.get(month_date.month, '')
            efrn_breakdown.append(f"💧 EFRN {quarter_num}: €{efrn_eur:,.0f}")
        
        if greek_eur > 0:
            greek_breakdown.append(f"🏛️ Greek Bond: €{greek_eur:,.0f}")
        
        # opacity לפי סטטוס החודש
        if is_current_month:
            opacity = 1.0
            status = f"📍 חודש נוכחי"
            status_emoji = "📍"
        elif is_future:
            opacity = 0.6
            status = f"📊 הערכה"
            status_emoji = "📊"
        else:
            opacity = 1.0
            status = f"✅ עבר"
            status_emoji = "✅"
        
        # בניית hover texts נפרדים לכל שכבה
        total_month = base_eur + efrn_eur + greek_eur
        
        # Hover לשכבת הבסיס (כחול)
        base_hover_lines = [f"<b>{status}</b>", f"<b>💰 הכנסה בסיסית: €{base_eur:,.0f}</b>"]
        if base_eur > 0:
            # פירוט מקורות
            vecp_row = portfolio[portfolio['Ticker'] == 'VECP']
            if not vecp_row.empty:
                qty = vecp_row.iloc[0]['Quantity']
                price = market.get('VECP', vecp_row.iloc[0]['AvgPrice']) if month_key not in income_history else None
                yrate = vecp_row.iloc[0]['YieldRate']
                vecp_val = (qty * (price if price else market.get('VECP', vecp_row.iloc[0]['AvgPrice'])) * yrate) / 12
                base_hover_lines.append(f"  🏢 VECP: €{vecp_val:,.0f}")
            
            deposit_row = portfolio[portfolio['Ticker'] == 'DEPOSIT_IL']
            if not deposit_row.empty:
                qty = deposit_row.iloc[0]['Quantity']
                yrate = deposit_row.iloc[0]['YieldRate']
                dep_val = (qty * yrate / 12) / eur_ils
                if dep_val > 0:
                    base_hover_lines.append(f"  🏦 פיקדון IL: €{dep_val:,.0f}")
            
            if month_date.month in [6, 12]:
                bond_il_row = portfolio[portfolio['Ticker'] == 'BOND_IL']
                if not bond_il_row.empty:
                    qty = bond_il_row.iloc[0]['Quantity']
                    yrate = bond_il_row.iloc[0]['YieldRate']
                    bond_val = (qty * yrate / 2) / eur_ils
                    if bond_val > 0:
                        base_hover_lines.append(f"  🇮🇱 אג\"ח IL: €{bond_val:,.0f}")
        
        if month_key in income_history:
            base_hover_lines.append("")
            base_hover_lines.append(f"🔒 נעול מ-{income_history[month_key]['locked_date'][:10]}")
        
        base_hover = "<br>".join(base_hover_lines)
        
        # Hover לשכבת EFRN (כתום)
        if efrn_eur > 0:
            quarter_num = {3: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}.get(month_date.month, '')
            efrn_hover_lines = [
                f"<b>{status}</b>",
                f"<b>💧 EFRN רבעון {quarter_num}: €{efrn_eur:,.0f}</b>"
            ]
            if month_key in income_history:
                efrn_hover_lines.append("")
                efrn_hover_lines.append(f"🔒 נעול מ-{income_history[month_key]['locked_date'][:10]}")
            efrn_hover = "<br>".join(efrn_hover_lines)
        else:
            efrn_hover = ""  # ריק = Plotly לא יציג
        
        # Hover לשכבת Greek Bond (ירוק)
        if greek_eur > 0:
            greek_hover_lines = [
                f"<b>{status}</b>",
                f"<b>🏛️ Greek Bond קופון: €{greek_eur:,.0f}</b>"
            ]
            if month_key in income_history:
                greek_hover_lines.append("")
                greek_hover_lines.append(f"🔒 נעול מ-{income_history[month_key]['locked_date'][:10]}")
            greek_hover = "<br>".join(greek_hover_lines)
        else:
            greek_hover = ""  # ריק = Plotly לא יציג
        
        base_income_data.append({
            'month': month_name, 
            'value': round(base_eur, 0), 
            'opacity': opacity, 
            'hover': base_hover,
            'total': round(total_month, 0)
        })
        efrn_income_data.append({
            'month': month_name, 
            'value': round(efrn_eur, 0), 
            'opacity': opacity, 
            'hover': efrn_hover,
            'total': round(total_month, 0)
        })
        greek_income_data.append({
            'month': month_name, 
            'value': round(greek_eur, 0), 
            'opacity': opacity, 
            'hover': greek_hover,
            'total': round(total_month, 0)
        })
    
    # יצירת הגרף המפולח
    months_labels = [d['month'] for d in base_income_data]
    totals = [d['total'] for d in base_income_data]
    
    # חישוב גובה מינימלי - 3% מהגובה המקסימלי
    max_total = max(totals) if totals else 10000
    min_visual_height = max_total * 0.03
    
    fig = go.Figure()
    
    # שכבה 1: בסיס (כחול) - עם גובה מינימלי
    base_values = [d['value'] for d in base_income_data]
    base_values_visual = [max(v, min_visual_height) if v > 0 else 0 for v in base_values]
    
    fig.add_trace(go.Bar(
        name='הכנסה בסיסית',
        x=months_labels,
        y=base_values_visual,
        marker=dict(
            color='#0066cc', 
            opacity=[d['opacity'] for d in base_income_data], 
            line=dict(width=0)
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=[d['hover'] for d in base_income_data],
        hoverinfo='text'
    ))
    
    # שכבה 2: EFRN (כתום)
    efrn_values = [d['value'] for d in efrn_income_data]
    fig.add_trace(go.Bar(
        name='EFRN רבעוני',
        x=months_labels,
        y=efrn_values,
        marker=dict(
            color='#ff9800', 
            opacity=[d['opacity'] for d in efrn_income_data], 
            line=dict(width=0)
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=[d['hover'] for d in efrn_income_data],
        hoverinfo='text'
    ))
    
    # שכבה 3: Greek Bond (ירוק)
    greek_values = [d['value'] for d in greek_income_data]
    fig.add_trace(go.Bar(
        name='Greek Bond (קופון)',
        x=months_labels,
        y=greek_values,
        marker=dict(
            color='#28a745', 
            opacity=[d['opacity'] for d in greek_income_data], 
            line=dict(width=0)
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=[d['hover'] for d in greek_income_data],
        hoverinfo='text'
    ))
    
    # הוספת סכום כולל מעל העמודות
    # חישוב Y מתוקן - מוסיפים 5% מעל הגובה
    max_total = max(totals) if totals else 10000
    y_offset = max_total * 0.05
    
    fig.add_trace(go.Scatter(
        x=months_labels,
        y=[t + y_offset if t > 0 else None for t in totals],
        mode='text',
        text=[f"<b>€{t:,.0f}</b>" if t > 0 else "" for t in totals],
        textposition='top center',
        textfont=dict(size=11, color='#1a1a1a', family='Arial'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # חישוב initial range - מרכוז החודש הנוכחי + offset
    now = datetime.now()
    current_month_index = 0
    
    # מציאת אינדקס החודש הנוכחי
    for i, month_data in enumerate(base_income_data):
        month_date = start_date + relativedelta(months=i)
        if month_date.year == now.year and month_date.month == now.month:
            current_month_index = i
            break
    
    # מרכוז התצוגה סביב החודש הנוכחי + הזזה לפי offset
    half_period = view_period // 2
    range_start = max(0, current_month_index - half_period + range_offset)
    range_end = min(total_months - 1, range_start + view_period - 1)
    
    # תיקון אם הגענו לקצה
    if range_end >= total_months - 1:
        range_start = max(0, total_months - view_period)
        range_end = total_months - 1
    
    if range_start < 0:
        range_start = 0
        range_end = min(total_months - 1, view_period - 1)
    
    initial_range = [range_start - 0.5, range_end + 0.5]
    
    # חישוב Y-max דינמי - לפי הנתונים בתצוגה הנוכחית
    visible_totals = totals[range_start:range_end+1]
    if visible_totals:
        max_visible = max(visible_totals)
        y_max = max_visible * 1.15  # 115% מהמקסימום (קצת מרווח למעלה)
    else:
        y_max = 10000
    
    fig.update_layout(
        barmode='stack',
        yaxis_title="הכנסה חודשית (€)",
        xaxis_title="",
        height=650,
        dragmode=False,  # ביטול גרירה
        hovermode='closest',
        margin=dict(t=30, b=60, l=50, r=20),
        xaxis=dict(
            rangeslider=dict(visible=False),
            fixedrange=True,  # נעילת X - לא ניתן לגרור
            type='category',
            range=initial_range,
            categoryorder='array',
            categoryarray=months_labels
        ),
        yaxis=dict(
            fixedrange=True,  # נעילת Y - לא ניתן לזום או לגרור
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            gridwidth=1,
            range=[0, y_max],  # טווח דינמי
            constraintoward='bottom'
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#ccc",
            borderwidth=1,
            font=dict(size=12)
        ),
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            font_size=11,
            font_family="Arial",
            bordercolor="#0066cc",
            font_color="black",
            align="left",
            namelength=0
        ),
        plot_bgcolor='rgba(250,250,250,0.5)'
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': False,  # ביטול זום עם גלגלת
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
        'doubleClick': 'reset'
    })
    
    st.caption(f"💡 בחר תקופה | השתמש בחיצים לניווט | תקופת נתונים: {portfolio_start_date} עד {(start_date + relativedelta(months=35)).strftime('%Y-%m-%d')}")
    
    # סיכום שנתי מתחת לגרף
    st.markdown("---")
    st.markdown("### 📊 תחזית הכנסות 2026 (פברואר - דצמבר)")
    st.caption("💡 כולל צפי קופונים, דיבידנדים וריבית | חישוב פרו-רטה לפי תאריך רכישה")
    
    # בחירת תצוגה: ברוטו או נטו
    show_net = st.toggle("הצג נטו (אחרי מס)", value=True, key="show_net_2026")
    
    # חישוב סיכומים
    year_2026_months = [i for i, d in enumerate(base_income_data) if '26' in d['month']]
    
    # ברוטו
    total_base_2026_gross = sum([base_income_data[i]['value'] for i in year_2026_months])
    total_efrn_2026_gross = sum([efrn_income_data[i]['value'] for i in year_2026_months])
    total_greek_2026_gross = sum([greek_income_data[i]['value'] for i in year_2026_months])
    
    # חישוב נטו - לפי תושבות
    if residency == "ישראל 🇮🇱":
        # תושב ישראל - 25% על הכל
        total_efrn_2026_net = total_efrn_2026_gross * 0.75
        total_greek_2026_net = total_greek_2026_gross * 1.0  # אג"ח יווני - 25%
        total_base_2026_net = total_base_2026_gross * 0.75
    else:
        # תושב יוון
        # EFRN: 5% (דיבידנד אירי)
        total_efrn_2026_net = total_efrn_2026_gross * 0.95
        
        # Greek Bond: 0% (פטור)
        total_greek_2026_net = total_greek_2026_gross * 1.0
        
        # Base income מעורב:
        # VECP: 15% (הולנד), פיקדון: 15%, אג"ח ישראלי: 15%
        # ממוצע שמרני: 15%
        total_base_2026_net = total_base_2026_gross * 0.85
    
    # בחירת תצוגה
    if show_net:
        total_base_2026 = total_base_2026_net
        total_efrn_2026 = total_efrn_2026_net
        total_greek_2026 = total_greek_2026_net
    else:
        total_base_2026 = total_base_2026_gross
        total_efrn_2026 = total_efrn_2026_gross
        total_greek_2026 = total_greek_2026_gross
    
    total_2026 = total_base_2026 + total_efrn_2026 + total_greek_2026
    
    col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
    
    pct_base = (total_base_2026/total_2026*100) if total_2026 > 0 else 0
    pct_efrn = (total_efrn_2026/total_2026*100) if total_2026 > 0 else 0
    pct_greek = (total_greek_2026/total_2026*100) if total_2026 > 0 else 0
    
    with col_summary1:
        st.metric("💰 הכנסה בסיסית", f"€{total_base_2026:,.0f}")
        st.caption(f"📊 {pct_base:.1f}% מסך ההכנסה")
    
    with col_summary2:
        st.metric("💧 EFRN רבעוני", f"€{total_efrn_2026:,.0f}")
        st.caption(f"📊 {pct_efrn:.1f}% מסך ההכנסה")
    
    with col_summary3:
        st.metric("🏛️ Greek Bond", f"€{total_greek_2026:,.0f}")
        st.caption(f"📊 {pct_greek:.1f}% מסך ההכנסה")
    
    with col_summary4:
        st.metric("📈 סה\"כ צפוי", f"€{total_2026:,.0f}")
        st.caption("📊 100% מסך ההכנסה")
    
    # פירוט נכסים בשורה נפרדת
    st.markdown("---")
    st.subheader("📋 פירוט נכסים בתיק")
    
    cols_assets = st.columns(3)
    
    for idx, row in enumerate(table_rows):
        col_idx = idx % 3
        with cols_assets[col_idx]:
            desc = descriptions.get(row['Ticker'], "אין מידע")
            with st.expander(f"{row['שווי']} - {row['נכס']}"):
                st.markdown(f'<div class="rtl-box">{desc}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("מעקב ביצועים ורווח/הפסד")
    
    if len(table_rows) > 0:
        # טבלה לתצוגה
        st.markdown("### 📊 סיכום ביצועים")
        detailed_df = pd.DataFrame(table_rows)
        detailed_df = detailed_df.sort_values('קבוצה', ascending=False)
        display_df = detailed_df[['קבוצה', 'נכס', 'תאריך רכישה', 'שווי', 'רווח', 'שינוי (%)', 'נוכחי']].copy()
        
        def color_pnl(val):
            if isinstance(val, (int, float)):
                return f'color: {"green" if val > 0 else "red"}'
            return ''
        
        st.dataframe(
            display_df.style.format({"שינוי (%)": "{:.2f}%"}).map(color_pnl, subset=['שינוי (%)']),
            use_container_width=True,
            height=350
        )
        
        st.divider()
        
        # עדכון כמויות מהיר
        st.markdown("### ⚡ עדכון כמויות מהיר")
        st.warning("⚠️ **שים לב**: שינוי כמויות ישפיע על רווח/הפסד כי מחיר הקנייה הממוצע יישאר זהה.")
        
        cols = st.columns(len(portfolio))
        new_quantities = {}
        
        for idx, (col, (i, row)) in enumerate(zip(cols, portfolio.iterrows())):
            with col:
                st.caption(f"**{row['Name']}**")
                new_qty = st.number_input(
                    "כמות:",
                    min_value=0,
                    value=int(row['Quantity']),
                    step=1,
                    key=f"qty_{row['Ticker']}",
                    label_visibility="collapsed"
                )
                new_quantities[i] = new_qty
                
                if new_qty != row['Quantity']:
                    diff = new_qty - row['Quantity']
                    st.metric("שינוי", f"{diff:+d}", delta_color="off")
        
        if st.button("💾 עדכן כמויות", type="primary", use_container_width=True):
            for idx, new_qty in new_quantities.items():
                portfolio.at[idx, 'Quantity'] = new_qty
            portfolio.to_csv("holdings.csv", index=False)
            st.success("✅ הכמויות עודכנו!")
            time.sleep(1)
            st.rerun()
        
        st.divider()
        
        # עריכה מתקדמת
        with st.expander("🔧 עריכה מתקדמת (כל השדות)"):
            st.info("💡 ערוך כל פרט: כמויות, מחירים, תאריכים, תשואות.")
            
            edited = st.data_editor(
                portfolio,
                num_rows="dynamic",
                use_container_width=True,
                key="portfolio_editor",
                column_config={
                    "Ticker": st.column_config.TextColumn("טיקר", disabled=True, width="small"),
                    "Name": st.column_config.TextColumn("שם נכס", width="medium"),
                    "Quantity": st.column_config.NumberColumn("כמות", format="%d", width="small"),
                    "AvgPrice": st.column_config.NumberColumn("מחיר קנייה", format="%.2f", width="small"),
                    "Currency": st.column_config.SelectboxColumn("מטבע", options=["EUR", "ILS"], width="small"),
                    "YieldType": st.column_config.SelectboxColumn("סוג תשואה", options=["Coupon", "Dividend", "Interest", "Capital"], width="small"),
                    "YieldRate": st.column_config.NumberColumn("שיעור תשואה", format="%.4f", help="כעשרוני (3.5% = 0.035)", width="small"),
                    "PurchaseDate": st.column_config.TextColumn("תאריך רכישה", help="פורמט: YYYY-MM-DD", width="medium")
                },
                height=350
            )
            
            col_save, col_cancel, col_reset = st.columns(3)
            
            with col_save:
                if st.button("💾 שמור הכל", type="primary", use_container_width=True, key="save_all"):
                    try:
                        for date_str in edited['PurchaseDate']:
                            datetime.strptime(date_str, "%Y-%m-%d")
                        
                        edited.to_csv("holdings.csv", index=False)
                        st.success("✅ כל השינויים נשמרו!")
                        time.sleep(1)
                        st.rerun()
                    except ValueError:
                        st.error("❌ תאריך לא תקין. השתמש בפורמט YYYY-MM-DD")
            
            with col_cancel:
                if st.button("↩️ בטל", type="secondary", use_container_width=True):
                    st.rerun()
            
            with col_reset:
                if st.button("🗑️ אפס תיק", type="secondary", use_container_width=True):
                    if os.path.exists("holdings.csv"):
                        os.remove("holdings.csv")
                        st.success("✅ התיק נמחק! רענן את העמוד.")
                        time.sleep(1)
                        st.rerun()
    
    else:
        st.warning("⚠️ אין נתונים להצגה.")
