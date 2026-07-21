import simpy

class Yard:
    def __init__(self, fuel_storage, coordinates):
        self.fuel_storage = fuel_storage
        self.coordinates = coordinates
        
        self.is_processed = False