def compute_schedule_score(
    bus_schedule,
    weights
):

    individual_cost = (
        bus_schedule.total_wait_time
    )

    overall_cost = (
        bus_schedule.arrival_time_final
    )

    # Placeholder for future
    operator_cost = 0

    total_score = (
        weights.individual * individual_cost
        +
        weights.operator * operator_cost
        +
        weights.overall * overall_cost
    )

    return total_score