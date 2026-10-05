import streamlit as st

st.title("통합 대시보드")
st.write("도시를 입력한 뒤 확인 버튼을 눌러 주세요.")

city = st.text_input("도시", value="")

if st.button("확인"):
    city = city.strip()

    if not city:
        st.info("도시를 입력해 주세요.")
        st.stop()

    st.success(f"입력한 도시: {city}")
