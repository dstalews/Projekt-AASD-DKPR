import time

from HealthAnalyzerAgent import HealthAnalyzerAgent
from DataCollectorAgent import DataCollectorAgent


def main():
    data_collector_agent: DataCollectorAgent = DataCollectorAgent("datacollector@localhost", "datacollector1")
    health_analyzer_agent: HealthAnalyzerAgent = HealthAnalyzerAgent("healthanalyzer@localhost", "healthanalyzer")
    health_analyzer_agent.start()
    data_collector_agent.start()
    time.sleep(1)
    while data_collector_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            data_collector_agent.stop()
            health_analyzer_agent.stop()
            break
    print("Agent finished")


if __name__ == "__main__":
    main()
