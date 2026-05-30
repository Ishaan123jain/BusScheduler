from collections import defaultdict


def compute_operator_waits(
    schedules
):

    operator_waits = defaultdict(int)

    for schedule in schedules:

        operator_waits[
            schedule.operator
        ] += schedule.total_wait_time

    return operator_waits