data {
  int<lower=0> N1;  // number of measurements for P1
  int<lower=0> N2;  // number of measurements for P2
  array[N1] vector[2] y1;  // measurements for P1 [distance, angle]
  array[N2] vector[2] y2;  // measurements for P2 [distance, angle]
  vector[2] E_p1;    // Evidence point E in P1's coordinate system [distance, angle]
  vector[2] E_p2;    // Evidence point E in P2's coordinate system [distance, angle]
}

parameters {
  vector[2] mu1;     // mean for P1 measurements
  vector[2] mu2;     // mean for P2 measurements
  vector<lower=0>[2] sigma1;  // [sigma_r, sigma_theta] for P1
  vector<lower=0>[2] sigma2;  // [sigma_r, sigma_theta] for P2
  real<lower=-1,upper=1> rho1;  // correlation between r and theta for P1
  real<lower=-1,upper=1> rho2;  // correlation between r and theta for P2
}

transformed parameters {
  matrix[2,2] Sigma1;
  matrix[2,2] Sigma2;
  
  Sigma1[1,1] = square(sigma1[1]);
  Sigma1[2,2] = square(sigma1[2]);
  Sigma1[1,2] = rho1 * sigma1[1] * sigma1[2];
  Sigma1[2,1] = Sigma1[1,2];
  
  Sigma2[1,1] = square(sigma2[1]);
  Sigma2[2,2] = square(sigma2[2]);
  Sigma2[1,2] = rho2 * sigma2[1] * sigma2[2];
  Sigma2[2,1] = Sigma2[1,2];

}

model {
  // Priors
  mu1 ~ normal(0, 10);
  mu2 ~ normal(0, 10);
  sigma1 ~ normal(0, 10);
  sigma2 ~ normal(0, 10);
  rho1 ~ uniform(-1, 1);
  rho2 ~ uniform(-1, 1);

  // Likelihood
  y1 ~ multi_normal(mu1, Sigma1);  // P1 measurements
  y2 ~ multi_normal(mu2, Sigma2);  // P2 measurements
}

generated quantities {
  real log_lik1;  // log-likelihood of evidence under P1's DGP
  real log_lik2;  // log-likelihood of evidence under P2's DGP
  real log_lik_ratio; // log-likelihood ratio

  log_lik1 = multi_normal_lpdf(E_p1 | mu1, Sigma1);
  log_lik2 = multi_normal_lpdf(E_p2 | mu2, Sigma2);
  log_lik_ratio = log_lik1 - log_lik2;


  // replicate data for posterior predictive checks
  array[N1] vector[2] y1_rep;
  array[N2] vector[2] y2_rep;

  for (n in 1:N1) {
    y1_rep[n] = multi_normal_rng(mu1, Sigma1);
  }

  for (n in 1:N2) {
    y2_rep[n] = multi_normal_rng(mu2, Sigma2);
  }
}