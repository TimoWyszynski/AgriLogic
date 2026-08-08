import simpy
import numpy as np

from src.field import Field
from src.manager import Manager
from src.vehicle import Vehicle, VehicleType, WorkingVehicle, ApplicationVehicle
from src.yard import Yard

def main():
    env = simpy.Environment()

    vehicle_fuel_tank = simpy.Container(env, capacity=450, init=450)
    vehicle_recources_tank = simpy.Container(env, capacity=4000, init=4000)
    tillage_vehicle = WorkingVehicle(
        0,
        env,
        5,
        vehicle_fuel_tank,
        10,
        15
    )
    seeding_vehicle = ApplicationVehicle(
        0,
        env,
        5,
        180,
        vehicle_fuel_tank,
        vehicle_recources_tank,
        10,
        5,
    )
    fertilization_vehicle = ApplicationVehicle(
        0,
        env,
        5,
        180,
        vehicle_fuel_tank,
        vehicle_recources_tank,
        10,
        5,
    )
    plant_protection_vehicle = ApplicationVehicle(
        0,
        env,
        5,
        300,
        vehicle_fuel_tank,
        vehicle_recources_tank,
        10,
        5,
    )
    vehicles = [tillage_vehicle, seeding_vehicle, fertilization_vehicle, plant_protection_vehicle]

    field_harvest = simpy.Container(env, 10, 10)
    field_1 = Field(1, 10, np.array((3, 5)), field_harvest)
    field_2 = Field(2, 5, np.array((2, 4)), field_harvest)
    field_3 = Field(3, 20, np.array((1, 3)), field_harvest)
    field_4 = Field(4, 10, np.array((3, 5)), field_harvest)
    field_5 = Field(5, 8, np.array((10, 4)), field_harvest)
    field_6 = Field(6, 20, np.array((1, 9)), field_harvest)
    field_7 = Field(7, 10, np.array((2, 5)), field_harvest)
    field_8 = Field(8, 9, np.array((6, 4)), field_harvest)
    field_9 = Field(9, 14, np.array((1, 7)), field_harvest)
    fields = [field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9]

    yard = Yard(simpy.Container(env, capacity=10000, init=10000), np.array((0, 0)))

    manager = Manager(env, yard, fields, vehicles)

    env.process(manager.work())
    env.run(until=20000)

    print(f"Finished Simulation with {manager.days_worked} days simulated.")


if __name__ == "__main__":
    main()
