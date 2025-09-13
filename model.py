import json
import os
import torch

from pretty_midi import PrettyMIDI

from mortm.models.mortm import MORTM, MORTMArgs
from mortm.models.modules.progress import _DefaultLearningProgress
from mortm.utils.generate import *


class ModelController:
    def __init__(self):
        model_folders = get_model_folder_paths()
        self.models = {}
        self.meta = {}
        for i, model in enumerate(model_folders):
            j = json.load(open(os.path.join(model, "data.json"), "r", encoding="utf-8"))
            print(f"Loading model: {j['model_name']} from {model}")
            self.models[j['model_name']] = j.copy()
            self.meta[i] = j.copy()
            args = MORTMArgs(os.path.join(model, "config.json"))
            progress = _DefaultLearningProgress()
            m = MORTM(args, progress).to(progress.get_device())
            m.load_state_dict(torch.load(os.path.join(model, "model.pth")))
            self.models[j['model_name']]['instance'] = m

        print(self.meta)

    async def generate(self, model_name, midi_path, save_directory):
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found.")
        model = self.models[model_name]
        return model.d_model


def get_model_folder_paths(base_dir="data/models"):
    """
    data/models配下の全フォルダパスをリストで返す
    """
    abs_base_dir = os.path.abspath(base_dir)
    return [os.path.join(abs_base_dir, name) for name in os.listdir(abs_base_dir)
            if os.path.isdir(os.path.join(abs_base_dir, name))]


class AbstractModelRapper(ABC):
    def __init__(self, data_path, config_path):
        with open(data_path, 'r') as f:
            self.meta = json.load(f)
        self.config = config_path

    @abstractmethod
    def preprocessing(self, midi_path):
        pass

    @abstractmethod
    def postprocessing(self, sequence, save_directory):
        pass

    @abstractmethod
    def generate(self, sequence, save_directory):
        pass

