from pathlib import Path

import pandas as pd
import streamlit as st

# 이 파일(dashboard.py)이 있는 폴더에서 CSV 파일을 찾습니다.
FOLDER = Path(__file__).parent
FORECAST_FILE = FOLDER / "forecast_records.csv"
KEYWORDS_FILE = FOLDER / "keywords.csv"

# 그래프 색: 최고기온은 주황, 최저기온은 파랑
MAX_COLOR = "#eb6834"
MIN_COLOR = "#2a78d6"


def read_table(file_path):
    """CSV 파일을 읽어서 돌려줍니다. 읽지 못하면 안내를 보여 주고 None을 돌려줍니다."""
    try:
        # read_csv는 파일을 읽기만 하고 바꾸지 않습니다.
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.warning(f"{file_path.name} 파일이 없습니다. dashboard.py와 같은 폴더에 넣어 주세요.")
    except Exception as error:
        st.warning(f"{file_path.name} 파일을 읽을 수 없습니다. ({error})")
    return None


def show_table(table):
    """표를 보여 줍니다."""
    st.dataframe(table, hide_index=True, use_container_width=True)


def show_weather_summary(table):
    """기록한 날 수, 가장 높은 최고기온, 가장 낮은 최저기온을 보여 줍니다."""
    hottest = table.loc[table["max"].idxmax()]  # 최고기온이 가장 높은 줄
    coldest = table.loc[table["min"].idxmin()]  # 최저기온이 가장 낮은 줄

    box1, box2, box3 = st.columns(3)
    with box1:
        st.metric("기록한 날 수", f"{len(table)}일")
    with box2:
        st.metric("가장 높은 최고기온", f"{hottest['max']}℃")
        st.caption(f"{hottest['date']}")
    with box3:
        st.metric("가장 낮은 최저기온", f"{coldest['min']}℃")
        st.caption(f"{coldest['date']}")


def show_weather_chart(table):
    """날짜별 최고기온과 최저기온을 선 그래프로 보여 줍니다."""
    # 원래 표는 그대로 두고, 그래프에 쓸 표를 따로 만듭니다.
    chart_table = pd.DataFrame(
        {
            "날짜": pd.to_datetime(table["date"]),  # 날짜로 바꾸면 날짜 사이 간격이 그대로 보입니다.
            "최고기온": table["max"],
            "최저기온": table["min"],
        }
    )
    st.line_chart(
        chart_table,
        x="날짜",
        y=["최고기온", "최저기온"],
        y_label="기온(℃)",
        color=[MAX_COLOR, MIN_COLOR],
    )


def show_keyword_summary(table):
    """가장 많이 나온 말과 그 횟수를 보여 줍니다."""
    top = table.loc[table["count"].idxmax()]  # 횟수가 가장 큰 줄
    st.metric("가장 많이 나온 말", f"{top['word']}")
    st.caption(f"{top['count']}번")


def show_keyword_chart(table):
    """많이 나온 말을 고른 개수만큼 막대그래프로 보여 줍니다."""
    # 화면에서 개수를 고릅니다. 3개부터 10개까지, 처음에는 5개입니다.
    how_many = st.slider("막대그래프에 보여 줄 말의 개수", min_value=3, max_value=10, value=5)

    # 횟수가 큰 순서로 고른 개수만큼 줄을 고릅니다. 횟수가 같으면 파일에 먼저 나온 말이 뽑힙니다.
    top_words = table.nlargest(how_many, "count")
    chart_table = pd.DataFrame({"말": top_words["word"], "횟수": top_words["count"]})
    st.bar_chart(chart_table, x="말", y="횟수", sort=False, horizontal=True)
    st.caption(f"많이 나온 {len(top_words)}개 (횟수가 같으면 파일에 먼저 나온 말)")


st.set_page_config(page_title="나의 기록 대시보드", layout="wide")
st.title("나의 기록 대시보드")

# 화면을 왼쪽과 오른쪽으로 나눕니다.
left, right = st.columns(2)

with left:
    st.subheader("날씨 기록")
    weather = read_table(FORECAST_FILE)
    if weather is not None:
        # 요약이나 그래프를 만들 수 없어도 표는 보여 줍니다.
        try:
            show_weather_summary(weather)
            show_weather_chart(weather)
        except Exception:
            st.info("요약과 그래프를 만들 수 없습니다. date, max, min 칸과 그 값을 확인해 주세요.")
        show_table(weather)

with right:
    st.subheader("말과 횟수")
    keywords = read_table(KEYWORDS_FILE)
    if keywords is not None:
        try:
            show_keyword_summary(keywords)
            show_keyword_chart(keywords)
        except Exception:
            st.info("요약과 그래프를 만들 수 없습니다. word, count 칸과 그 값을 확인해 주세요.")
        show_table(keywords)
