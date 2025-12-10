import streamlit as st
from PIL import Image, ImageDraw

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="서울일러스트레이션코리아 2025 길찾기", page_icon="🎨")

st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 1.1rem; }
    .guide-text { font-size: 1.3rem; font-weight: bold; color: #FF4B4B; margin-top: 20px;}
    .sub-text { font-size: 1.0rem; color: #555; }
    .error-text { color: #FF4B4B; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 통합 부스 데이터 (수정됨: 5- → S-) ---
# [중요] 실제 좌표(x, y)는 'sik_floor_plan.jpg' 이미지를 보시고 꼭 미세 조정해주세요.
BOOTH_LOCATIONS = {
    # [주요 시설]
    "출입구 (Entrance)": (50, 95),
    "카페테리아 (Cafeteria)": (10, 20),
    "화장실 (Restroom)": (90, 50),
    
    # [기획관 및 이벤트존]
    "캐리커쳐 기획관": (20, 15),
    "디저트팝업 (Dessert Pop-up)": (15, 40),
    "아트작가 초대전": (15, 60),
    "밀리 이벤트존": (30, 15),
    "글로벌 아티스트존": (40, 10),
    
    # [S존 - 기존 5-에서 S-로 수정완료]
    "S-101 계원예대 순수미술작가": (80, 20),
    "S-114 홍무아": (82, 20),
    "S-106 밸트글라스 (BALTGLAS)": (84, 20),
    "S-108 KANGZI (강지)": (86, 20),
    
    # [참가업체/작가]
    "A-101 클립아트코리아 (Clipartkorea)": (10, 80),
    "O-101 키스틱빌리지": (15, 80),
    "T-001 톤어스 (TOONUS)": (20, 80),
    "BKKIF (태국페어)": (25, 80),
    
    # [C존 작가]
    "C-118 Art Work Shop Kyoko (쿄코)": (10, 30),
    "C-112 MIND FAMILY (마인드 패밀리)": (12, 30),
    "C-111 MachiK": (14, 30),
    "C-115 inkpainting": (16, 30),
    "C-218 기온스튜디오": (18, 32),
    
    # [D존 작가]
    "D-216 namodo (나모도 那么多)": (30, 40),
    "D-214 Sleepybere (슬리피베어)": (32, 40),
    "D-232 Draft.apics": (34, 40),
    "D-101 미야오타운": (36, 42),
    "D-213 Straycat tarot": (38, 40),
    
    # [F존 작가]
    "F-204 두루뭉이두더지": (70, 30),
    "F-203 듀원": (72, 30),
    "F-220 잠동사니": (74, 30),
    
    # [디저트 존]
    "Dessert-13 과밀과즙젤리": (10, 45),
    "Dessert-10 꼬마루육포": (12, 45),
    "Dessert-11 뉴욕의 저스트 쿠키": (14, 45),
    "Dessert-01 쿠키는 역시 아리감성": (16, 45),
    
    # [J존]
    "J-229 젤리부 (JeliRivu)": (60, 60),
    "J-226 하리커피": (60, 65)
}

# --- 3. 스마트 검색 함수 (업그레이드: 5/S 자동 보정) ---
def find_best_matches(user_input, db_keys):
    """
    사용자가 입력한 검색어(부스번호, 이름 등)가 포함된 모든 결과를 찾습니다.
    (5와 S를 혼동하여 입력해도 찾아냅니다)
    """
    if not user_input:
        return []
    
    user_input = user_input.lower().strip()
    matches = []
    
    # 입력 편의성을 위한 전처리
    # 1. 공백 제거 ("S 101" -> "s101")
    input_nospace = user_input.replace("-", "").replace(" ", "")
    # 2. '5'를 's'로 치환한 버전 생성 (오타 보정용)
    input_corrected = input_nospace.replace("5", "s")
    
    for key in db_keys:
        key_lower = key.lower()
        key_nospace = key_lower.replace("-", "").replace(" ", "")
        
        # [조건 1] 일반 포함 검색 (예: "소니" in "A-101 소니")
        if user_input in key_lower:
            matches.append(key)
        # [조건 2] 부스번호 하이픈(-) 생략 검색 (예: "s101" in "s101계원예대...")
        elif input_nospace in key_nospace:
            matches.append(key)
        # [조건 3] '5'를 입력했지만 'S'존인 경우 (예: "5101" -> "s101" 검색)
        elif input_corrected in key_nospace and "s" in key_nospace:
             matches.append(key)
            
    # 정확도 순 정렬 (짧은 것이 더 정확할 확률 높음)
    matches.sort(key=len)
    return matches

def draw_manhattan_path(image, start_name, end_name):
    """경로 그리기 함수"""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    start_pos = BOOTH_LOCATIONS[start_name]
    end_pos = BOOTH_LOCATIONS[end_name]

    sx, sy = start_pos[0] * width / 100, start_pos[1] * height / 100
    ex, ey = end_pos[0] * width / 100, end_pos[1] * height / 100

    # 선 스타일
    line_color = "#FF007F" # 핫핑크
    line_width = 8

    # 직각 경로
    mid_x, mid_y = ex, sy 
    path_points = [(sx, sy), (mid_x, mid_y), (ex, ey)]

    draw.line(path_points, fill=line_color, width=line_width)

    # 마커
    r = 12
    draw.ellipse((sx-r, sy-r, sx+r, sy+r), fill="#00C853", outline="white", width=3) # 출발
    draw.ellipse((ex-r, ey-r, ex+r, ey+r), fill="#FF0000", outline="white", width=4) # 도착
    
    return img_copy

# --- 4. 메인 UI ---

st.title("🎨 서울일러스트레이션코리아 2025")
st.markdown("##### 부스번호, 작가명, 업체명 무엇이든 검색하세요!")

# 입력 폼
with st.form("nav_form"):
    col1, col2 = st.columns(2)
    with col1:
        start_input = st.text_input("📍 현재 위치", placeholder="예: 출입구, S-101")
    with col2:
        end_input = st.text_input("🚩 목적지", placeholder="예: 젤리부, 5-101")
    
    submit_button = st.form_submit_button("길찾기 🚀")

# 결과 처리
if submit_button:
    start_matches = find_best_matches(start_input, BOOTH_LOCATIONS.keys())
    end_matches = find_best_matches(end_input, BOOTH_LOCATIONS.keys())

    if not start_input or not end_input:
        st.warning("출발지와 목적지를 모두 입력해주세요.")
    
    elif not start_matches:
        st.error(f"❌ '{start_input}'을(를) 찾을 수 없습니다. 철자를 확인해주세요.")
    elif not end_matches:
        st.error(f"❌ '{end_input}'을(를) 찾을 수 없습니다. 철자를 확인해주세요.")
        
    else:
        start_point = start_matches[0]
        end_point = end_matches[0]

        # 사용자가 5-101로 검색했어도 S-101로 안내한다는 메시지 표시
        if len(start_matches) >= 1:
            st.info(f"📍 출발지: '{start_point}'")
        if len(end_matches) >= 1:
            st.info(f"🚩 목적지: '{end_point}'")

        try:
            image = Image.open("sik_floor_plan.jpg")
            result_image = draw_manhattan_path(image, start_point, end_point)
            
            st.divider()
            st.success("경로 탐색 완료! 분홍색 선을 따라가세요.")
            st.image(result_image, use_container_width=True)

        except FileNotFoundError:
            st.error("⚠️ 'sik_floor_plan.jpg' 이미지를 찾을 수 없습니다.")
