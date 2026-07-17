import simpy

def main():
    env = simpy.Environment()

    vehicle = Vehicle(20, 5, simpy.Container(env, capacity=1000, init=1000), 100)
    field = Field(10, 3000)
    yard = Yard(simpy.Container(env, capacity=1000, init=1000))

    env.process(vehicle_process(env, vehicle, field, yard))
    env.run()


def vehicle_process(env, vehicle, field, yard):
    while True:
        print(f"Vehicle fuel capacity {vehicle.tank.level}")
        yield env.process(drive_from_yard_to_field_process(env, vehicle, field))
        # How do you start a process while env.run() is seet active? Events?

        
        if vehicle.tank.level == 0:
            False


def drive_from_yard_to_field_process(env, vehicle, field):
    remaining_distance = field.distance_to_yard
    while True:
        yield env.timeout(1)
        yield vehicle.tank.get(1 * vehicle.road_energy_demand)
        remaining_distance -= (1 * (vehicle.driving_speed/3.6))
        print(remaining_distance)

        if remaining_distance <= 0:
            print(f"Reached the field.")
            False
        if vehicle.tank.level == 0:
            print(f"Vehciel fuel is empty")
            False


class Vehicle:
    def __init__(self, driving_speed, area_performance, tank, road_energy_demand):
        self.driving_speed = driving_speed
        self.area_performance = area_performance
        self.tank = tank
        self.road_energy_demand = road_energy_demand

class Field:
    def __init__(self, field_area, distance_to_yard):
        self.field_area = field_area
        self.distance_to_yard = distance_to_yard

class Yard:
    def __init__(self, fuel_storage):
        self.fuel_storage = fuel_storage


if __name__ == "__main__":
    main()
