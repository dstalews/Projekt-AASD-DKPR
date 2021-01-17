import time

from ActionExecutorAgent import ActionExecutorAgent
from DecisionMakerAgent import DecisionMakerAgent
from HealthAnalyzerAgent import HealthAnalyzerAgent
from DataCollectorAgent import DataCollectorAgent


def main():
    data_collector_agent: DataCollectorAgent = DataCollectorAgent("datacollector@localhost", "datacollector1")
    health_analyzer_agent: HealthAnalyzerAgent = HealthAnalyzerAgent("healthanalyzer@localhost", "healthanalyzer")
    decision_maker_agent: DecisionMakerAgent = DecisionMakerAgent("decisionmaker@localhost", "decisionmaker")
    action_executor_agent: ActionExecutorAgent = ActionExecutorAgent("actionexecutor@localhost", "actionexecutor")
    health_analyzer_agent.start()
    data_collector_agent.start()
    decision_maker_agent.start()
    action_executor_agent.start()
    time.sleep(1)
    while data_collector_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            data_collector_agent.stop()
            health_analyzer_agent.stop()
            decision_maker_agent.stop()
            action_executor_agent.stop()
            break
    print("Agent finished")


if __name__ == "__main__":
    main()
