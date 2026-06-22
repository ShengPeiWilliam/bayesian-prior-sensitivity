import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Low Birth Weight Risk Predictor")
st.markdown("**Prior Sensitivity in Bayesian Logistic Regression: A Small-Sample Medical Study**")
st.markdown("**William Chen · Stat 205P: Bayesian Data Analysis · UC Irvine**")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-bayesian--prior--sensitivity-181717?logo=github)](https://github.com/ShengPeiWilliam/bayesian-prior-sensitivity)")
st.markdown("---")

left, right = st.columns([1, 2])

with left:
    st.markdown("**Enter patient characteristics to see how prior choice matters across different data sizes.**")
    with st.form("patient_form"):
        age   = st.slider("Maternal Age", 14, 45, 25)
        lwt   = st.slider("Pre-pregnancy Weight (lbs)", 80, 250, 120)
        race  = st.selectbox("Race", options=["1","2","3"],
                            format_func=lambda x: {"1":"White","2":"Black","3":"Other"}[x])
        ht    = st.selectbox("History of Hypertension", options=["0","1"],
                            format_func=lambda x: "Yes" if x=="1" else "No")
        smoke = st.selectbox("Smoking During Pregnancy", options=["0","1"],
                            format_func=lambda x: "Yes" if x=="1" else "No")
        ui    = st.selectbox("Uterine Irritability", options=["0","1"],
                            format_func=lambda x: "Yes" if x=="1" else "No")
        ptl   = st.number_input("Previous Premature Labours", min_value=0, max_value=3, value=0)
        ftv   = st.number_input("Physician Visits (1st Trimester)", min_value=0, max_value=6, value=1)
        submitted = st.form_submit_button("Predict", use_container_width=True)

with right:
    if submitted:
        base_payload = {
            "age": int(age), "lwt": int(lwt),
            "race": race,    "smoke": smoke,
            "ptl": int(ptl), "ht": ht,
            "ui": ui,        "ftv": int(ftv)
        }

        all_results = {}
        n_sizes = [20, 40, 80, 189]

        try:
            for n in n_sizes:
                payload = {**base_payload, "n": n}
                response = requests.post("http://localhost:8000/predict", json=payload, timeout=30)
                all_results[n] = response.json()

            st.subheader("Predicted Risk of Low Birth Weight")
            st.caption("Same patient, same prior — but trained on different amounts of data. Notice how the CIs widen at small n, especially for the diffuse prior.")

            colors = {"Diffuse": "#E41A1C", "Weak": "#377EB8", "Informative": "#4DAF4A"}
            priors = ["informative", "weak", "diffuse"]
            prior_labels = ["Informative", "Weak", "Diffuse"]

            row1 = st.columns(2)
            row2 = st.columns(2)
            grid = [row1[0], row1[1], row2[0], row2[1]]

            for col, n in zip(grid, n_sizes):
                result = all_results[n]
                means  = [result[k]["mean"][0]     for k in priors]
                lowers = [result[k]["ci_lower"][0] for k in priors]
                uppers = [result[k]["ci_upper"][0] for k in priors]

                fig, ax = plt.subplots(figsize=(5, 2.8))
                for i, (mean, lower, upper, label) in enumerate(zip(means, lowers, uppers, prior_labels)):
                    color = colors[label]
                    ax.plot([lower, upper], [i, i], color=color, linewidth=2.5)
                    ax.plot(mean, i, "o", color=color, markersize=9, zorder=5)

                ax.set_yticks(range(3))
                ax.set_yticklabels(prior_labels, fontsize=11)
                ax.set_xlim(0, 1)
                n_labels = {20: "n = 20  (very small clinic)", 40: "n = 40  (small clinic)",
                            80: "n = 80  (medium clinic)", 189: "n = 189  (full dataset)"}
                ax.set_title(n_labels[n], fontsize=11, fontweight="bold")
                ax.axvline(0.5, color="grey", linestyle="--", linewidth=1)
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
                ax.set_xlabel("Predicted Probability", fontsize=10)
                ax.grid(axis="x", alpha=0.3)
                ax.spines[["top","right"]].set_visible(False)
                plt.tight_layout()

                col.pyplot(fig)
                plt.close()

                df_n = pd.DataFrame({
                    "Prior":    prior_labels[::-1],
                    "Mean":     [f"{result[k]['mean'][0]:.1%}"     for k in priors[::-1]],
                    "CI Lower": [f"{result[k]['ci_lower'][0]:.1%}" for k in priors[::-1]],
                    "CI Upper": [f"{result[k]['ci_upper'][0]:.1%}" for k in priors[::-1]],
                })
                col.dataframe(df_n, hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"API error: {e}")
    else:
        st.info("Fill in patient characteristics on the left and click Predict.")