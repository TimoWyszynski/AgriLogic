import simpy

def main():
    env = simpy.Environment()

    vehicle_tank = simpy.Container(env, capacity=350, init=350)
    vehicle = Vehicle(env, 25, 5, vehicle_tank, 10, 15, 0.1)

    field_harvest = simpy.Container(env, 10, 10)
    field_1 = Field(1, 10, 3, field_harvest)
    field_2 = Field(2, 5, 3, field_harvest)
    field_3 = Field(3, 3, 3, field_harvest)

    fields = [field_1, field_2, field_3]

    yard = Yard(simpy.Container(env, capacity=10000, init=10000), 0)

    manager = Manager(env, yard, fields, vehicle)

    env.process(manager.simple_process())
    env.run()


class Vehicle:
    def __init__(
            self,
            env,
            driving_speed,
            area_performance,
            fuel_tank,
            road_energy_demand,
            field_energy_demand,
            set_up_time,
            current_location=0
        ):
        self.env = env
        self.driving_speed = driving_speed                  #km/h
        self.area_performance = area_performance            #ha/h
        self.fuel_tank = fuel_tank                          #L
        self.road_energy_demand = road_energy_demand        #L/h
        self.field_energy_demand = field_energy_demand      #L/ha
        self.set_up_time = set_up_time                      #h

        self.current_location = 0


    def drive_between_yard_and_field(self, env, field, yard):
        distance = abs(yard.coordinates - field.coordinates)
        time = distance / self.driving_speed
        energy = time * self.road_energy_demand

        if energy >= self.fuel_tank.level:
            raise simpy.Interrupt("Insufficient fuel to reach field.")
        
        yield self.fuel_tank.get(energy)
        yield env.timeout(time)

        print(f"Reached the field in {time} hours using {energy} liters Diesel.")
        return
    


    

    def work_on_field(self, env, field):
        time = field.field_area / self.area_performance
        energy = self.field_energy_demand * field.field_area

        if energy >= self.fuel_tank.level:
            raise simpy.Interrupt("Insufficient fuel to finish fieldwork.")
        
        yield self.fuel_tank.get(energy)
        yield env.timeout(time)

        print(f"Finished fieldwork in {time} hours using {energy} liters Diesel.")
        return
    

    def refuel_at_yard(self, yard):
        to_refuel = self.fuel_tank.capacity - self.fuel_tank.level
        yield yard.fuel_storage.get(to_refuel)
        yield self.fuel_tank.put(to_refuel)
        print(f"Refueled the vehicle with {to_refuel} liter diesel.")


    def set_up_vehicle(self, env):
        yield env.timeout(self.set_up_time)


class Field:
    def __init__(self, field_id, field_area, coordinates, harvest):
        self.field_id = field_id
        self.field_area = field_area
        self.coordinates = coordinates
        self.harvest = harvest


class Yard:
    def __init__(self, fuel_storage, coordinates):
        self.fuel_storage = fuel_storage
        self.coordinates = coordinates
        
        self.is_processed = False


class Manager:
    def __init__(self, env, yard, fields, vehicle):
        self.env = env
        self.yard = yard
        self.fields = fields
        self.vehicle = vehicle

    def simple_process(self):
        remaining_fields = self.fields

        yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, remaining_fields[0], self.yard))

        for field in remaining_fields:                
            try:
                yield self.env.process(self.vehicle.work_on_field(self.env, field))
            except simpy.Interrupt:
                yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, field, self.yard))
                yield self.env.process(self.vehicle.refuel_at_yard(self.yard))
                yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, field, self.yard))
                yield self.env.process(self.vehicle.work_on_field(self.env, field))

        yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, remaining_fields[-1], self.yard))


if __name__ == "__main__":
    main()
