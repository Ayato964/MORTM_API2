import json
import os
import torch

from pretty_midi import PrettyMIDI
from rapper import *

from mortm.models.mortm import MORTM, MORTMArgs
from mortm.models.modules.progress import _DefaultLearningProgress
from mortm.utils.generate import *
from mortm.utils.convert import MetaData2Chord
from mortm.train.tokenizer import get_token_converter
from model import AbstractModelRapper



class MORTM4Rapper(AbstractModelRapper):

    """MORTMモデル用の具体的な処理を実装したクラス (Concrete Strategy)"""
    def _load_model(self):
        model_path = self.meta['model_folder_path']
        config_path = os.path.join(model_path, "config.json")
        model_pth_path = os.path.join(model_path, "model.pth")

        print(f"Loading model: {self.meta['model_name']} from {model_path}")
        args = MORTMArgs(config_path)
        progress = _DefaultLearningProgress()
        model = MORTM(args, progress).to(progress.get_device())
        model.load_state_dict(torch.load(model_pth_path))
        model.eval() # 推論モードに設定
        return model

    def preprocessing(self, midi_path, meta):
        return {"midi_path": midi_path, "meta": meta}

    def generate(self, **kwargs):
        return kwargs

    def postprocessing(self, save_directory, **kwargs):
        output_path = os.path.join(save_directory, "output.mid")
        midi_path = kwargs['midi_path']
        meta: GenerateMeta = kwargs['meta']
        if self.meta['tag']['model'] == 'pretrained':
            tokenizer = Tokenizer(get_token_converter(TO_TOKEN))
            pre_train_generate(self.model, tokenizer, save_directory, [midi_path],
                               program=meta.program,
                               p=meta.p, temperature=meta.temperature,
                               split_measure=meta.split_measure)
            os.rename(os.path.join(save_directory, f"generated_{os.path.basename(midi_path)}"), output_path)
        elif self.meta['tag']['model'] == 'sft':
            tokenizer = Tokenizer(get_token_converter(TO_TOKEN))
            chord_prompt = None
            if meta.chord_item is not None and meta.chord_times is not None:
                c = MetaData2Chord(tokenizer, "C minor",
                                   all_chords=meta.chord_item, all_chord_timestamps=meta.chord_times,
                                   tempo=meta.tempo, split_measure=meta.split_measure,
                                   directory=None, file_name=None, is_include_special_token=False)
                c.convert()
                chord_prompt = c.aya_node[1]
            gem = task_trained_generate(self.model, tokenizer, save_directory, midi_path,
                                  chord_prompt=chord_prompt, program=meta.program,
                                  task=meta.task, split_measure=meta.split_measure, temperature=meta.temperature,
                                  p=meta.p)
            if meta.task == "CHORD_GEM":
                with open(os.path.join(save_directory, "chord_output.txt"), "w", encoding="utf-8") as f:
                    if gem is not None:
                        tokenizer.mode(TO_MUSIC)
                        f.write(" ".join([tokenizer.rev_get(t) for t in gem]))
                        return os.path.join(save_directory, "chord_output.txt")


        return output_path