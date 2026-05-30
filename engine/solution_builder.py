from engine.models import (
    BusSchedule,
    ChargeEvent
)


def build_solution(
    buses,
    solver,
    variables,
    station_assignments
):

    schedules = []

    for bus in buses:

        charge_events = []

        for event_data in (
            station_assignments[bus.id]
        ):

            start_var = event_data["start"]

            end_var = event_data["end"]

            arrival_var = (
                event_data["arrival"]
            )

            charge_event = ChargeEvent(
                station_id=event_data[
                    "station_id"
                ],

                arrival_time=solver.Value(
                    arrival_var
                ),

                wait_start=solver.Value(
                    arrival_var
                ),

                charge_start=solver.Value(
                    start_var
                ),

                charge_end=solver.Value(
                    end_var
                ),

                wait_duration=(
                    solver.Value(start_var)
                    -
                    solver.Value(arrival_var)
                )
            )

            charge_events.append(
                charge_event
            )

        final_arrival = max(
            e.charge_end
            for e in charge_events
        )

        schedule = BusSchedule(
            bus_id=bus.id,

            operator=bus.operator,

            departure_time=0,

            charging_plan=[
                e.station_id
                for e in charge_events
            ],

            charge_events=charge_events,

            arrival_time_final=(
                final_arrival
            ),

            total_wait_time=sum(
                e.wait_duration
                for e in charge_events
            )
        )

        schedules.append(schedule)

    return schedules