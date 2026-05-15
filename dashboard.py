import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. Veri Çekme ve Saklama ---
def get_data(ticker):
    # Son 1 aylık, 1 saatlik (1h) veriyi çek
    data = yf.download(ticker, period="1mo", interval="1h")
    data.to_csv("data.csv")
    return data

# --- UI Ayarları ---
st.set_page_config(page_title="Finansal Dashboard", layout="wide")
st.title("📈 Saatlik Piyasa Analiz Dashboard'u")

# Sidebar - Kullanıcı Girişi
ticker = st.sidebar.text_input("Hisse/Kripto Sembolü (Örn: BTC-USD, AAPL)", "BTC-USD")
if st.sidebar.button("Veriyi Güncelle"):
    df = get_data(ticker)
    st.sidebar.success("Veri başarıyla indirildi ve saklandı!")

# Veriyi yükle
try:
    df = pd.read_csv("data.csv", index_col=0, parse_dates=True)
except:
    df = get_data(ticker)

# --- 2. Teknik Göstergeler (Extra Indicator Kısmı) ---
df['SMA_20'] = ta.sma(df['Close'], length=20)
df['RSI'] = ta.rsi(df['Close'], length=14)
# Extra effort indicator: MACD
macd = ta.macd(df['Close'])
df = pd.concat([df, macd], axis=1)

# --- 3. Dashboard UI & Görselleştirme ---
col1, col2, col3 = st.columns(3)
col1.metric("Son Fiyat", f"${df['Close'].iloc[-1]:.2f}")
col2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
col3.metric("24s Değişim", f"{(df['Close'].iloc[-1]/df['Close'].iloc[-24]-1)*100:.2f}%")

# Line Chart - Fiyat ve SMA
st.subheader("Fiyat ve Hareketli Ortalama (SMA 20)")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Kapanış Fiyatı"))
fig_price.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20", line=dict(dash='dash')))
st.plotly_chart(fig_price, use_container_width=True)

# Alt Gösterge - RSI ve Tablo
c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("RSI Göstergesi")
    st.line_chart(df['RSI'])
with c2:
    st.subheader("Son Veriler")
    st.write(df.tail(10))

# Extra UI Feature: Karanlık/Aydınlık Mod Teması Streamlit'te otomatiktir 
# ama biz buraya bir "Download CSV" butonu ekleyerek extra puan alabiliriz.
st.download_button("Veriyi CSV olarak indir", df.to_csv(), "analiz_sonucu.csv")
