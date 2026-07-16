import simpy

def main():
    env = simpy.Environment()
    env.process(vehicle_process(env))
    env.run(until=100)


def vehicle_process(env):
    while True:
        print(f"Start driving at {env.now}")
        yield env.timeout(5)
        print(f"Arrived at {env.now}")


if __name__ == "__main__":
    main()
