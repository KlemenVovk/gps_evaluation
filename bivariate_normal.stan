data {
  int<lower=0> N1;  // number of measurements for P1
  int<lower=0> N2;  // number of measurements for P2
  array[N1] vector[2] y1;  // measurements for P1 [distance, angle]
  array[N2] vector[2] y2;  // measurements for P2 [distance, angle]
  vector[2] E_p1;    // Evidence point E in P1's coordinate system [distance, angle]
  vector[2] E_p2;    // Evidence point E in P2's coordinate system [distance, angle]
}

parameters {
  vector[2] mu1;  // mean for P1 [mean_distance, mean_angle]
  vector[2] mu2;  // mean for P2 [mean_distance, mean_angle]
  cholesky_factor_corr[2] L_Omega1;  // cholesky factor of correlation matrix for P1
  cholesky_factor_corr[2] L_Omega2;  // cholesky factor of correlation matrix for P2
  vector<lower=0>[2] sigma1;  // standard deviations for P1 [sd_distance, sd_angle]
  vector<lower=0>[2] sigma2;  // standard deviations for P2 [sd_distance, sd_angle]
}

model {
  // Priors (if not specified (as for sigma1 and sigma2 and mu1 and mu2), default, non-informative (uniform) priors are used)
  L_Omega1 ~ lkj_corr_cholesky(2);
  L_Omega2 ~ lkj_corr_cholesky(2);

  // Likelihood
  y1 ~ multi_normal_cholesky(mu1, diag_pre_multiply(sigma1, L_Omega1));
  y2 ~ multi_normal_cholesky(mu2, diag_pre_multiply(sigma2, L_Omega2));
}

generated quantities {
  matrix[2,2] L1 = diag_pre_multiply(sigma1, L_Omega1);
  matrix[2,2] L2 = diag_pre_multiply(sigma2, L_Omega2);
  real log_lik1 = multi_normal_cholesky_lpdf(E_p1 | mu1, L1);
  real log_lik2 = multi_normal_cholesky_lpdf(E_p2 | mu2, L2);
  real log_lik_ratio = log_lik1 - log_lik2;
  
  // Replicate datasets for posterior predictive checks
  array[N1] vector[2] y1_rep;
  array[N2] vector[2] y2_rep;
  
  for (n in 1:N1)
    y1_rep[n] = multi_normal_cholesky_rng(mu1, L1);
  
  for (n in 1:N2)
    y2_rep[n] = multi_normal_cholesky_rng(mu2, L2);

}