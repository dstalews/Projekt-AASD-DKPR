import asyncio
from datetime import datetime, timedelta
from json import dumps
from typing import TypedDict

from spade import agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


class Data(TypedDict):
    data_int: int


class DataCollectorAgent(agent.Agent):
    class CollectData(PeriodicBehaviour):
        data: Data

        async def run(self):
            print("[DataCollector] Starting collecting data")
            print("[DataCollector] Collecting data")
            await asyncio.sleep(5)
            print("[DataCollector] Data collected")
            print("[DataCollector] Preparing data to send")
            local_data: Data = dict(
                data_int=10
            )
            msg_to_send = Message(to="healthanalyzer@localhost")
            msg_to_send.body = dumps(local_data)
            await self.send(msg_to_send)
            print("[DataCollector] Message to Health Analyzer sent!")
            data = local_data

        async def on_start(self):
            print("[DataCollector] Starting collecting data Behaviour")

        async def on_end(self):
            print("[DataCollector] Ended and now sending collected data")
            await self.agent.stop()

    async def collect_data(self):
        pass

    async def setup(self):
        print("[DataCollector] Hello World! I'm agent {}".format(str(self.jid)))
        start_at: datetime = datetime.now() + timedelta(seconds=5)
        collect_data_b = self.CollectData(period=20, start_at=start_at)
        self.add_behaviour(collect_data_b)
