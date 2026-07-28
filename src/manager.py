import simpy

class Manager:
    def __init__(self, env, yard, fields, vehicle):
        self.env = env
        self.yard = yard
        self.fields = fields
        self.vehicle = vehicle

        self.start_of_day = 8
        self.end_of_day = 17
        self.days_worked = 1
        self.env.process(self.count_days())

    def simple_process(self):

        yield self.env.process(self.skip_to_working_hours())
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

        print(f"Simulation ends  at {self.env.now % 24} o'clock.")
        print(f"Worked for {self.days_worked} days and {self.env.now} hours.")


    def work(self):

        remaining_fields = self.fields

        while remaining_fields:
            yield self.env.process(self.skip_to_working_hours())

            if (self.vehicle.current_location == self.yard.coordinates).all():
                yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, remaining_fields[0], self.yard))
            else:
                yield self.env.process(self.vehicle.drive_between_field_and_field(self.env, remaining_fields[0]))

            try:
                yield self.env.process(self.vehicle.work_on_field(self.env, remaining_fields[0]))
            except simpy.Interrupt:
                yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, remaining_fields[0], self.yard))
                yield self.env.process(self.vehicle.refuel_at_yard(self.yard))
                yield self.env.process(self.vehicle.drive_between_yard_and_field(self.env, remaining_fields[0], self.yard))
                yield self.env.process(self.vehicle.work_on_field(self.env, remaining_fields[0]))

            remaining_fields = remaining_fields[1:]

        print(self.vehicle.current_location)
        yield self.env.process(self.vehicle.return_to_yard(self.env, self.yard)) 



    def skip_to_working_hours(self):
        current_day_time = self.env.now % 24
        wait_time = (self.start_of_day - current_day_time) % 24

        yield self.env.timeout(wait_time)


    def count_days(self):
        while True:
            yield self.env.timeout(24)
            self.days_worked += 1
