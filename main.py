import simpy
import numpy as np

from src.field import Field
from src.manager import Manager
from src.vehicle import Vehicle
from src.yard import Yard

def main():
    env = simpy.Environment()

    vehicle_tank = simpy.Container(env, capacity=350, init=350)
    vehicle = Vehicle(env, 25, 5, vehicle_tank, 10, 15, 0.1)

    field_harvest = simpy.Container(env, 10, 10)
    field_1 = Field(1, 10, np.array((3, 5)), field_harvest)
    field_2 = Field(2, 5, np.array((2, 4)), field_harvest)
    field_3 = Field(3, 3, np.array((1, 3)), field_harvest)
    fields = [field_1, field_2, field_3]

    yard = Yard(simpy.Container(env, capacity=10000, init=10000), np.array((0, 0)))

    manager = Manager(env, yard, fields, vehicle)

    env.process(manager.simple_process())
    env.run()


if __name__ == "__main__":
    main()
