from engine.plan_generator import (
    generate_feasible_plans
)

from engine.simulation import (
    simulate_bus_journey
)

from engine.station_queue import (
    StationQueue
)

from engine.timeline import (
    time_to_minutes
)

from engine.scoring import (
    compute_schedule_score
)


class Scheduler:

    def __init__(self, scenario):

        self.scenario = scenario

        self.station_queues = {
            station.id: StationQueue(
                station.id
            )
            for station in scenario.route.stations
        }

        self.feasible_plans = (
            generate_feasible_plans(
                route=scenario.route,
                battery_range_km=(
                    scenario.vehicle_config
                    .battery_range_km
                )
            )
        )

    def schedule(self):

        bus_schedules = []

        buses_sorted = sorted(
            self.scenario.buses,
            key=lambda b: b.departure_time
        )

        for bus in buses_sorted:

            best_schedule = None

            best_score = float("inf")

            departure_minutes = (
                time_to_minutes(
                    bus.departure_time
                )
            )

            for plan in self.feasible_plans:

                temp_station_queues = (
                    self._clone_station_queues()
                )

                schedule = (
                    simulate_bus_journey(
                        bus=bus,
                        route=self.scenario.route,
                        charging_plan=plan,
                        station_queues=temp_station_queues,
                        vehicle_config=(
                            self.scenario
                            .vehicle_config
                        ),
                        departure_time_minutes=(
                            departure_minutes
                        )
                    )
                )

                score = (
                    compute_schedule_score(
                        schedule,
                        self.scenario.weights
                    )
                )

                if score < best_score:

                    best_score = score

                    best_schedule = schedule

                    best_queues = (
                        temp_station_queues
                    )

            self.station_queues = best_queues

            bus_schedules.append(
                best_schedule
            )

        return bus_schedules

    def _clone_station_queues(self):

        cloned = {}

        for station_id, queue in (
            self.station_queues.items()
        ):

            new_queue = StationQueue(
                station_id
            )

            new_queue.available_at = (
                queue.available_at
            )

            new_queue.events = (
                queue.events.copy()
            )

            cloned[station_id] = new_queue

        return cloned