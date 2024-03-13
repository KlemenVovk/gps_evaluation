# libraries --------------------------------------------------------------------
library(cmdstanr)
library(ggplot2)
library(ggdist)
library(posterior)
library(bayesplot)
library(mcmcse)

csv <- 'p2'
df <- read.csv(paste0(csv, ".csv"))

model <- cmdstan_model("model.stan")


stan_data <- list(
  n = nrow(df),
  x = matrix(c(df$Distance, df$Angle), nrow = nrow(df), ncol = 2)
)

fit <- model$sample(
  data = stan_data,
  seed = 1,
  parallel_chains = 4
)

mcmc_trace(fit$draws())
fit$summary()

results <- as_draws_df(fit$draws())
results <- results[,c(2,3,4,5,6,7)]
colnames(results) <- c("mu_dist", "mu_angle", "sigma11", "sigma21", "sigma12", "sigma22")
write.csv(results, paste0(csv, "_draws.csv"), row.names = FALSE, quote = FALSE)
