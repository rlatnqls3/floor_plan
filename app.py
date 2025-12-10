import streamlit as st
from PIL import Image, ImageDraw
import difflib # 문자열 유사도 비교를 위한 라이브러리

# --- 페이지 설정 ---
st.set_page_config(page_title="KPEX 2025 스마트 내비게이션", page_icon="🗺️")

# --- CSS 스타일 ---
st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 1.1rem; }
    .guide-text { font-size: 1.3rem; font-weight: bold; color: #1f77b4; margin-top: 20px;}
    .error-text { color: #FF4B4B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 부스 좌표 데이터 (업데이트됨) ---
# 실제 서비스 시에는 이 데이터를 최대한 많이, 정확하게 입력해야 합니다.
# 좌표 기준: 이미지 좌측 상단(0,0) ~ 우측 하단(100,100) % 좌표
BOOTH_LOCATIONS = {
    # 주요 시설
    "출입구(세미나장 A측)": (15, 95),
    "출입구(세미나장 B측)": (15, 5),
    "카페테리아": (25, 15),
    "KPEX 라운지": (40, 15),
    "세미나장 A": (10, 85),
    "세미나장 B": (10, 35),
    "KOTRA 수출상담회장": (10, 55),
    # 주요 참가업체 (도면 기반 추정)
    "경찰과학수사관": (50, 15),
    "Naviworks": (60, 15),
    "KADIF": (70, 15),
    "한국도로교통공단": (80, 15),
    "첨단교통관": (88, 15),
    "DAEJI": (92, 20),
    "KT": (45, 82),
    "ETRI": (26, 82),
    "소방청": (58, 88),
    "드론 시큐리티 특별관": (65, 45),
    "Drager": (75, 40),
    "KAI": (85, 40),
    "LIG넥스원": (80, 65),
    "한화시스템": (80, 55),
    "현대자동차": (60, 65)
}

# --- 도우미 함수: 스마트 부스 찾기 (Fuzzy Matching) ---
def find_best_match(user_input, db_keys):
    """사용자 입력과 가장 유사한 부스 이름을 데이터베이스에서 찾습니다."""
    if not user_input:
        return None
    # 1. 완전 일치 확인
    if user_input in db_keys:
        return user_input
    
    # 2. 소문자로 변환하여 부분 일치 확인 (예: 'kt' 입력 시 'KT' 찾기)
    user_lower = user_input.lower()
    candidates = []
    for key in db_keys:
        if user_lower in key.lower():
            candidates.append(key)
    
    if candidates:
        # 부분 일치하는 것 중 가장 짧은 것(가장 핵심적인 것) 반환 (단순화)
        return min(candidates, key=len)

    # 3. (선택사항) difflib을 이용한 유사도 매칭 (오타 보정 등)
    # matches = difflib.get_close_matches(user_input, db_keys, n=1, cutoff=0.5)
    # if matches:
    #     return matches[0]
        
    return None

# --- 도우미 함수: 직각 경로 그리기 (Manhattan Path) ---
def draw_manhattan_path(image, start_name, end_name):
    """출발지와 도착지를 직각으로 꺾이는 선으로 연결합니다."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    start_pos_pct = BOOTH_LOCATIONS[start_name]
    end_pos_pct = BOOTH_LOCATIONS[end_name]

    # 픽셀 좌표로 변환
    sx, sy = start_pos_pct[0] * width / 100, start_pos_pct[1] * height / 100
    ex, ey = end_pos_pct[0] * width / 100, end_pos_pct[1] * height / 100

    # 경로 스타일 설정
    line_color = "#0044FF" # 진한 파랑
    line_width = 8

    # 직각 경로 포인트 계산 (L자 형태)
    # 1. 출발점에서 수평으로 이동하여 도착점의 X좌표까지 이동
    # 2. 그 지점에서 수직으로 도착점의 Y좌표까지 이동
    # (전시장 레이아웃에 따라 수직 먼저 이동하는 게 나을 수도 있습니다)
    mid_x, mid_y = ex, sy

    path_points = [(sx, sy), (mid_x, mid_y), (ex, ey)]

    # 선 그리기
    draw.line(path_points, fill=line_color, width=line_width)

    # 출발/도착 마커 그리기
    r_start = 12
    r_end = 15
    # 출발지 (초록 원)
    draw.ellipse((sx-r_start, sy-r_start, sx+r_start, sy+r_start), fill="#28a745", outline="white", width=3)
    # 도착지 (빨강 원)
    draw.ellipse((ex-r_end, ey-r_end, ex+r_end, ey+r_end), fill="#dc3545", outline="white", width=4)
    
    return img_copy

# --- 메인 UI ---
st.title("🗺️ KPEX 2025 스마트 내비게이션")
st.markdown("부스 이름을 직접 입력하여 경로를 확인하세요. (예: KT, 소방청, 카페테리아)")

# 입력 폼
with st.form("nav_form"):
    col1, col2 = st.columns(2)
    with col1:
        start_input = st.text_input("📍 현재 위치 (입력)", placeholder="예: 출입구")
    with col2:
        end_input = st.text_input("🚩 목적지 (입력)", placeholder="예: 경찰과학수사관")
    
    submit_button = st.form_submit_button("길찾기 시작 🚀", type="primary")

# 결과 처리
if submit_button:
    # 1. 입력값 검증 및 매칭 찾기
    start_match = find_best_match(start_input.strip(), BOOTH_LOCATIONS.keys())
    end_match = find_best_match(end_input.strip(), BOOTH_LOCATIONS.keys())

    # 2. 오류 처리 및 결과 표시
    if not start_input or not end_input:
         st.warning("출발지와 목적지를 모두 입력해주세요.")
    elif not start_match:
        st.markdown(f"<p class='error-text'>❌ '{start_input}'과(와) 일치하는 부스를 찾을 수 없습니다. 이름을 확인해주세요.</p>", unsafe_allow_html=True)
    elif not end_match:
        st.markdown(f"<p class='error-text'>❌ '{end_input}'과(와) 일치하는 부스를 찾을 수 없습니다. 이름을 확인해주세요.</p>", unsafe_allow_html=True)
    elif start_match == end_match:
         st.warning("출발지와 목적
