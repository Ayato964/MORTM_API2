import json
import os
from typing import Optional, List

from rapper import *
from models.mortm.mortm4 import MORTM4Rapper

# --- Controller ---
class ModelController:
    def __init__(self):
        self.rapper_factory = ModelRapperFactory()
        self._register_rappers()

        self.available_models = {}
        self._scan_model_folders()

        self.meta = {i: info for i, info in enumerate(self.available_models.values())}
        print("Initialized. Available models:")
        print(self.meta)

    def _register_rappers(self):
        """
        ここに新しいRapperクラスを登録します。
        これにより、新しいモデルアーキテクチャに簡単対応できます。
        """
        self.rapper_factory.register_rapper("MORTM4.1-SAX", MORTM4Rapper)
        self.rapper_factory.register_rapper("MORTM4.1Pro-SAX", MORTM4Rapper)

        # 例: self.rapper_factory.register_rapper("NewModel", NewModelRapper)

    def _scan_model_folders(self, base_dir="data/models"):
        """
        モデルフォルダをスキャンし、モデルのメタデータを読み込みます。
        この時点ではモデルのインスタンス化は行いません。
        """
        if not os.path.isdir(base_dir):
            return
        abs_base_dir = os.path.abspath(base_dir)
        for name in os.listdir(abs_base_dir):
            model_path = os.path.join(abs_base_dir, name)
            if not os.path.isdir(model_path):
                continue

            data_json_path = os.path.join(model_path, "data.json")
            if os.path.exists(data_json_path):
                try:
                    with open(data_json_path, "r", encoding="utf-8") as f:
                        model_info = json.load(f)
                    model_name = model_info.get('model_name')
                    if model_name:
                        model_info['model_folder_path'] = model_path
                        self.available_models[model_name] = model_info
                        print(f"Found model: {model_name}")
                except Exception as e:
                    print(f"Error loading model info from {model_path}: {e}")

    async def generate(self, model_type, midi_path: str, meta: GenerateMeta, save_directory):
        if model_type not in self.available_models:
            raise ValueError(f"指定されたモデル({model_type})は存在しません")

        # generateが呼ばれたタイミングで、初めてRapperとモデルをインスタンス化する
        model_info = self.available_models[model_type]
        rapper = self.rapper_factory.create_rapper(model_info)

        kwargs = rapper.preprocessing(midi_path, meta)
        generated_data_kwargs = rapper.generate(**kwargs)
        output_file_path = rapper.postprocessing(save_directory, **generated_data_kwargs)

        return {
            "result": "success",
            "model_type": model_type,
            "save_path": str(save_directory),
            "output_file": output_file_path
        }
