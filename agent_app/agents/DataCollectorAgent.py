import asyncio
from datetime import datetime, timedelta
from json import dumps, loads
from typing import TypedDict, List

from spade import agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import logging
import requests   

class Data(TypedDict):
    data_int: int
    datetime_created: datetime

PERFORMED_ACTION_MESSAGE_TEMPLATE: Template = Template(
    metadata=dict(performative="inform"),
)

REQUEST_DATA_TEMPLATE: Template = Template(
    metadata=dict(performative="request"),
)


URL = "http://localhost:8080/api/v1/resources/users"


class DataCollectorAgent(agent.Agent):
    performed_actions: List
    agent_name: str
    data: Data

    def __init__(self, logger, id, *args, **kwargs):
        self.logger = logger
        self.id = id
        super(DataCollectorAgent, self).__init__(*args, **kwargs)

    class ReceivePerformedAction(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=5)

            if msg:
                action = loads(msg.body)
                self.agent.performed_actions.append(action)
                self.agent.logger.info(f"[{self.agent.agent_name}] ActionExecutor sent message, {action}")

    class DataRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                self.agent.logger.info(f"[{self.agent.agent_name}] Received data request from HealthAnalyzer")
                msg_to_send = Message(
                    "healthanalyzerID{self.id}@localhost",
                    metadata=dict(performative="inform"),
                )
                msg_to_send.body = dumps(self.agent.data)
                await self.send(msg_to_send)

    class CollectData(PeriodicBehaviour):

        async def run(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Starting collecting data")
            self.agent.logger.info(f"[{self.agent.agent_name}] Collecting data")
            self.agent.logger.info(f"[{self.agent.agent_name}] Data collected")
            self.agent.logger.info(f"[{self.agent.agent_name}] Preparing data to send")
            PARAMS = {'id': self.agent.id} 
            r = requests.get(url = URL, params = PARAMS) 
            data = r.json()
            self.agent.logger.info(f"[{self.agent.agent_name}] Request made to API Data: {data}")
            local_data: Data = data
            logging.info('Finished')
            msg_to_send = Message(to=f"healthanalyzerID{self.agent.id}@localhost", metadata=dict(performative="inform"))
            msg_to_send.body = dumps(local_data)
            self.agent.data = local_data
            await self.send(msg_to_send)
            self.agent.logger.info(f"[{self.agent.agent_name}] Message to Health Analyzer sent!")

    async def setup(self):
        self.agent_name = "DataCollector"

        self.logger.info(f"[{self.agent_name}] Hello World! I'm agent {self.name}")
        start_at: datetime = datetime.now() + timedelta(seconds=5)
        self.performed_actions = []

        collect_data_b = self.CollectData(period=20, start_at=start_at)
        self.add_behaviour(collect_data_b)
        self.add_behaviour(self.ReceivePerformedAction(), template=PERFORMED_ACTION_MESSAGE_TEMPLATE)
        self.add_behaviour(self.DataRequest(), template=REQUEST_DATA_TEMPLATE)