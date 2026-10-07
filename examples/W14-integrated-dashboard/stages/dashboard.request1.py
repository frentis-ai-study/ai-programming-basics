from pathlib import Path

import pandas as pd
import streamlit as st

# 이 파일(dashboard.py)이 있는 폴더에서 CSV 파일을 찾습니다.
FOLDER = Path(__file__).parent
FORECAST_FILE = FOLDER / "forecast_records.csv"
KEYWORDS_FILE = FOLDER / "keywords.csv"


def show_table(file_path):
    """CSV 파일을 읽어서 표로 보여 줍니다. 읽지 못하면 안내를 보여 줍니다."""
    try:
        # read_csv는 파일을 읽기만 하고 바꾸지 않습니다.
        table = pd.read_csv(file_path)
    except FileNotFoundError:
        st.warning(f"{file_path.name} 파일이 없습니다. dashboard.py와 같은 폴더에 넣어 주세요.")
        return
    except Exception as error:
        st.warning(f"{file_path.name} 파일을 읽을 수 없습니다. ({error})")
        return

    st.dataframe(table, hide_index=True, use_container_width=True)


st.set_page_config(page_title="나의 기록 대시보드", layout="wide")
st.title("나의 기록 대시보드")

# 화면을 왼쪽과 오른쪽으로 나눕니다.
left, right = st.columns(2)

with left:
    st.subheader("날씨 기록")
    show_table(FORECAST_FILE)

with right:
    st.subheader("말과 횟수")
    show_table(KEYWORDS_FILE)
