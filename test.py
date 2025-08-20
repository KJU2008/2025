# app.py
# My Health Diary - Streamlit 웹앱
# by Jiu & GPT-5 Thinking

import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(
    page_title="My Health Diary",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path("health_data.json")

# -------------------------------
# 유틸: 데이터 로드/세이브
# -------------------------------
def _empty_store() -> Dict[str, Any]:
    return {
        "profile": {
            "name": "지우",
            "height_cm": None,
            "weight_kg": None,
            "bmi": None,
            "bmi_updated_at": None,
            "vaccines": [],  # [{"name":"독감", "date":"2025-01-15"}]
        },
        "logs": []  # list of daily logs
    }

def load_store() -> Dict[str, Any]:
    if not DATA_PATH.exists():
        return _empty_store()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _empty_store()

def save_store(store: Dict[str, Any]) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

def upsert_daily_log(store: Dict[str, Any], log: Dict[str, Any]) -> None:
    # 날짜 기준으로 업데이트 또는 추가
    logs = store["logs"]
    for i, l in enumerate(logs):
        if l["date"] == log["date"]:
            logs[i] = log
            break
    else:
        logs.append(log)
    # 날짜 순 정렬
    logs.sort(key=lambda x: x["date"])
    store["logs"] = logs
    save_store(store)

def delete_log_by_date(store: Dict[str, Any], target_date: str) -> None:
    store["logs"] = [l for l in store["logs"] if l["date"] != target_date]
    save_store(store)

# -------------------------------
# 데이터프레임 변환 & 지표 계산
# -------------------------------
STRESS_OPTIONS = {
    "🙂 낮음": 1,
    "😐 보통": 2,
    "😢 슬픔/우울": 3,
    "😡 높음": 4,
}

STRESS_EMOJI = {1:"🙂", 2:"😐", 3:"😢", 4:"😡"}

SYMPTOM_CHOICES = ["두통", "복통", "피로", "기침", "콧물", "근육통", "없음"]

def logs_to_df(logs: List[Dict[str, Any]]) -> pd.DataFrame:
    if not logs:
        return pd.DataFrame(columns=[
            "date","sleep_hours","stress_label","stress_score",
            "symptoms","water_glasses","memo"
        ])
    df = pd.DataFrame(logs)
    if "stress_label" not in df.columns and "stress" in df.columns:
        # backward compatibility
        df["stress_label"] = df["stress"]
    df["stress_score"] = df["stress_label"].map(STRESS_OPTIONS).fillna(df.get("stress_score", 2))
    df["date"] = pd.to_datetime(df["date"])
    df["sleep_hours"] = pd.to_numeric(df["sleep_hours"], errors="coerce")
    df["water_glasses"] = pd.to_numeric(df["water_glasses"], errors="coerce")
    # ensure symptoms list
    df["symptoms"] = df["symptoms"].apply(lambda x: x if isinstance(x, list) else [])
    return df.sort_values("date")

def week_month_windows(today: date):
    start_of_week = today - timedelta(days=today.weekday())  # 월요일 시작
    start_of_month = today.replace(day=1)
    return start_of_week, start_of_month

def feedback_messages(df: pd.DataFrame, today: date) -> List[str]:
    msgs = []
    if df.empty:
        return msgs
    _, start_of_month = week_month_windows(today)
    month_df = df[df["date"] >= pd.to_datetime(start_of_month)]
    if not month_df.empty:
        sleep_avg = month_df["sleep_hours"].dropna().mean()
        stress_avg = month_df["stress_score"].dropna().mean()
        if pd.notna(sleep_avg):
            if sleep_avg < 6:
                msgs.append(f"이번 달 평균 수면 {sleep_avg:.1f}시간 → 수면 부족 경고 😴")
            elif sleep_avg < 7:
                msgs.append(f"이번 달 평균 수면 {sleep_avg:.1f}시간 → 조금 더 자보자 💤")
            else:
                msgs.append(f"이번 달 평균 수면 {sleep_avg:.1f}시간 → 잘 관리 중이에요 👏")
        if pd.notna(stress_avg):
            if stress_avg >= 3.2:
                msgs.append("스트레스 지수 상승 → 가벼운 운동/산책/호흡법 추천 🏃")
            elif stress_avg <= 1.6:
                msgs.append("스트레스 관리가 좋아요 → 지금 루틴 유지하기 💚")
    return msgs

# -------------------------------
# 사이드바 내비게이션
# -------------------------------
with st.sidebar:
    st.title("🩺 My Health Diary")
    page = st.radio(
        "메뉴",
        ["홈 Home", "일일 기록 Daily Log", "내 건강 통계 Statistics",
         "나의 건강 이력 Health Profile", "도움말 Health Tips"],
        index=0
    )
    st.markdown("---")
    st.caption("누적 기록을 통해 스스로 건강을 관리해요 🌱")

# 스토어 로드
if "store" not in st.session_state:
    st.session_state.store = load_store()
store = st.session_state.store

# -------------------------------
# 0. 공통: 오늘 날짜 & 오늘 로그 가져오기
# -------------------------------
today = date.today()
today_str = today.isoformat()

df_all = logs_to_df(store["logs"])
today_log = None
if not df_all.empty:
    tdf = df_all[df_all["date"] == pd.to_datetime(today_str)]
    if not tdf.empty:
        row = tdf.iloc[0].to_dict()
        today_log = {
            "date": today_str,
            "sleep_hours": row.get("sleep_hours"),
            "stress_label": row.get("stress_label"),
            "stress_score": int(row.get("stress_score", 2)) if pd.notna(row.get("stress_score", 2)) else 2,
            "symptoms": row.get("symptoms", []),
            "water_glasses": int(row.get("water_glasses", 0)) if pd.notna(row.get("water_glasses", 0)) else 0,
            "memo": row.get("memo", "")
        }

# -------------------------------
# 1. 홈
# -------------------------------
if page == "홈 Home":
    st.header("오늘 하루도 건강하게 보내요 🌱")
    col1, col2 = st.columns([1, 2], vertical_alignment="center")
    with col1:
        st.subheader(f"📅 {today.strftime('%Y-%m-%d (%a)')}")
        st.write("나의 건강 일지에 오신 걸 환영해요!")
    with col2:
        if today_log:
            st.success("오늘 기록 현황 요약")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("수면", f"{today_log['sleep_hours']}시간")
            with c2:
                emoji = STRESS_EMOJI.get(today_log["stress_score"], "😐")
                st.metric("스트레스", f"{emoji}")
            with c3:
                st.metric("물 섭취", f"{today_log['water_glasses']}잔")
            with c4:
                sym = today_log["symptoms"]
                st.metric("증상", "없음" if (not sym or "없음" in sym) else " / ".join(sym))
        else:
            st.info("아직 오늘 기록이 없어요. 왼쪽 메뉴 **일일 기록**에서 기록해볼까요?")

    st.markdown("---")
    st.subheader("✨ 이번 달 자동 피드백")
    msgs = feedback_messages(df_all, today)
    if msgs:
        for m in msgs:
            st.write(f"- {m}")
    else:
        st.caption("기록이 더 쌓이면 맞춤 피드백이 보여요.")

    st.markdown("---")
    if not df_all.empty:
        st.subheader("📈 최근 일주일 스냅샷")
        last7 = df_all[df_all["date"] >= pd.to_datetime(today - timedelta(days=6))]
        if not last7.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.line(
                    last7,
                    x="date", y="sleep_hours",
                    title="일주일 수면 시간"
                )
                fig.update_traces(mode="lines+markers")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.line(
                    last7,
                    x="date", y="stress_score",
                    title="일주일 스트레스 추세",
                    markers=True
                )
                fig2.update_yaxes(tickmode="array", tickvals=[1,2,3,4],
                                  ticktext=["🙂 1","😐 2","😢 3","😡 4"])
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("최근 일주일 데이터가 아직 부족해요.")

# -------------------------------
# 2. 일일 기록
# -------------------------------
elif page == "일일 기록 Daily Log":
    st.header("📝 일일 기록")
    with st.form("daily_log_form", clear_on_submit=False):
        log_date = st.date_input("기록할 날짜", value=today, format="YYYY-MM-DD")
        c1, c2, c3 = st.columns(3)
        with c1:
            sleep_hours = st.number_input("수면 시간 (시간)", min_value=0.0, max_value=24.0, step=0.5,
                                          value=float(today_log["sleep_hours"]) if today_log and today_log["sleep_hours"] is not None else 7.0)
        with c2:
            stress_label = st.select_slider(
                "기분/스트레스",
                options=list(STRESS_OPTIONS.keys()),
                value=today_log["stress_label"] if today_log else "😐 보통"
            )
        with c3:
            water_glasses = st.number_input("물 섭취 (잔)", min_value=0, max_value=30, step=1,
                                            value=int(today_log["water_glasses"]) if today_log else 6)

        symptoms = st.multiselect("신체 증상 체크 (복수 선택 가능)", SYMPTOM_CHOICES,
                                  default=today_log["symptoms"] if today_log else [])
        memo = st.text_area("메모", value=today_log["memo"] if today_log else "", placeholder="예) 시험 때문에 피곤")

        submitted = st.form_submit_button("💾 오늘 기록 저장")
        if submitted:
            # '없음'이 선택되면 다른 증상은 제거
            if "없음" in symptoms:
                symptoms = ["없음"]
            new_log = {
                "date": log_date.isoformat(),
                "sleep_hours": float(sleep_hours),
                "stress_label": stress_label,
                "stress_score": int(STRESS_OPTIONS[stress_label]),
                "symptoms": symptoms,
                "water_glasses": int(water_glasses),
                "memo": memo.strip(),
            }
            upsert_daily_log(store, new_log)
            st.success(f"{log_date.isoformat()} 기록을 저장했어요 ✅")
            st.rerun()

    st.markdown("---")
    st.subheader("📜 최근 기록")
    df = logs_to_df(store["logs"]).tail(10)
    if df.empty:
        st.caption("아직 기록이 없어요.")
    else:
        df_show = df.copy()
        df_show["date"] = df_show["date"].dt.date
        df_show["stress"] = df_show["stress_score"].map(lambda s: STRESS_EMOJI.get(int(s), "😐"))
        df_show = df_show[["date","sleep_hours","stress","water_glasses","symptoms","memo"]]
        st.dataframe(df_show, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑️ 기록 삭제")
    if df_all.empty:
        st.caption("삭제할 기록이 없어요.")
    else:
        del_date = st.selectbox(
            "삭제할 날짜 선택",
            options=[d.date().isoformat() for d in df_all["date"].sort_values()],
            index=len(df_all)-1
        )
        if st.button("선택한 날짜 기록 삭제"):
            delete_log_by_date(store, del_date)
            st.success(f"{del_date} 기록을 삭제했어요.")
            st.rerun()

# -------------------------------
# 3. 통계
# -------------------------------
elif page == "내 건강 통계 Statistics":
    st.header("📊 내 건강 통계")
    df = logs_to_df(store["logs"])
    if df.empty:
        st.info("데이터가 아직 없어요. '일일 기록'에서 먼저 기록을 추가해주세요.")
    else:
        # 기간 선택
        mode = st.segmented_control("기간", options=["주간", "월간"], default="주간")
        if mode == "주간":
            start = today - timedelta(days=6)  # 오늘 포함 7일
        else:
            start = today.replace(day=1)
        fdf = df[df["date"] >= pd.to_datetime(start)]

        c1, c2 = st.columns(2)
        with c1:
            st.metric("기간 평균 수면", f"{fdf['sleep_hours'].mean():.1f} 시간")
        with c2:
            st.metric("기간 평균 스트레스", f"{fdf['stress_score'].mean():.2f} 점")

        st.markdown("### ⏱️ 수면 & 스트레스 추세")
        fig1 = px.line(fdf, x="date", y="sleep_hours", title="수면 시간 추세", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(fdf, x="date", y="stress_score", title="스트레스 추세", markers=True)
        fig2.update_yaxes(tickmode="array", tickvals=[1,2,3,4],
                          ticktext=["🙂 1","😐 2","😢 3","😡 4"])
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 🤒 자주 기록된 증상 Top3")
        # 증상 카운트 (없음 제외)
        symptom_series = (
            fdf.explode("symptoms")["symptoms"]
            .dropna()
            .loc[lambda s: s != "없음"]
        )
        if symptom_series.empty:
            st.caption("증상 기록 데이터가 부족해요.")
        else:
            top_counts = symptom_series.value_counts().head(3).reset_index()
            top_counts.columns = ["symptom", "count"]
            fig3 = px.bar(top_counts, x="symptom", y="count", title="증상 Top3")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 💬 자동 피드백")
        for m in feedback_messages(df, today):
            st.write(f"- {m}")

# -------------------------------
# 4. 건강 이력 (프로필)
# -------------------------------
elif page == "나의 건강 이력 Health Profile":
    st.header("🧍 나의 건강 이력")
    profile = store["profile"]

    with st.form("profile_form"):
        name = st.text_input("이름", value=profile.get("name") or "지우")
        c1, c2 = st.columns(2)
        with c1:
            height_cm = st.number_input("키 (cm)", min_value=0.0, max_value=250.0, step=0.1,
                                        value=float(profile.get("height_cm") or 0.0))
        with c2:
            weight_kg = st.number_input("몸무게 (kg)", min_value=0.0, max_value=300.0, step=0.1,
                                        value=float(profile.get("weight_kg") or 0.0))
        submitted = st.form_submit_button("프로필 저장")
        if submitted:
            bmi = None
            if height_cm and weight_kg and height_cm > 0:
                bmi = round(weight_kg / ((height_cm/100) ** 2), 2)
            profile.update({
                "name": name.strip() or "지우",
                "height_cm": round(height_cm, 1) if height_cm else None,
                "weight_kg": round(weight_kg, 1) if weight_kg else None,
                "bmi": bmi,
                "bmi_updated_at": datetime.now().isoformat(timespec="seconds"),
            })
            store["profile"] = profile
            save_store(store)
            st.success("프로필을 저장했어요.")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("키 (cm)", f"{profile.get('height_cm') or '-'}")
    with c2:
        st.metric("몸무게 (kg)", f"{profile.get('weight_kg') or '-'}")
    with c3:
        bmi = profile.get("bmi")
        st.metric("BMI", f"{bmi if bmi is not None else '-'}")

    st.caption("※ BMI는 참고용 지표이며, 개인의 건강 상태는 여러 요인을 함께 고려해야 합니다.")

    st.markdown("### 💉 예방접종 기록")
    vacs = profile.get("vaccines", [])
    if vacs:
        vdf = pd.DataFrame(vacs)
        vdf = vdf.sort_values("date")
        st.dataframe(vdf, use_container_width=True, hide_index=True)
    else:
        st.caption("예방접종 기록이 없습니다.")

    with st.expander("예방접종 기록 추가"):
        with st.form("vaccine_form", clear_on_submit=True):
            v_name = st.text_input("백신명 (예: 독감, HPV, A형간염)")
            v_date = st.date_input("접종일", value=today)
            add_v = st.form_submit_button("추가")
            if add_v:
                if v_name.strip():
                    vacs.append({"name": v_name.strip(), "date": v_date.isoformat()})
                    profile["vaccines"] = vacs
                    store["profile"] = profile
                    save_store(store)
                    st.success("예방접종 기록을 추가했어요.")
                    st.rerun()
                else:
                    st.error("백신명을 입력해주세요.")

    st.markdown("---")
    st.subheader("📚 증상 이력 요약")
    df = logs_to_df(store["logs"])
    if df.empty:
        st.caption("아직 기록이 없어요.")
    else:
        counts = (
            df.explode("symptoms")["symptoms"]
            .dropna()
            .loc[lambda s: s != "없음"]
            .value_counts()
        )
        if counts.empty:
            st.caption("증상 이력이 충분하지 않아요.")
        else:
            top = counts.head(10).reset_index()
            top.columns = ["증상", "횟수"]
            st.dataframe(top, use_container_width=True, hide_index=True)

# -------------------------------
# 5. 도움말
# -------------------------------
elif page == "도움말 Health Tips":
    st.header("🧰 Health Tips (자가 관리 가이드)")
    st.write("학생 생활에 맞춘 간단한 건강 관리 팁이에요. 필요할 때마다 펼쳐서 확인해요!")

    with st.expander("🧘 스트레스 완화법"):
        st.markdown("""
- 4-7-8 호흡: **4초 들이마시기 → 7초 멈추기 → 8초 내쉬기**를 4~8회 반복  
- 20분 산책: 햇빛 · 리듬 걸음이 기분 개선에 도움  
- **디지털 디톡스**: 잠자기 30분 전부터 화면 끄기
        """)

    with st.expander("😴 수면 습관 개선"):
        st.markdown("""
- 기상/취침 시간 **고정**  
- 오후 늦게 **카페인 줄이기**  
- 침대는 **잠과 휴식만** (공부/핸드폰은 책상에서)
        """)

    with st.expander("🤒 흔한 증상 대처(두통/복통/피로)"):
        st.markdown("""
- **두통**: 수분 섭취, 조용한 공간에서 10~15분 휴식, 과도한 화면 사용 줄이기  
- **복통**: 기름진 음식 피하고 미지근한 물, 통증이 심하면 보건실/병원 방문  
- **피로**: 규칙 수면 + 가벼운 스트레칭, 과제는 **작게 쪼개서** 하기
        """)

    with st.expander("🩺 보건 지식 코너 (간호 진로 연결)"):
        st.markdown("""
- **기록의 힘**: 간호사는 환자 **V/S(활력징후)**와 증상 변화를 **시간 흐름**으로 기록/해석해요.  
  이 앱에서의 **수면·스트레스·증상 그래프**는 간호 기록의 기초 연습이에요.
- **피드백 루프**: 데이터 → 변화 파악 → **개입(산책/호흡/수면 조정)** → 재평가
        """)

    st.caption("※ 건강 문제로 걱정될 땐 반드시 보호자/의료진과 상의하세요.")

# -------------------------------
# 푸터
# -------------------------------
st.markdown("---")
st.caption("© 2025 My Health Diary · 하루 한 줄 기록으로 건강 습관 만들기 🌱")
