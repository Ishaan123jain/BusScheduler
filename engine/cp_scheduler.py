from collections import defaultdict

from ortools.sat.python import cp_model

from engine.plan_generator import (
    generate_feasible_plans
)

from engine.timeline import (
    time_to_minutes
)

from engine.route_utils import (
    compute_travel_time_minutes
)

from engine.objectives import (
    build_objective
)

from engine.solution_builder import (
    build_solution
)


class CPScheduler:

    def __init__(self, scenario):

        self.scenario = scenario

        self.model = cp_model.CpModel()

        self.solver = cp_model.CpSolver()

        self.station_assignments = defaultdict(list)

    def estimate_plan_score(
        self,
        plan,
        bus,
        station_usage,
        operator_usage,
        vehicle
    ):

        congestion_score = sum(
            station_usage[station_id]
            for station_id in plan
        )

        fairness_score = sum(
            operator_usage[
                bus.operator
            ][station_id]
            for station_id in plan
        )

        stop_penalty = len(plan)

        estimated_wait = (
            congestion_score
            * vehicle.charge_duration_min
        )

        score = (
            estimated_wait * 5
            + congestion_score * 3
            + fairness_score * 2
            + stop_penalty
        )

        return score

    def schedule(self):

        route = self.scenario.route

        vehicle = (
            self.scenario.vehicle_config
        )

        for bus in self.scenario.buses:

            feasible_plans = (
                generate_feasible_plans(
                    route=route,
                    battery_range_km=(
                        vehicle.battery_range_km
                    ),
                    direction=bus.direction
                )
            )

            departure_minutes = (
                time_to_minutes(
                    bus.departure_time
                )
            )

        station_intervals = defaultdict(list)

        station_usage = defaultdict(int)

        operator_usage = defaultdict(
            lambda: defaultdict(int)
        )

        wait_vars = []

        arrival_vars = []

        operator_wait_vars = []

        for bus in self.scenario.buses:

            departure_minutes = (
                time_to_minutes(
                    bus.departure_time
                )
            )

            # --------------------------------------------------
            # PLAN SELECTION
            # --------------------------------------------------

            chosen_plan = min(
                feasible_plans,
                key=lambda plan:
                self.estimate_plan_score(
                    plan,
                    bus,
                    station_usage,
                    operator_usage,
                    vehicle
                )
            )

            for station_id in chosen_plan:

                station_usage[
                    station_id
                ] += 1

                operator_usage[
                    bus.operator
                ][station_id] += 1

            print(
                f"{bus.id}"
                f" | {bus.operator}"
                f" | {chosen_plan}"
            )

            # --------------------------------------------------
            # ROUTE DIRECTION
            # --------------------------------------------------

            current_position = (
                0
                if bus.direction
                == "forward"
                else route.total_distance
            )

            current_time = departure_minutes

            # --------------------------------------------------
            # BUILD CHARGING EVENTS
            # --------------------------------------------------

            for station_id in chosen_plan:

                station = next(
                    s
                    for s in route.stations
                    if s.id == station_id
                )

                distance = abs(
                    station.distance_from_start
                    -
                    current_position
                )

                travel_time = (
                    compute_travel_time_minutes(
                        distance,
                        vehicle.speed_kmph
                    )
                )

                arrival_time = (
                    current_time
                    + travel_time
                )

                arrival_var = (
                    self.model.NewIntVar(
                        0,
                        10000,
                        f"arrival_{bus.id}_{station_id}"
                    )
                )

                self.model.Add(
                    arrival_var
                    == arrival_time
                )

                charge_start = (
                    self.model.NewIntVar(
                        0,
                        10000,
                        f"start_{bus.id}_{station_id}"
                    )
                )

                self.model.Add(
                    charge_start
                    >= arrival_var
                )

                charge_end = (
                    self.model.NewIntVar(
                        0,
                        10000,
                        f"end_{bus.id}_{station_id}"
                    )
                )

                self.model.Add(
                    charge_end
                    ==
                    charge_start
                    + vehicle.charge_duration_min
                )

                interval = (
                    self.model.NewIntervalVar(
                        charge_start,
                        vehicle.charge_duration_min,
                        charge_end,
                        f"interval_{bus.id}_{station_id}"
                    )
                )

                station_intervals[
                    station_id
                ].append(interval)

                wait_var = (
                    self.model.NewIntVar(
                        0,
                        10000,
                        f"wait_{bus.id}_{station_id}"
                    )
                )

                self.model.Add(
                    wait_var
                    ==
                    charge_start
                    - arrival_var
                )

                wait_vars.append(wait_var)

                arrival_vars.append(
                    charge_end
                )

                operator_wait_vars.append(
                    wait_var
                )

                self.station_assignments[
                    bus.id
                ].append({
                    "station_id": station_id,
                    "arrival": arrival_var,
                    "start": charge_start,
                    "end": charge_end
                })

                current_position = (
                    station.distance_from_start
                )

                current_time = charge_end

        # --------------------------------------------------
        # CHARGER CONSTRAINTS
        # --------------------------------------------------

        for intervals in (
            station_intervals.values()
        ):

            self.model.AddNoOverlap(
                intervals
            )

        # --------------------------------------------------
        # OBJECTIVE
        # --------------------------------------------------

        build_objective(
            model=self.model,
            wait_vars=wait_vars,
            arrival_vars=arrival_vars,
            operator_wait_vars=(
                operator_wait_vars
            ),
            weights=self.scenario.weights
        )

        status = self.solver.Solve(
            self.model
        )

        if status not in (
            cp_model.OPTIMAL,
            cp_model.FEASIBLE
        ):
            raise Exception(
                "No feasible solution found"
            )

        schedules = build_solution(
            buses=self.scenario.buses,
            solver=self.solver,
            variables=None,
            station_assignments=(
                self.station_assignments
            )
        )

        print("\nStation Utilization")

        station_counts = defaultdict(int)

        for schedule in schedules:

            for event in (
                schedule.charge_events
            ):

                station_counts[
                    event.station_id
                ] += 1

        for station, count in sorted(
            station_counts.items()
        ):

            print(
                f"{station}: {count}"
            )

        return schedules
    