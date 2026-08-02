import simpy
import numpy as np
from enum import Enum
from src.field import Field
from src.yard import Yard


class VehicleType(Enum):
    WORKING = "working"
    APPLICATION = "application"
    HARVESTER = "harvester"
    TENDER = "tender"


class Vehicle:
    def __init__(
            self,
            vehicle_id: int,
            vehicle_type: VehicleType,
            env: simpy.Environment,
            driving_speed: float,
            area_performance: float,
            application_rate: float,
            fuel_tank: simpy.Container,
            recources_tank: simpy.Container,
            road_energy_demand: float,
            field_energy_demand: float,
            set_up_time: float,
            current_location: np.array = np.array((0, 0))
        ):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.env = env
        self.driving_speed = driving_speed                  #km/h
        self.area_performance = area_performance            #ha/h
        self.application_rate = application_rate
        self.fuel_tank = fuel_tank                          #L
        self.recources_tank = recources_tank                #L or Kg
        self.road_energy_demand = road_energy_demand        #L/h
        self.field_energy_demand = field_energy_demand      #L/ha
        self.set_up_time = set_up_time                      #h

        self.current_location = current_location
        self.fuel_safety_level = 0.1                        #%


    def drive_to(self, env: simpy.Environment, destination: Field|Yard):
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


    def work_on_field(self, env: simpy.Environment, field: Field):
        time = (field.field_area * (1-field.progress_level)) / self.area_performance
        energy = self.field_energy_demand * field.field_area * (1-field.progress_level)
        availeable_energy = self.fuel_tank.level

        yield env.process(self.set_up_vehicle(env))

        if energy >= availeable_energy:
            progress_factor = availeable_energy/energy - self.fuel_safety_level
            yield self.fuel_tank.get(energy * progress_factor)
            yield env.timeout(time * progress_factor)
            field.progress_level = progress_factor
            print(f"Partly finished ({progress_factor*100}%) field {field.field_id} in {time * progress_factor} hours using {energy * progress_factor} liters Diesel.")
            yield env.process(self.set_up_vehicle(env))
            raise simpy.Interrupt("Insufficient fuel to finish fieldwork.")
        
        else:
            yield self.fuel_tank.get(energy)
            yield env.timeout(time)
            print(f"Finished field {field.field_id} in {time} hours using {energy} liters Diesel.")
            yield env.process(self.set_up_vehicle(env))
    

    def refuel_at_yard(self, yard: Yard):
        to_refuel = self.fuel_tank.capacity - self.fuel_tank.level
        yield yard.fuel_storage.get(to_refuel)
        yield self.fuel_tank.put(to_refuel)
        print(f"Refueled the vehicle with {to_refuel} liter diesel.")


    def set_up_vehicle(self, env: simpy.Environment):
        yield env.timeout(self.set_up_time)
        print(f"Setting up vehicle for {self.set_up_time} hours.")