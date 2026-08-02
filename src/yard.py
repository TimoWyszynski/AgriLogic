import simpy
import numpy as np
from dataclasses import dataclass

@dataclass
class Yard:
    fuel_storage: simpy.Container
    coordinates: np.array