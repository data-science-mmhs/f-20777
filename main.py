import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
)

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="다이아몬드 가격 예측 분석 대시보드",
    page_icon="💎",
    layout="wide",
)


# 2. 데이터 로드 및 모델 학습 (최초 1회 실행 후 캐싱)
@st.cache_resource
def load_and_train():
    train_df = pd.read_csv("diamonds_train.csv")
    test_df = pd.read_csv("diamonds_test.csv")

    feature_cols = [c for c in train_df.columns if c != "log_price"]
    X_train, y_train = train_df[feature_cols], train_df["log_price"]
    X_test, y_test = test_df[feature_cols], test_df["log_price"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # 테스트 세트 예측 (로그 및 달러 환산)
    y_pred_log = pd.Series(model.predict(X_test), index=y_test.index)
    y_actual_dollar = np.exp(y_test)
    y_pred_dollar = np.exp(y_pred_log)

    metrics = {
        "r2_log": r2_score(y_test, y_pred_log),
        "r2_dollar": r2_score(y_actual_dollar, y_pred_dollar),
        "rmse_dollar": np.sqrt(mean_squared_error(y_actual_dollar, y_pred_dollar)),
        "mae_dollar": mean_absolute_error(y_actual_dollar, y_pred_dollar),
        "mape_pct": mean_absolute_percentage_error(y_actual_dollar, y_pred_dollar) * 100,
        "train_n": len(train_df),
        "test_n": len(test_df),
    }

    coef_df = pd.DataFrame(
        {
            "피처명": feature_cols,
            "회귀계수(coef)": model.coef_,
            "가격_변화율(%)": (np.exp(model.coef_) - 1) * 100,
        }
    )

    return model, feature_cols, metrics, coef_df


model, feature_cols, metrics, coef_df = load_and_train()

# 3. 헤더 영역
st.title("💎 다이아몬드 가격 예측 다중 선형 회귀 분석")
st.caption(
    f"정제 데이터 53,772건 (Train {metrics['train_n']:,}건 / Test {metrics['test_n']:,}건) | "
    "Log-Log 다중 선형 회귀 모델"
)

# 4. 탭 구성
tab1, tab2, tab3 = st.tabs(
    ["🔮 실시간 가격 예측", "📊 모델 성능 및 회귀 계수", "🧹 데이터 정제 및 전처리 상세"]
)

# ==============================================================================
# TAB 1: 실시간 가격 예측 시뮬레이터
# ==============================================================================
with tab1:
    st.subheader("다이아몬드 조건 입력 및 예측 가격 산출")

    col_input, col_result = st.columns([1.2, 1])

    with col_input:
        carat = st.slider("무게 (Carat)", min_value=0.20, max_value=5.00, value=1.00, step=0.01)

        c1, c2, c3 = st.columns(3)
        with c1:
            cut = st.selectbox(
                "컷 등급 (Cut)",
                ["Fair", "Good", "Very Good", "Premium", "Ideal"],
                index=4,
            )
        with c2:
            color = st.selectbox(
                "색상 등급 (Color, D=최상)",
                ["J", "I", "H", "G", "F", "E", "D"],
                index=3,
            )
        with c3:
            clarity = st.selectbox(
                "투명도 등급 (Clarity, IF=최상)",
                ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"],
                index=3,
            )

        c4, c5 = st.columns(2)
        with c4:
            depth = st.number_input("깊이 비율 (Depth %)", min_value=43.0, max_value=79.0, value=61.7, step=0.1)
        with c5:
            table = st.number_input("테이블 비율 (Table %)", min_value=43.0, max_value=95.0, value=57.5, step=0.1)

    # 입력값 -> 피처 벡터 변환
    input_dict = {col: 0.0 for col in feature_cols}
    input_dict["log_carat"] = np.log(carat)
    input_dict["depth"] = depth
    input_dict["table"] = table

    if f"cut_{cut}" in input_dict:
        input_dict[f"cut_{cut}"] = 1.0
    if f"color_{color}" in input_dict:
        input_dict[f"color_{color}"] = 1.0
    if f"clarity_{clarity}" in input_dict:
        input_dict[f"clarity_{clarity}"] = 1.0

    input_df = pd.DataFrame([input_dict])[feature_cols]
    pred_log_val = model.predict(input_df)[0]
    pred_dollar_val = np.exp(pred_log_val)
    low_bound = np.exp(pred_log_val - 0.1353)
    high_bound = np.exp(pred_log_val + 0.1353)

    with col_result:
        st.markdown("### 예측 결과")
        st.metric(label="예상 적정 가격 (USD)", value=f"${pred_dollar_val:,.2f}")
        st.info(
            f"**68% 신뢰 예측 범위 (±1σ)**: `${low_bound:,.2f}` ~ `${high_bound:,.2f}`\n\n"
            f"- 모델 로그 출력값 (`log_price`): `{pred_log_val:.4f}`\n"
            f"- 캐럿당 환산 단가: `${pred_dollar_val / carat:,.2f} / ct`"
        )

# ==============================================================================
# TAB 2: 모델 성능 및 회귀 계수 분석
# ==============================================================================
with tab2:
    st.subheader("테스트 세트(10,755건) 성능 지표")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("설명력 R² (달러 기준)", f"{metrics['r2_dollar']:.4f}")
    m2.metric("설명력 R² (로그 기준)", f"{metrics['r2_log']:.4f}")
    m3.metric("평균 절대 오차 (MAE)", f"${metrics['mae_dollar']:,.2f}")
    m4.metric("평균 오차율 (MAPE)", f"{metrics['mape_pct']:.2f}%")

    st.divider()
    st.subheader("등급별 기준 대비 가격 상승률 (%)")

    cat_coef = coef_df[coef_df["피처명"].str.startswith(("cut_", "color_", "clarity_"))].copy()
    fig_coef, ax = plt.subplots(figsize=(10, 5))
    colors = [
        "#4c72b0" if x.startswith("cut_") else "#55a868" if x.startswith("color_") else "#c44e52"
        for x in cat_coef["피처명"]
    ]
    ax.barh(cat_coef["피처명"], cat_coef["가격_변화율(%)"], color=colors)
    ax.set_xlabel("Price Premium vs. Base Grade (%)")
    ax.set_title("Price Multiplier by Quality Grade (Base: Cut=Fair, Color=J, Clarity=I1)")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_coef)

    with st.expander("전체 회귀 계수 상세 테이블 보기"):
        st.dataframe(coef_df.round(4), use_container_width=True)

