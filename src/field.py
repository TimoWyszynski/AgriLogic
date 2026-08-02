from dataclasses import dataclass
import numpy as np
import simpy

@dataclass
class Field:
    field_id: int
    field_area: int
    coordinates: np.array
    harvest: simpy.Container
    progress_level: float = 0.0