import os

import pandas as pd
import streamlit as st

from engine.loader import load_scenario
from engine.cp_scheduler import CPScheduler

from engine.timeline import (
    minutes_to_time
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Bus Charging Scheduler",
    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🚌 Bus Charging Scheduler")

st.markdown(
    """
    Constraint-based EV bus charging scheduler
    using OR-Tools CP-SAT optimization.
    """
)

# ---------------------------------------------------
# LOAD SCENARIOS
# ---------------------------------------------------

SCENARIO_DIR = "scenarios"

scenario_files = sorted(
    [
        file
        for file in os.listdir(SCENARIO_DIR)
        if file.endswith(".json")
    ]
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("Scenario Selection")

selected_scenario = st.sidebar.selectbox(
    "Choose Scenario",
    scenario_files
)

# ---------------------------------------------------
# LOAD SCENARIO
# ---------------------------------------------------

scenario = load_scenario(
    selected_scenario
)

# ---------------------------------------------------
# SCENARIO OVERVIEW
# ---------------------------------------------------

st.header("Scenario Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Buses",
        len(scenario.buses)
    )

with col2:
    st.metric(
        "Stations",
        len(scenario.route.stations)
    )

with col3:
    st.metric(
        "Battery Range",
        f"{scenario.vehicle_config.battery_range_km} km"
    )

# ---------------------------------------------------
# WEIGHTS
# ---------------------------------------------------

st.subheader("Optimization Weights")

weights_df = pd.DataFrame(
    [
        {
            "Individual": scenario.weights.individual,
            "Operator": scenario.weights.operator,
            "Overall": scenario.weights.overall
        }
    ]
)

st.dataframe(
    weights_df,
    use_container_width=True
)

# ---------------------------------------------------
# ROUTE INFORMATION
# ---------------------------------------------------

st.subheader("Route Information")

route_rows = []

for station in scenario.route.stations:

    route_rows.append({
        "Station": station.id,
        "Distance From Start": (
            station.distance_from_start
        ),
        "Chargers": station.chargers
    })

route_df = pd.DataFrame(route_rows)

st.dataframe(
    route_df,
    use_container_width=True
)

# ---------------------------------------------------
# RAW BUS INPUT
# ---------------------------------------------------

st.subheader("Bus Input Data")

bus_rows = []

for bus in scenario.buses:

    bus_rows.append({
        "Bus ID": bus.id,
        "Operator": bus.operator,
        "Direction": bus.direction,
        "Departure": bus.departure_time
    })

bus_df = pd.DataFrame(bus_rows)

st.dataframe(
    bus_df,
    use_container_width=True
)

# ---------------------------------------------------
# RUN SCHEDULER
# ---------------------------------------------------

st.header("Running Scheduler")

with st.spinner(
    "Optimizing charging schedules..."
):

    scheduler = CPScheduler(
        scenario
    )

    schedules = scheduler.schedule()

st.success(
    "Scheduling completed successfully!"
)

# ---------------------------------------------------
# BUS TIMETABLES
# ---------------------------------------------------

st.header("Per-Bus Timetable")

for schedule in schedules:

    with st.expander(
        f"{schedule.bus_id} ({schedule.operator})"
    ):

        st.write(
            f"### Charging Plan: "
            f"{' → '.join(schedule.charging_plan)}"
        )

        event_rows = []

        for event in schedule.charge_events:

            event_rows.append({
                "Station": event.station_id,

                "Arrival": minutes_to_time(
                    event.arrival_time
                ),

                "Charge Start": minutes_to_time(
                    event.charge_start
                ),

                "Charge End": minutes_to_time(
                    event.charge_end
                ),

                "Wait (mins)": (
                    event.wait_duration
                )
            })

        event_df = pd.DataFrame(
            event_rows
        )

        st.dataframe(
            event_df,
            use_container_width=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Final Arrival",
                minutes_to_time(
                    schedule.arrival_time_final
                )
            )

        with col2:
            st.metric(
                "Total Wait",
                f"{schedule.total_wait_time} mins"
            )

# ---------------------------------------------------
# STATION QUEUES
# ---------------------------------------------------

st.header("Per-Station Charging Order")

station_data = {}

for schedule in schedules:

    for event in schedule.charge_events:

        if event.station_id not in station_data:

            station_data[
                event.station_id
            ] = []

        station_data[
            event.station_id
        ].append({
            "Bus ID": schedule.bus_id,

            "Operator": schedule.operator,

            "Arrival": minutes_to_time(
                event.arrival_time
            ),

            "Charge Start": minutes_to_time(
                event.charge_start
            ),

            "Charge End": minutes_to_time(
                event.charge_end
            ),

            "Wait": event.wait_duration
        })

# ---------------------------------------------------
# DISPLAY STATION TABLES
# ---------------------------------------------------

for station_id, rows in station_data.items():

    st.subheader(
        f"Station {station_id}"
    )

    rows = sorted(
        rows,
        key=lambda x: x["Charge Start"]
    )

    station_df = pd.DataFrame(rows)

    st.dataframe(
        station_df,
        use_container_width=True
    )

# ---------------------------------------------------
# NETWORK METRICS
# ---------------------------------------------------

st.header("Network Metrics")

total_wait = sum(
    schedule.total_wait_time
    for schedule in schedules
)

avg_wait = (
    total_wait / len(schedules)
    if schedules
    else 0
)

latest_arrival = max(
    schedule.arrival_time_final
    for schedule in schedules
)

metric_col1, metric_col2, metric_col3 = (
    st.columns(3)
)

with metric_col1:

    st.metric(
        "Total Wait Time",
        f"{total_wait} mins"
    )

with metric_col2:

    st.metric(
        "Average Wait",
        f"{avg_wait:.2f} mins"
    )

with metric_col3:

    st.metric(
        "Latest Network Arrival",
        minutes_to_time(latest_arrival)
    )

# ---------------------------------------------------
# RAW SCENARIO JSON
# ---------------------------------------------------

with st.expander(
    "View Raw Scenario JSON"
):

    st.json(
        scenario.model_dump()
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.caption(
    """
    Built with:
    Python + Streamlit + OR-Tools CP-SAT
    """
)