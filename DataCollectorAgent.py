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


PERFORMED_ACTION_MESSAGE_TEMPLATE: Template = Template(
    metadata=dict(performative="inform"),
    sender="actionexecutor@localhost"
)


class DataCollectorAgent(agent.Agent):
    performed_actions: List
    agent_name: str

    class ReceivePerformedAction(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=5)

            if msg:
                action = loads(msg.body)
                self.agent.performed_actions.append(action)
                print(f"[{self.agent.agent_name}] ActionExecutor sent message, {action}")

    class CollectData(PeriodicBehaviour):
        data: Data

        async def run(self):
            print(f"[{self.agent.agent_name}] Starting collecting data")
            print(f"[{self.agent.agent_name}] Collecting data")
            await asyncio.sleep(5)
            print(f"[{self.agent.agent_name}] Data collected")
            print(f"[{self.agent.agent_name}] Preparing data to send")
            local_data: Data = dict(
                data_int=10
            )
            msg_to_send = Message(to="healthanalyzer@localhost")
            msg_to_send.body = dumps(local_data)
            await self.send(msg_to_send)
            print(f"[{self.agent.agent_name}] Message to Health Analyzer sent!")
            self.data = local_data

        async def on_start(self):
            print(f"[{self.agent.agent_name}] Starting collecting data Behaviour")

        async def on_end(self):
            print(f"[{self.agent.agent_name}] Ended and now sending collected data")
            await self.agent.stop()

    async def setup(self):
        self.agent_name = "DataCollector"
        print(f"[{self.agent_name}] Hello World! I'm agent")
        start_at: datetime = datetime.now() + timedelta(seconds=5)
        self.performed_actions = []

        collect_data_b = self.CollectData(period=20, start_at=start_at)
        self.add_behaviour(collect_data_b)
        self.add_behaviour(self.ReceivePerformedAction(), template=PERFORMED_ACTION_MESSAGE_TEMPLATE)
