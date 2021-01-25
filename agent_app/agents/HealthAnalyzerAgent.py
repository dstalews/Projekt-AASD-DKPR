from json import dumps

from spade import agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

DATA_COLLECTOR_DATA_TEMPLATE: Template = Template(
    metadata=dict(performative='inform'),
)


class HealthAnalyzerAgent(agent.Agent):
    agent_name: str

    def __init__(self, logger, id, *args, **kwargs):
        self.logger = logger
        self.id = id
        super(HealthAnalyzerAgent, self).__init__(*args, **kwargs)

    class RequestData(OneShotBehaviour):
        async def run(self):
            msg = Message(
                f"datacollectorID{self.agent.id}@localhost",
                metadata=dict(performative="request")
            )
            await self.send(msg)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for DataCollector's data")
            msg = await self.receive(timeout=15)

            if msg:
                self.agent.logger.info(f"[{self.agent.agent_name}] Received data from DataCollector: {msg.body}")
                msg_to_send = Message(f"decisionmakerID{self.agent.id}@localhost", metadata=dict(performative="inform"))
                msg_to_send.body = dumps(dict(health_status="poor", blod_pressure="height"))
                await self.send(msg_to_send)
            else:
                request_behaviour = self.agent.RequestData()
                self.agent.add_behaviour(request_behaviour)
                await request_behaviour.join()

    async def setup(self):
        self.agent_name = "HealthAnalyzer"
        self.logger.info(f"[{self.agent_name}] Hello World! I'm agent {self.name} I'm analyzing your health!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b, template=DATA_COLLECTOR_DATA_TEMPLATE)
