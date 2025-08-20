import streamlit as st
import pandas as pd
from datetime import date, timedelta

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="My Health Diary", layout="wide")

if "logs" not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=["date", "sleep", "mood", "symptoms", "memo"])
if "profile" not in st.session_state:
    st.session_state.profile = {"height": None, "weight": None, "vaccines": []}

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
    st.subheader("이번 주 건강 요약")
    week_ago = (date.today() - timedelta(days=6)).strftime("%Y-%m-%d")
    week_logs = st.session_state.logs[st.session_state.logs["date"] >= week_ago]
    if not week_logs.empty:
        week_logs["sleep"] = pd.to_numeric(week_logs["sleep"], errors="coerce")
        avg_sleep = week_logs["sleep"].mean()
        st.write(f"이번 주 평균 수면 시간: {avg_sleep:.1f} 시간")
        mood_map = {"🙂": 1, "😐": 2, "😢": 3, "😡": 4}
        week_logs["mood_score"] = week_logs["mood"].map(mood_map)
        avg_mood = week_logs["mood_score"].mean()
        mood_display = "🙂" if avg_mood < 1.5 else "😐" if avg_mood < 2.5 else "😢" if avg_mood < 3.5 else "😡"
        st.write(f"이번 주 평균 기분: {mood_display}")

# -----------------------------
# 일일 기록
# -----------------------------
def daily_log():
    st.title("📝 일일 기록")
    today = date.today().strftime("%Y-%m-%d")
    st.write(f"오늘: {today}")

    sleep = st.number_input("수면 시간 (시간)", min_value=0.0, max_value=24.0, step=0.5)
    mood = st.selectbox("오늘 기분/스트레스", ["🙂", "😐", "😢", "😡"])
    symptoms = st.multiselect("신체 증상", ["두통", "복통", "피로", "없음"])
    memo = st.text_area("메모")

    if st.button("저장하기"):
        if not st.session_state.logs[st.session_state.logs["date"] == today].empty:
            if not st.confirm("오늘 기록이 이미 있습니다. 덮어쓰시겠습니까?"):
                return
            st.session_state.logs = st.session_state.logs[st.session_state.logs["date"] != today]

        st.session_state.logs = pd.concat(
            [
                st.session_state.logs,
                pd.DataFrame(
                    [[today, sleep, mood, ",".join(symptoms), memo]],
                    columns=["date", "sleep", "mood", "symptoms", "memo"],
                ),
            ],
            ignore_index=True,
        )
        st.success("오늘 기록 완료 ✅")

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

    # 수면 시간 변화
    st.subheader("수면 시간 변화")
    sleep_chart = df.set_index("date")["sleep"]
    sleep_color = sleep_chart.apply(lambda x: "red" if x < 6 else "green" if x >= 8 else "orange")
    st.bar_chart(sleep_chart)

    # 스트레스 변화
    st.subheader("스트레스 변화 추세")
    mood_map = {"🙂": 1, "😐": 2, "😢": 3, "😡": 4}
    df["mood_score"] = df["mood"].map(mood_map)
    st.line_chart(df.set_index("date")["mood_score"])

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

    st.subheader("🩺 증상 이력")
    st.dataframe(st.session_state.logs.sort_values("date", ascending=False)[["date", "symptoms"]])

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
