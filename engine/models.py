from typing import List, Literal, Optional
from pydantic import BaseModel


class Weights(BaseModel):
    individual: float
    operator: float
    overall: float


class Station(BaseModel):
    id: str
    distance_from_start: int
    chargers: int


class Route(BaseModel):
    name: str
    total_distance: int
    stations: List[Station]


class VehicleConfig(BaseModel):
    battery_range_km: int
    charge_duration_min: int
    speed_kmph: int


class Bus(BaseModel):
    id: str
    operator: str

    # forward = Bengaluru -> Kochi
    # backward = Kochi -> Bengaluru
    direction: Literal["forward", "backward"]

    departure_time: str


class Scenario(BaseModel):
    scenario_id: str

    weights: Weights

    route: Route

    vehicle_config: VehicleConfig

    buses: List[Bus]


class ChargeEvent(BaseModel):
    station_id: str

    arrival_time: int

    wait_start: int
    charge_start: int
    charge_end: int

    wait_duration: int


class BusSchedule(BaseModel):
    bus_id: str

    operator: str

    departure_time: int

    charging_plan: List[str]

    charge_events: List[ChargeEvent]

    arrival_time_final: int

    total_wait_time: int