import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Birthweight Risk Predictor", layout="centered")
st.title("Low Birth Weight Risk Predictor")
st.markdown("Enter patient characteristics to compare predictions across three Bayesian priors.")

# --- Input Form ---
with st.form("patient_form"):
    col1, col2 = st.columns(2)

    with col1:
        age   = st.slider("Maternal Age", 14, 45, 25)
        lwt   = st.slider("Pre-pregnancy Weight (lbs)", 80, 250, 120)
        race  = st.selectbox("Race", options=["1","2","3"],
                              format_func=lambda x: {"1":"White","2":"Black","3":"Other"}[x])
        smoke = st.selectbox("Smoking During Pregnancy", options=["0","1"],
                              format_func=lambda x: "Yes" if x=="1" else "No")

    with col2:
        ptl = st.number_input("Previous Premature Labours", min_value=0, max_value=3, value=0)
        ht  = st.selectbox("History of Hypertension", options=["0","1"],
                            format_func=lambda x: "Yes" if x=="1" else "No")
        ui  = st.selectbox("Uterine Irritability", options=["0","1"],
                            format_func=lambda x: "Yes" if x=="1" else "No")
        ftv = st.number_input("Physician Visits (1st Trimester)", min_value=0, max_value=6, value=1)

    submitted = st.form_submit_button("Predict", use_container_width=True)

# --- Prediction ---
if submitted:
    payload = {
        "age": int(age), "lwt": int(lwt),
        "race": race,    "smoke": smoke,
        "ptl": int(ptl), "ht": ht,
        "ui": ui,        "ftv": int(ftv)
    }

    try:
        response = requests.post("http://localhost:8000/predict", json=payload, timeout=30)
        result   = response.json()

        # Table
        df = pd.DataFrame({
            "Prior":    ["Diffuse", "Weak", "Informative"],
            "Mean":     [f"{result[k]['mean'][0]:.1%}"     for k in ["diffuse","weak","informative"]],
            "CI Lower": [f"{result[k]['ci_lower'][0]:.1%}" for k in ["diffuse","weak","informative"]],
            "CI Upper": [f"{result[k]['ci_upper'][0]:.1%}" for k in ["diffuse","weak","informative"]]
        })

        st.subheader("Predicted Risk of Low Birth Weight")
        st.dataframe(df, hide_index=True, use_container_width=True)

        # Chart
        means  = [result[k]["mean"][0]     for k in ["diffuse","weak","informative"]]
        lowers = [result[k]["ci_lower"][0] for k in ["diffuse","weak","informative"]]
        uppers = [result[k]["ci_upper"][0] for k in ["diffuse","weak","informative"]]
        colors = ["#E41A1C", "#377EB8", "#4DAF4A"]
        labels = ["Diffuse", "Weak", "Informative"]

        fig, ax = plt.subplots(figsize=(8, 3))
        for i, (mean, lower, upper, color, label) in enumerate(zip(means, lowers, uppers, colors, labels)):
            ax.plot([lower, upper], [i, i], color=color, linewidth=2.5)
            ax.plot(mean, i, "o", color=color, markersize=9, zorder=5)

        ax.set_yticks(range(3))
        ax.set_yticklabels(labels, fontsize=12)
        ax.set_xlabel("Predicted Probability", fontsize=11)
        ax.set_xlim(0, 1)
        ax.axvline(0.5, color="grey", linestyle="--", linewidth=1)
        ax.set_title("Posterior Predictive Probability by Prior\n(point = mean, line = 95% CI)", fontsize=12)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        ax.grid(axis="x", alpha=0.3)
        ax.spines[["top","right"]].set_visible(False)

        st.pyplot(fig)
        plt.close()

    except Exception as e:
        st.error(f"API error: {e}")