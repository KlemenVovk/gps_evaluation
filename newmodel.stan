data {
  int<lower=1> N_A;  // number of points in set A
  int<lower=1> N_B;  // number of points in set B
  array[N_A] vector[2] A;  // points in set A
  array[N_B] vector[2] B;  // points in set B
  vector[2] E_A;       // E wrt set A
  vector[2] E_B;       // E wrt set B
}

parameters {
  vector[2] mu_A;    // mean for set A
  vector[2] mu_B;    // mean for set B
  matrix[2,2] L_A;   // Cholesky factor of covariance for A
  matrix[2,2] L_B;   // Cholesky factor of covariance for B
}

model {
  // Likelihood for set A
  A ~ multi_normal(mu_A, L_A * L_A');

  // Likelihood for set B
  B ~ multi_normal(mu_B, L_B * L_B');
}

generated quantities {
  real log_lik_A;
  real log_lik_B;
  real log_likelihood_ratio;
  real likelihood_ratio;
  real prob_A;

  log_lik_A = multi_normal_lpdf(E_A | mu_A, L_A * L_A');
  log_lik_B = multi_normal_lpdf(E_B | mu_B, L_B * L_B');
  
  prob_A = exp(log_lik_A) / (exp(log_lik_A) + exp(log_lik_B));
  log_likelihood_ratio = log_lik_A - log_lik_B;
  likelihood_ratio = exp(log_likelihood_ratio); // not really numerically stable
}

