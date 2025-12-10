import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np
import heapq
from collections import deque
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="SIK 2025 스마트 내비게이션", page_icon="🎨", layout="wide")

# --- 2. 부스 데이터 (PDF 정밀 재분석 결과) ---
RAW_BOOTH_DATA = {
    # [시설 & 기획관]
    "Ent-1": "목/토 입구", "Ent-2": "금/일 입구",
    "Cafe": "카페테리아", "Live": "라이브드로잉",
    "Sp-1": "캐리커쳐 기획관", "Sp-2": "디저트팝업",
    "Sp-3": "아트작가 초대전", "Sp-4": "네컷프레임 사진관",
    "Sp-5": "글로벌 아티스트존", "Sp-6": "머스 기획관",
    "Sp-7": "밀리 이벤트존",

    # [A존]
    "A-100": "1989 PALETTE", "A-101": "클립아트코리아", "A-104": "끼니디자인", 
    "A-111": "소량", "A-114": "메이마트", "A-118": "디지", 
    "A-121": "페이퍼", "A-124": "자이언트아이", "A-125": "나다스토리", 
    "A-128": "홈어스", "A-130": "굿워크", "A-132": "하함스튜디오",

    # [B존]
    "B-104": "고양이다방", "B-110": "지니요니", "B-111": "TTIPCY", 
    "B-112": "자민해", "B-115": "지지(MONZIZI)", "B-120": "블루츠", 
    "B-124": "투유럽미", "B-126": "설기일러스트", "B-131": "빈집", 
    "B-201": "Gimm", "B-218": "초목점화", "B-219": "페녀리니", 
    "B-220": "농농이", "B-221": "한림사", "B-224": "키팅제이",

    # [C존]
    "C-100": "윤조유라", "C-103": "비모델 스튜디오", "C-104": "달빛곰", 
    "C-110": "붓터치", "C-111": "MachiK", "C-112": "MIND FAMILY", 
    "C-113": "yaoyao", "C-115": "inkpainting", "C-118": "Art Work Shop Kyoko", 
    "C-120": "산그리메", "C-125": "김효정", "C-129": "일러스트레이터 양파", 
    "C-130": "위시유", "C-131": "오묘", "C-200": "말로하곰곰", 
    "C-211": "광태", "C-214": "김이네", "C-218": "기온스튜디오", 
    "C-219": "리터프롤러브드", "C-220": "옴즈", "C-231": "피피",

    # [D존]
    "D-100": "말앞이 디자인", "D-101": "미야오타운", "D-103": "제니빌리지", 
    "D-107": "박산", "D-110": "로스트앤파운드", "D-115": "스튜디오 다람", 
    "D-118": "DONEARTH", "D-123": "영도리", "D-124": "타노월드", 
    "D-128": "바이고대", "D-130": "그러는 인", "D-201": "113", 
    "D-213": "Straycat tarot", "D-214": "Sleepybere", "D-215": "The 3rd Daughter", 
    "D-216": "namodo", "D-219": "머리", "D-224": "모도리 스튜디오", 
    "D-232": "Draft.apics",

    # [F존]
    "F-101": "코코의 그림공간", "F-102": "고동성", "F-103": "호랑", 
    "F-104": "아라빅스", "F-106": "프렌즈", "F-107": "담장아래", 
    "F-108": "고라니", "F-114": "달담", "F-115": "허다마리", 
    "F-116": "모모이하우스", "F-119": "오기환", "F-120": "구리", 
    "F-124": "니어바이디어", "F-128": "milky rapstar", "F-129": "모서리 스튜디오", 
    "F-130": "코스모 익스프레스", "F-131": "Rosemary Hill", "F-201": "싱포유스튜디오", 
    "F-202": "고동성", "F-203": "듀원", "F-204": "두루뭉이두더지", 
    "F-207": "복자하우스", "F-209": "단식원", "F-211": "젠디디", 
    "F-212": "연두십", "F-213": "우당탕탕스토어", "F-215": "도순상현", 
    "F-220": "잠동사니", "F-221": "다람", "F-223": "다블랙", 
    "F-224": "지우 스마일", "F-226": "스튜디오 표니", "F-229": "루이와코이누", 
    "F-231": "Catist",

    # [G존] - 수정됨
    "G-100": "쇼킹핑크로즈", 
    "G-101": "유어투데이", # [수정] 유어투데이로 확정
    "G-111": "도아세", "G-112": "동식품원", "G-114": "우연철", 
    "G-118": "백구성스튜디오", "G-120": "닛(Knit)", "G-121": "2-121", 
    "G-128": "하이볼루유", "G-129": "Ideal Idea", "G-130": "레드이어스클럽", 
    "G-200": "Thustimesu", "G-201": "콜리스튜디오", "G-214": "토끼 과 친구들", 
    "G-215": "하슈밴드", "G-223": "앙고라로라", "G-228": "CEE", 
    "G-229": "dawnitive wave", "G-231": "사리안루니",

    # [H존] - 수정됨
    "H-100": "주스", "H-101": "안녕, 말로하", "H-102": "리노프렌즈", 
    "H-104": "벨로이루", "H-107": "조각", "H-110": "츄리서랍", 
    "H-112": "유교곰", "H-119": "OHD", 
    "H-120": "민뽀패밀리", # [수정] 민뽀패밀리로 확정
    "H-129": "다라미네", "H-130": "단주스퀘어", "H-133": "studio som", 
    "H-200": "루루피94", "H-201": "채보리", "H-202": "스튜디오니모", 
    "H-203": "판타포레", "H-204": "김보미", "H-208": "수피", 
    "H-211": "디어폴리", "H-212": "세라베어", "H-216": "전", 
    "H-219": "From Gyeol", "H-220": "산뽀", "H-223": "공진어트", 
    "H-225": "아득", "H-228": "연메이드", "H-230": "큐티지파실", 
    "H-231": "허다마리",

    # [J존]
    "J-102": "차리", "J-103": "스누즈키즈", "J-106": "Netty Lee", 
    "J-112": "에이드바이용", "J-115": "스디", "J-120": "바나밀러스트", 
    "J-124": "EM, C", "J-125": "니드", "J-134": "범캣츠", 
    "J-200": "블랙라터", "J-201": "딩굴", "J-202": "카라", 
    "J-203": "메이마트", "J-204": "뚜디어리", "J-208": "록시(HOXIE)", 
    "J-215": "어봤구", "J-219": "독다학방", "J-220": "스튜디오 퐁듀", 
    "J-223": "비타폼폼", "J-226": "하리커피", "J-229": "젤리부", 
    "J-231": "개구리라미",

    # [K존]
    "K-101": "코리아", "K-104": "오덕스튜디오", "K-106": "라운드루프", 
    "K-107": "율무상상", "K-108": "미뉴", "K-121": "아임구르미", 
    "K-128": "방쥬", "K-130": "우거진", "K-201": "별히인공여 공방", 
    "K-204": "마늄이", "K-206": "말순마켓", "K-207": "비아 크래프트", 
    "K-208": "포물덕상점", "K-211": "브패", "K-214": "묘카상심", 
    "K-220": "마냥", "K-223": "쏘그리즈", "K-225": "보다스페이스", 
    "K-229": "야음팬", "K-231": "이트맨", "K-235": "김중이",

    # [L존]
    "L-100": "하나님", "L-101": "심냥즈", "L-103": "니버스", 
    "L-107": "힘교미", "L-109": "콩동이네", "L-112": "루명의 그림들", 
    "L-113": "멜팅컷", "L-120": "리얼(서예린)", "L-123": "푸어오", 
    "L-131": "고선타", "L-207": "민타", "L-215": "다그림", 
    "L-220": "모체토리", "L-224": "크리미밀키",

    # [M존] - 수정됨
    "M-101": "문학 섭", "M-102": "아야네", "M-103": "더푸리 빌리지", 
    "M-106": "코코의 그림공간", "M-107": "네", "M-110": "시코르 동사무소", 
    "M-115": "이화여대병설미디어고등학교", "M-118": "오뚝이숲", "M-120": "말로하곰곰", 
    "M-121": "채보리", "M-126": "상점", "M-128": "홈어스", 
    "M-129": "모든", "M-130": "미모", "M-131": "러브크레센트", 
    "M-201": "은 nuleun", "M-204": "노베지지에", "M-206": "밍다함 그림일기", 
    "M-207": "구냥이", "M-211": "아르베", "M-212": "으니세작업실", 
    "M-214": "Book해피핸디", "M-215": "nunnu", "M-216": "꾸꾸만들기", 
    "M-220": "리포포", "M-225": "므", 
    "M-226": "유슬", # [수정] 유어투데이 -> 유슬
    "M-228": "채도", "M-229": "Gunwoo Frierids", "M-230": "사리안루니",

    # [O존]
    "O-101": "키스틱빌리지", "O-102": "zeeky", "O-104": "감성공작소", 
    "O-110": "뚜모네", "O-111": "동식품원", "O-112": "개박하", 
    "O-113": "KNOTKNOT", "O-114": "포카포카", "O-115": "최연진", 
    "O-120": "김모양군", "O-121": "7AM", "O-126": "루마", 
    "O-131": "니어바이디어", "O-200": "3분수채초상화", "O-201": "냉이골골", 
    "O-203": "노마", "O-210": "스튜디오 쪼물", "O-211": "Bangkok Fair", 
    "O-213": "단비스페이스", "O-215": "태림", "O-218": "푸키큐티", 
    "O-220": "단풍", "O-221": "도시오브드림", "O-223": "위티프라티", 
    "O-224": "다끼스튜디오", "O-225": "차", "O-226": "모던보이", 
    "O-228": "전셋", "O-229": "네모진", "O-230": "요요", "O-231": "올리",

    # [P존] - 수정됨
    "P-100": "야울이미당", "P-101": "디엠피 북스토어", "P-103": "마트", 
    "P-108": "지연", 
    "P-111": "밀크빵스튜디오", # [수정] 밀크빵스튜디오
    "P-113": "소녀 유니버스", "P-114": "리동네친구들", "P-115": "CEE", 
    "P-116": "오불", "P-117": "마오안(ADAN)", "P-118": "즈(ploppyz)",

    # [디저트존 & 기타]
    "Dessert-01": "아리감성", "Dessert-02": "비단수적", "Dessert-03": "플라잉더치", 
    "Dessert-10": "꼬마루육포", "Dessert-13": "과밀과즙젤리", "SoSo": "소소컴",
}

