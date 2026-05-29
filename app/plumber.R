library(plumber)
library(rstanarm)

fit.diffuse     <- readRDS("../models/fit_diffuse.rds")
fit.weak        <- readRDS("../models/fit_weak.rds")
fit.informative <- readRDS("../models/fit_informative.rds")

#* @apiTitle Birthweight Prediction API
#* @apiDescription Predict low birth weight risk under three Bayesian priors

#* @post /predict
function(age, lwt, race, smoke, ptl, ht, ui, ftv) {

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

  predict_model <- function(fit) {
    samples <- posterior_epred(fit, newdata = new_patient)
    list(
      mean     = round(mean(samples), 4),
      ci_lower = round(quantile(samples, 0.025), 4),
      ci_upper = round(quantile(samples, 0.975), 4)
    )
  }

  list(
    diffuse     = predict_model(fit.diffuse),
    weak        = predict_model(fit.weak),
    informative = predict_model(fit.informative)
  )
}