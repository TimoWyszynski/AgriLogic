import simpy
import numpy as np

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
            current_location=np.array((0, 0))
        ):
        self.env = env
        self.driving_speed = driving_speed                  #km/h
        self.area_performance = area_performance            #ha/h
        self.fuel_tank = fuel_tank                          #L
        self.road_energy_demand = road_energy_demand        #L/h
        self.field_energy_demand = field_energy_demand      #L/ha
        self.set_up_time = set_up_time                      #h

        self.current_location = current_location


    def drive_to(self, env, destination):
        if destination.coordinates is None:
            raise ValueError("Destination has no coordinates.")

        distance = np.linalg.norm(self.current_location - destination.coordinates)
        time = distance / self.driving_speed
        energy = time * self.road_energy_demand

        if energy >= self.fuel_tank.level:
                raise simpy.Interrupt("Insufficient fuel to reach field.")

        if energy > 0:
            yield self.fuel_tank.get(energy)
        yield env.timeout(time)

        self.current_location = destination.coordinates

        print(f"Driving to {destination.coordinates} in {time} hours using {energy} liters Diesel.")


    def work_on_field(self, env, field):
        time = field.field_area / self.area_performance
        energy = self.field_energy_demand * field.field_area

        if energy >= self.fuel_tank.capacity:
            raise ValueError("Fuel tank is to small.")

        if energy >= self.fuel_tank.level:
            raise simpy.Interrupt("Insufficient fuel to finish fieldwork.")
        
        yield self.fuel_tank.get(energy)
        yield env.timeout(time)

        field.is_processed = True

        print(f"Finished field {field.field_id} in {time} hours using {energy} liters Diesel.")
        return
    

    def refuel_at_yard(self, yard):
        to_refuel = self.fuel_tank.capacity - self.fuel_tank.level
        yield yard.fuel_storage.get(to_refuel)
        yield self.fuel_tank.put(to_refuel)
        print(f"Refueled the vehicle with {to_refuel} liter diesel.")


    def set_up_vehicle(self, env):
        yield env.timeout(self.set_up_time)