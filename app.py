import streamlit as st
from PIL import Image, ImageDraw
import difflib

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="서울일러스트레이션코리아 2025 길찾기", page_icon="🎨")

st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 1.1rem; }
    .guide-text { font-size: 1.3rem; font-weight: bold; color: #FF4B4B; margin-top: 20px;}
    .sub-text { font-size: 1.0rem; color: #555; }
    .error-text { color: #FF4B4B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 부스 좌표 데이터 (0~100% 좌표계) ---
# [중요] PDF 도면을 보시고 각 부스의 대략적인 위치(%)를 수정해주세요.
# 예: (0, 0)은 좌측상단, (50, 50)은 정중앙, (100, 100)은 우측하단입니다.
BOOTH_LOCATIONS = {
    # [주요 기획관 및 시설]
    "출입구": (50, 95),  # 하단 중앙 가정
    "카페테리아": (10, 20), # 좌측 상단 부근 (CAFETERIA)
    "캐리커쳐 기획관": (20, 15),
    "디저트팝업": (15, 40),
    "아트작가 초대전": (15, 60),
    "밀리 이벤트존": (30, 15),
    "글로벌 아티스트존": (40, 10),
    "머스 기획관": (50, 10),
    "오늘의 세계(원화전)": (60, 10),
    "네컷프레임 사진관": (10, 10),
    
    # [주요 참가업체 - 예시 데이터]
    # PDF 파일에 있는 업체명과 부스번호를 매핑했습니다.
    "주최 MESSE ESANG": (10, 90),
    "클립아트코리아 (A-101)": (10, 80),
    "키스틱빌리지 (0-101)": (15, 80),
    "톤어스 (TOONUS)": (20, 80),
    "BKKIF (태국페어)": (25, 80),
    "젤리부 (J-229)": (60, 60),
    "하리커피 (J-226)": (60, 65),
    "두루뭉이두더지 (F-204)": (70, 30),
    "미야오타운 (D-101)": (80, 30),
    "소니 (SONY)": (30, 50),
    "와콤 (Wacom)": (35, 50), # 가정
    
    # [디저트 존]
    "과밀과즙젤리 (Dessert-13)": (10, 45),
    "꼬마루육포 (Dessert-10)": (12, 45),
    "달치나 (Dessert-17)": (14, 45),
    "순두부젤라또": (16, 45)
}

# --- 3. 도우미 함수들 ---

def find_best_match(user_input, db_keys):
    """사용자 입력과 가장 유사한 부스 이름을 찾습니다."""
    if not user_input:
        return None
    
    # 1. 완전 일치
    if user_input in db_keys:
        return user_input
    
    # 2. 부분 포함 (대소문자 무시)
    user_lower = user_input.lower()
    candidates = []
    for key in db_keys:
        if user_lower in key.lower():
            candidates.append(key)
    
    if candidates:
        return min(candidates, key=len) # 가장 짧은(핵심) 단어 우선
        
    return None

def draw_manhattan_path(image, start_name, end_name):
    """출발지와 도착지를 직각 경로로 연결합니다."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    # 좌표 가져오기
    start_pos_pct = BOOTH_LOCATIONS[start_name]
    end_pos_pct = BOOTH_LOCATIONS[end_name]

    sx, sy = start_pos_pct[0] * width / 100, start_pos_pct[1] * height / 100
    ex, ey = end_pos_pct[0] * width / 100, end_pos_pct[1] * height / 100

    # 선 스타일 (일러스트 페어에 맞는 분홍/보라 계열 추천)
    line_color = "#FF007F"  # 핫핑크
    line_width = 10

    # 직각 경로 (가로 이동 -> 세로 이동)
    mid_x, mid_y = ex, sy 
    path_points = [(sx, sy), (mid_x, mid_y), (ex, ey)]

    # 경로 그리기
    draw.line(path_points, fill=line_color, width=line_width)

    # 마커 그리기
    r = 15
    draw.ellipse((sx-r, sy-r, sx+r, sy+r), fill="#00C853", outline="white", width=3) # 출발(초록)
    draw.ellipse((ex-r, ey-r, ex+r, ey+r), fill="#FF0000", outline="white", width=4) # 도착(빨강)
    
    return img_copy

# --- 4. 메인 UI 화면 ---

st.title("🎨 서울일러스트레이션코리아 2025")
st.markdown("### 부스 스마트 내비게이션")
st.write("원하는 작가님이나 부스 이름을 입력하세요. (예: 젤리부, 카페테리아)")

# 입력 폼
with st.form("nav_form"):
    col1, col2 = st.columns(2)
    with col1:
        start_input = st.text_input("📍 현재 위치", placeholder="예: 출입구")
    with col2:
        end_input = st.text_input("🚩 목적지 (작가/부스명)", placeholder="예: 디저트팝업")
    
    submit_button = st.form_submit_button("길찾기 시작 ✨", type="primary")

# 결과 처리 로직
if submit_button:
    s_text = start_input.strip() if start_input else ""
    e_text = end_input.strip() if end_input else ""

    start_match = find_best_match(s_text, BOOTH_LOCATIONS.keys())
    end_match = find_best_match(e_text, BOOTH_LOCATIONS.keys())

    if not s_text or not e_text:
        st.warning("출발지와 목적지를 모두 입력해주세요.")
    elif not start_match:
        st.markdown(f"<p class='error-text'>❌ '{s_text}' 부스를 찾을 수 없습니다.</p>", unsafe_allow_html=True)
    elif not end_match:
        st.markdown(f"<p class='error-text'>❌ '{e_text}' 부스를 찾을 수 없습니다.</p>", unsafe_allow_html=True)
    elif start_match == end_match:
        st.warning("출발지와 목적지가 같습니다.")
    else:
        try:
            # 이미지 파일명이 바뀌었습니다!
            image = Image.open("sik_floor_plan.jpg")
            
            result_image = draw_manhattan_path(image, start_match, end_match)
            
            st.divider()
            st.markdown(f"<p class='guide-text'>✅ '{start_match}' ➡️ '{end_match}'</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='sub-text'>분홍색 선을 따라 이동하세요.</p>", unsafe_allow_html=True)
            
            st.image(result_image, use_container_width=True)

        except FileNotFoundError:
            st.error("⚠️ 'sik_floor_plan.jpg' 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
