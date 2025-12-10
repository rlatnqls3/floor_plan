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
    "KOTRA 수출상담회장": (10, 55),
    # [부스]
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

# --- 3. 도우미 함수들 ---

def find_best_match(user_input, db_keys):
    """사용자 입력과 가장 유사한 부스 이름을 찾습니다."""
    if not user_input:
        return None
    
    # 1단계: 완전 일치
    if user_input in db_keys:
        return user_input
    
    # 2단계: 부분 포함 (대소문자 무시)
    user_lower = user_input.lower()
    candidates = []
    for key in db_keys:
        if user_lower in key.lower():
            candidates.append(key)
    
    if candidates:
        # 가장 짧은 이름(가장 핵심 단어)을 우선 반환
        return min(candidates, key=len)
        
    return None

def draw_manhattan_path(image, start_name, end_name):
    """출발지와 도착지를 'ㄴ'자 형태(직각)로 연결합니다."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    # 좌표 가져오기
    start_pos_pct = BOOTH_LOCATIONS[start_name]
    end_pos_pct = BOOTH_LOCATIONS[end_name]

    # % 좌표를 픽셀 좌표로 변환
    sx, sy = start_pos_pct[0] * width / 100, start_pos_pct[1] * height / 100
    ex, ey = end_pos_pct[0] * width / 100, end_pos_pct[1] * height / 100

    # 선 스타일
    line_color = "#0044FF"  # 파란색
    line_width = 8

    # 직각 경로 포인트 계산 (수평 이동 -> 수직 이동)
    # 1. (sx, sy)에서 시작
    # 2. (ex, sy)까지 수평 이동 (중간 지점)
    # 3. (ex, ey)까지 수직 이동
    
    mid_x, mid_y = ex, sy 
    path_points = [(sx, sy), (mid_x, mid_y), (ex, ey)]

    # 경로 그리기
    draw.line(path_points, fill=line_color, width=line_width)

    # 마커 그리기 (출발: 초록원, 도착: 빨간원)
    r_start = 12
    r_end = 15
    
    draw.ellipse((sx-r_start, sy-r_start, sx+r_start, sy+r_start), fill="#28a745", outline="white", width=3)
    draw.ellipse((ex-r_end, ey-r_end, ex+r_end, ey+r_end), fill="#dc3545", outline="white", width=4)
    
    return img_copy

# --- 4. 메인 UI 화면 ---

st.title("🗺️ KPEX 2025 스마트 내비게이션")
st.markdown("부스 이름을 입력하면 길을 안내해 드립니다. (예: KT, 소방청)")

# 입력 폼
with st.form("nav_form"):
    col1, col2 = st.columns(2)
    with col1:
        start_input = st.text_input("📍 현재 위치", placeholder="예: 출입구")
    with col2:
        end_input = st.text_input("🚩 목적지", placeholder="예: 경찰과학수사관")
    
    submit_button = st.form_submit_button("길찾기 시작 🚀", type="primary")

# 결과 처리 로직
if submit_button:
    # 입력값 정리
    s_text = start_input.strip() if start_input else ""
    e_text = end_input.strip() if end_input else ""

    # DB 매칭 시도
    start_match = find_best_match(s_text, BOOTH_LOCATIONS.keys())
    end_match = find_best_match(e_text, BOOTH_LOCATIONS.keys())

    # 유효성 검사 및 에러 메시지
    if not s_text or not e_text:
        st.warning("출발지와 목적지를 모두 입력해주세요.")
        
    elif not start_match:
        st.markdown(f"<p class='error-text'>❌ '{s_text}' 부스를 찾을 수 없습니다.</p>", unsafe_allow_html=True)
        
    elif not end_match:
        st.markdown(f"<p class='error-text'>❌ '{e_text}' 부스를 찾을 수 없습니다.</p>", unsafe_allow_html=True)
        
    elif start_match == end_match:
        # 여기가 오류가 났던 부분입니다. 따옴표를 잘 닫았습니다.
        st.warning("출발지와 목적지가 같습니다. 다른 곳을 입력해주세요.")
        
    else:
        # 정상 처리: 지도 로딩 및 경로 그리기
        try:
            # 같은 폴더에 floor_plan.jpg가 있어야 합니다.
            image = Image.open("floor_plan.jpg")
            
            result_image = draw_manhattan_path(image, start_match, end_match)
            
            st.divider()
            st.markdown(f"<p class='guide-text'>✅ '{start_match}' ➡️ '{end_match}' 경로입니다.</p>", unsafe_allow_html=True)
            st.markdown("파란색 선을 따라 이동하세요.")
            
            st.image(result_image, use_container_width=True)

        except FileNotFoundError:
            st.error("⚠️ 'floor_plan.jpg' 파일을 찾을 수 없습니다. GitHub에 이미지를 업로드했는지 확인해주세요.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