# --- 3. 좌표 자동 생성 로직 (이미지 분석 기반) ---
def get_auto_coordinates(booth_code):
    fixed_locations = {
        "Ent-1": (350, 950), "Ent-2": (750, 950),
        "Cafe": (150, 300), "Live": (150, 350),
        "Sp-1": (100, 100), "Sp-2": (100, 500),
        "SoSo": (400, 400),
    }
    if booth_code in fixed_locations: return fixed_locations[booth_code]

    match = re.match(r"([A-Za-z]+)-(\d+)", booth_code)
    if not match: return (500, 500)

    zone, num = match.group(1), int(match.group(2))
    # 존별 X좌표
    x_map = {'A': 950, 'B': 900, 'C': 850, 'D': 800, 'F': 700, 'G': 650, 'H': 600, 
             'J': 550, 'K': 500, 'L': 450, 'M': 400, 'O': 920, 'P': 350, 'S': 100}
    base_x = x_map.get(zone, 500)
    # 번호별 Y좌표
    base_y = 850 - ((num % 100) * 22)
    if num >= 200: base_x -= 20
    return (base_x, base_y)

# --- 4. A* 알고리즘 ---
@st.cache_data
def load_nav_mesh(image_path, grid_size=(100, 70)):
    try:
        img = Image.open(image_path).convert("L")
        img_resized = img.resize(grid_size)
        img_array = np.array(img_resized)
        grid = np.where(img_array > 230, 0, 1) 
        return grid, img.size
    except: return None, None

