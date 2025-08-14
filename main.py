import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="🌈 MBTI 직업 추천 🎯",
    page_icon="💼",
    layout="centered"
)

# CSS 스타일 (배경 + 그라데이션 + 카드 디자인)
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #FFFACD, #FFD700, #FFA500);
        color: white;
        font-family: 'Pretendard', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 42px !important;
        font-weight: bold;
        background: linear-gradient(90deg, #ff7eb3, #ff758c, #ff9770);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    .job-card {
        background-color: rgba(255, 255, 255, 0.25);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        font-size: 18px;
        backdrop-filter: blur(6px);
        cursor: pointer;
        transition: 0.3s;
    }
    .job-card:hover {
        background-color: rgba(255, 255, 255, 0.4);
        transform: scale(1.03);
    }
    </style>
""", unsafe_allow_html=True)

# MBTI별 추천 직업 + 설명 데이터
mbti_jobs = {
    "ISTJ": [
        ("📊 회계사", "재무 관리와 세무를 담당하며 기업과 개인의 회계 기록을 관리하는 전문가"),
        ("🏛️ 행정공무원", "국가와 지방자치단체의 행정업무를 수행하는 공무원"),
        ("📈 데이터 분석가", "데이터를 수집하고 분석하여 의사결정에 활용하는 직업"),
        ("🔍 품질 관리 전문가", "제품과 서비스의 품질을 유지·개선하는 전문가")
    ],
    "ENFP": [
        (
