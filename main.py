import simpy

def main():
    env = simpy.Environment()

    vehicle_tank = simpy.Container(env, capacity=350, init=350)
    vehicle = Vehicle(env, 25, 5, vehicle_tank, 10, 15)

    field_harvest = simpy.Container(env, 10, 10)
    field = Field(10, 3, field_harvest)

    yard = Yard(simpy.Container(env, capacity=10000, init=10000), 0)

    manager = Manager(env, yard, field, vehicle)

    env.process(manager.simple_process())
    env.run()


class Vehicle:
    def __init__(
            self,
            env,
            driving_speed,
            area_performance,
            tank,
            road_energy_demand,
            field_energy_demand
        ):
        self.env = env
        self.driving_speed = driving_speed                  #km/h
        self.area_performance = area_performance            #ha/h
        self.tank = tank                                    #L
        self.road_energy_demand = road_energy_demand        #L/h
        self.field_energy_demand = field_energy_demand      #L/ha


    def drive_between_yard_and_field(self, env, field, yard):
        distance = abs(yard.coordinates - field.coordinates)
        time = distance / self.driving_speed
        energy = time * self.road_energy_demand

        if energy >= self.tank.level:
            raise simpy.Interrupt("Insufficient fuel to reach field.")
        
        yield self.tank.get(energy)
        yield env.timeout(time)

        print(f"Reached the field in {time} hours using {energy} liters Diesel.")
        return
    

    def work_on_field(self, env, field):
        time = field.field_area / self.area_performance
        energy = self.field_energy_demand * field.field_area

        if energy >= self.tank.level:
            raise simpy.Interrupt("Insufficient fuel to finish fieldwork.")
        
        yield self.tank.get(energy)
        yield env.timeout(time)

        print(f"Finished fieldwork in {time} hours using {energy} liters Diesel.")
        return


class Field:
    def __init__(self, field_area, coordinates, harvest):
        self.field_area = field_area
        self.coordinates = coordinates
        self.harvest = harvest


class Yard:
    def __init__(self, fuel_storage, coordinates):
        self.fuel_storage = fuel_storage
        self.coordinates = coordinates


class Manager:
    def __init__(self, env, yard, field, vehicle):
        self.env = env
        self.yard = yard
        self.field = field
        self.vehicle = vehicle

    def simple_process(self):
        yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, self.field, self.yard))
        yield self.env.process(self.vehicle.work_on_field(self.env, self.field))
        yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, self.field, self.yard))


if __name__ == "__main__":
    main()