def get_nearest_walkable(grid, start_node, max_radius=15):
    rows, cols = grid.shape
    r, c = start_node
    r, c = max(0, min(r, rows-1)), max(0, min(c, cols-1))
    if grid[r][c] == 0: return (r, c)
    queue, visited = deque([(r, c)]), set([(r, c)])
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

def astar(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    close_set = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(goal[0]-start[0]) + abs(goal[1]-start[1])}
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
            if 0 <= neighbor[0] < array.shape[0] and 0 <= neighbor[1] < array.shape[1]:
                if array[neighbor[0]][neighbor[1]] == 1: continue
            else: continue
            tentative_g_score = g_score[current] + 1
            if neighbor in close_set and tentative_g_score >= g_score.get(neighbor, 0): continue
            if tentative_g_score < g_score.get(neighbor, 0) or neighbor not in [x[1] for x in oheap]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + abs(goal[0]-neighbor[0]) + abs(goal[1]-neighbor[1])
                heapq.heappush(oheap, (f_score[neighbor], neighbor))
    return None

def search_booth(keyword):
    if not keyword: return None
    kw = keyword.lower().replace("-", "").replace(" ", "")
    matches = []
    for code, name in RAW_BOOTH_DATA.items():
        full = f"{code} {name}".lower().replace("-", "").replace(" ", "")
        if kw in full: matches.append(code)
    matches.sort(key=len)
    return matches[0] if matches else None

