import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
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

    eval_df = pd.DataFrame(
        {
            "y_test_log": y_test,
            "y_pred_log": y_pred_log,
            "residuals_log": y_test - y_pred_log,
            "actual_dollar": y_actual_dollar,
            "pred_dollar": y_pred_dollar,
        }
    )

    return model, feature_cols, metrics, coef_df, eval_df


model, feature_cols, metrics, coef_df, eval_df = load_and_train()

# 3. 헤더 영역
st.title("💎 다이아몬드 가격 예측 다중 선형 회귀 분석")
st.caption(
    f"정제 데이터 53,772건 (Train {metrics['train_n']:,}건 / Test {metrics['test_n']:,}건) | "
    "Log-Log 다중 선형 회귀 모델"
)

# 4. 탭 구성
tab1, tab2, tab3 = st.tabs(
    ["🔮 실시간 가격 예측", "📊 모델 성능 및 회귀 계수", "🔬 잔차 진단 및 데이터 정제 요약"]
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
    # 로그 잔차 표준편차(~0.135) 기반 대략적 ±1σ 구간
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
# TAB 3: 잔차 진단 및 데이터 정제 요약
# ==============================================================================
with tab3:
    st.subheader("데이터 정제 및 전처리 파이프라인 요약")
    summary_steps = pd.DataFrame(
        {
            "단계": ["0. 원본", "1. 중복 제거", "2. 0값 제거", "3. 이상치 제거", "4. 최종 피처 확정"],
            "처리 내용": [
                "초기 데이터 로드",
                "완전 중복 146건 삭제",
                "물리적 치수(x,y,z) 0값 19건 삭제",
                "명백한 표기 오류 3건 삭제",
                "x,y,z 제거(VIF 해소) + log(carat), log(price) 변환 + 원-핫 인코딩",
            ],
            "데이터 규모": ["53,940행 × 10열", "53,794행 × 10열", "53,775행 × 10열", "53,772행 × 10열", "53,772행 × 21열"],
        }
    )
    st.table(summary_steps)

    st.subheader("테스트 세트 잔차 진단 시각화 (n = 10,755)")
    residuals = eval_df["residuals_log"]
    fitted = eval_df["y_pred_log"]

    fig_res, axes = plt.subplots(2, 2, figsize=(13, 10))

    # 1. Residuals vs Fitted
    axes[0, 0].scatter(fitted, residuals, alpha=0.15, s=8, color="#2b5c8f", edgecolors="none")
    axes[0, 0].axhline(0, color="#d62728", linestyle="--", linewidth=1.3)
    axes[0, 0].set_title("1. Residuals vs. Fitted (log_price)")
    axes[0, 0].set_xlabel("Fitted Values")
    axes[0, 0].set_ylabel("Residuals")
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Residual Histogram
    sns.histplot(residuals, bins=60, kde=True, stat="density", color="#2b5c8f", alpha=0.5, ax=axes[0, 1])
    x_grid = np.linspace(residuals.min(), residuals.max(), 200)
    axes[0, 1].plot(x_grid, stats.norm.pdf(x_grid, residuals.mean(), residuals.std()), "r--", linewidth=1.5)
    axes[0, 1].set_title("2. Residual Distribution vs. Normal")
    axes[0, 1].set_xlabel("Residuals")
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Q-Q Plot
    stats.probplot(residuals, dist="norm", plot=axes[1, 0])
    axes[1, 0].get_lines()[0].set_markersize(3)
    axes[1, 0].get_lines()[0].set_alpha(0.35)
    axes[1, 0].set_title("3. Normal Q-Q Plot")
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Actual vs Predicted ($)
    axes[1, 1].scatter(eval_df["actual_dollar"], eval_df["pred_dollar"], alpha=0.15, s=8, color="#2ca02c", edgecolors="none")
    axes[1, 1].plot([0, 20000], [0, 20000], "r--", linewidth=1.3)
    axes[1, 1].set_xlim(0, 20000)
    axes[1, 1].set_ylim(0, 22000)
    axes[1, 1].set_title("4. Actual vs. Predicted Price ($)")
    axes[1, 1].set_xlabel("Actual Price ($)")
    axes[1, 1].set_ylabel("Predicted Price ($)")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig_res)
