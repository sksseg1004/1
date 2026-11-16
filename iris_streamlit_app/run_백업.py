import streamlit as st

urls = urls = [
        'https://www.youtube.com/watch?v=KR8ddnPjCtk', 
        'https://www.youtube.com/watch?v=CgSvahZkJmc', 
        'https://www.youtube.com/watch?v=CgSvahZkJmc'
    ]
images = ['data:image/webp;base64,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']

st.title("This is my first webapp")
con1, con2 = st.columns((4, 1))
with con1:
    with st.expander("Content..."):
        for i in range(len(urls)):
            st.video(urls[i])
        pass

with con2:
    with st.expander("Tips..."):
        st.image(images[0])
        pass

con3, con4 = st.columns((4,1))
with con3:
    with st.expander('Content....'):
        import pandas as pd
        from pathlib import Path
        df = pd.read_csv(Path(__file__).parent / "data.csv")
        st.write(df)
with con4:
    with st.expander("Tips..."):
        with open("ml.txt", "r", encoding="utf8") as f:
            mytxt = f.read()
            st.markdown(mytxt)

        st.image(images[0])