import streamlit as st
from PIL import Image, ImageDraw
import difflib  # 유사한 단어를 찾기 위한 라이브러리

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="KPEX 2025 스마트 내비게이션", page_icon="🗺️")

st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 1.1rem; }
    .guide-text { font-size: 1.3rem; font-weight: bold; color: #1f77b4; margin-top: 20px;}
    .error-text { color: #FF4B4B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 부스 좌표 데이터 (0~100% 좌표계) ---
BOOTH_LOCATIONS = {
    # [시설]
    "출입구(세미나장 A측)": (15, 95),
    "출입구(세미나장 B측)": (15, 5),
    "카페테리아": (25, 15),
    "KPEX 라운지": (40, 15),
    "세미나장 A": (10, 85),
    "세미나장 B": (10, 35),
    "
