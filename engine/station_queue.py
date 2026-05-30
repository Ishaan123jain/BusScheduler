class StationQueue:

    def __init__(self, station_id: str):

        self.station_id = station_id

        # When charger becomes free
        self.available_at = 0

        # Track charging order
        self.events = []

    def reserve_slot(
        self,
        bus_id: str,
        arrival_time: int,
        charge_duration: int
    ):

        charge_start = max(
            arrival_time,
            self.available_at
        )

        charge_end = (
            charge_start + charge_duration
        )

        wait_duration = (
            charge_start - arrival_time
        )

        self.available_at = charge_end

        event = {
            "bus_id": bus_id,
            "arrival_time": arrival_time,
            "charge_start": charge_start,
            "charge_end": charge_end,
            "wait_duration": wait_duration
        }

        self.events.append(event)

        return event