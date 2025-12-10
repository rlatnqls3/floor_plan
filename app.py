import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import heapq
from collections import deque
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="SIK 2025 스마트 내비게이션", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2rem; font-weight: bold; color: #1E88E5; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1E88E5; color: white; font-weight: bold;}
    .coord-box { 
        background-color: #e3f2fd; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #1E88E5; 
        font-family: monospace;
        color: #0d47a1;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 부스 데이터 (PDF 2페이지 완벽 반영) ---
# [알림] 데이터가 매우 많으므로 딕셔너리로 관리합니다.
# 형식: "부스번호": "업체명" (검색의 편의를 위해 번호를 키로 사용)

RAW_BOOTH_DATA = {
    # [주요 시설]
    "Ent-1": "목/토 입구 (Entrance)",
    "Ent-2": "금/일 입구 (Entrance)",
    "Cafe": "카페테리아 (Cafeteria)",
    "Live": "라이브드로잉 & 카페",
    "Sp-1": "캐리커쳐 기획관",
    "Sp-2": "디저트팝업",
    "Sp-3": "아트작가 초대전",
    "Sp-4": "네컷프레임 사진관",
    
    # [A존]
    "A-100": "1989 PALETTE", "A-101": "클립아트코리아", "A-104": "끼니디자인", "A-111": "소량",
    "A-114": "메이마트", "A-118": "디지", "A-121": "페이퍼", "A-124": "자이언트아이 아트스튜디오",
    "A-125": "나다스토리", "A-128": "홈어스", "A-130": "굿워크", "A-132": "하함스튜디오",
    
    # [B존]
    "B-104": "고양이다방", "B-110": "지니요니", "B-111": "TTIPCY", "B-112": "자민해",
    "B-115": "지지(MONZIZI)", "B-120": "블루츠", "B-124": "투유럽미", "B-126": "설기일러스트",
    "B-131": "빈집", "B-201": "Gimm", "B-218": "초목점화", "B-219": "페녀리니",
    "B-220": "농농이", "B-221": "한림사", "B-224": "키팅제이",
    
    # [C존]
    "C-100": "윤조유라", "C-103": "비모델 스튜디오", "C-104": "달빛곰", "C-110": "붓터치",
    "C-111": "MachiK", "C-112": "MIND FAMILY", "C-113": "yaoyao", "C-115": "inkpainting",
    "C-118": "Art Work Shop Kyoko", "C-120": "산그리메", "C-125": "김효정", "C-129": "일러스트레이터 양파",
    "C-130": "위시유", "C-131": "오묘", "C-200": "말로하곰곰", "C-208": "6-208",
    "C-211": "광태", "C-214": "김이네", "C-218": "기온스튜디오", "C-219": "리터프롤러브드",
    "C-220": "옴즈", "C-231": "피피",
    
    # [D존]
    "D-100": "말앞이 디자인", "D-101": "미야오타운", "D-103": "제니빌리지", "D-107": "박산",
    "D-110": "로스트앤파운드", "D-115": "스튜디오 다람", "D-118": "DONEARTH", "D-123": "영도리",
    "D-124": "타노월드", "D-128": "바이고대", "D-130": "그러는 인", "D-201": "113",
    "D-213": "Straycat tarot", "D-214": "Sleepybere", "D-215": "The 3rd Daughter", "D-216": "namodo",
    "D-219": "머리", "D-224": "모도리 스튜디오", "D-232": "Draft.apics",
    
    # [F존]
    "F-101": "코코의 그림공간", "F-102": "고동성", "F-103": "호랑", "F-104": "아라빅스",
    "F-106": "프렌즈", "F-107": "담장아래", "F-108": "고라니", "F-114": "달담",
    "F-115": "허다마리", "F-116": "모모이하우스", "F-119": "오기환", "F-120": "구리",
    "F-124": "니어바이디어", "F-128": "milky rapstar", "F-129": "모서리 스튜디오", "F-130": "코스모 익스프레스",
    "F-131": "Rosemary Hill", "F-201": "싱포유스튜디오", "F-203": "듀원", "F-204": "두루뭉이두더지",
    "F-207": "복자하우스", "F-209": "단식원", "F-211": "젠디디", "F-212": "연두십",
    "F-213": "우당탕탕스토어", "F-215": "도순상현", "F-220": "잠동사니", "F-221": "다람",
    "F-223": "다블랙", "F-224": "지우 스마일", "F-226": "스튜디오 표니", "F-229": "루이와코이누",
    "F-231": "Catist",
    
    # [G존]
    "G-100": "쇼킹핑크로즈", "G-101": "유승", "G-111": "도아세", "G-112": "동식품원",
    "G-114": "우연철", "G-118": "백구성스튜디오", "G-120": "닛(Knit)", "G-121": "2-121",
    "G-128": "하이볼루유", "G-129": "Ideal Idea", "G-130": "레드이어스클럽", "G-200": "Thustimesu",
    "G-201": "콜리스튜디오", "G-214": "토끼 과 친구들", "G-215": "하슈밴드", "G-223": "앙고라로라",
    "G-228": "CEE", "G-229": "dawnitive wave", "G-231": "사리안루니",
    
    # [H존]
    "H-100": "주스", "H-101": "안녕, 말로하", "H-102": "리노프렌즈", "H-104": "벨로이루",
    "H-107": "조각", "H-110": "츄리서랍", "H-112": "유교곰", "H-119": "OHD",
    "H-120": "밀크병스튜디오", "H-129": "다라미네", "H-130": "단주스퀘어", "H-133": "studio som",
    "H-200": "루루피94", "H-201": "채보리", "H-202": "스튜디오니모", "H-203": "판타포레",
    "H-204": "김보미", "H-208": "수피", "H-211": "디어폴리", "H-212": "세라베어",
    "H-216": "전", "H-219": "From Gyeol", "H-220": "산뽀", "H-223": "공진어트",
    "H-225": "아득", "H-228": "연메이드", "H-230": "큐티지파실", "H-231": "허다마리",
    
    # [J존]
    "J-102": "차리", "J-103": "스누즈키즈", "J-106": "Netty Lee", "J-112": "에이드바이용",
    "J-115": "스디", "J-120": "바나밀러스트", "J-124": "EM, C", "J-125": "니드",
    "J-134": "범캣츠", "J-200": "블랙라터", "J-201": "딩굴", "J-202": "카라",
    "J-203": "메이마트", "J-204": "뚜디어리", "J-208": "록시(HOXIE)", "J-215": "어봤구",
    "J-219": "독다학방", "J-220": "스튜디오 퐁듀", "J-223": "비타폼폼", "J-226": "하리커피",
    "J-229": "젤리부", "J-231": "개구리라미",
    
    # [K존]
    "K-101": "코리아", "K-104": "오덕스튜디오", "K-106": "라운드루프", "K-107": "율무상상",
    "K-108": "미뉴", "K-121": "아임구르미", "K-128": "방쥬", "K-130": "우거진",
    "K-201": "별히인공여", "K-204": "마늄이", "K-206": "말순마켓", "K-207": "비아 크래프트",
    "K-208": "포물덕상점", "K-211": "브패", "K-214": "묘카상심", "K-220": "마냥",
    "K-223": "쏘그리즈", "K-225": "보다스페이스", "K-229": "야음팬", "K-231": "이트맨",
    "K-235": "김중이",
    
    # [O존 - 키스틱빌리지 등]
    "O-101": "키스틱빌리지", "O-102": "zeeky", "O-104": "감성공작소", "O-110": "뚜모네",
    "O-111": "동식품원", "O-112": "개박하", "O-113": "KNOTKNOT", "O-114": "포카포카",
    "O-211": "Bangkok Fair (BKKIF)", "O-220": "단풍", "O-226": "모던보이",

    # [P존]
    "P-100": "야울이미당", "P-101": "디엠피 북스토어", "P-103": "마트", "P-108": "지연",
    "P-111": "밀크병스튜디오", "P-113": "소녀 유니버스", "P-117": "마오안(ADAN)",

    # [기타]
    "SoSo": "소소컴 (SoSo Com)",
}

# --- 3. 좌표 자동 생성 로직 (이미지 분석 기반) ---
def get_auto_coordinates(booth_code):
    """
    부스 번호(예: A-101, F-204)를 분석하여 도면상의 대략적인 좌표를 반환합니다.
    이미지 크기: 1000 x 700 (가로 x 세로) 기준 정규화
    """
    # 1. 고정 시설 좌표 (수동 매핑)
    fixed_locations = {
        "Ent-1": (350, 950), "Ent-2": (750, 950), # 입구 (하단)
        "Cafe": (150, 300), "Live": (150, 350),   # 카페테리아 (좌측 상단)
        "Sp-1": (100, 100), "Sp-2": (100, 500),   # 기획관 (좌측)
        "Sp-3": (100, 700), "Sp-4": (100, 50),
        "SoSo": (400, 400), # 소소컴 임의 위치
    }
    
    if booth_code in fixed_locations:
        return fixed_locations[booth_code]

    # 2. 부스 번호 파싱 (예: "F-204")
    match = re.match(r"([A-Z])-(\d+)", booth_code)
    if not match:
        return (500, 500) # 파싱 실패 시 중앙

    zone_char = match.group(1) # 'F'
    number = int(match.group(2)) # 204

    # 3. X축 결정 (존 별 위치)
    # A(우측) <--- ... ---> M,P(좌측)
    # 이미지 분석 결과: A존은 x=950 부근, P존은 x=300 부근
    zone_x_map = {
        'A': 950, 'B': 900, 'C': 850, 'D': 800,
        'F': 700, 'G': 650, 'H': 600, 'J': 550,
        'K': 500, 'L': 450, 'M': 400, 
        'O': 920, 'P': 350, # O, P는 특수 위치
        'S': 100 # S존은 좌측 하단 핑크색 구역
    }
    
    base_x = zone_x_map.get(zone_char, 500)

    # 4. Y축 결정 (번호 별 위치)
    # 100번대: 하단 -> 상단 (101이 아래, 130이 위)
    # 200번대: 하단 -> 상단 (201이 아래, 230이 위)
    # 도면 높이 y=50(위) ~ y=900(아래)
    
    # 번호 정규화 (0 ~ 30 사이로 변환)
    norm_num = number % 100 
    
    # 100번대와 200번대는 같은 열에 있을 수도 있고 옆 열일 수도 있음.
    # 단순화를 위해 y축은 번호가 커질수록 위로 올라간다고 설정 (이미지상 101이 아래쪽)
    # y = 900 - (norm_num * 25) 
    base_y = 850 - (norm_num * 22)

    # 약간의 X축 지그재그 (홀/짝수 열 구분 효과)
    if number >= 200:
        base_x -= 20 # 200번대는 왼쪽으로 살짝
    
    return (base_x, base_y)

# --- 4. 핵심 알고리즘 (A* & Snapping) ---
@st.cache_data
def load_nav_mesh(image_path, grid_size=(100, 70)): # 가로 100, 세로 70 비율
    try:
        img = Image.open(image_path).convert("L")
        img_resized = img.resize(grid_size)
        img_array = np.array(img_resized)
        # 흰색(배경)은 통로(0), 나머지는 벽(1)
        grid = np.where(img_array > 230, 0, 1) 
        return grid, img.size
    except Exception as e:
        return None, None

def get_nearest_walkable(grid, start_node, max_radius=15):
    rows, cols = grid.shape
    r, c = start_node
    # 범위 체크
    r = max(0, min(r, rows-1))
    c = max(0, min(c, cols-1))
    
    if grid[r][c] == 0: return (r, c)
    
    queue = deque([(r, c)])
    visited = set([(r, c)])
    
    while queue:
        curr_r, curr_c = queue.popleft()
        if grid[curr_r][curr_c] == 0: return (curr_r, curr_c)
        
        if abs(curr_r - r) > max_radius or abs(curr_c - c) > max_radius: continue
        
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return None

def heuristic(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def astar(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (f_score[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = g_score[current] + 1
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1: continue
                else: continue
            else: continue
            if neighbor in close_set and tentative_g_score >= g_score.get(neighbor, 0): continue
            if tentative_g_score < g_score.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (f_score[neighbor], neighbor))
    return None

# --- 5. 검색 함수 ---
def search_booth(keyword):
    if not keyword: return None
    kw = keyword.lower().replace("-", "").replace(" ", "")
    
    matches = []
    for code, name in RAW_BOOTH_DATA.items():
        # 검색 대상: 부스번호, 업체명
        full_str = f"{code} {name}".lower().replace("-", "").replace(" ", "")
        if kw in full_str:
            matches.append(code)
    
    # 정확도 순 정렬 (길이가 짧을수록 정확)
    matches.sort(key=len)
    return matches[0] if matches else None

# --- 6. 메인 UI ---
st.sidebar.title("🔧 관리자 메뉴")
admin_mode = st.sidebar.checkbox("좌표 직접 수정 모드", value=False)

img_path = "sik_floor_plan.jpg"

try:
    original_image = Image.open(img_path)
    # 이미지 사이즈 분석
    W, H = original_image.size
    GRID_W = 100
    GRID_H = int(GRID_W * (H / W))
    
    # 맵 데이터 로드
    grid_map, original_size = load_nav_mesh(img_path, grid_size=(GRID_W, GRID_H))
    
except FileNotFoundError:
    st.error("⚠️ 'sik_floor_plan.jpg' 파일이 필요합니다.")
    st.stop()

# ==========================================
# [관리자 모드] 좌표 미세 조정
# ==========================================
if admin_mode:
    st.title("📍 좌표 수정 시스템")
    st.info("자동 계산된 좌표가 틀렸다면, 지도에서 클릭하여 수정하세요.")
    
    # 부스 선택
    booth_list = [f"{k} ({v})" for k, v in RAW_BOOTH_DATA.items()]
    selected_str = st.selectbox("수정할 부스 선택", booth_list)
    selected_code = selected_str.split(" ")[0]
    
    st.write(f"👇 **{selected_str}**의 정확한 위치를 클릭하세요.")
    value = streamlit_image_coordinates(original_image, key="pil")
    
    if value:
        x, y = value['x'], value['y']
        
        # 시각화
        draw = ImageDraw.Draw(original_image)
        r = 15
        draw.ellipse((x-r, y-r, x+r, y+r), fill="red", outline="white", width=4)
        st.image(original_image, caption=f"수정된 위치: {selected_code}")
        
        # 코드 생성
        st.success("좌표 추출 완료! 아래 코드를 복사해서 `fixed_locations`에 추가하세요.")
        st.code(f'"{selected_code}": ({x}, {y}),')

# ==========================================
# [사용자 모드] 길찾기
# ==========================================
else:
    st.title("🎨 SIK 2025 스마트 내비게이션")
    
    with st.form("search_form"):
        c1, c2 = st.columns(2)
        start_txt = c1.text_input("출발지", placeholder="예: Ent-1, 입구")
        end_txt = c2.text_input("목적지", placeholder="예: A-101, 키스틱")
        btn = st.form_submit_button("길찾기 🚀")
    
    if btn:
        s_code = search_booth(start_txt)
        e_code = search_booth(end_txt)
        
        if not s_code or not e_code:
            st.error("❌ 장소를 찾을 수 없습니다. (업체명이나 부스번호를 확인해주세요)")
        else:
            s_name = RAW_BOOTH_DATA[s_code]
            e_name = RAW_BOOTH_DATA[e_code]
            st.success(f"🚩 경로 탐색: **{s_name}** ➡ **{e_name}**")
            
            # 1. 좌표 계산 (자동 로직 사용)
            sx, sy = get_auto_coordinates(s_code)
            ex, ey = get_auto_coordinates(e_code)
            
            # 2. 그리드 매핑 및 스내핑 (벽 탈출)
            scale_x = GRID_W / W
            scale_y = GRID_H / H
            
            g_sx, g_sy = int(sx * scale_x), int(sy * scale_y)
            g_ex, g_ey = int(ex * scale_x), int(ey * scale_y)
            
            start_node = get_nearest_walkable(grid_map, (g_sy, g_sx))
            end_node = get_nearest_walkable(grid_map, (g_ey, g_ex))
            
            # 3. 경로 탐색
            if start_node and end_node:
                path = astar(grid_map, start_node, end_node)
                
                if path:
                    # 결과 그리기
                    draw = ImageDraw.Draw(original_image)
                    
                    # 경로 (그리드 -> 픽셀)
                    pixel_path = [(int(c / scale_x), int(r / scale_y)) for r, c in path]
                    if len(pixel_path) > 1:
                        draw.line(pixel_path, fill="#FF007F", width=8)
                    
                    # 출발/도착 마커
                    r = 15
                    draw.ellipse((sx-r, sy-r, sx+r, sy+r), fill="#00C853", outline="white", width=4)
                    draw.ellipse((ex-r, ey-r, ex+r, ey+r), fill="#2962FF", outline="white", width=4)
                    
                    st.image(original_image, use_container_width=True)
                else:
                    st.warning("⚠️ 경로가 막혀있습니다. (출발지/목적지가 벽 내부에 깊숙이 있습니다)")
            else:
                st.error("⚠️ 위치를 지도상에서 특정할 수 없습니다. (맵 인식 오류)")
