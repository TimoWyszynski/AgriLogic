import simpy

class Manager:
    def __init__(self, env, yard, fields, vehicle):
        self.env = env
        self.yard = yard
        self.fields = fields
        self.vehicle = vehicle

        self.start_of_day = 8
        self.end_of_day = 17

    def simple_process(self):

        yield self.env.timeout(8)
        print(f"Simulation starts at {self.env.now % 24} o'clock.")


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

        print(f"Simulation ends at {self.env.now % 24} o'clock.")


    def skip_to_working_hours(self):
        current_day_time = self.env.now % 24
        wait_time = (self.start_of_day - current_day_time) % 24

        yield self.env.timeout(wait_time)
