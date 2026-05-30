import json
from pathlib import Path

from engine.models import Scenario


SCENARIO_DIR = Path("scenarios")


def load_scenario(filename: str) -> Scenario:
    path = SCENARIO_DIR / filename

    with open(path, "r") as f:
        data = json.load(f)

    scenario = Scenario(**data)

    return scenario