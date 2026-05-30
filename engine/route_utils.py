from typing import List

from engine.models import Route, Station


def get_station_order(route: Route, direction: str) -> List[Station]:
    """
    Returns stations in travel order depending on direction.
    """

    stations = sorted(
        route.stations,
        key=lambda s: s.distance_from_start
    )

    if direction == "forward":
        return stations

    return list(reversed(stations))


def compute_travel_time_minutes(
    distance_km: int,
    speed_kmph: int
) -> int:
    """
    Computes travel time in minutes.
    """

    hours = distance_km / speed_kmph

    return int(hours * 60)