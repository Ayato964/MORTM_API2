from model import AbstractModelRapper

class MORTM4Rapper(AbstractModelRapper):

    def __init__(self):
        super().__init__()

    def preprocessing(self, midi_path):
        pass

    def postprocessing(self, sequence, save_directory):
        pass

    def generate(self, sequence, save_directory):
        pass