# --- 5. UI ---
st.sidebar.title("🔧 관리자 모드")
admin_mode = st.sidebar.checkbox("좌표 직접 수정", value=False)
img_path = "sik_floor_plan.jpg"

try:
    original_image = Image.open(img_path)
    W, H = original_image.size
    GRID_W, GRID_H = 100, int(100 * (H / W))
    grid_map, original_size = load_nav_mesh(img_path, grid_size=(GRID_W, GRID_H))
except:
    st.error("⚠️ sik_floor_plan.jpg 파일이 없습니다.")
    st.stop()

if admin_mode:
    st.title("📍 좌표 수정")
    booth_list = [f"{k} ({v})" for k, v in RAW_BOOTH_DATA.items()]
    sel = st.selectbox("부스 선택", booth_list)
    code = sel.split(" ")[0]
    val = streamlit_image_coordinates(original_image, key="pil")
    if val:
        x, y = val['x'], val['y']
        st.code(f'"{code}": ({x}, {y}),')
else:
    st.title("🎨 SIK 2025 스마트 내비게이션")
    with st.form("search"):
        c1, c2 = st.columns(2)
        s_txt = c1.text_input("출발지", placeholder="예: 입구")
        e_txt = c2.text_input("목적지", placeholder="예: 밀크빵, 유슬, 민뽀패밀리")
        btn = st.form_submit_button("길찾기 🚀")
    
    if btn:
        s_code, e_code = search_booth(s_txt), search_booth(e_txt)
        if s_code and e_code:
            st.success(f"🚩 **{RAW_BOOTH_DATA[s_code]}** ➡ **{RAW_BOOTH_DATA[e_code]}**")
            sx, sy = get_auto_coordinates(s_code)
            ex, ey = get_auto_coordinates(e_code)
            scale_x, scale_y = GRID_W / W, GRID_H / H
            sn, en = get_nearest_walkable(grid_map, (int(sy*scale_y), int(sx*scale_x))), get_nearest_walkable(grid_map, (int(ey*scale_y), int(ex*scale_x)))
            
            if sn and en:
                path = astar(grid_map, sn, en)
                if path:
                    draw = ImageDraw.Draw(original_image)
                    draw.line([(int(c/scale_x), int(r/scale_y)) for r, c in path], fill="#FF007F", width=6)
                    r = 15
                    draw.ellipse((sx-r, sy-r, sx+r, sy+r), fill="#00C853", outline="white", width=4)
                    draw.ellipse((ex-r, ey-r, ex+r, ey+r), fill="#2962FF", outline="white", width=4)
                    st.image(original_image, use_container_width=True)
                else: st.warning("경로가 막혀있습니다.")
            else: st.error("위치 인식 불가")
        else: st.error("부스를 찾을 수 없습니다.")
