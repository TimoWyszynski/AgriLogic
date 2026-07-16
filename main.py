import simpy

def main():
    env = simpy.Environment()

    vehicle = Vehicle(20, 5, simpy.Container(env, capacity=100, init=100), 10)
    field = Field(10, 3)
    yard = Yard(simpy.Container(env, capacity=1000, init=1000))

    env.process(vehicle_process(env, vehicle, field, yard))
    env.run()


def vehicle_process(env, vehicle, field, yard):
    while True:
        print(f"Vehicle fuel capacity {vehicle.tank.level}")

        energy, time = calculate_road_energy_time_demand(vehicle, field)

        yield vehicle.tank.get(energy)
        yield env.timeout(time)

        
        if vehicle.tank.level == 0:
            False


def calculate_road_energy_time_demand(vehicle, field):
    distance = field.distance_to_yard
    speed = vehicle.driving_speed
    demand = vehicle.road_energy_demand

    time = distance/speed
    energy = demand * time

    return energy, time


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
