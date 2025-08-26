from fastapi import Form
from pathlib import Path
import io, os, uuid, mido

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from mortm.utils.generate import *
from model import *

app = FastAPI()
CONTROLLER: Optional[ModelController] = None
SAVE_DIR = Path("data/saves")


@app.post("/model_info")
async def model_info():
    return JSONResponse(CONTROLLER.meta)


@app.post("/pre_train_generate")
async def pre_train_generate(
        midi: UploadFile = File(...),
        model_type: str = Form(...),
        temperature: float = Form(1.0),
        p: float = Form(0.95),
):
    allowed_types = {"audio/midi", "audio/x-midi", "application/x-midi", "application/octet-stream"}
    if midi.content_type not in allowed_types:
        return JSONResponse({"error": "MIDIファイルをアップロードしてください"}, status_code=400)

    try:
        raw = await midi.read()
        midi_obj = mido.MidiFile(file=io.BytesIO(raw))

        SAVE_DIR.mkdir(parents=True, exist_ok=True)

        # 元のファイル名があれば使う。なければUUIDに退避
        orig = (midi.filename or "input.mid").replace("\\", "_").replace("/", "_")
        if not orig.lower().endswith(".mid"):
            orig += ".mid"
        save_path = SAVE_DIR / orig

        midi_obj.save(save_path.as_posix())
        # TODO: 生成処理
        return {"saved": str(save_path), "model_type": model_type, "temperature": temperature, "p": p} # 仮のレスポンス
    except Exception:
        return JSONResponse({"error": "有効なMIDIファイルのみ受け付けます"}, status_code=400)

if __name__ == "__main__":
    print("モデルの初期化を行っています・・・・")
    CONTROLLER = ModelController()
    print("モデルの初期化が完了しました。")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
