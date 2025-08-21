import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta
import os

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="My Health Diary 🌱", layout="wide")

# 파스텔톤 컬러 CSS 적용
st.markdown(
    """
    <style>
    body {
        background-color: #fdfcfb;
    }
    .stApp {
        background: linear-gradient(180deg, #fdfcfb 0%, #f6f9f9 100%);
    }
    h1, h2, h3 {
        color: #2a4d4e;
    }
    .stButton>button {
        background-color: #a8e6cf;
        color: black;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #ffd3b6;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 데이터 로드 / 초기화
# -----------------------------
DATA_FILE = "health_logs.csv"

if "logs" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.logs = pd.read_csv(DATA_FILE)
    else:
        st.session_state.logs = pd.DataFrame(columns=["date", "sleep", "mood", "symptoms", "memo"])

if "profile" not in st.session_state:
    st.session_state.profile = {"height": None, "weight": None, "vaccines": []}

if "goal" not in st.session_state:
    st.session_state.goal = {"sleep_goal": 7.0}  # 기본 목표: 7시간 수면

def save_logs():
    st.session_state.logs.to_csv(DATA_FILE, index=False)

# -----------------------------
# 홈 화면
# -----------------------------
def home():
    st.title("My Health Diary 🌱")
    today = date.today().strftime("%Y-%m-%d")
    st.subheader(f"오늘 날짜: {today}")
    st.write("오늘 하루도 건강하게 보내요 🌱")

    today_log = st.session_state.logs[st.session_state.logs["date"] == today]
    if not today_log.empty:
        log = today_log.iloc[0]
        st.success(
            f"오늘 기록 현황: 수면 {log['sleep']}시간 / 기분 {log['mood']} / 증상 {log['symptoms']}"
        )
    else:
        st.info("오늘 기록이 아직 없습니다. 👉 '일일 기록'에서 작성해보세요!")

    # 주간 통계
    st.subheader("📅 이번 주 건강 요약")
    week_ago = (date.today() - timedelta(days=6)).strftime("%Y-%m-%d")
    week_logs = st.session_state.logs[st.session_state.logs["date"] >= week_ago]
    if not week_logs.empty:
        week_logs["sleep"] = pd.to_numeric(week_logs["sleep"], errors="coerce")
        avg_sleep = week_logs["sleep"].mean()
        st.write(f"이번 주 평균 수면 시간: {avg_sleep:.1f} 시간")

        # 목표 달성률
        goal = st.session_state.goal["sleep_goal"]
        achievement = (week_logs["sleep"] >= goal).sum() / len(week_logs) * 100
        st.progress(int(achievement))
        st.write(f"👉 수면 목표({goal}시간) 달성률: {achievement:.0f}%")

        # 피드백
        st.subheader("📌 자기 분석 피드백")
        if avg_sleep < goal:
            st.warning(f"이번 주는 평균 수면 시간이 {avg_sleep:.1f}시간으로 부족했어요. 주말에 휴식을 더 취해보세요!")
        else:
            st.success(f"이번 주는 평균 수면 시간이 {avg_sleep:.1f}시간으로 충분해요! 👍 앞으로도 잘 유지해봐요.")

        # 대표 기분
        mood_map = {"🙂": 1, "😐": 2, "😢": 3, "😡": 4, "🤩": 5, "😴": 6, "😰": 7, "😍": 8, "🥱": 9, "😭": 10}
        week_logs["mood_score"] = week_logs["mood"].map(mood_map)
        mood_display = week_logs["mood"].mode()[0]  # 가장 많이 선택된 기분 표시
        st.write(f"이번 주 대표 기분: {mood_display}")

# -----------------------------
# 일일 기록
# -----------------------------
def daily_log():
    st.title("📝 일일 기록")

    # 날짜 선택 가능
    selected_date = st.date_input("기록할 날짜 선택", value=date.today())
    record_date = selected_date.strftime("%Y-%m-%d")

    sleep = st.number_input("수면 시간 (시간)", min_value=0.0, max_value=24.0, step=0.5)

    # 기분/스트레스 이모티콘
    mood_options = ["🙂", "😐", "😢", "😡", "🤩", "😴", "😰", "😍", "🥱", "😭"]
    mood = st.selectbox("오늘 기분/스트레스", mood_options)

    # 증상 선택지
    symptom_options = ["두통", "복통", "피로", "감기", "기침", "콧물", "어지럼증", "근육통", "없음"]
    symptoms = st.multiselect("신체 증상", symptom_options)

    memo = st.text_area("메모")

    if st.button("저장하기"):
        if not st.session_state.logs[st.session_state.logs["date"] == record_date].empty:
            confirm = st.radio("이미 해당 날짜 기록이 있습니다. 덮어쓸까요?", ["예", "아니오"], index=1)
            if confirm == "아니오":
                st.warning("저장을 취소했습니다.")
                return
            st.session_state.logs = st.session_state.logs[st.session_state.logs["date"] != record_date]

        st.session_state.logs = pd.concat(
            [
                st.session_state.logs,
                pd.DataFrame(
                    [[record_date, sleep, mood, ",".join(symptoms), memo]],
                    columns=["date", "sleep", "mood", "symptoms", "memo"],
                ),
            ],
            ignore_index=True,
        )
        save_logs()
        st.success(f"{record_date} 기록 완료 ✅")

# -----------------------------
# 건강 통계
# -----------------------------
def statistics():
    st.title("📊 내 건강 통계")
    if st.session_state.logs.empty:
        st.warning("아직 기록이 없습니다. 먼저 일일 기록을 작성해주세요!")
        return

    df = st.session_state.logs.copy()
    df["sleep"] = pd.to_numeric(df["sleep"], errors="coerce")

    st.write(f"전체 평균 수면 시간: {df['sleep'].mean():.1f} 시간")

    # 목표 성취율
    goal = st.session_state.goal["sleep_goal"]
    achievement = (df["sleep"] >= goal).sum() / len(df) * 100
    st.write(f"👉 전체 기간 수면 목표({goal}시간) 달성률: {achievement:.0f}%")

    # 수면 시간 변화 (Altair 막대그래프)
    st.subheader("수면 시간 변화")
    df["sleep_color"] = df["sleep"].apply(lambda x: "부족(빨강)" if x < 6 else "충분(초록)" if x >= 8 else "보통(주황)")
    chart = alt.Chart(df).mark_bar().encode(
        x="date",
        y="sleep",
        color=alt.Color("sleep_color", scale=alt.Scale(domain=["부족(빨강)", "보통(주황)", "충분(초록)"],
                                                      range=["#ffaaa5", "#ffd3b6", "#a8e6cf"]))
    )
    st.altair_chart(chart, use_container_width=True)

    # 스트레스 변화 추세 (표)
    st.subheader("스트레스 변화 추세 (표)")
    mood_df = df[["date", "mood"]].sort_values("date", ascending=False)
    st.table(mood_df)  # 🟢 다시 추가

    # 자주 기록된 증상
    st.subheader("자주 기록된 증상 Top 3")
    all_symptoms = ",".join(df["symptoms"].dropna()).split(",")
    symptom_counts = pd.Series(all_symptoms).value_counts().head(3)
    st.bar_chart(symptom_counts)

# -----------------------------
# 건강 이력
# -----------------------------
def health_profile():
    st.title("📖 나의 건강 이력")
    st.subheader("📏 신체 정보")
    height = st.number_input("키 (cm)", value=st.session_state.profile["height"] or 160.0)
    weight = st.number_input("몸무게 (kg)", value=st.session_state.profile["weight"] or 50.0)
    bmi = weight / ((height / 100) ** 2) if height > 0 else 0
    st.write(f"👉 BMI: {bmi:.1f}")
    st.session_state.profile["height"] = height
    st.session_state.profile["weight"] = weight

    st.subheader("💉 예방접종 기록")
    vaccine = st.text_input("예방접종 추가")
    if st.button("추가하기"):
        if vaccine and vaccine not in st.session_state.profile["vaccines"]:
            st.session_state.profile["vaccines"].append(vaccine)
    st.write(st.session_state.profile["vaccines"])

    st.subheader("🩺 증상/메모 이력")
    st.dataframe(st.session_state.logs.sort_values("date", ascending=False)[["date", "symptoms", "memo"]])

# -----------------------------
# 도움말
# -----------------------------
def health_tips():
    st.title("💡 건강 관리 팁")
    st.subheader("스트레스 완화법")
    st.write("- 깊게 호흡하기, 스트레칭, 가벼운 산책")
    st.subheader("두통/복통 대처법")
    st.write("- 두통: 조용한 곳에서 휴식, 수분 섭취")
    st.write("- 복통: 따뜻한 찜질, 충분한 수분 섭취")
    st.subheader("수면 습관 개선 팁")
    st.write("- 규칙적인 수면 시간 유지")
    st.write("- 자기 전 스마트폰 사용 줄이기")
    st.subheader("보건 지식 코너")
    st.info("실제 간호사가 환자 건강을 관리하듯, 학생도 스스로 건강을 기록하고 관리할 수 있어요!")

# -----------------------------
# 메인 실행
# -----------------------------
menu = st.sidebar.radio("메뉴 선택", ["홈", "일일 기록", "건강 통계", "건강 이력", "도움말"])
st.sidebar.markdown("### 🎯 건강 목표 설정")
st.session_state.goal["sleep_goal"] = st.sidebar.number_input("수면 목표 (시간)", min_value=4.0, max_value=12.0, step=0.5, value=st.session_state.goal["sleep_goal"])

if menu == "홈":
    home()
elif menu == "일일 기록":
    daily_log()
elif menu == "건강 통계":
    statistics()
elif menu == "건강 이력":
    health_profile()
elif menu == "도움말":
    health_tips()
