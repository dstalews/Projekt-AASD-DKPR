import time

from DataCollectorAgent import DataCollectorAgent


def main():
    data_collector_agent = DataCollectorAgent("datacollector@localhost", "datacollector1")
    data_collector_agent.start()
    time.sleep(1)
    while data_collector_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            data_collector_agent.stop()
            break
    print("Agent finished")


if __name__ == "__main__":
    main()
