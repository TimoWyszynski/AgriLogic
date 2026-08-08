import simpy
from src.yard import Yard
from src.vehicle import Vehicle, VehicleType
from src.field import Field
from src.job import Job, ProcessChain, ProcessStep

class Manager:
    def __init__(
            self,
            env: simpy.Environment,
            yard: Yard,
            fields: list[Field],
            vehicles: list[Vehicle]
        ):
        self.env = env
        self.yard = yard
        self.fields = fields
        self.vehicles = vehicles

        self.process_chains = [ProcessChain.WHEAT]
        self.process_steps = [ProcessStep.TILLAGE, ProcessStep.SEEDING]

        self.start_of_day = 8
        self.end_of_day = 17
        self.days_worked = 0
        self.env.process(self.count_days())
        self.job_list = self.create_job_list()


    def work(self):
        while self.job_list:
            yield self.env.process(self.skip_to_working_hours())

            while self.is_working_hours() and self.job_list:

                if (self.vehicles[1].current_location == self.yard.coordinates).all():
                    yield self.env.process(self.vehicles[1].drive_to(self.env, self.job_list[0].field))
                else:
                    yield self.env.process(self.vehicles[1].drive_to(self.env, self.job_list[0].field))

                try:
                    yield self.env.process(self.vehicles[1].work_on_field(self.env, self.job_list[0].field))
                except simpy.Interrupt:
                    yield self.env.process(self.vehicles[1].drive_to(self.env, self.yard))
                    yield self.env.process(self.vehicles[1].refuel_at_yard(self.yard))
                    yield self.env.process(self.vehicles[1].drive_to(self.env, self.job_list[0].field))
                    yield self.env.process(self.vehicles[1].work_on_field(self.env, self.job_list[0].field))

                self.job_list = self.job_list[1:]

            yield self.env.process(self.vehicles[1].drive_to(self.env, self.yard))
            yield self.env.process(self.vehicles[1].refuel_at_yard(self.yard))
            print("Workday finished")
            yield self.env.process(self.work())


    def skip_to_working_hours(self):
        current_day_time = self.env.now % 24
        wait_time = (self.start_of_day - current_day_time) % 24
        yield self.env.timeout(wait_time)
        print(f"Skipping {wait_time} hours to next working window.")


    def count_days(self):
        while self.job_list:
            yield self.env.timeout(24)
            self.days_worked += 1

    
    def is_working_hours(self)->bool:
        current_time = self.env.now % 24
        return True if 8 <= current_time <= 17 else False


    def create_job_list(self)->list[Job]:
        job_list = []

        for process_chain in self.process_chains:
            for process_step in self.process_steps:
                for field in self.fields:
                    new_job = Job(process_chain, process_step, field, self.vehicles[0])
                    job_list.append(new_job)

        return job_list
