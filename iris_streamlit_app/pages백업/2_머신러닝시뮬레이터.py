import streamlit as st
import pandas as pd
import altair as alt
from iris_model import FEATURES, train_model
from ui import page_intro

page_intro("03 / IRIS LAB", "네 가지 측정값, 세 가지 붓꽃", "꽃받침과 꽃잎의 길이·너비를 입력하고 SVM 모델이 어떤 종으로 분류하는지 실험해 보세요.")
st.caption("예측 대상은 씨앗 자체가 아니라 붓꽃의 종(species)입니다. 네 특징의 단위는 모두 cm입니다.")

@st.cache_resource
def get_model():
    return train_model()

bundle = get_model()
X, names = bundle["X"], bundle["names"]
a, b, c = st.columns(3)
a.metric("학습 데이터", f'{len(bundle["X_train"])}개')
b.metric("평가 데이터", f'{len(bundle["X_test"])}개')
c.metric("평가 정확도", f'{bundle["accuracy"]:.1%}')
st.caption(f'150개 중 120개로 학습하고 별도 30개에서 {bundle["correct"]}개를 맞혔습니다. 종별 비율을 유지하여 분리하며 random_state=42로 고정합니다.')

with st.expander("입력하기 전 · 꽃받침과 꽃잎은 무엇인가요?"):
    st.markdown('''- **꽃받침(sepal):** 꽃 바깥쪽을 받치는 부분입니다.
- **꽃잎(petal):** 꽃의 안쪽에서 관찰되는 꽃잎입니다.
- 네 값의 **순서**를 바꾸면 다른 예측이 나올 수 있습니다.
- 아래 범위는 전체 붓꽃 데이터에서 관측된 값이며 생물학적으로 가능한 모든 범위는 아닙니다.''')
    st.table(pd.DataFrame({"특징": FEATURES, "관측 최솟값": X.min().values, "관측 최댓값": X.max().values}))

st.markdown("## 1. 측정값 입력")
st.caption("직접 숫자를 입력하거나 예시를 불러오세요. 예시는 실제 데이터의 한 행이며 정답을 가려 보는 평가용 샘플이 아닙니다.")
PRESETS = {"직접 입력": None, "setosa 예시": (5.1, 3.5, 1.4, 0.2), "versicolor 예시": (7.0, 3.2, 4.7, 1.4), "virginica 예시": (6.3, 3.3, 6.0, 2.5)}
keys = ["iris_sl", "iris_sw", "iris_pl", "iris_pw"]
for key, val in zip(keys, PRESETS["setosa 예시"]):
    if key not in st.session_state:
        st.session_state[key] = val

def apply_preset():
    values = PRESETS[st.session_state["iris_preset"]]
    if values is not None:
        for key, value in zip(keys, values):
            st.session_state[key] = value
    st.session_state.pop("iris_result", None)

st.selectbox("실험 시작값", list(PRESETS), key="iris_preset", on_change=apply_preset)
with st.form("iris_inputs"):
    left, right = st.columns(2)
    with left:
        sl = st.number_input(FEATURES[0], min_value=0.1, max_value=20.0, step=0.1, format="%.1f", key=keys[0])
        sw = st.number_input(FEATURES[1], min_value=0.1, max_value=20.0, step=0.1, format="%.1f", key=keys[1])
    with right:
        pl = st.number_input(FEATURES[2], min_value=0.1, max_value=20.0, step=0.1, format="%.1f", key=keys[2])
        pw = st.number_input(FEATURES[3], min_value=0.1, max_value=20.0, step=0.1, format="%.1f", key=keys[3])
    submitted = st.form_submit_button("붓꽃의 종 예측하기", type="primary")

if submitted:
    values = [sl, sw, pl, pw]
    sample = pd.DataFrame([values], columns=FEATURES)
    prediction = int(bundle["model"].predict(sample)[0])
    result = {"values": values, "species": names[prediction]}
    st.session_state["iris_result"] = result
    history = st.session_state.get("iris_history", [])
    history.append(dict(zip(FEATURES, values), 예측=result["species"]))
    st.session_state["iris_history"] = history[-20:]

