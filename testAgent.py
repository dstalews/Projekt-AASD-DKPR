import time

from spade import agent

print('test')


class DummyAgent(agent.Agent):
    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))


dummy = DummyAgent("datacollector@localhost", "datacollector1")
dummy.start()
time.sleep(1)
dummy.stop()
