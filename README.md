# Prior Sensitivity in Bayesian Logistic Regression: A Small-Sample Medical Study

Stat 205P: Bayesian Data Analysis · UC Irvine · William Chen

Bayesian logistic regression on the `birthwt` dataset (n=189), comparing three prior specifications — diffuse N(0, 100), weakly informative N(0, 2.5), and clinically informed — across sample sizes from n=20 to n=189. At full sample, all three priors converge to comparable posteriors and AUC (~0.75). At n=20, the diffuse prior produces credible intervals roughly twice as wide as the informative prior for key predictors (`smoke`, `ht`), demonstrating that prior choice has measurable consequences precisely when clinical data is scarcest.

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)](http://13.221.116.154:8501)

[![Full Report](https://img.shields.io/badge/📄_Read_Full_Report-PDF-blue?style=for-the-badge)](report/birthwt_report.pdf)


---

## Motivation

Healthcare is a domain where decisions must be made under genuine uncertainty — a new patient walks in, data is scarce, and yet a clinical judgment is required. In Bayesian terms, this is the prior problem: when the data cannot speak loudly, what we believe before seeing it shapes what we conclude afterward.

This project asks two related questions. First, how sensitive are posterior inferences to prior choice, and does that sensitivity depend on sample size? Second, what does it actually look like when different priors lead to different answers about the same patient?

To explore this interactively, I deployed the fitted models on AWS S3 and EC2 — so rather than a static table of coefficients, you can input a patient's characteristics and see how each prior responds differently.

---