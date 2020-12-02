import time

from spade import agent

print('test')


class DataCollectorAgent(agent.Agent):
    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))


data_collector = DataCollectorAgent("datacollector@localhost", "datacollector1")
data_collector.start()
time.sleep(1)
data_collector.stop()
