data {
    int<lower=1> n; // total number of reference points collected for one proposal
    array[n] vector[2] x; // reference points for one proposal
}

parameters {
    vector[2] mu;
    cov_matrix[2] sigma;
}

model {
    x ~ multi_normal(mu, sigma);
}