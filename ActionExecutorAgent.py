import asyncio
from json import dumps, loads

from spade import agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

DECISION_MAKER_DATA_TEMPLATE: Template = Template(
    sender="decisionmaker@localhost",
    metadata=dict(performative="submit")
)


class ActionExecutorAgent(agent.Agent):
    agent_name: str
    decision: dict

    class ExecuteAction(OneShotBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Executing action {self.agent.decision['type']}")
            await asyncio.sleep(1)

        async def on_end(self):
            print(f"[{self.agent.agent_name}] Sending information to DataCollector")
            msg_to_send = Message("datacollector@localhost", metadata=dict(performative="inform"))
            msg_to_send.body = dumps(dict(action=self.agent.decision, status="SUCCESS"))
            await self.send(msg_to_send)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for an action to execute")
            msg = await self.receive(timeout=10)

            if msg:
                print(f"[{self.agent.agent_name}] Received data from HealthAnalyzer: {msg.body}")
                self.agent.decision = loads(msg.body)
                self.agent.execute_action = self.agent.ExecuteAction()
                self.agent.add_behaviour(self.agent.execute_action)
                await self.agent.execute_action.join()
            else:
                print(f"[{self.agent.agent_name}] Didn't receive data from DecisionMaker")
                # self.kill()

    async def setup(self):
        self.agent_name = "ActionExecutor"
        print(
            f"[{self.agent_name}] Hello World! I'm agent {self.jid} I'm executing action made by DecisionMaker!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b, template=DECISION_MAKER_DATA_TEMPLATE)
