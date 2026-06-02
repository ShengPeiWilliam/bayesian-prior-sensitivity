library(plumber)
library(rstanarm)

model_sets <- list()
for (n in c(20, 40, 80, 189)) {
  model_sets[[as.character(n)]] <- list(
    diffuse     = readRDS(paste0("../models/fit_diffuse_n",     n, ".rds")),
    weak        = readRDS(paste0("../models/fit_weak_n",        n, ".rds")),
    informative = readRDS(paste0("../models/fit_informative_n", n, ".rds"))
  )
}

#* @apiTitle Birthweight Prediction API
#* @apiDescription Predict low birth weight risk under three Bayesian priors

#* @post /predict
function(age, lwt, race, smoke, ptl, ht, ui, ftv, n = "189") {

  new_patient <- data.frame(
    age   = as.integer(age),
    lwt   = as.integer(lwt),
    race  = factor(race,  levels = c("1", "2", "3")),
    smoke = factor(smoke, levels = c("0", "1")),
    ptl   = as.integer(ptl),
    ht    = factor(ht,    levels = c("0", "1")),
    ui    = factor(ui,    levels = c("0", "1")),
    ftv   = as.integer(ftv)
  )

  fits <- model_sets[[as.character(n)]]

  predict_model <- function(fit) {
    samples <- posterior_epred(fit, newdata = new_patient)
    list(
      mean     = round(mean(samples), 4),
      ci_lower = round(quantile(samples, 0.025), 4),
      ci_upper = round(quantile(samples, 0.975), 4)
    )
  }

  list(
    n           = as.integer(n),
    diffuse     = predict_model(fits$diffuse),
    weak        = predict_model(fits$weak),
    informative = predict_model(fits$informative)
  )
}