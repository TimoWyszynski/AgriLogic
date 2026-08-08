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
            env: simpy.Environment,
            area_performance: float,
            fuel_tank: simpy.Container,
            road_energy_demand: float,
            field_energy_demand: float,
            driving_speed: float = 25,
            set_up_time: float = 0.1,
            current_location: np.array = np.array((0, 0)),
            vehicle_type: VehicleType = None
        ):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.env = env
        self.driving_speed = driving_speed                  #km/h
        self.area_performance = area_performance            #ha/h
        self.fuel_tank = fuel_tank                          #L
        self.road_energy_demand = road_energy_demand        #L/h
        self.field_energy_demand = field_energy_demand      #L/ha
        self.set_up_time = set_up_time                      #h

        self.current_location = current_location
        self.vehicle_type = vehicle_type
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
        pass
    

    def refuel_at_yard(self, yard: Yard):
        pass


    def set_up_vehicle(self, env: simpy.Environment):
        yield env.timeout(self.set_up_time)
        print(f"Setting up vehicle for {self.set_up_time} hours.")


class WorkingVehicle(Vehicle):
    def __init__(
            self,
            vehicle_id,
            env,
            area_performance,
            fuel_tank,
            road_energy_demand,
            field_energy_demand,
            driving_speed = 25,
            set_up_time = 0.1,
            current_location = np.array((0, 0)),
            vehicle_type = VehicleType.WORKING
        ):
        super().__init__(
            vehicle_id,
            env,
            area_performance,
            fuel_tank,
            road_energy_demand,
            field_energy_demand,
            driving_speed,
            set_up_time,
            current_location,
            vehicle_type
        )


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


class ApplicationVehicle(Vehicle):
    def __init__(
            self,
            vehicle_id,
            env,
            area_performance,
            application_rate,            #l or kg per ha
            fuel_tank,
            recource_tank,
            road_energy_demand,
            field_energy_demand,
            driving_speed = 25,
            set_up_time = 0.1,
            current_location = np.array((0, 0)),
            vehicle_type = VehicleType.APPLICATION
        ):
        super().__init__(
            vehicle_id,
            env,
            area_performance,
            fuel_tank,
            road_energy_demand,
            field_energy_demand,
            driving_speed,
            set_up_time,
            current_location,
            vehicle_type
        )
        self.application_rate = application_rate
        self.recource_tank = recource_tank


    def work_on_field(self, env: simpy.Environment, field: Field):
        time = (field.field_area * (1-field.progress_level)) / self.area_performance

        energy = self.field_energy_demand * field.field_area * (1-field.progress_level)
        availeable_energy = self.fuel_tank.level

        recource = self.application_rate * field.field_area * (1-field.progress_level)
        availeable_recource = self.recource_tank.level

        yield env.process(self.set_up_vehicle(env))

        if energy >= availeable_energy or recource >= availeable_recource:
            progress_factor_energy = availeable_energy/energy - self.fuel_safety_level
            progress_factor_recource = availeable_recource/recource
            progress_factor = min(progress_factor_energy, progress_factor_recource)

            yield self.fuel_tank.get(energy * progress_factor)
            yield self.recource_tank.get(recource * progress_factor)
            yield env.timeout(time * progress_factor)
            field.progress_level = progress_factor
            print(f"Partly finished ({progress_factor*100}%) field {field.field_id} in {time * progress_factor} hours using {energy * progress_factor} liters Diesel.")
            yield env.process(self.set_up_vehicle(env))
            raise simpy.Interrupt("Insufficient fuel or recource to finish fieldwork.")
        
        else:
            yield self.fuel_tank.get(energy)
            yield self.recource_tank.get(recource)
            yield env.timeout(time)
            print(f"Finished field {field.field_id} in {time} hours using {energy} liters Diesel and {recource} liters/kilograms of recources.")
            yield env.process(self.set_up_vehicle(env))


    def refuel_at_yard(self, yard: Yard):
        to_refuel_energy = self.fuel_tank.capacity - self.fuel_tank.level
        to_refuel_recource = self.recource_tank.capacity - self.recource_tank.level
        yield yard.fuel_storage.get(to_refuel_energy)
        yield self.fuel_tank.put(to_refuel_energy)
        yield self.recource_tank.put(to_refuel_recource)
        print(f"Refueled the vehicle with {to_refuel_energy} liter diesel and {to_refuel_recource} liters/kilograms recource.")