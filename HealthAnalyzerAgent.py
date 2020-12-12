from json import dumps

from spade import agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message


class HealthAnalyzerAgent(agent.Agent):
    agent_name: str

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for DataCollector's data")
            msg = await self.receive(timeout=15)

            if msg:
                print(f"[{self.agent.agent_name}] Received data from DataCollector: {msg.body}")
                msg_to_send = Message("decisionmaker@localhost")
                msg_to_send.body = dumps(dict(health_status="poor", blod_pressure="height"))
                await self.send(msg_to_send)
            else:
                print(f"[{self.agent.agent_name}] Didn't receive data from collector")

    async def setup(self):
        self.agent_name = "HealthAnalyzer"
        print(f"[{self.agent_name}] Hello World! I'm agent {self.jid} I'm analyzing your health!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b)