# ==============================================================================
# TAB 3: 데이터 정제 및 전처리 상세 기록
# ==============================================================================
with tab3:
    st.subheader("1. 단계별 데이터 정제 및 전처리 전체 이력")
    st.markdown(
        "원본 `diamonds.csv` 데이터(53,940건)에서 결측치(0건)를 확인한 뒤, "
        "선형 회귀 모델의 통계적 가정과 수치 안정성을 확보하기 위해 아래 6단계 전처리를 수행했습니다."
    )

    pipeline_detail = pd.DataFrame(
        {
            "단계": [
                "0단계: 원본 데이터 로드",
                "1단계: 완전 중복 행 제거",
                "2단계: 물리적 0값 정제",
                "3단계: 명백한 입력 오류 제거",
                "4단계: 범주형 변수 원-핫 인코딩",
                "5단계: 피처 선택 및 로그 변환",
                "6단계: 8:2 층화 분할",
            ],
            "세부 처리 기준 및 적용 방법": [
                "diamonds.csv 초기 로드 (수치형 7열, 범주형 3열, 결측치 0건 확인)",
                "모든 열 값이 완전히 동일한 중복 레코드 탐지 후 첫 행만 유지 (drop_duplicates)",
                "실물 보석에서 불가능한 가로·세로·깊이 치수(x, y, z) 중 하나라도 0인 행 삭제",
                "소수점 오기 및 열 밀림으로 판단되는 극단적 기하학 오류 3건 삭제 (y=58.9, z=31.8, y=31.8)",
                "cut(5등급), color(7등급), clarity(8등급)에 대해 다중공선성 방지를 위한 기준 범주 제외 인코딩 (drop_first=True)",
                "VIF > 1,000을 유발하는 x, y, z 열 삭제 후 carat·price 자연로그(np.log) 변환 적용",
                "가격 오름차순 정렬 편향 방지를 위해 log_price를 10개 분위수(Decile)로 나눈 뒤 8:2 층화 분할 (random_state=42)",
            ],
            "변화 내역": [
                "기준 데이터셋",
                "-146건 삭제",
                "-19건 삭제",
                "-3건 삭제",
                "+14열 확장 (더미 17열 생성)",
                "-3열 삭제, 스케일 변환",
                "Train 43,017 / Test 10,755",
            ],
            "데이터 규모": [
                "53,940행 × 10열",
                "53,794행 × 10열",
                "53,775행 × 10열",
                "53,772행 × 10열",
                "53,772행 × 24열",
                "53,772행 × 21열",
                "Train 80% / Test 20%",
            ],
        }
    )
    st.dataframe(pipeline_detail, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("2. 주요 전처리 의사결정 및 기술적 근거")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### ① 다중공선성(Multicollinearity) 해소")
        st.markdown(
            """
            - **문제 진단**: 무게(`carat`)와 물리적 크기(`x, y, z`) 간 상관계수가 0.95 이상이며, 분산팽창지수(**VIF > 1,000**)로 회귀 계수의 분산이 크게 팽창함.
            - **해결 조치**: 치수 변수 **`x`, `y`, `z`를 모두 제거**하고 무게(`carat`), 깊이 비율(`depth`), 테이블 비율(`table`)만 유지하여 독립변수 간 선형 종속성을 제거함.
            """
        )

        st.markdown("#### ② 범주형 인코딩 기준 (Reference Category)")
        st.markdown(
            """
            - 더미 변수 함정(Dummy Variable Trap) 방지를 위해 각 등급의 최하위 카테고리를 기준(0)으로 설정하고 **총 17개 더미 변수** 생성:
              - **Cut (4열)**: `Good`, `Very Good`, `Premium`, `Ideal` *(기준: `Fair`)*
              - **Color (6열)**: `I`, `H`, `G`, `F`, `E`, `D` *(기준: `J`)*
              - **Clarity (7열)**: `SI2`, `SI1`, `VS2`, `VS1`, `VVS2`, `VVS1`, `IF` *(기준: `I1`)*
            """
        )

    with col_b:
        st.markdown("#### ③ `carat` 및 `price` 자연로그(`np.log`) 변환 근거")
        st.markdown(
            """
            - **비선형 관계 직선화**: 다이아몬드 가격은 무게 증가에 따라 지수적으로 급등하므로 양변에 자연로그를 취해 1:1 선형 비례 관계로 변환함.
            - **음수($) 예측 원천 차단**: `price` 원본으로 학습 시 소형 다이아몬드 **1,857건이 마이너스(-) 가격으로 예측**되는 문제를 `np.exp()` 역변환 구조로 완전히 해결함.
            - **예측 오차 절반 감소**: 테스트 RMSE가 `$1,832.93`에서 **`$807.59`**로 55% 이상 개선됨.
            """
        )

        st.markdown("#### ④ 최종 모델 입력 변수 구조 (총 21열)")
        st.markdown(
            """
            - **독립변수 (20개)**: `log_carat`, `depth`, `table` (3개) + 범주형 더미 (17개)
            - **타겟 변수 (1개)**: `log_price` (예측 시 지수 함수 `np.exp()`로 USD 환산)
            - **분할 검증**: Train 평균 `$3,929.77` / Test 평균 `$3,936.62`로 가격대별 분포 동일하게 유지
            """
        )
