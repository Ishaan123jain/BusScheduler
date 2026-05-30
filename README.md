# EV Bus Charging Scheduler

## Overview

This project is a constraint-based scheduling system for electric buses operating on a fixed route with charging stations.

The scheduler generates feasible charging plans, allocates charging resources, avoids charger conflicts, and minimizes waiting time using Google OR-Tools CP-SAT.

The system supports:

* Multiple operators
* Multiple buses
* Forward and backward routes
* Weighted optimization objectives
* Charging station capacity constraints
* Interactive visualization through Streamlit

---

## Technology Stack

* Python 3.11+
* Streamlit
* Google OR-Tools (CP-SAT)
* Pydantic
* Pandas
* Plotly

---

## Project Structure

```text
project/
│
├── app.py
├── scenarios/
│
├── engine/
│   ├── models.py
│   ├── loader.py
│   ├── plan_generator.py
│   ├── cp_scheduler.py
│   ├── objectives.py
│   ├── solution_builder.py
│   ├── route_utils.py
│   └── timeline.py
│
└── docs/
```

---

## Running Locally

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
streamlit run app.py
```

---

## How to Change Optimization Weights

Weights are defined inside each scenario JSON file.

Example:

```json
{
  "weights": {
    "individual": 1.0,
    "operator": 0.5,
    "overall": 0.2
  }
}
```

Meaning:

* individual → prioritizes reducing bus waiting time
* operator → prioritizes fairness across operators
* overall → prioritizes earlier completion of schedules

Example:

```json
{
  "weights": {
    "individual": 5.0,
    "operator": 1.0,
    "overall": 0.5
  }
}
```

This makes minimizing waiting time much more important.

No code changes are required.

---

## How to Add a New Scheduling Rule

Scheduling rules are implemented inside:

```text
engine/cp_scheduler.py
```

Example: Maximum Allowed Waiting Time

```python
MAX_WAIT = 60

self.model.Add(
    wait_var <= MAX_WAIT
)
```

This prevents any bus from waiting more than 60 minutes before charging.

The rule becomes part of the optimization model automatically.

---

## Current Optimization Goals

The objective minimizes:

* Individual waiting time
* Operator-level waiting
* Overall completion time

The objective is built in:

```text
engine/objectives.py
```

---

## Example Scenario

A scenario contains:

* Route definition
* Charging stations
* Vehicle configuration
* Optimization weights
* Bus schedules

The scheduler generates charging plans and computes an optimized charging schedule.

---

## Future Improvements

* Variable charging durations
* Battery state-of-charge tracking
* Dynamic electricity pricing
* Multi-route support
* Real-time traffic integration
* Charger maintenance windows
* Predictive congestion models

---
