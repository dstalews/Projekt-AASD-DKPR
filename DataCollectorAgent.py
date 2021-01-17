import asyncio
from datetime import datetime, timedelta
from json import dumps, loads
from typing import TypedDict, List

from spade import agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class Data(TypedDict):
    data_int: int
    datetime_created: datetime


PERFORMED_ACTION_MESSAGE_TEMPLATE: Template = Template(
    metadata=dict(performative="inform"),
    sender="actionexecutor@localhost"
)

REQUEST_DATA_TEMPLATE: Template = Template(
    metadata=dict(performative="request"),
)


class DataCollectorAgent(agent.Agent):
    performed_actions: List
    agent_name: str
    data: Data

    class ReceivePerformedAction(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=5)

            if msg:
                action = loads(msg.body)
                self.agent.performed_actions.append(action)
                print(f"[{self.agent.agent_name}] ActionExecutor sent message, {action}")

    class DataRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                print(f"[{self.agent.agent_name}] Received data request from HealthAnalyzer")
                msg_to_send = Message(
                    "healthanalyzer@localhost",
                    metadata=dict(performative="inform"),
                )
                msg_to_send.body = dumps(self.agent.data)
                await self.send(msg_to_send)

    class CollectData(PeriodicBehaviour):

        async def run(self):
            print(f"[{self.agent.agent_name}] Starting collecting data")
            print(f"[{self.agent.agent_name}] Collecting data")
            await asyncio.sleep(5)
            print(f"[{self.agent.agent_name}] Data collected")
            print(f"[{self.agent.agent_name}] Preparing data to send")
            local_data: Data = dict(
                data_int=10
            )
            msg_to_send = Message(to="healthanalyzer@localhost", metadata=dict(performative="inform"))
            msg_to_send.body = dumps(local_data)
            self.agent.data = local_data
            await self.send(msg_to_send)
            print(f"[{self.agent.agent_name}] Message to Health Analyzer sent!")

    async def setup(self):
        self.agent_name = "DataCollector"
        print(f"[{self.agent_name}] Hello World! I'm agent")
        start_at: datetime = datetime.now() + timedelta(seconds=5)
        self.performed_actions = []

        collect_data_b = self.CollectData(period=20, start_at=start_at)
        self.add_behaviour(collect_data_b)
        self.add_behaviour(self.ReceivePerformedAction(), template=PERFORMED_ACTION_MESSAGE_TEMPLATE)
        self.add_behaviour(self.DataRequest(), template=REQUEST_DATA_TEMPLATE)
