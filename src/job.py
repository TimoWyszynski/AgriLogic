from enum import Enum

class ProcessStep(Enum):
    TILLAGE = "tillage"
    SEEDING = "seeding"
    FERTILIZATION = "fertilization"
    PLANT_PROTECTION = "plant_protection"
    HARVEST = "harvest"

class ProcessChain(Enum):
    WHEAT = "wheat"

class Job:
    def __init__(self):
        pass
