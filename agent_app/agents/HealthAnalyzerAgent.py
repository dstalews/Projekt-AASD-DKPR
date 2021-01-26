import json
import asyncio

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
                "datacollector@localhost",
                metadata=dict(performative="request")
            )
            await self.send(msg)

    class RetrieveData(CyclicBehaviour):
        async def run(self):
            self.agent.logger.info(f"[{self.agent.agent_name}] Cyclic behaviour. I'm waiting for DataCollector's data")
            msg = await self.receive(timeout=60) # TODO: uncomment after merge

            if msg:
                self.agent.logger.info(f"[{self.agent.agent_name}] Received data from DataCollector: {msg.body}") # TODO: uncomment after merge
                data = json.loads(msg.body) # TODO: uncomment after merge
                heart_beat = int(data['heartbeat'])
                blood_pressure = int(data['pressure'])
                age = int(data['age'])
                weight = int(data['weight'])
                height = int(data['hight'])

                bmi = calculate_bmi(weight, height)
                age_range = categorize_age(age)
                bmi_range = categorize_bmi(bmi)
                heart_beat_range = categorize_heart_beat(heart_beat, age_range)
                blood_pressure_range = categorize_blood_pressure(blood_pressure, age_range)            

                msg_to_send = Message(f"decisionmakerID{self.agent.id}@localhost", metadata=dict(performative="inform"))
                msg_to_send.body = json.dumps(dict(heartbeat=heart_beat_range, pressure=blood_pressure_range, bmi=bmi_range, age=age_range))

                await self.send(msg_to_send)
            else:
                request_behaviour = self.agent.RequestData()
                self.agent.add_behaviour(request_behaviour)
                await request_behaviour.join()

    async def setup(self):
        self.agent_name = "HealthAnalyzer"
        self.logger.info(f"[{self.agent_name}] Hello World! I'm agent {self.jid} I'm analyzing your health!")
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b, template=DATA_COLLECTOR_DATA_TEMPLATE)

def calculate_bmi(weight, height):
    if height == 0:
        return 0
    return weight / ((height/100)*(height/100))

def categorize_age(age):
    if age < 18:
        return 1
    if age < 40:
        return 2
    if age < 60:
        return 3
    else:
        return 4

def categorize_bmi(bmi):
    if bmi < 16:
        return 4
    if bmi < 18.5:
        return 1
    if bmi < 25:
        return 2
    if bmi < 30:
        return 3
    else:
        return 4

def categorize_blood_pressure(blood_pressure, age_range):
    if age_range == 1:
        if blood_pressure < 90:
            return 4
        if blood_pressure < 110:
            return 1
        if blood_pressure < 125:
            return 2
        if blood_pressure < 140:
            return 3
        else:
            return 4
    if age_range == 2:
        if blood_pressure < 100:
            return 4
        if blood_pressure < 115:
            return 1
        if blood_pressure < 135:
            return 2
        if blood_pressure < 150:
            return 3
        else:
            return 4
    if age_range == 3:
        if blood_pressure < 105:
            return 4
        if blood_pressure < 120:
            return 1
        if blood_pressure < 140:
            return 2
        if blood_pressure < 160:
            return 3
        else:
            return 4
    if age_range == 4:
        if blood_pressure < 110:
            return 4
        if blood_pressure < 125:
            return 1
        if blood_pressure < 145:
            return 2
        if blood_pressure < 165:
            return 3
        else:
            return 4

def categorize_heart_beat(heart_beat, age_range):
    if age_range == 1:
        if heart_beat < 55:
            return 4
        if heart_beat < 75:
            return 1
        if heart_beat < 95:
            return 2
        if heart_beat < 125:
            return 3
        else:
            return 4
    if age_range == 2:
        if heart_beat < 50:
            return 4
        if heart_beat < 70:
            return 1
        if heart_beat < 90:
            return 2
        if heart_beat < 120:
            return 3
        else:
            return 4
    if age_range == 3:
        if heart_beat < 45:
            return 4
        if heart_beat < 60:
            return 1
        if heart_beat < 80:
            return 2
        if heart_beat < 110:
            return 3
        else:
            return 4
    if age_range == 4:
        if heart_beat < 40:
            return 4
        if heart_beat < 50:
            return 1
        if heart_beat < 70:
            return 2
        if heart_beat < 90:
            return 3
        else:
            return 4
