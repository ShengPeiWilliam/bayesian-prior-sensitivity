# Prior Sensitivity in Bayesian Logistic Regression: A Small-Sample Medical Study

Stat 205P: Bayesian Data Analysis · UC Irvine · William Chen

[![Full Report](https://img.shields.io/badge/📄_Read_Full_Report-PDF-blue?style=for-the-badge)](report/birthwt_report.pdf)

Bayesian logistic regression on the `birthwt` dataset (n=189), comparing three prior specifications, diffuse N(0,100), weakly informative N(0,2.5), and clinically informed, across sample sizes n ∈ {20, 40, 80, 189}. At full sample all three priors converge (AUC ≈ 0.747, LOOIC difference < 4). At n=20 the diffuse prior collapses under complete separation (β̂_smoke = 203), while the regularizing priors stay stable. Crucially, how quickly a coefficient stabilizes is governed not by sample size but by the number of positive cases for that predictor: smoking (74/189) stabilizes by n=40, while hypertension (12/189) persists until n=80, confirmed across 100 repeated subsampling draws.

---

## Motivation

Healthcare is a domain where decisions must be made under genuine uncertainty, a new patient walks in, data is scarce, and yet a clinical judgment is required. In Bayesian terms, this is the prior problem: when the data cannot speak loudly, what we believe before seeing it shapes what we conclude afterward.

This project asks: how sensitive are posterior inferences to prior choice, and does that sensitivity depend on sample size? The answer turns out to depend not on sample size alone, but on **predictor rarity**, a finding with direct implications for clinical datasets where the most important risk factors are often uncommon.

To explore this interactively, the fitted models are deployed on AWS S3 and EC2, so rather than a static table of coefficients, you can input a patient's characteristics and see how each prior responds differently.

--- 
## Interactive Demo

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)](http://13.221.116.154:8501)

Enter a patient's characteristics (age, smoking status, race, etc.) and the app returns predicted probability of low birth weight from all three priors, trained at four different sample sizes. The key insight is visible in the confidence intervals: at n=20, the diffuse prior collapses to near-certainty while the informative prior retains honest uncertainty.

---

## Design Decisions

**Why three priors?**

Diffuse N(0,100) represents a common default that lets the data speak freely. Weakly informative N(0,2.5) acts as a regularizer without encoding strong beliefs. The clinically informed prior sets N(1,0.5) for `smoke` and `ht`, corresponding to OR ≈ 2.7 (±2 SD: OR ∈ [1.4, 7.4]), consistent with published estimates of the smoking–adverse birth outcome association.

**Why repeated subsampling?**

A single random draw at each n risks mistaking a lucky (or unlucky) sample for a general pattern. Running 100 independent draws per n and recording the explosion rate (|β̂| > 10) converts a single observation into a distributional claim: at n=40, hypertension still explodes in 17.6% of draws; at n=80, the rate reaches zero.

**Why LOOIC and Pareto k̂ instead of in-sample AUC?**

The diffuse prior achieves AUC=1.0 at n=20, not because it predicts well, but because complete separation lets it perfectly memorize the training data. Pareto k̂ diagnostics confirm this: 20 of 20 observations have k̂ > 0.7 under the diffuse prior at n=20, making the LOO estimates unreliable. The informative prior produces only 1 problematic observation at the same sample size.

---

## Key Results

**Full data (n=189): prior choice is inconsequential**

| Model | LOOIC | AUC |
|-------|-------|-----|
| Diffuse | 223.85 | 0.746 |
| Weak | 223.32 | 0.747 |
| Informative | 220.43 | 0.748 |

**Small samples: prior choice is decisive**

| n | Model | AUC | LOOIC | Pareto k̂ > 0.7 |
|---|-------|-----|-------|-----------------|
| 20 | Diffuse | 1.000 | 8.3 | 20 |
| 20 | Weak | 0.952 | 28.1 | 5 |
| 20 | Informative | 0.905 | 27.1 | 1 |
| 40 | Diffuse | 0.808 | 65.3 | 4 |
| 40 | Informative | 0.750 | 56.3 | 1 |
| 80 | Informative | 0.777 | 98.2 | 0 |

**Repeated subsampling (100 draws per n, diffuse prior)**

| Predictor | n=20 explosion rate | n=40 explosion rate | n=80 |
|-----------|--------------------|--------------------|------|
| smoke1 | 13.0% | 1.0% | 0% |
| ui1 | 17.5% | 3.0% | 1% |
| ht1 | 31.1% (+26% undefined) | 17.6% | 0% |

---

## Reflections & Next Steps

The threshold effect, not a gradient but a step function governed by positive case count, is the finding most likely to generalize to other clinical datasets. Rare binary predictors are precisely the ones clinicians care most about, and they are the last to shed prior influence.

Next steps:
- **k-fold CV** at small n: LOO becomes unreliable when k̂ > 0.7; 10-fold CV would provide more trustworthy estimates at n=20
- **Multi-dataset validation**: replicate the rarity threshold finding on other small clinical datasets to assess generalizability
- **Hierarchical priors**: partial pooling across predictor groups as an alternative to hand-specifying informative priors

---

## Repository

```
app/
  ├── plumber.R                  # AWS-deployed API
  ├── app.py                     # Streamlit frontend
  └── requirements.txt
code/
  └── birthwt_analysis.ipynb     # Main analysis (R notebook)
figures/
  └── *.png                      # All report figures
report/
  └── birthwt_report.pdf         # Full analysis writeup
```

## Tools

**Statistical methods**: Bayesian logistic regression, LOO-CV, Pareto k̂ diagnostics, repeated subsampling  
**Language**: R  
**Libraries**: rstanarm, loo, pROC, ggplot2, dplyr  
**Deployment**: AWS S3 + EC2, Streamlit

## References

Simpson, W.J. (1957). A preliminary report on cigarette smoking and the incidence of prematurity. *American Journal of Obstetrics and Gynecology*, 73(4), 807–815.

Shah, N.R., & Bracken, M.B. (2000). A systematic review and meta-analysis of prospective studies on the association between maternal cigarette smoking and preterm delivery. *American Journal of Obstetrics and Gynecology*, 182(2), 465–472.

Hosmer, D.W., Lemeshow, S., & Sturdivant, R.X. (2013). *Applied Logistic Regression* (3rd ed.). Wiley. [source of `birthwt` dataset]
