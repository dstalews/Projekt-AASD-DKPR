import asyncio
from json import dumps

from spade import agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

HEALTH_ANALYZER_DATA_TEMPLATE: Template = Template(
    sender="healthanalyzer@localhost",
    metadata=dict(performative="submit")
)


class DecisionMakerAgent(agent.Agent):
    decision: dict = dict()
    agent_name: str

    class MakeDecision(OneShotBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Making decision")
            await asyncio.sleep(2)
            self.agent.decision = dict(
                type='walk',
                requirements=dict(
                    min_len=10,
                )
            )

        async def on_end(self):
            msg_to_send: Message = Message("actionexecutor@localhost", metadata=dict(performative="submit"))
            msg_to_send.body = dumps(self.agent.decision)
            await self.send(msg_to_send)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for HealthAnalyzer's data")
            msg = await self.receive(timeout=15)

            if msg:
                print(f"[{self.agent.agent_name}] Received data from HealthAnalyzer: {msg.body}")
                self.agent.make_decision = self.agent.MakeDecision()
                self.agent.add_behaviour(self.agent.make_decision)
                await self.agent.make_decision.join()

                print(f"[{self.agent.agent_name}] Made decision: {self.agent.decision}")
            else:
                print(f"[{self.agent.agent_name}] Didn't receive data from HealthAnalyzer")

    async def setup(self):
        self.agent_name = "DecisionMaker"
        print(
            f"[{self.agent_name}] Hello World! I'm agent {self.jid} I'm deciding what to do based on data received from HealthAnalyzer!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b, template=HEALTH_ANALYZER_DATA_TEMPLATE)
