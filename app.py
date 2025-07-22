
import gradio as gr
import pandas as pd
import requests
import datetime

API_KEY = "c29bb32cbe35431fa78a8b09629b9dfd"
symbols = ["EUR/USD", "GBP/USD", "XAU/USD"]
intervals = ["15min", "1h", "4h"]

def get_price(symbol, interval):
    symbol_fmt = symbol.replace("/", "")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol_fmt}&interval={interval}&apikey={API_KEY}&outputsize=100"
    r = requests.get(url).json()
    try:
        df = pd.DataFrame(r['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')
        df.set_index('datetime', inplace=True)
        df = df.astype(float)
        return df
    except:
        return None

def generate_signal(df):
    if df is None or len(df) < 20:
        return "HOLD", None, None
    df['EMA9'] = df['close'].ewm(span=9).mean()
    df['EMA21'] = df['close'].ewm(span=21).mean()
    signal = "HOLD"
    entry = None
    exit = None
    if df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and df['EMA9'].iloc[-2] <= df['EMA21'].iloc[-2]:
        signal = "BUY"
        entry = df['close'].iloc[-1]
        exit = entry + (entry * 0.015)
    elif df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and df['EMA9'].iloc[-2] >= df['EMA21'].iloc[-2]:
        signal = "SELL"
        entry = df['close'].iloc[-1]
        exit = entry - (entry * 0.015)
    return signal, entry, exit

def analyze():
    results = ""
    for symbol in symbols:
        for interval in intervals:
            df = get_price(symbol, interval)
            signal, entry, exit_point = generate_signal(df)
            results += f"🔹 {symbol} ({interval}): {signal}"
            if signal in ["BUY", "SELL"]:
                results += f" | Entry: {entry:.2f} | Target: {exit_point:.2f}"
            results += "\n"
    return results + "\nLast updated: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

with gr.Blocks() as app:
    gr.Markdown("# 🤖 Tristarnold v1 EA - AI Forex Bot")
    output = gr.Textbox(label="Signal Output", lines=20)
    refresh = gr.Button("🔄 Refresh")
    refresh.click(fn=analyze, outputs=output)
    app.load(fn=analyze, outputs=output, every=300)

app.launch()
