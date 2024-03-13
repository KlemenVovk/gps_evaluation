data {
    int<lower=1> n; // total number of points
    array[n] vector[2] x; // points
}

parameters {
    // bivariate normal parameters
    vector[2] mu;
    cov_matrix[2] sigma;
}

model {
    // distances and angles are bivariate normal
    x ~ multi_normal(mu, sigma);
}
