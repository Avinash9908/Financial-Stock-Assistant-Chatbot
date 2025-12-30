import json
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import hashlib
import re
import os

# Read API key
with open('API_KEY', 'r') as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)

# -------- USER AUTHENTICATION -------- #
# User database file
USER_DB_FILE = 'users_db.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default users
        default_users = {
            "admin": hashlib.sha256("admin123".encode()).hexdigest(),
            "demo": hashlib.sha256("demo123".encode()).hexdigest()
        }
        save_users(default_users)
        return default_users

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

def validate_username(username):
    """Validate username: only letters, no numbers or special characters"""
    if not username:
        return False, "Username cannot be empty"
    if not re.match(r'^[a-zA-Z]+$', username):
        return False, "Username must contain only letters (no numbers or special characters)"
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    return True, "Valid"

def validate_password(password):
    """Validate password: at least 6 characters, can contain special characters"""
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Valid"

def register_user(username, password):
    """Register a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    # Hash password and save
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = hashed_password
    save_users(users)
    return True, "Registration successful!"

def verify_login(username, password):
    """Verify login credentials"""
    users = load_users()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return username in users and users[username] == hashed_password

def login_register_page():
    st.markdown("""
    <style>
        .auth-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 3rem 2rem;
            background: #1a1a1a;
            border-radius: 4px;
            border: 1px solid #2a2a2a;
            margin-top: 3rem;
        }
        .auth-title {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2rem !important;
        }
        .tab-container {
            display: flex;
            margin-bottom: 2rem;
            border-bottom: 1px solid #2a2a2a;
        }
        .success-message {
            background: #0a3a0a !important;
            border: 1px solid #2a6a2a !important;
            color: #66ff66 !important;
            padding: 0.75rem;
            border-radius: 2px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">📈 Stock Analysis</h1>', unsafe_allow_html=True)
    
    # Tab selection
    tab = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    
    if tab == "Login":
        st.markdown("### Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Login", use_container_width=True):
                if verify_login(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['current_page'] = 'Home'
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        

    
    else:  # Register
        st.markdown("### Create New Account")
        new_username = st.text_input("Username (letters only)", key="reg_username")
        new_password = st.text_input("Password (min 6 chars, must include number)", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        # Show validation hints
        if new_username:
            valid, msg = validate_username(new_username)
            if not valid:
                st.warning(msg)
        
        if new_password:
            valid, msg = validate_password(new_password)
            if not valid:
                st.warning(msg)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Register", use_container_width=True):
                # Validate username
                valid_user, user_msg = validate_username(new_username)
                if not valid_user:
                    st.error(user_msg)
                    return
                
                # Validate password
                valid_pass, pass_msg = validate_password(new_password)
                if not valid_pass:
                    st.error(pass_msg)
                    return
                
                # Check password match
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
                
                # Register user
                success, message = register_user(new_username, new_password)
                if success:
                    st.markdown(f'<div class="success-message">✓ {message} You can now login.</div>', unsafe_allow_html=True)
                else:
                    st.error(message)
        
        st.markdown("---")
        st.markdown("**Username Rules:** Letters only, no numbers or special characters")
        st.markdown("**Password Rules:** Min 6 characters, must include letters and numbers")
    
    st.markdown("</div>", unsafe_allow_html=True)

# -------- CUSTOM CSS FOR DARK MINIMALIST DESIGN -------- #
st.markdown("""
<style>
    /* Dark minimalist background */
    .stApp {
        background: #0a0a0a;
        background-attachment: fixed;
    }
    
    /* Title styling - bold minimal */
    h1 {
        color: #ffffff !important;
        font-weight: 300 !important;
        padding: 3rem 0 1rem 0;
        font-size: 3rem !important;
        letter-spacing: -1px;
        border-bottom: 1px solid #1a1a1a;
        margin-bottom: 2rem;
    }
    
    h2, h3 {
        color: #ffffff !important;
        font-weight: 300 !important;
    }
    
    /* Input field styling - dark minimal */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 2px !important;
        padding: 14px 18px !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #666666 !important;
    }
    
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
        border: 1px solid #404040 !important;
        box-shadow: none !important;
        outline: none !important;
        background: #151515 !important;
    }
    
    /* Label styling - minimal uppercase */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        color: #999999 !important;
        font-weight: 400 !important;
        font-size: 0.75rem !important;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Text styling */
    p {
        color: #cccccc !important;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    
    /* Error message styling */
    .stAlert {
        background: #1a0a0a !important;
        border: 1px solid #4a2020 !important;
        border-radius: 2px !important;
        color: #ff6b6b !important;
        padding: 1rem;
    }
    
    /* Image container - dark card */
    .stImage {
        border-radius: 2px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border: 1px solid #1a1a1a;
        background: #0f0f0f;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Code blocks */
    code {
        background: #1a1a1a !important;
        color: #ffffff !important;
        padding: 3px 8px;
        border-radius: 2px;
        border: 1px solid #2a2a2a;
        font-size: 0.9em;
    }
    
    /* Accent color for emphasis */
    strong {
        color: #b8860b !important;
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    
    /* Button styling */
    .stButton > button {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 2px !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #2a2a2a !important;
        border-color: #404040 !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: #0a0a0a;
        padding: 0.5rem;
        border-radius: 2px;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 2px !important;
    }
    
    /* Metric card styling */
    [data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #999999 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------- STOCK FUNCTIONS -------- #

def get_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    if data.empty:
        return None, "Error: No data found for this ticker."
    return data.iloc[-1].Close, None


def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    if data.empty:
        return None, "Error: No data found for this ticker."
    sma_values = data.rolling(window=window).mean()
    return sma_values, None


def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y').Close
    if data.empty:
        return None, "Error: No data found for this ticker."
    ema_values = data.ewm(span=window, adjust=False).mean()
    return ema_values, None


def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    if data.empty:
        return None, None, "Error: No data found for this ticker."

    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)

    ema_up = up.ewm(com=14-1, adjust=False).mean()
    ema_down = down.ewm(com=14-1, adjust=False).mean()

    rs = ema_up / ema_down
    rsi_values = 100 - (100 / (1 + rs))
    return rsi_values.iloc[-1], rsi_values, None


def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period='1y').Close
    if data.empty:
        return None, None, None, None, "Error: No data found for this ticker."

    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    histogram = MACD - signal

    return MACD.iloc[-1], signal.iloc[-1], histogram.iloc[-1], (MACD, signal, histogram, data.index), None


def plot_indicator(ticker, indicator_name, data, window=None):
    """Plot technical indicator with price"""
    plt.style.use('dark_background')
    
    if indicator_name in ['SMA', 'EMA']:
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        # Get price data
        price_data = yf.Ticker(ticker).history(period='1y').Close
        
        # Plot price
        ax.plot(price_data.index, price_data.values, color='#ffffff', linewidth=1.5, alpha=0.6, label='Price')
        # Plot indicator
        ax.plot(data.index, data.values, color='#00ff88', linewidth=2, label=f'{indicator_name}({window})')
        
        ax.set_title(f"{ticker} - {indicator_name}({window})", color='#ffffff', fontsize=16, fontweight='300', pad=20)
        ax.set_ylabel("Price ($)", color='#666666', fontsize=10)
        ax.legend(loc='upper left', framealpha=0.2)
        
    elif indicator_name == 'RSI':
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
        fig.patch.set_facecolor('#0a0a0a')
        
        # Price plot
        price_data = yf.Ticker(ticker).history(period='1y').Close
        ax1.set_facecolor('#0a0a0a')
        ax1.plot(price_data.index, price_data.values, color='#ffffff', linewidth=1.5, alpha=0.9)
        ax1.set_title(f"{ticker} - Price", color='#ffffff', fontsize=14, fontweight='300', pad=15)
        ax1.set_ylabel("Price ($)", color='#666666', fontsize=10)
        ax1.grid(True, alpha=0.1, color='#2a2a2a')
        ax1.tick_params(colors='#666666', labelsize=8)
        
        # RSI plot
        ax2.set_facecolor('#0a0a0a')
        ax2.plot(data.index, data.values, color='#00ff88', linewidth=2)
        ax2.axhline(y=70, color='#ff4444', linestyle='--', alpha=0.5, label='Overbought')
        ax2.axhline(y=30, color='#ff4444', linestyle='--', alpha=0.5, label='Oversold')
        ax2.fill_between(data.index, 30, 70, alpha=0.1, color='#ffaa00')
        ax2.set_title("RSI", color='#ffffff', fontsize=14, fontweight='300', pad=15)
        ax2.set_ylabel("RSI", color='#666666', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.legend(loc='upper left', framealpha=0.2)
        ax2.grid(True, alpha=0.1, color='#2a2a2a')
        ax2.tick_params(colors='#666666', labelsize=8)
        
    elif indicator_name == 'MACD':
        macd_line, signal_line, histogram, dates = data
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
        fig.patch.set_facecolor('#0a0a0a')
        
        # Price plot
        price_data = yf.Ticker(ticker).history(period='1y').Close
        ax1.set_facecolor('#0a0a0a')
        ax1.plot(price_data.index, price_data.values, color='#ffffff', linewidth=1.5, alpha=0.9)
        ax1.set_title(f"{ticker} - Price", color='#ffffff', fontsize=14, fontweight='300', pad=15)
        ax1.set_ylabel("Price ($)", color='#666666', fontsize=10)
        ax1.grid(True, alpha=0.1, color='#2a2a2a')
        ax1.tick_params(colors='#666666', labelsize=8)
        
        # MACD plot
        ax2.set_facecolor('#0a0a0a')
        ax2.plot(dates, macd_line.values, color='#00ff88', linewidth=2, label='MACD')
        ax2.plot(dates, signal_line.values, color='#ff6b6b', linewidth=2, label='Signal')
        colors = ['#00ff88' if h > 0 else '#ff4444' for h in histogram.values]
        ax2.bar(dates, histogram.values, color=colors, alpha=0.3, label='Histogram')
        ax2.axhline(y=0, color='#666666', linestyle='-', alpha=0.3)
        ax2.set_title("MACD", color='#ffffff', fontsize=14, fontweight='300', pad=15)
        ax2.set_ylabel("MACD", color='#666666', fontsize=10)
        ax2.legend(loc='upper left', framealpha=0.2)
        ax2.grid(True, alpha=0.1, color='#2a2a2a')
        ax2.tick_params(colors='#666666', labelsize=8)
    
    # Common styling
    for ax in fig.get_axes():
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1a1a1a')
        ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    if data.empty:
        return None, "Error: No data found for this ticker."

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    ax.plot(data.index, data.Close, color='#ffffff', linewidth=1.5, alpha=0.9)
    
    ax.set_title(f"{ticker} - Last Year Performance", color='#ffffff', fontsize=16, fontweight='300', pad=20)
    ax.set_ylabel("Price ($)", color='#666666', fontsize=10)
    ax.tick_params(colors='#666666', labelsize=8)
    ax.grid(True, alpha=0.1, color='#2a2a2a', linestyle='-', linewidth=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#1a1a1a')
    ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig, None


def get_stock_recommendation(ticker):
    """Analyzes stock and returns recommendation data"""
    try:
        data = yf.Ticker(ticker).history(period='1y')
        if data.empty:
            return None, "Error: No data found for this ticker."
        
        # Calculate indicators
        current_price = data.Close.iloc[-1]
        sma_50 = data.Close.rolling(window=50).mean().iloc[-1]
        sma_200 = data.Close.rolling(window=200).mean().iloc[-1]
        
        # RSI
        delta = data.Close.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # MACD
        ema_12 = data.Close.ewm(span=12, adjust=False).mean()
        ema_26 = data.Close.ewm(span=26, adjust=False).mean()
        macd = ema_12.iloc[-1] - ema_26.iloc[-1]
        signal = (ema_12 - ema_26).ewm(span=9, adjust=False).mean().iloc[-1]
        
        # Scoring
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        if current_price > sma_50 > sma_200:
            buy_signals += 2
            reasons.append("Strong uptrend: Price above 50-day and 200-day SMA")
        elif current_price < sma_50 < sma_200:
            sell_signals += 2
            reasons.append("Strong downtrend: Price below 50-day and 200-day SMA")
        elif current_price > sma_50:
            buy_signals += 1
            reasons.append("Price above 50-day SMA")
        else:
            sell_signals += 1
            reasons.append("Price below 50-day SMA")
        
        if rsi < 30:
            buy_signals += 2
            reasons.append(f"RSI indicates oversold ({rsi:.2f})")
        elif rsi > 70:
            sell_signals += 2
            reasons.append(f"RSI indicates overbought ({rsi:.2f})")
        elif rsi < 45:
            buy_signals += 1
            reasons.append(f"RSI moderately low ({rsi:.2f})")
        elif rsi > 55:
            sell_signals += 1
            reasons.append(f"RSI moderately high ({rsi:.2f})")
        
        if macd > signal:
            buy_signals += 1
            reasons.append("MACD above signal line (bullish)")
        else:
            sell_signals += 1
            reasons.append("MACD below signal line (bearish)")
        
        recent_volume = data.Volume.iloc[-5:].mean()
        avg_volume = data.Volume.mean()
        if recent_volume > avg_volume * 1.2:
            reasons.append("Above average volume detected")
        
        if buy_signals > sell_signals + 1:
            recommendation = "BUY"
            confidence = "High" if buy_signals >= 4 else "Moderate"
        elif sell_signals > buy_signals + 1:
            recommendation = "SELL"
            confidence = "High" if sell_signals >= 4 else "Moderate"
        else:
            recommendation = "HOLD"
            confidence = "Neutral"
        
        fig = plot_recommendation_visual(ticker, recommendation, confidence, buy_signals, sell_signals, rsi, current_price)
        
        result = {
            "ticker": ticker,
            "recommendation": recommendation,
            "confidence": confidence,
            "current_price": round(current_price, 2),
            "rsi": round(rsi, 2),
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "reasons": reasons,
            "fig": fig
        }
        
        return result, None
        
    except Exception as e:
        return None, f"Error analyzing stock: {str(e)}"


def plot_recommendation_visual(ticker, recommendation, confidence, buy_signals, sell_signals, rsi, current_price):
    """Creates recommendation visualization"""
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor('#0a0a0a')
    
    gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
    
    # Main recommendation
    ax_main = fig.add_subplot(gs[0, :])
    ax_main.set_facecolor('#0a0a0a')
    ax_main.axis('off')
    
    if recommendation == "BUY":
        color = '#00ff88'
        emoji = '📈'
    elif recommendation == "SELL":
        color = '#ff4444'
        emoji = '📉'
    else:
        color = '#ffaa00'
        emoji = '⏸️'
    
    ax_main.text(0.5, 0.7, f"{emoji} {recommendation}", 
                ha='center', va='center', fontsize=48, fontweight='bold', color=color)
    ax_main.text(0.5, 0.3, f"Confidence: {confidence}", 
                ha='center', va='center', fontsize=20, color='#ffffff', alpha=0.8)
    ax_main.text(0.5, 0.1, f"{ticker} - ${current_price:.2f}", 
                ha='center', va='center', fontsize=16, color='#999999')
    
    # Signal bars
    ax_signals = fig.add_subplot(gs[1, 0])
    ax_signals.set_facecolor('#0a0a0a')
    
    signals = ['Buy\nSignals', 'Sell\nSignals']
    values = [buy_signals, sell_signals]
    colors_bar = ['#00ff88', '#ff4444']
    
    bars = ax_signals.bar(signals, values, color=colors_bar, alpha=0.7, edgecolor='#1a1a1a', linewidth=2)
    ax_signals.set_ylabel('Signal Count', color='#666666', fontsize=10)
    ax_signals.set_title('Signal Strength', color='#ffffff', fontsize=12, fontweight='300', pad=15)
    ax_signals.tick_params(colors='#666666', labelsize=9)
    ax_signals.spines['top'].set_visible(False)
    ax_signals.spines['right'].set_visible(False)
    ax_signals.spines['left'].set_color('#1a1a1a')
    ax_signals.spines['bottom'].set_color('#1a1a1a')
    ax_signals.grid(True, alpha=0.1, color='#2a2a2a', axis='y')
    ax_signals.set_ylim(0, max(values) + 2)
    
    for bar in bars:
        height = bar.get_height()
        ax_signals.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', color='#ffffff', fontsize=12, fontweight='bold')
    
    # RSI Gauge
    ax_rsi = fig.add_subplot(gs[1, 1])
    ax_rsi.set_facecolor('#0a0a0a')
    
    rsi_zones = ['Oversold\n(<30)', 'Neutral\n(30-70)', 'Overbought\n(>70)']
    zone_colors = ['#00ff88', '#ffaa00', '#ff4444']
    zone_values = [30, 40, 30]
    
    bars_rsi = ax_rsi.barh(rsi_zones, zone_values, color=zone_colors, alpha=0.3, 
                           edgecolor='#1a1a1a', linewidth=1)
    
    if rsi < 30:
        zone_idx = 0
        position = (rsi / 30) * 30
    elif rsi <= 70:
        zone_idx = 1
        position = 30 + ((rsi - 30) / 40) * 40
    else:
        zone_idx = 2
        position = 70 + ((min(rsi, 100) - 70) / 30) * 30
    
    ax_rsi.plot([position], [zone_idx], 'o', markersize=15, color='#ffffff', 
                markeredgecolor=zone_colors[zone_idx], markeredgewidth=3, zorder=5)
    
    ax_rsi.set_xlabel('RSI Value', color='#666666', fontsize=10)
    ax_rsi.set_title(f'RSI: {rsi:.1f}', color='#ffffff', fontsize=12, fontweight='300', pad=15)
    ax_rsi.tick_params(colors='#666666', labelsize=9)
    ax_rsi.spines['top'].set_visible(False)
    ax_rsi.spines['right'].set_visible(False)
    ax_rsi.spines['left'].set_color('#1a1a1a')
    ax_rsi.spines['bottom'].set_color('#1a1a1a')
    ax_rsi.set_xlim(0, 100)
    ax_rsi.grid(True, alpha=0.1, color='#2a2a2a', axis='x')
    
    # Recommendation meter
    ax_meter = fig.add_subplot(gs[2, :])
    ax_meter.set_facecolor('#0a0a0a')
    ax_meter.set_xlim(0, 10)
    ax_meter.set_ylim(0, 1)
    ax_meter.axis('off')
    
    meter_width = 8
    meter_x = 1
    
    ax_meter.barh(0.5, 3, left=meter_x, height=0.3, color='#ff4444', alpha=0.3)
    ax_meter.barh(0.5, 3, left=meter_x+3, height=0.3, color='#ffaa00', alpha=0.3)
    ax_meter.barh(0.5, 2, left=meter_x+6, height=0.3, color='#00ff88', alpha=0.3)
    
    total_signals = buy_signals + sell_signals
    if total_signals > 0:
        buy_ratio = buy_signals / total_signals
        needle_pos = meter_x + (buy_ratio * meter_width)
    else:
        needle_pos = meter_x + meter_width / 2
    
    ax_meter.plot([needle_pos, needle_pos], [0.2, 0.8], 'w-', linewidth=3, zorder=5)
    ax_meter.plot([needle_pos], [0.5], 'o', markersize=12, color='#ffffff', zorder=6)
    
    ax_meter.text(meter_x + 1.5, 0.1, 'SELL', ha='center', color='#ff4444', fontsize=12, fontweight='bold')
    ax_meter.text(meter_x + 4.5, 0.1, 'HOLD', ha='center', color='#ffaa00', fontsize=12, fontweight='bold')
    ax_meter.text(meter_x + 7, 0.1, 'BUY', ha='center', color='#00ff88', fontsize=12, fontweight='bold')
    ax_meter.text(5, 0.95, 'Recommendation Meter', ha='center', color='#ffffff', fontsize=14, fontweight='300')
    
    plt.tight_layout()
    return fig


# -------- PAGE FUNCTIONS -------- #

def show_home_page():
    """Home page with chatbot"""
    st.title('📈 Stock Analysis Chatbot Assistant')
    
    user_input = st.text_input('Your message:', placeholder='e.g., Should I buy AAPL stock?', key='chatbot_input')

    if user_input:
        try:
            st.session_state['messages'].append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state['messages'],
                tools=[{"type": "function", "function": f} for f in functions],
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                st.session_state['messages'].append(response_message)

                for call in tool_calls:
                    function_name = call.function.name
                    args = json.loads(call.function.arguments)

                    if function_name == "plot_stock_price_chatbot":
                        fig, error = plot_stock_price(args['ticker'])
                        if error:
                            st.error(error)
                        else:
                            st.pyplot(fig)
                        result = "Chart displayed" if not error else error
                    elif function_name == "get_stock_recommendation_chatbot":
                        rec_data, error = get_stock_recommendation(args['ticker'])
                        if error:
                            st.error(error)
                            result = error
                        else:
                            st.pyplot(rec_data['fig'])
                            result = json.dumps({k: v for k, v in rec_data.items() if k != 'fig'})
                    else:
                        result = f"Function {function_name} not found"
                    
                    st.session_state['messages'].append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": function_name,
                        "content": str(result)
                    })

                final = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state['messages']
                )
                msg = final.choices[0].message.content
                st.write(msg)
                st.session_state['messages'].append({"role": "assistant", "content": msg})

            else:
                msg = response_message.content
                st.write(msg)
                st.session_state['messages'].append({"role": "assistant", "content": msg})

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def show_price_lookup_page():
    """Stock price lookup page"""
    st.title('💰 Stock Price Lookup')
    
    st.info('💡 **Tip**: For Indian stocks, add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`). For US stocks, use ticker directly (e.g., `AAPL`, `TSLA`).')
    
    ticker = st.text_input('Enter Stock Ticker Symbol (e.g., AAPL, RELIANCE.NS):', key='price_ticker').upper()
    
    if st.button('Get Price', key='price_btn'):
        if ticker:
            with st.spinner('Fetching price...'):
                price, error = get_stock_price(ticker)
                if error:
                    st.error(error)
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label=f"{ticker} Current Price", value=f"${price:.2f}")
                    
                    with col2:
                        # Get 1-day change
                        data = yf.Ticker(ticker).history(period='5d')
                        if len(data) >= 2:
                            change = ((data.Close.iloc[-1] - data.Close.iloc[-2]) / data.Close.iloc[-2]) * 100
                            st.metric(label="1-Day Change", value=f"{change:+.2f}%")
                    
                    # Plot price
                    fig, error = plot_stock_price(ticker)
                    if not error:
                        st.pyplot(fig)
        else:
            st.warning('Please enter a ticker symbol')


def show_technical_indicators_page():
    """Technical indicators page"""
    st.title('📊 Technical Indicators')
    
    st.info('💡 **Tip**: For Indian stocks, add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`). For US stocks, use ticker directly (e.g., `AAPL`, `TSLA`).')
    
    ticker = st.text_input('Enter Stock Ticker Symbol:', key='ti_ticker').upper()
    
    indicator = st.selectbox(
        'Select Indicator:',
        ['SMA (Simple Moving Average)', 'EMA (Exponential Moving Average)', 'RSI (Relative Strength Index)', 'MACD']
    )
    
    window = None
    if 'SMA' in indicator or 'EMA' in indicator:
        window = st.number_input('Window Period:', min_value=5, max_value=200, value=50, step=5, key='ti_window')
    
    if st.button('Calculate Indicator', key='ti_btn'):
        if ticker:
            with st.spinner('Calculating...'):
                if 'SMA' in indicator:
                    data, error = calculate_SMA(ticker, window)
                    if error:
                        st.error(error)
                    else:
                        current_value = data.iloc[-1]
                        st.success(f'**{indicator}({window})**: ${current_value:.2f}')
                        fig = plot_indicator(ticker, 'SMA', data, window)
                        st.pyplot(fig)
                        
                elif 'EMA' in indicator:
                    data, error = calculate_EMA(ticker, window)
                    if error:
                        st.error(error)
                    else:
                        current_value = data.iloc[-1]
                        st.success(f'**{indicator}({window})**: ${current_value:.2f}')
                        fig = plot_indicator(ticker, 'EMA', data, window)
                        st.pyplot(fig)
                        
                elif 'RSI' in indicator:
                    current_rsi, rsi_data, error = calculate_RSI(ticker)
                    if error:
                        st.error(error)
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Current RSI", value=f"{current_rsi:.2f}")
                        with col2:
                            if current_rsi < 30:
                                st.success("🟢 Oversold - Potential Buy Signal")
                            elif current_rsi > 70:
                                st.error("🔴 Overbought - Potential Sell Signal")
                            else:
                                st.info("🟡 Neutral")
                        
                        fig = plot_indicator(ticker, 'RSI', rsi_data)
                        st.pyplot(fig)
                        
                elif 'MACD' in indicator:
                    macd_val, signal_val, hist_val, plot_data, error = calculate_MACD(ticker)
                    if error:
                        st.error(error)
                    else:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="MACD", value=f"{macd_val:.2f}")
                        with col2:
                            st.metric(label="Signal", value=f"{signal_val:.2f}")
                        with col3:
                            st.metric(label="Histogram", value=f"{hist_val:.2f}")
                        
                        if macd_val > signal_val:
                            st.success("🟢 MACD above Signal - Bullish")
                        else:
                            st.error("🔴 MACD below Signal - Bearish")
                        
                        fig = plot_indicator(ticker, 'MACD', plot_data)
                        st.pyplot(fig)
        else:
            st.warning('Please enter a ticker symbol')


def plot_candlestick_chart(ticker, period='3mo'):
    """Create candlestick chart"""
    data = yf.Ticker(ticker).history(period=period)
    if data.empty:
        return None, "Error: No data found for this ticker."
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Create candlestick chart
    for idx, (date, row) in enumerate(data.iterrows()):
        color = '#00ff88' if row['Close'] >= row['Open'] else '#ff4444'
        
        # Draw the wick (high-low line)
        ax.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1, alpha=0.8)
        
        # Draw the body (open-close rectangle)
        height = abs(row['Close'] - row['Open'])
        bottom = min(row['Open'], row['Close'])
        ax.bar(idx, height, bottom=bottom, color=color, width=0.8, alpha=0.9, edgecolor=color)
    
    # Formatting
    ax.set_title(f"{ticker} - Candlestick Chart", color='#ffffff', fontsize=16, fontweight='300', pad=20)
    ax.set_ylabel("Price", color='#666666', fontsize=10)
    ax.tick_params(colors='#666666', labelsize=8)
    ax.grid(True, alpha=0.1, color='#2a2a2a', linestyle='-', linewidth=0.5)
    
    # Set x-axis labels
    step = max(len(data) // 10, 1)
    ax.set_xticks(range(0, len(data), step))
    ax.set_xticklabels([data.index[i].strftime('%m/%d') for i in range(0, len(data), step)], rotation=45)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#1a1a1a')
    ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig, None


def plot_line_chart(ticker, period='1y'):
    """Create line chart"""
    data = yf.Ticker(ticker).history(period=period)
    if data.empty:
        return None, "Error: No data found for this ticker."
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Plot closing price line
    ax.plot(data.index, data.Close, color='#00ff88', linewidth=2, alpha=0.9, label='Close Price')
    
    # Add moving averages
    ma20 = data.Close.rolling(window=20).mean()
    ma50 = data.Close.rolling(window=50).mean()
    ax.plot(data.index, ma20, color='#ffaa00', linewidth=1.5, alpha=0.7, label='MA(20)', linestyle='--')
    ax.plot(data.index, ma50, color='#ff6b6b', linewidth=1.5, alpha=0.7, label='MA(50)', linestyle='--')
    
    ax.set_title(f"{ticker} - Line Chart with Moving Averages", color='#ffffff', fontsize=16, fontweight='300', pad=20)
    ax.set_ylabel("Price", color='#666666', fontsize=10)
    ax.legend(loc='upper left', framealpha=0.2, fontsize=9)
    ax.tick_params(colors='#666666', labelsize=8)
    ax.grid(True, alpha=0.1, color='#2a2a2a', linestyle='-', linewidth=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#1a1a1a')
    ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig, None


def plot_bar_chart(ticker, period='3mo'):
    """Create volume bar chart with price overlay"""
    data = yf.Ticker(ticker).history(period=period)
    if data.empty:
        return None, "Error: No data found for this ticker."
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1], sharex=True)
    fig.patch.set_facecolor('#0a0a0a')
    
    # Price bars (top)
    ax1.set_facecolor('#0a0a0a')
    colors = ['#00ff88' if close >= open_ else '#ff4444' 
              for close, open_ in zip(data.Close, data.Open)]
    
    ax1.bar(range(len(data)), data.Close, color=colors, alpha=0.7, width=0.8)
    ax1.set_title(f"{ticker} - Bar Chart (Price & Volume)", color='#ffffff', fontsize=16, fontweight='300', pad=20)
    ax1.set_ylabel("Price", color='#666666', fontsize=10)
    ax1.tick_params(colors='#666666', labelsize=8)
    ax1.grid(True, alpha=0.1, color='#2a2a2a', axis='y')
    
    # Volume bars (bottom)
    ax2.set_facecolor('#0a0a0a')
    ax2.bar(range(len(data)), data.Volume, color=colors, alpha=0.5, width=0.8)
    ax2.set_ylabel("Volume", color='#666666', fontsize=10)
    ax2.tick_params(colors='#666666', labelsize=8)
    ax2.grid(True, alpha=0.1, color='#2a2a2a', axis='y')
    
    # Set x-axis labels
    step = max(len(data) // 10, 1)
    ax2.set_xticks(range(0, len(data), step))
    ax2.set_xticklabels([data.index[i].strftime('%m/%d') for i in range(0, len(data), step)], rotation=45)
    
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1a1a1a')
        ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig, None


def plot_ohlc_chart(ticker, period='3mo'):
    """Create OHLC (Open-High-Low-Close) chart"""
    data = yf.Ticker(ticker).history(period=period)
    if data.empty:
        return None, "Error: No data found for this ticker."
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Create OHLC chart
    for idx, (date, row) in enumerate(data.iterrows()):
        color = '#00ff88' if row['Close'] >= row['Open'] else '#ff4444'
        
        # Draw high-low line
        ax.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1.5, alpha=0.9)
        
        # Draw open tick (left)
        ax.plot([idx - 0.3, idx], [row['Open'], row['Open']], color=color, linewidth=2, alpha=0.9)
        
        # Draw close tick (right)
        ax.plot([idx, idx + 0.3], [row['Close'], row['Close']], color=color, linewidth=2, alpha=0.9)
    
    ax.set_title(f"{ticker} - OHLC Chart", color='#ffffff', fontsize=16, fontweight='300', pad=20)
    ax.set_ylabel("Price", color='#666666', fontsize=10)
    ax.tick_params(colors='#666666', labelsize=8)
    ax.grid(True, alpha=0.1, color='#2a2a2a', linestyle='-', linewidth=0.5)
    
    # Set x-axis labels
    step = max(len(data) // 10, 1)
    ax.set_xticks(range(0, len(data), step))
    ax.set_xticklabels([data.index[i].strftime('%m/%d') for i in range(0, len(data), step)], rotation=45)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#1a1a1a')
    ax.spines['bottom'].set_color('#1a1a1a')
    
    plt.tight_layout()
    return fig, None


def show_price_chart_page():
    """Price chart page with multiple chart types"""
    st.title('📈 Stock Price Charts')
    
    st.info('💡 **Tip**: For Indian stocks, add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`). For US stocks, use ticker directly (e.g., `AAPL`, `TSLA`).')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input('Enter Stock Ticker Symbol:', key='chart_ticker').upper()
    with col2:
        chart_type = st.selectbox('Chart Type:', 
                                  ['Candlestick', 'Line Chart', 'Bar Chart', 'OHLC'],
                                  key='chart_type_select')
    
    period = st.select_slider('Time Period:', 
                             options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
                             value='3mo',
                             key='period_select')
    
    if st.button('Generate Chart', key='chart_btn'):
        if ticker:
            with st.spinner('Generating chart...'):
                # Generate selected chart type
                if chart_type == 'Candlestick':
                    fig, error = plot_candlestick_chart(ticker, period)
                    st.markdown("""
                    **📊 Candlestick Chart**: Shows open, high, low, and close prices. 
                    - 🟢 Green = Close > Open (bullish)
                    - 🔴 Red = Close < Open (bearish)
                    - Wicks show high/low range
                    """)
                elif chart_type == 'Line Chart':
                    fig, error = plot_line_chart(ticker, period)
                    st.markdown("""
                    **📈 Line Chart**: Shows closing price trend with moving averages.
                    - 🟢 Green = Close Price
                    - 🟡 Yellow = 20-day MA
                    - 🔴 Red = 50-day MA
                    """)
                elif chart_type == 'Bar Chart':
                    fig, error = plot_bar_chart(ticker, period)
                    st.markdown("""
                    **📊 Bar Chart**: Shows price bars with volume.
                    - Top: Price bars (green=up, red=down)
                    - Bottom: Trading volume
                    """)
                elif chart_type == 'OHLC':
                    fig, error = plot_ohlc_chart(ticker, period)
                    st.markdown("""
                    **📉 OHLC Chart**: Shows Open-High-Low-Close with ticks.
                    - Vertical line = High to Low range
                    - Left tick = Open price
                    - Right tick = Close price
                    """)
                
                if error:
                    st.error(error)
                else:
                    st.pyplot(fig)
                    
                    # Additional statistics
                    data = yf.Ticker(ticker).history(period=period)
                    st.markdown("---")
                    st.markdown("### 📊 Statistics")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Current", f"${data.Close.iloc[-1]:.2f}")
                    with col2:
                        st.metric("High", f"${data.Close.max():.2f}")
                    with col3:
                        st.metric("Low", f"${data.Close.min():.2f}")
                    with col4:
                        change = ((data.Close.iloc[-1] - data.Close.iloc[0]) / data.Close.iloc[0]) * 100
                        st.metric("Return", f"{change:+.2f}%")
                    with col5:
                        avg_vol = data.Volume.mean() / 1000000
                        st.metric("Avg Volume", f"{avg_vol:.2f}M")
        else:
            st.warning('Please enter a ticker symbol')


def show_recommendation_page():
    """Buy/Sell/Hold recommendation page"""
    st.title('🎯 Stock Recommendation')
    
    st.markdown("""
    Get AI-powered buy/sell/hold recommendations based on multiple technical indicators including:
    - Simple Moving Averages (SMA 50 & 200)
    - Relative Strength Index (RSI)
    - MACD (Moving Average Convergence Divergence)
    - Volume Analysis
    """)
    
    st.info('💡 **Tip**: For Indian stocks, add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`). For US stocks, use ticker directly (e.g., `AAPL`, `TSLA`).')
    
    ticker = st.text_input('Enter Stock Ticker Symbol:', key='rec_ticker').upper()
    
    if st.button('Get Recommendation', key='rec_btn'):
        if ticker:
            with st.spinner('Analyzing stock...'):
                result, error = get_stock_recommendation(ticker)
                if error:
                    st.error(error)
                else:
                    # Display recommendation chart
                    st.pyplot(result['fig'])
                    
                    # Display detailed info
                    st.markdown("---")
                    st.markdown("### 📋 Analysis Details")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Recommendation", result['recommendation'])
                    with col2:
                        st.metric("Confidence", result['confidence'])
                    with col3:
                        st.metric("Current Price", f"${result['current_price']:.2f}")
                    
                    st.markdown("### 🔍 Reasoning")
                    for i, reason in enumerate(result['reasons'], 1):
                        st.markdown(f"{i}. {reason}")
                    
                    st.markdown("---")
                    st.info("⚠️ **Disclaimer**: This recommendation is based on technical analysis only and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.")
        else:
            st.warning('Please enter a ticker symbol')


def show_ticker_lookup_page():
    """Ticker symbol lookup page"""
    st.title('🔍 Ticker Symbol Lookup')
    
    st.markdown("""
    Search for stock ticker symbols by company name. This helps you find the correct ticker symbol 
    to use in other features. Supports both **US stocks** and **Indian stocks (NSE/BSE)**.
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input('Enter Company Name:', key='ticker_search', placeholder='e.g., Apple, Reliance, TCS')
    with col2:
        market = st.selectbox('Market:', ['Both', 'US', 'India'], key='market_select')
    
    if st.button('Search Ticker', key='ticker_search_btn'):
        if company_name:
            with st.spinner('Searching...'):
                try:
                    import yfinance as yf
                    
                    # Search for ticker
                    ticker_obj = yf.Ticker(company_name)
                    info = ticker_obj.info
                    
                    # Try to get ticker from common variations
                    possible_tickers = [
                        company_name.upper(),
                        company_name.upper().replace(' ', ''),
                        company_name.upper().split()[0]
                    ]
                    
                    found_results = []
                    
                    for tick in possible_tickers:
                        try:
                            test_ticker = yf.Ticker(tick)
                            test_info = test_ticker.info
                            if 'symbol' in test_info and test_info.get('symbol'):
                                found_results.append({
                                    'symbol': test_info.get('symbol', tick),
                                    'name': test_info.get('longName', test_info.get('shortName', 'N/A')),
                                    'sector': test_info.get('sector', 'N/A'),
                                    'industry': test_info.get('industry', 'N/A'),
                                    'exchange': test_info.get('exchange', 'N/A')
                                })
                        except:
                            continue
                    
                    # Manual mapping for popular companies (US + India)
                    popular_companies = {
                        # US Stocks
                        'apple': 'AAPL',
                        'microsoft': 'MSFT',
                        'google': 'GOOGL',
                        'alphabet': 'GOOGL',
                        'amazon': 'AMZN',
                        'tesla': 'TSLA',
                        'meta': 'META',
                        'facebook': 'META',
                        'netflix': 'NFLX',
                        'nvidia': 'NVDA',
                        'intel': 'INTC',
                        'amd': 'AMD',
                        'coca cola': 'KO',
                        'pepsi': 'PEP',
                        'walmart': 'WMT',
                        'disney': 'DIS',
                        'nike': 'NKE',
                        'mcdonalds': 'MCD',
                        'starbucks': 'SBUX',
                        'boeing': 'BA',
                        'ibm': 'IBM',
                        'oracle': 'ORCL',
                        'salesforce': 'CRM',
                        'visa': 'V',
                        'mastercard': 'MA',
                        'paypal': 'PYPL',
                        'uber': 'UBER',
                        'spotify': 'SPOT',
                        'twitter': 'X',
                        'jpmorgan': 'JPM',
                        'bank of america': 'BAC',
                        'wells fargo': 'WFC',
                        'goldman sachs': 'GS',
                        'exxon': 'XOM',
                        'chevron': 'CVX',
                        'pfizer': 'PFE',
                        'johnson': 'JNJ',
                        'procter': 'PG',
                        'ford': 'F',
                        'gm': 'GM',
                        'general motors': 'GM',
                        'att': 'T',
                        'verizon': 'VZ',
                        'comcast': 'CMCSA',
                        'adobe': 'ADBE',
                        'cisco': 'CSCO',
                        'qualcomm': 'QCOM',
                        # Indian Stocks (NSE)
                        'reliance': 'RELIANCE.NS',
                        'tcs': 'TCS.NS',
                        'tata consultancy': 'TCS.NS',
                        'infosys': 'INFY.NS',
                        'hdfc bank': 'HDFCBANK.NS',
                        'hdfc': 'HDFCBANK.NS',
                        'icici bank': 'ICICIBANK.NS',
                        'icici': 'ICICIBANK.NS',
                        'state bank': 'SBIN.NS',
                        'sbi': 'SBIN.NS',
                        'bharti airtel': 'BHARTIARTL.NS',
                        'airtel': 'BHARTIARTL.NS',
                        'itc': 'ITC.NS',
                        'wipro': 'WIPRO.NS',
                        'axis bank': 'AXISBANK.NS',
                        'axis': 'AXISBANK.NS',
                        'kotak': 'KOTAKBANK.NS',
                        'kotak mahindra': 'KOTAKBANK.NS',
                        'maruti': 'MARUTI.NS',
                        'maruti suzuki': 'MARUTI.NS',
                        'tata motors': 'TATAMOTORS.NS',
                        'mahindra': 'M&M.NS',
                        'm&m': 'M&M.NS',
                        'asian paints': 'ASIANPAINT.NS',
                        'bajaj finance': 'BAJFINANCE.NS',
                        'bajaj': 'BAJFINANCE.NS',
                        'titan': 'TITAN.NS',
                        'ultratech': 'ULTRACEMCO.NS',
                        'ultratech cement': 'ULTRACEMCO.NS',
                        'nestle': 'NESTLEIND.NS',
                        'nestle india': 'NESTLEIND.NS',
                        'hul': 'HINDUNILVR.NS',
                        'hindustan unilever': 'HINDUNILVR.NS',
                        'adani': 'ADANIPORTS.NS',
                        'adani ports': 'ADANIPORTS.NS',
                        'tata steel': 'TATASTEEL.NS',
                        'sun pharma': 'SUNPHARMA.NS',
                        'dr reddy': 'DRREDDY.NS',
                        'tech mahindra': 'TECHM.NS',
                        'ongc': 'ONGC.NS',
                        'ntpc': 'NTPC.NS',
                        'power grid': 'POWERGRID.NS',
                        'larsen': 'LT.NS',
                        'l&t': 'LT.NS',
                        'grasim': 'GRASIM.NS',
                        'jsw steel': 'JSWSTEEL.NS',
                        'hindalco': 'HINDALCO.NS',
                        'britannia': 'BRITANNIA.NS',
                        'coal india': 'COALINDIA.NS',
                        'bpcl': 'BPCL.NS',
                        'bharat petroleum': 'BPCL.NS',
                        'ioc': 'IOC.NS',
                        'indian oil': 'IOC.NS',
                        'eicher': 'EICHERMOT.NS',
                        'eicher motors': 'EICHERMOT.NS',
                        'divi': 'DIVISLAB.NS',
                        'divis lab': 'DIVISLAB.NS',
                        'cipla': 'CIPLA.NS',
                        'bajaj auto': 'BAJAJ-AUTO.NS',
                        'hero motocorp': 'HEROMOTOCO.NS',
                        'hero': 'HEROMOTOCO.NS',
                        'shree cement': 'SHREECEM.NS',
                        'indusind': 'INDUSINDBK.NS',
                        'indusind bank': 'INDUSINDBK.NS',
                        'vedanta': 'VEDL.NS',
                        'tata consumer': 'TATACONSUM.NS',
                        'godrej consumer': 'GODREJCP.NS',
                        'sbi life': 'SBILIFE.NS',
                        'hdfc life': 'HDFCLIFE.NS',
                        'icici prudential': 'ICICIPRULI.NS',
                        'pidilite': 'PIDILITIND.NS',
                        'berger paints': 'BERGEPAINT.NS',
                        'dabur': 'DABUR.NS',
                        'marico': 'MARICO.NS',
                        'colgate': 'COLPAL.NS',
                        'colgate palmolive': 'COLPAL.NS'
                    }
                    
                    # Filter by market selection
                    if market == 'US':
                        popular_companies = {k: v for k, v in popular_companies.items() if '.NS' not in v and '.BO' not in v}
                    elif market == 'India':
                        popular_companies = {k: v for k, v in popular_companies.items() if '.NS' in v or '.BO' in v}
                    
                    # Check manual mapping
                    company_lower = company_name.lower()
                    matched_ticker = None
                    
                    for key, ticker_symbol in popular_companies.items():
                        if key in company_lower:
                            matched_ticker = ticker_symbol
                            break
                    
                    if matched_ticker:
                        try:
                            ticker_obj = yf.Ticker(matched_ticker)
                            ticker_info = ticker_obj.info
                            
                            st.success(f"✅ Found: **{matched_ticker}**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Symbol:** `{matched_ticker}`")
                                st.markdown(f"**Company:** {ticker_info.get('longName', 'N/A')}")
                                st.markdown(f"**Sector:** {ticker_info.get('sector', 'N/A')}")
                            with col2:
                                st.markdown(f"**Industry:** {ticker_info.get('industry', 'N/A')}")
                                st.markdown(f"**Exchange:** {ticker_info.get('exchange', 'N/A')}")
                                st.markdown(f"**Currency:** {ticker_info.get('currency', 'N/A')}")
                            
                            # Get current price
                            current_price = ticker_info.get('currentPrice', ticker_info.get('regularMarketPrice'))
                            if current_price:
                                st.metric("Current Price", f"${current_price:.2f}")
                            
                            st.markdown("---")
                            st.info(f"💡 Use **`{matched_ticker}`** in other features to analyze this stock!")
                            
                        except Exception as e:
                            st.warning(f"Found ticker symbol but couldn't fetch details: {matched_ticker}")
                    
                    elif found_results:
                        st.success(f"✅ Found {len(found_results)} result(s)")
                        for result in found_results:
                            with st.expander(f"📊 {result['symbol']} - {result['name']}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Symbol:** `{result['symbol']}`")
                                    st.markdown(f"**Sector:** {result['sector']}")
                                with col2:
                                    st.markdown(f"**Industry:** {result['industry']}")
                                    st.markdown(f"**Exchange:** {result['exchange']}")
                    else:
                        st.warning("❌ No exact match found. Try these tips:")
                        st.markdown("""
                        - **For Indian stocks**: Add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`)
                        - **For US stocks**: Use ticker directly (e.g., `AAPL`, `TSLA`)
                        - Use the full company name (e.g., "Reliance" not "Reliance Industries")
                        - Try common abbreviations (e.g., "TCS" for Tata Consultancy Services)
                        - Visit NSE India or Yahoo Finance for accurate ticker symbols
                        """)
                        
                        # Show popular tickers by market
                        if market == 'India' or market == 'Both':
                            st.markdown("### 🇮🇳 Popular Indian Stocks (NSE):")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown("**IT & Tech:**")
                                st.markdown("• TCS.NS - TCS")
                                st.markdown("• INFY.NS - Infosys")
                                st.markdown("• WIPRO.NS - Wipro")
                                st.markdown("• TECHM.NS - Tech Mahindra")
                            with col2:
                                st.markdown("**Banking:**")
                                st.markdown("• HDFCBANK.NS - HDFC Bank")
                                st.markdown("• ICICIBANK.NS - ICICI Bank")
                                st.markdown("• SBIN.NS - SBI")
                                st.markdown("• AXISBANK.NS - Axis Bank")
                            with col3:
                                st.markdown("**Others:**")
                                st.markdown("• RELIANCE.NS - Reliance")
                                st.markdown("• BHARTIARTL.NS - Airtel")
                                st.markdown("• ITC.NS - ITC")
                                st.markdown("• MARUTI.NS - Maruti")
                        
                        if market == 'US' or market == 'Both':
                            st.markdown("### 🇺🇸 Popular US Stocks:")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown("**Tech:**")
                                st.markdown("• AAPL - Apple")
                                st.markdown("• MSFT - Microsoft")
                                st.markdown("• GOOGL - Google")
                                st.markdown("• TSLA - Tesla")
                            with col2:
                                st.markdown("**Finance:**")
                                st.markdown("• JPM - JPMorgan")
                                st.markdown("• BAC - Bank of America")
                                st.markdown("• V - Visa")
                                st.markdown("• MA - Mastercard")
                            with col3:
                                st.markdown("**Consumer:**")
                                st.markdown("• KO - Coca-Cola")
                                st.markdown("• WMT - Walmart")
                                st.markdown("• DIS - Disney")
                                st.markdown("• NKE - Nike")
                
                except Exception as e:
                    st.error(f"Error searching: {str(e)}")
                    st.info("Try entering the ticker symbol directly if you know it, or visit Yahoo Finance for accurate ticker symbols.")
        else:
            st.warning('Please enter a company name')


# -------- TOOL DEFINITIONS FOR CHATBOT -------- #

functions = [
    {
        'name': 'plot_stock_price_chatbot',
        'description': 'Plot last year stock price chart.',
        'parameters': {
            'type': 'object',
            'properties': {'ticker': {'type': 'string'}},
            'required': ['ticker'],
        }
    },
    {
        'name': 'get_stock_recommendation_chatbot',
        'description': 'Get buy/sell/hold recommendation with visual chart.',
        'parameters': {
            'type': 'object',
            'properties': {'ticker': {'type': 'string'}},
            'required': ['ticker'],
        }
    }
]


# -------- SESSION STATE INITIALIZATION -------- #
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

# -------- MAIN APP -------- #
if not st.session_state['logged_in']:
    login_register_page()
else:
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"**👤 {st.session_state.get('username', 'User')}**")
        if st.button("🚪 Logout", key='logout_btn'):
            st.session_state['logged_in'] = False
            st.session_state['messages'] = []
            st.session_state['current_page'] = 'Home'
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        
        if st.button("🏠 Home (Chatbot)", use_container_width=True, key='nav_home'):
            st.session_state['current_page'] = 'Home'
            st.rerun()
            
        if st.button("💰 Stock Price Lookup", use_container_width=True, key='nav_price'):
            st.session_state['current_page'] = 'Price Lookup'
            st.rerun()
            
        if st.button("📊 Technical Indicators", use_container_width=True, key='nav_indicators'):
            st.session_state['current_page'] = 'Technical Indicators'
            st.rerun()
            
        if st.button("📈 Price Charts", use_container_width=True, key='nav_charts'):
            st.session_state['current_page'] = 'Price Charts'
            st.rerun()
            
        if st.button("🎯 Buy/Sell/Hold", use_container_width=True, key='nav_recommendation'):
            st.session_state['current_page'] = 'Recommendation'
            st.rerun()
            
        if st.button("🔍 Ticker Lookup", use_container_width=True, key='nav_ticker'):
            st.session_state['current_page'] = 'Ticker Lookup'
            st.rerun()
    
    # Display selected page
    if st.session_state['current_page'] == 'Home':
        show_home_page()
    elif st.session_state['current_page'] == 'Price Lookup':
        show_price_lookup_page()
    elif st.session_state['current_page'] == 'Technical Indicators':
        show_technical_indicators_page()
    elif st.session_state['current_page'] == 'Price Charts':
        show_price_chart_page()
    elif st.session_state['current_page'] == 'Recommendation':
        show_recommendation_page()
    elif st.session_state['current_page'] == 'Ticker Lookup':
        show_ticker_lookup_page()[]