st.markdown("## 2. 예측 결과")
result = st.session_state.get("iris_result")
if result is None:
    st.info("네 값을 확인한 후 ‘붓꽃의 종 예측하기’를 눌러 주세요.")
else:
    st.success(f'예측한 붓꽃의 종: **{result["species"]}**')
    st.dataframe(pd.DataFrame([result["values"]], columns=FEATURES), hide_index=True)
    outside = [label for label, val, lo, hi in zip(FEATURES, result["values"], X.min(), X.max()) if val < lo or val > hi]
    if outside:
        st.warning("관측 범위를 벗어난 특징: " + ", ".join(outside) + ". 모델은 범위 밖에서도 한 종을 출력하므로 이 결과를 신뢰하기 어렵습니다.")
    st.caption("위 결과는 마지막으로 제출한 입력에 대한 것입니다. 값을 바꿨다면 예측 버튼을 다시 눌러 주세요. 평가 정확도는 이 개별 예측의 확률이 아닙니다.")
    chart_data = X.copy()
    chart_data["종"] = [names[int(i)] for i in bundle["y"]]
    base = alt.Chart(chart_data).mark_circle(size=65, opacity=0.65).encode(
        x=alt.X(f"{FEATURES[2]}:Q", scale=alt.Scale(zero=False)),
        y=alt.Y(f"{FEATURES[3]}:Q", scale=alt.Scale(zero=False)),
        color=alt.Color("종:N", scale=alt.Scale(domain=names, range=["#0f766e", "#2563eb", "#a855f7"])),
        tooltip=FEATURES + ["종"],
    )
    point = pd.DataFrame([{FEATURES[2]: result["values"][2], FEATURES[3]: result["values"][3]}])
    overlay = alt.Chart(point).mark_point(shape="diamond", size=260, color="#dc2626", filled=True, stroke="white").encode(x=f"{FEATURES[2]}:Q", y=f"{FEATURES[3]}:Q")
    st.altair_chart((base + overlay).properties(height=320), use_container_width=True)
    st.caption("빨간 마름모는 입력값입니다. 산점도는 꽃잎의 두 특징만 보여 주지만 모델은 네 특징을 모두 사용합니다. 점들의 위치는 결정 경계가 아닙니다.")

with st.expander("실험 기록 · 최근 20회"):
    history = st.session_state.get("iris_history", [])
    if history:
        records = pd.DataFrame(history)
        st.dataframe(records, hide_index=True)
        st.download_button("기록 CSV 다운로드", records.to_csv(index=False).encode("utf-8-sig"), "iris_experiments.csv", "text/csv")
        if st.button("기록 지우기"):
            st.session_state["iris_history"] = []
            st.rerun()
    else:
        st.write("아직 예측 기록이 없습니다.")

with st.expander("모델과 평가 살펴보기"):
    st.markdown('''**표준화 → SVM(RBF 커널)** 파이프라인을 사용합니다. `C=1.0`, `gamma="scale"`로 고정합니다.
표준화와 모델 모두 학습 데이터 120개에만 맞춥니다. 예측에도 같은 모델을 사용하며 평가 데이터로 다시 학습하지 않습니다.

**혼동행렬:** 행은 실제 종, 열은 예측한 종입니다. 대각선은 정답 수입니다.''')
    st.dataframe(pd.DataFrame(bundle["confusion"], index=["실제 " + n for n in names], columns=["예측 " + n for n in names]))
    st.markdown("**관찰 활동:** 꽃받침 값을 고정한 채 꽃잎 길이만 조금씩 바꿔 보세요. 예측이 바뀌는 구간을 찾고 다른 특징도 같은 역할을 하는지 비교해 보세요.")
with st.expander("원본 데이터 보기"):
    full = X.copy()
    full["종"] = [names[int(i)] for i in bundle["y"]]
    st.dataframe(full, hide_index=True)
st.markdown("[데이터 출처: scikit-learn Iris](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html) · [SVM 문서](https://scikit-learn.org/stable/modules/svm.html)")
