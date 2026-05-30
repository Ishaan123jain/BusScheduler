def build_objective(
    model,
    wait_vars,
    arrival_vars,
    operator_wait_vars,
    weights
):

    individual_term = (
        weights.individual
        * sum(wait_vars)
    )

    overall_term = (
        weights.overall
        * sum(arrival_vars)
    )

    operator_term = (
        weights.operator
        * sum(operator_wait_vars)
    )

    model.Minimize(
        individual_term
        + overall_term
        + operator_term
    )