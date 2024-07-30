data {
    int<lower=1> n; // total number of reference points collected for one proposal
    array[n] vector[2] dist_ang; // reference points for one proposal
}

parameters {
    vector[2] mu;
    cov_matrix[2] sigma;
}

model {
    dist_ang ~ multi_normal(mu, sigma);
}