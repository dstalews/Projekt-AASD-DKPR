import asyncio
from json import dumps, loads

from spade import agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

DECISION_MAKER_DATA_TEMPLATE: Template = Template(
    metadata=dict(performative="inform")
)

class ActionExecutorAgent(agent.Agent):
    agent_name: str
    decision: dict

    def __init__(self, logger, id, *args, **kwargs):
        self.logger = logger
        self.id = id
        super(ActionExecutorAgent, self).__init__(*args, **kwargs)

    class ExecuteAction(OneShotBehaviour):
        async def run(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Executing action {self.agent.decision['actions']}")
            await asyncio.sleep(1)

        async def on_end(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Sending information to DataCollector")
            msg_to_send = Message(f"datacollectorID{self.agent.id}@localhost", metadata=dict(performative="inform"))
            msg_to_send.body = dumps(dict(action=self.agent.decision, status="SUCCESS"))
            await self.send(msg_to_send)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for an action to execute")
            msg = await self.receive(timeout=10)

            if msg:
                self.agent.logger.info(f"[{self.agent.agent_name}] Received data from DecisionMaker: {msg.body}")
                self.agent.decision = loads(msg.body)
                self.agent.execute_action = self.agent.ExecuteAction()
                self.agent.add_behaviour(self.agent.execute_action)
                await self.agent.execute_action.join()
            else:
                self.agent.logger.info(f"[{self.agent.agent_name}] Didn't receive data from DecisionMaker")
                # self.kill()

    async def setup(self):
        self.agent_name = "ActionExecutor"
        self.logger.info(
            f"[{self.agent_name}] Hello World! I'm agent {self.name} I'm executing action made by DecisionMaker!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b, template=DECISION_MAKER_DATA_TEMPLATE)
