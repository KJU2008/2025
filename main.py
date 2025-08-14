import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="🌈 MBTI 직업 추천 🎯",
    page_icon="💼",
    layout="centered"
)

# CSS로 폰트 & 배경 꾸미기
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #FFD3A5, #FD6585);
        color: blue;
        font-family: 'Pretendard', sans-serif;
    }
    .stSelectbox label {
        font-size: 18px;
        font-weight: bold;
        color: #fff !important;
    }
    .title {
        text-align: center;
        font-size: 40px !important;
        font-weight: bold;
        color: #fff;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .job-card {
        background-color: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        font-size: 18px;
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

# MBTI별 추천 직업 데이터 (이모지 추가)
mbti_jobs = {
    "ISTJ": ["📊 회계사", "🏛️ 행정공무원", "📈 데이터 분석가", "🔍 품질 관리 전문가"],
    "ISFJ": ["💉 간호사", "🤝 사회복지사", "📚 교사", "📝 비서"],
    "INFJ": ["🗣️ 심리상담사", "✍️ 작가", "🌍 사회운동가", "📖 교사"],
    "INTJ": ["📊 경영 컨설턴트", "📌 전략 기획가", "🔬 과학자", "💻 시스템 분석가"],
    "ISTP": ["⚙️ 엔지니어", "🛠️ 항공 정비사", "🚑 응급 구조사", "🧭 탐험가"],
    "ISFP": ["🎨 디자이너", "🎵 작곡가", "💆‍♀️ 치료사", "📷 사진작가"],
    "INFP": ["✍️ 작가", "🧠 상담사", "🎭 예술가", "🔍 연구원"],
    "INTP": ["🔍 연구원", "💻 프로그래머", "💡 발명가", "📚 교수"],
    "ESTP": ["💼 영업 전문가", "📰 기자", "🚑 구급대원", "🎉 이벤트 기획자"],
    "ESFP": ["🎬 배우", "🎤 방송 진행자", "🗺️ 관광 가이드", "🏋️ 트레이너"],
    "ENFP": ["📣 마케팅 전문가", "🎤 강연가", "✍️ 작가", "📢 광고 기획자"],
    "ENTP": ["🚀 기업가", "⚖️ 변호사", "🎥 PD", "🏛️ 정치가"],
    "ESTJ": ["📂 경영자", "🪖 군인", "⚖️ 판사", "📅 프로젝트 매니저"],
    "ESFJ": ["📚 교사", "💉 간호사", "🤝 상담사", "📢 홍보 전문가"],
    "ENFJ": ["🧭 리더십 코치", "📚 교사", "📢 홍보 전문가", "🏛️ 정치인"],
    "ENTJ": ["💼 CEO", "⚖️ 변호사", "📌 전략 컨설턴트", "🪖 군 장교"]
}

# 앱 제목
st.markdown("<h1 class='title'>🌈 MBTI 기반 직업 추천 🎯</h1>", unsafe_allow_html=True)
st.write("당신의 MBTI를 선택하면 ✨ 화려하게 ✨ 직업을 추천해드립니다!")

# MBTI 선택
mbti_options = list(mbti_jobs.keys())
selected_mbti = st.selectbox("📌 MBTI를 선택하세요:", mbti_options)

# 추천 직업 표시
if selected_mbti:
    st.markdown(f"## 🔍 {selected_mbti} 유형 추천 직업")
    for job in mbti_jobs[selected_mbti]:
        st.markdown(f"<div class='job-card'>{job}</div>", unsafe_allow_html=True)

# 참고 문구
st.markdown("---")
st.caption("※ 추천 직업은 일반적인 성향을 기반으로 참고용으로만 제공됩니다.")
