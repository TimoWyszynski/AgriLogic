import simpy

class Field:
    def __init__(self, field_id, field_area, coordinates, harvest):
        self.field_id = field_id
        self.field_area = field_area
        self.coordinates = coordinates
        self.harvest = harvest

        self.is_processed = False