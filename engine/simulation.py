from engine.models import (
    Bus,
    BusSchedule,
    ChargeEvent,
    Route
)

from engine.route_utils import (
    compute_travel_time_minutes,
    get_station_order
)


def simulate_bus_journey(
    bus: Bus,
    route: Route,
    charging_plan,
    station_queues,
    vehicle_config,
    departure_time_minutes
):

    stations = get_station_order(
        route,
        bus.direction
    )

    station_map = {
        s.id: s
        for s in route.stations
    }

    current_time = departure_time_minutes

    if bus.direction == "forward":
        current_position = 0
    else:
        current_position = route.total_distance

    charge_events = []

    total_wait = 0

    for station_id in charging_plan:

        station = station_map[station_id]

        target_position = (
            station.distance_from_start
        )

        distance = abs(
            target_position - current_position
        )

        travel_time = compute_travel_time_minutes(
            distance,
            vehicle_config.speed_kmph
        )

        arrival_time = current_time + travel_time

        queue = station_queues[station_id]

        reservation = queue.reserve_slot(
            bus_id=bus.id,
            arrival_time=arrival_time,
            charge_duration=vehicle_config.charge_duration_min
        )

        charge_event = ChargeEvent(
            station_id=station_id,

            arrival_time=arrival_time,

            wait_start=arrival_time,

            charge_start=reservation["charge_start"],

            charge_end=reservation["charge_end"],

            wait_duration=reservation["wait_duration"]
        )

        charge_events.append(charge_event)

        total_wait += (
            reservation["wait_duration"]
        )

        current_time = reservation["charge_end"]

        current_position = target_position

    # Final trip to destination
    if bus.direction == "forward":
        destination = route.total_distance
    else:
        destination = 0

    final_distance = abs(
        destination - current_position
    )

    final_travel_time = (
        compute_travel_time_minutes(
            final_distance,
            vehicle_config.speed_kmph
        )
    )

    arrival_final = (
        current_time + final_travel_time
    )

    return BusSchedule(
        bus_id=bus.id,

        operator=bus.operator,

        departure_time=departure_time_minutes,

        charging_plan=charging_plan,

        charge_events=charge_events,

        arrival_time_final=arrival_final,

        total_wait_time=total_wait
    )