# Architecture

## Scheduling Framework

### Approach Chosen

The scheduler uses:

**Constraint Programming (CP-SAT) with Google OR-Tools**

The scheduling problem contains:

* Resource allocation
* Time windows
* Conflict avoidance
* Optimization objectives

These characteristics make it a classic constraint satisfaction and optimization problem.

CP-SAT is a strong fit because it naturally models:

* Charger occupancy
* Waiting times
* Scheduling dependencies
* Resource conflicts

while simultaneously optimizing multiple objectives.

---

## Why CP-SAT Is the Right Fit

Alternative approaches considered:

### Greedy Scheduling

Pros:

* Simple

Cons:

* Produces poor global solutions
* Cannot guarantee conflict-free schedules

### Simulation Only

Pros:

* Easy to implement

Cons:

* Does not optimize
* Only evaluates outcomes

### Reinforcement Learning

Pros:

* Flexible

Cons:

* Requires training data
* Difficult to explain decisions

### CP-SAT (Chosen)

Pros:

* Finds globally feasible schedules
* Handles resource conflicts naturally
* Supports weighted objectives
* Easy to add new rules

For this problem, CP-SAT provides the best balance of correctness, extensibility, and implementation effort.

---

# Data Structure Design

## Scenario

```python
class Scenario
```

Acts as the root configuration object.

Contains:

* weights
* route
* vehicle configuration
* buses

This keeps all scenario inputs self-contained.

---

## Route

```python
class Route
```

Contains:

* total distance
* station list

Stations are independent objects.

This allows stations to be added without changing scheduler logic.

---

## Station

```python
class Station
```

Contains:

* id
* distance
* charger count

Stations are stored separately from buses.

This prevents tight coupling.

---

## Bus

```python
class Bus
```

Contains:

* operator
* direction
* departure time

Bus state is intentionally minimal.

Scheduling information is generated later.

---

## BusSchedule

```python
class BusSchedule
```

Contains computed results only.

Separating input models from output models keeps responsibilities clean.

---

# Future Changes Anticipated

## Additional Stations

Example:

```text
A B C D E F
```

No code changes required.

Stations are already stored dynamically in Route.

---

## Additional Operators

Example:

```text
KPN
FreshBus
KSRTC
Volvo
```

No code changes required.

Operators are represented as strings.

---

## Additional Buses

No code changes required.

The scheduler iterates through the bus list dynamically.

---

## New Charging Stations

No code changes required.

The plan generator automatically evaluates all stations.

---

## Different Route Lengths

No code changes required.

Distance calculations use route.total_distance.

---

## Different Battery Ranges

No code changes required.

Vehicle configuration is scenario-driven.

---

## Different Charging Durations

No code changes required.

Vehicle configuration controls charging duration.

---

# How To Change A Weight

Weights are defined in the scenario.

Example:

Before:

```json
{
  "individual": 1.0,
  "operator": 1.0,
  "overall": 1.0
}
```

After:

```json
{
  "individual": 10.0,
  "operator": 1.0,
  "overall": 0.5
}
```

No code changes required.

The objective automatically updates:

```python
model.Minimize(
    individual_term
    + operator_term
    + overall_term
)
```

---

# How To Add A New Rule

Example:

Maximum Waiting Time

Add inside:

```text
engine/cp_scheduler.py
```

```python
MAX_WAIT = 60

self.model.Add(
    wait_var <= MAX_WAIT
)
```

Example:

Station Closing Time

```python
STATION_CLOSE = 1320

self.model.Add(
    charge_end <= STATION_CLOSE
)
```

Example:

Mandatory Rest Gap Between Charges

```python
MIN_GAP = 15

self.model.Add(
    next_charge_start
    >= previous_charge_end + MIN_GAP
)
```

The CP-SAT architecture allows new constraints to be added without modifying existing optimization logic.

---

# Assumptions

The current implementation assumes:

1. Charging duration is fixed.

2. Travel speed is constant.

3. Chargers are always operational.

4. Traffic conditions are ignored.

5. Battery consumption is proportional to distance traveled.

6. Stations are located on the route.

7. Buses start with a fully charged battery.

8. Charging stations have deterministic capacity.

9. Departure times are known in advance.

10. Charging sessions cannot be interrupted.

These assumptions simplify the optimization problem while preserving the core scheduling challenge.

---

# Scalability

The architecture separates:

* Input data
* Feasible plan generation
* Optimization
* Solution extraction
* Visualization

This separation allows future extensions with minimal impact on existing code.

The design follows a modular constraint-based architecture and is intended to support future operational rules without requiring major refactoring.
