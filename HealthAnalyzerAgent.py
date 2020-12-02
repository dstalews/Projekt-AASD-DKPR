from spade import agent
from spade.behaviour import CyclicBehaviour


class HealthAnalyzerAgent(agent.Agent):
    class RetrieveData(CyclicBehaviour):
        async def run(self):
            print("[HealthAnalyzer] Cyclic behaviour. I'm waiting for DataCollector's data")
            msg = await self.receive(timeout=15)

            if msg:
                print(f"[HealthAnalyzer] Received data from DataCollector: {msg.body}")
            else:
                print("[HealthAnalyzer] Didn't receive data from collector")
                # self.kill()

    async def setup(self):
        print("[HealthAnalyzer] Hello World! I'm agent {} I'm analyzing your health!".format(str(self.jid)))
        retrieve_data_b = self.RetrieveData()
        self.add_behaviour(retrieve_data_b)
