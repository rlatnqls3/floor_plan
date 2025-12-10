import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# --- 페이지 설정 ---
st.set_page_config(page_title="KPEX 2025 길찾기", page_icon="🗺️")

# --- CSS 스타일 ---
st.markdown("""
    <style>
    .stSelectbox { margin-bottom: 20px; }
    .guide-text { font-size: 1.2rem; font-weight: bold; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- 부스 좌표 데이터 (Demo용 주요 부스 매핑) ---
# 이미지의 왼쪽 상단을 (0, 0), 오른쪽 하단을 (100, 100)으로 보았을 때의 % 좌표입니다.
# 실제 운영 시에는 모든 부스의 좌표를 이 딕셔너리에 추가해야 합니다.
BOOTH_LOCATIONS = {
    "출입구 (세미나장 A 측)": (15, 95),
    "출입구 (세미나장 B 측)": (15, 5),
    "카페테리아": (25, 15),
    "KT (중앙 하단)": (45, 82),
    "DAEJI (우측 상단)": (88, 18),
    "경찰과학수사관": (40, 15),
    "Naviworks": (55, 15),
    "KADIF (자율주행)": (65, 15),
    "세미나장 A": (10, 85),
    "세미나장 B": (10, 35),
    "KOTRA 수출상담회장": (10, 55),
    "ETRI (연구원)": (26, 82),
    "드론 시큐리티 특별관": (65, 45),
    "소방청": (58, 88),
    "Drager (우측 중단)": (75, 40),
    "KAI (우측 중단)": (85, 40)
}

def draw_path(image, start_name, end_name):
    """이미지 위에 출발지와 도착지를 잇는 선을 그립니다."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    # 좌표 가져오기 (퍼센트를 픽셀로 변환)
    start_pos = BOOTH_LOCATIONS[start_name]
    end_pos = BOOTH_LOCATIONS[end_name]

    start_x, start_y = start_pos[0] * width / 100, start_pos[1] * height / 100
    end_x, end_y = end_pos[0] * width / 100, end_pos[1] * height / 100

    # 1. 경로 선 그리기 (두껍고 파란 선)
    # 실제 앱에서는 장애물을 피하는 알고리즘(A*)이 필요하지만, 여기서는 직관적인 직선 안내를 구현
    draw.line([(start_x, start_y), (end_x, end_y)], fill="blue", width=10)

    # 2. 출발지 표시 (초록색 원)
    r = 15 # 반지름
    draw.ellipse((start_x-r, start_y-r, start_x+r, start_y+r), fill="green", outline="white", width=3)
    
    # 3. 도착지 표시 (빨간색 원 + 타겟 마크)
    draw.ellipse((end_x-r, end_y-r, end_x+r, end_y+r), fill="red", outline="white", width=3)
    
    return img_copy

# --- 메인 UI ---
st.title("🗺️ KPEX 2025 부스 내비게이션")
st.markdown("현재 위치와 가고 싶은 부스를 선택하시면 경로를 안내해 드립니다.")

# 사이드바 혹은 메인 상단에 입력 폼 배치
col1, col2 = st.columns(2)

with col1:
    start_point = st.selectbox("📍 현재 나의 위치", list(BOOTH_LOCATIONS.keys()), index=0)

with col2:
    # 도착지는 출발지를 제외한 목록에서 선택
    target_options = [b for b in BOOTH_LOCATIONS.keys() if b != start_point]
    end_point = st.selectbox("🚩 가고 싶은 부스", target_options, index=0)

# 이미지 로드 및 처리
try:
    # GitHub 배포 시 이미지 파일 경로가 정확해야 합니다.
    image = Image.open("floor_plan.jpg")
    
    # 경로 그리기 함수 호출
    result_image = draw_path(image, start_point, end_point)
    
    st.divider()
    
    # 결과 텍스트
    st.markdown(f"<p class='guide-text'>🚀 '{start_point}'에서 '{end_point}'(으)로 이동하는 경로입니다.</p>", unsafe_allow_html=True)
    
    # 지도 표시 (화면 너비에 맞춤)
    st.image(result_image, caption="파란색 선을 따라 이동하세요.", use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ 'floor_plan.jpg' 파일을 찾을 수 없습니다. 같은 폴더에 지도 이미지를 넣어주세요.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
