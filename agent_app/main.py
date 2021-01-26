import time
import logging


import threading
import atexit
from flask import Flask

from  agents.ActionExecutorAgent import ActionExecutorAgent
from  agents.DecisionMakerAgent import DecisionMakerAgent
from  agents.HealthAnalyzerAgent import HealthAnalyzerAgent
from  agents.DataCollectorAgent import DataCollectorAgent

POOL_TIME = 5 #Seconds
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO

class HandlerPerChildLogger(logging.Logger):
    selector = "agent"

    def __init__(self, name, handler_factory, level=logging.NOTSET):
        super(HandlerPerChildLogger, self).__init__(name, level=level)
        self.handler_factory = handler_factory

    def getChild(self, suffix):
        logger = super(HandlerPerChildLogger, self).getChild(suffix)
        if not logger.handlers:
            logger.addHandler(self.handler_factory(logger.name))
            logger.setLevel(DEFAULT_LOG_LEVEL)
        return logger

def file_handler_factory(name):
    handler = logging.FileHandler(filename="log/{}.log".format(name), encoding="utf-8", mode="a")
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    return handler

logger = HandlerPerChildLogger("aasd", file_handler_factory)
logger.setLevel(DEFAULT_LOG_LEVEL)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="log/aasd.log", encoding="utf-8", mode="a")
ch.setLevel(DEFAULT_LOG_LEVEL)
fh.setLevel(DEFAULT_LOG_LEVEL)
formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()

def run_agent(user):
    global yourThread
    id = user["id"]
    agent_logger = logger.getChild(f'agent_{id}')
    data_collector_agent: DataCollectorAgent = DataCollectorAgent(agent_logger, id, f"datacollectorid{id}@localhost", user['password'])
    health_analyzer_agent: HealthAnalyzerAgent = HealthAnalyzerAgent(agent_logger,id, f"healthanalyzerid{id}@localhost", user['password'])
    decision_maker_agent: DecisionMakerAgent = DecisionMakerAgent(agent_logger, id, f"decisionmakerid{id}@localhost", user['password'])
    action_executor_agent: ActionExecutorAgent = ActionExecutorAgent(agent_logger,id, f"actionexecutorid{id}@localhost", user['password'])
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
    yourThread = threading.Thread(target=run_agent, args=(user,))
    yourThread.setDaemon(True)
    yourThread.start()   

def run_agent_start(user):
    global yourThread
    # Create your thread
    yourThread = threading.Thread(target=run_agent, args=(user,))
    yourThread.setDaemon(True)
    yourThread.start()


def run(users):
    logger.info("Run Agents")

    for user in users:
        run_agent_start(user)
    logger.info("Agents Finished") 