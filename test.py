import streamlit as st
import pandas as pd
from datetime import date

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="My Health Diary", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #f9fafc;
        font-family: "Arial", sans-serif;
    }
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #4a90e2;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-title {
        font-size: 20px;
        color: #555;
        margin-bottom: 10px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 상태 초기화
# -----------------------------
if "logs" not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=["date", "sleep", "mood", "symptoms", "memo"])
if "goal" not in st.session_state:
    st.session_state.goal = ""
if "profile" not in st.session_state:
    st.session_state.profile = {"name": "학생", "age": 17}

# -----------------------------
# 제목
# -----------------------------
st.markdown('<div class="main-title">🌿 My Health Diary</div>', unsafe_allow_html=True)

# -----------------------------
# 사이드바 메뉴
# -----------------------------
menu = st.sidebar.radio("메뉴 선택", ["오늘 기록하기", "주간 기록 보기", "건강 목표", "자기 분석 피드백"])

# -----------------------------
# 오늘 기록하기
# -----------------------------
if menu == "오늘 기록하기":
    st.markdown('<div class="sub-title">📝 오늘의 건강 상태 기록</div>', unsafe_allow_html=True)

    with st.form("log_form", clear_on_submit=True):
        today = date.today()
        sleep = st.number_input("수면 시간 (시간)", min_value=0.0, max_value=24.0, step=0.5)
        mood = st.slider("오늘 기분", 1, 5, 3)
        symptoms = st.text_input("증상/특이사항")
        memo = st.text_area("메모")
        submitted = st.form_submit_button("저장")

        if submitted:
            new_log = {"date": today, "sleep": sleep, "mood": mood, "symptoms": symptoms, "memo": memo}
            st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_log])], ignore_index=True)
            st.success("오늘 기록이 저장되었습니다 ✅")

# -----------------------------
# 주간 기록 보기
# -----------------------------
elif menu == "주간 기록 보기":
    st.markdown('<div class="sub-title">📊 이번 주 기록</div>', unsafe_allow_html=True)

    if len(st.session_state.logs) > 0:
        last_week = st.session_state.logs.tail(7)
        st.dataframe(last_week, use_container_width=True)

        avg_sleep = last_week["sleep"].mean()
        avg_mood = last_week["mood"].mean()

        st.markdown(
            f"""
            <div class="card">
            <b>이번 주 평균</b><br>
            🌙 수면 시간: {avg_sleep:.1f}시간 <br>
            🙂 기분 점수: {avg_mood:.1f}/5
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("아직 기록이 없습니다.")

# -----------------------------
# 건강 목표 설정
# -----------------------------
elif menu == "건강 목표":
    st.markdown('<div class="sub-title">🎯 이번 주 건강 목표</div>', unsafe_allow_html=True)

    goal_input = st.text_area("이번 주 목표를 입력하세요:", st.session_state.goal)
    if st.button("목표 저장"):
        st.session_state.goal = goal_input
        st.success("목표가 저장되었습니다!")

    if st.session_state.goal:
        st.markdown(
            f"""
            <div class="card">
            현재 목표:<br> <b>{st.session_state.goal}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# 자기 분석 피드백
# -----------------------------
elif menu == "자기 분석 피드백":
    st.markdown('<div class="sub-title">🔍 자기 분석 피드백</div>', unsafe_allow_html=True)

    if len(st.session_state.logs) == 0:
        st.info("아직 기록이 없습니다. 기록을 먼저 입력해주세요!")
    else:
        recent = st.session_state.logs.tail(7)
        avg_sleep = recent["sleep"].mean()
        avg_mood = recent["mood"].mean()

        feedback = []
        if avg_sleep < 6:
            feedback.append("💤 수면 시간이 부족해요. 이번 주엔 조금 더 일찍 잠자리에 드는 건 어떨까요?")
        else:
            feedback.append("👍 수면 습관이 좋아요! 계속 유지해보세요.")

        if avg_mood <= 2:
            feedback.append("🙂 기분 점수가 낮아요. 스트레스를 풀 수 있는 활동을 해보세요.")
        elif avg_mood >= 4:
            feedback.append("🌈 기분이 안정적이네요. 좋은 습관을 잘 유지하고 있어요!")

        st.markdown(
            f"""
            <div class="card">
            <b>이번 주 자기 분석</b><br><br>
            {'<br>'.join(feedback)}
            </div>
            """,
            unsafe_allow_html=True
        )
