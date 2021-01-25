import asyncio
from json import dumps, load, loads

from spade import agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

HEALTH_ANALYZER_DATA_TEMPLATE: Template = Template(
    metadata=dict(performative="inform")
)

with open("actions.json", "r") as read_file:
    actions = load(read_file)

class DecisionMakerAgent(agent.Agent):
    decision: dict = dict()
    agent_name: str
    message: dict
    

    class MakeDecision(OneShotBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Making decision")
            await asyncio.sleep(2)
            data = loads(self.agent.message)
            key = str(data['heartbeat']) + str(data['pressure']) + str(data['bmi']) + str(data['age'])
            self.agent.decision = actions[key]

        async def on_end(self):
            msg_to_send: Message = Message(f"actionexecutorID{self.agent.id}@localhost", metadata=dict(performative="inform"))
            msg_to_send.body = dumps(self.agent.decision)
            await self.send(msg_to_send)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for HealthAnalyzer's data")
            msg = await self.receive(timeout=15)

            if msg:
                print(f"[{self.agent.agent_name}] Received data from HealthAnalyzer: {msg.body}")
                self.agent.message = msg.body
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
