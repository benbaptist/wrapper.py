import os

class Plugins:
    def __init__(self, wrapper):
        self.wrapper = wrapper

        if not os.path.exists("wrapper-data/plugins"):
            os.makedirs("wrapper-data/plugins")

    def load_plugins(self):
        return
