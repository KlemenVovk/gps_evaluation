library(cmdstanr)
library(bayesplot)
library(mcmcse)
library(posterior)

# csv of points
csv <- 'p1'
df <- read.csv(paste0(csv, ".csv"))

# compile the stan model
model <- cmdstan_model("model.stan")

# fit a bivariate normal distribution using stan (MCMC)
stan_data <- list(
  n = nrow(df),
  x = matrix(c(df$dist, df$angle), nrow = nrow(df), ncol = 2)
)

fit <- model$sample(
  data = stan_data,
  seed = 1,
  parallel_chains = 4
)

# diagnostics
mcmc_trace(fit$draws())
fit$summary()

# save the draws
results <- as_draws_df(fit$draws())
results <- results[,c(2,3,4,5,6,7)]
colnames(results) <- c("mu_dist", "mu_angle", "sigma11", "sigma21", "sigma12", "sigma22")
write.csv(results, paste0(csv, "_draws.csv"), row.names = FALSE, quote = FALSE)
