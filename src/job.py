from enum import Enum
from src.vehicle import Vehicle
from src.field import Field
from dataclasses import dataclass


class ProcessStep(Enum):
    TILLAGE = "tillage"
    SEEDING = "seeding"
    FERTILIZATION = "fertilization"
    PLANT_PROTECTION = "plant_protection"
    HARVEST = "harvest"


class ProcessChain(Enum):
    WHEAT = "wheat"


@dataclass
class Job:
    process_chain: ProcessChain
    process_step: ProcessStep
    field: Field
    vehcile: Vehicle
    in_progress: bool = False