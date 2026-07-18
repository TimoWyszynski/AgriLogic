import simpy

def main():
    env = simpy.Environment()

    vehicle = Vehicle(20, 5, simpy.Container(env, capacity=100, init=100), 100, 300)
    field = Field(10, 3)
    yard = Yard(simpy.Container(env, capacity=1000, init=1000), 0)

    env.process(run_simulation(env, vehicle, field, yard))
    env.run()


def run_simulation(env, vehicle, field, yard):
    while True:
        print(f"Vehicle fuel capacity {vehicle.tank.level}")

        try:
            yield env.process(vehicle.drive_from_yard_to_field(env, field, yard))
        except simpy.Interrupt:
            break


class Vehicle:
    def __init__(self, driving_speed, area_performance, tank, road_energy_demand, field_energy_demand):
        self.driving_speed = driving_speed
        self.area_performance = area_performance
        self.tank = tank
        self.road_energy_demand = road_energy_demand
        self.field_energy_demand = field_energy_demand

    def drive_from_yard_to_field(self, env, field, yard):
        remaining_distance = abs(yard.coordinate - field.coordinate) * 1000
        while True:

            energy_demand = (self.road_energy_demand) * 1/1000

            if energy_demand >= self.tank.level:
                print(f"Vehciel fuel is empty")
                raise simpy.Interrupt(None)

            yield self.tank.get((self.road_energy_demand) * 1/1000)
            yield env.timeout(1)



            remaining_distance -= (self.driving_speed / 3.6)
            print(remaining_distance)

            if remaining_distance <= 0:
                print(f"Reached the field.")
                break

class Field:
    def __init__(self, field_area, coordinates):
        self.field_area = field_area
        self.coordinates = coordinates

class Yard:
    def __init__(self, fuel_storage, coordinates):
        self.fuel_storage = fuel_storage
        self.coordinates = coordinates

class Manager:
    def __init__(self):
        pass


if __name__ == "__main__":
    main()
