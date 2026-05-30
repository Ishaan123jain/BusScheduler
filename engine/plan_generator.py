from itertools import combinations
from typing import List

from engine.models import Route, Station


def generate_feasible_plans(
    route: Route,
    battery_range_km: int,
    direction: str
) -> List[List[str]]:

    stations = sorted(
        route.stations,
        key=lambda s: s.distance_from_start
    )

    if direction == "backward":
        stations = list(reversed(stations))

    station_ids = [s.id for s in stations]

    valid_plans = []

    for r in range(1, len(station_ids) + 1):

        for combo in combinations(station_ids, r):

            if is_plan_valid(
                plan=combo,
                stations=stations,
                battery_range_km=battery_range_km,
                total_distance=route.total_distance,
                direction=direction
            ):
                valid_plans.append(
                    list(combo)
                )

    return valid_plans


def is_plan_valid(
    plan,
    stations: List[Station],
    battery_range_km: int,
    total_distance: int,
    direction: str
) -> bool:

    station_map = {
        s.id: s.distance_from_start
        for s in stations
    }

    if direction == "forward":

        checkpoints = [0]

        for station_id in plan:
            checkpoints.append(
                station_map[station_id]
            )

        checkpoints.append(
            total_distance
        )

    else:

        checkpoints = [total_distance]

        for station_id in plan:
            checkpoints.append(
                station_map[station_id]
            )

        checkpoints.append(0)

    for i in range(
        len(checkpoints) - 1
    ):

        segment_distance = abs(
            checkpoints[i + 1]
            -
            checkpoints[i]
        )

        if (
            segment_distance
            >
            battery_range_km
        ):
            return False

    return True