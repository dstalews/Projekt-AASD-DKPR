import asyncio
from datetime import datetime, timedelta
from typing import TypedDict

from spade import agent
from spade.behaviour import PeriodicBehaviour


class Data(TypedDict):
    data_int: int


class DataCollectorAgent(agent.Agent):
    class CollectData(PeriodicBehaviour):
        data: Data

        async def run(self):
            print("Starting Periodic Behaviour")
            print("Collecting data")
            await asyncio.sleep(5)
            print("Data collected")

        async def on_start(self):
            print("Starting collecting data")

        async def on_end(self):
            print("Ended and now sending collected data")

    async def collect_data(self):
        pass

    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))
        start_at: datetime = datetime.now() + timedelta(seconds=5)
        collect_data_b = self.CollectData(period=20, start_at=start_at)
        self.add_behaviour(collect_data_b)
