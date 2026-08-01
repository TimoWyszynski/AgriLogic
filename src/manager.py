import simpy

class Manager:
    def __init__(self, env, yard, fields, vehicle):
        self.env = env
        self.yard = yard
        self.fields = fields
        self.vehicle = vehicle

        self.start_of_day = 8
        self.end_of_day = 17
        self.days_worked = 0
        self.env.process(self.count_days())


    def work(self):
        while self.fields:
            yield self.env.process(self.skip_to_working_hours())

            while self.is_working_hours() and self.fields:

                if (self.vehicle.current_location == self.yard.coordinates).all():
                    yield self.env.process(self.vehicle.drive_to(self.env, self.fields[0]))
                else:
                    yield self.env.process(self.vehicle.drive_to(self.env, self.fields[0]))

                try:
                    yield self.env.process(self.vehicle.set_up_vehicle(self.env))
                    yield self.env.process(self.vehicle.work_on_field(self.env, self.fields[0]))
                    yield self.env.process(self.vehicle.set_up_vehicle(self.env))
                except simpy.Interrupt:
                    yield self.env.process(self.vehicle.set_up_vehicle(self.env))
                    yield self.env.process(self.vehicle.drive_to(self.env, self.yard))
                    yield self.env.process(self.vehicle.refuel_at_yard(self.yard))
                    yield self.env.process(self.vehicle.drive_to(self.env, self.fields[0]))
                    yield self.env.process(self.vehicle.set_up_vehicle(self.env))
                    yield self.env.process(self.vehicle.work_on_field(self.env, self.fields[0]))
                    yield self.env.process(self.vehicle.set_up_vehicle(self.env))

                self.fields = self.fields[1:]

            yield self.env.process(self.vehicle.drive_to(self.env, self.yard))
            yield self.env.process(self.vehicle.refuel_at_yard(self.yard))
            print("Workday finished")
            yield self.env.process(self.work())


    def skip_to_working_hours(self):
        current_day_time = self.env.now % 24
        wait_time = (self.start_of_day - current_day_time) % 24
        yield self.env.timeout(wait_time)
        print(f"Skipping {wait_time} hours to next working window.")


    def count_days(self):
        while self.fields:
            yield self.env.timeout(24)
            self.days_worked += 1

    
    def is_working_hours(self):
        current_time = self.env.now % 24
        return True if 8 <= current_time <= 17 else False