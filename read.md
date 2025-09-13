了解しました！以下に **README.md 形式** でまとめました。

````markdown
# 🎵 MIDI Generation API

このリポジトリは、MIDIファイルを入力として処理・生成を行う **FastAPI ベースのサーバー** です。  
エンドポイントを通じてモデル情報の取得や事前学習モデルを使った生成を実行できます。

---

## 🚀 セットアップ

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
````

主な依存関係:

* fastapi
* uvicorn
* mido

### 2. サーバーの起動

```bash
python app.py
```

起動後、サーバーは以下でアクセスできます:

```
http://127.0.0.1:8000
```

---

## 📡 エンドポイント

### 1. `/model_info`

モデルのメタ情報を返します。

* **Method**: `POST`
* **Request**

  ```bash
  curl -X POST http://127.0.0.1:8000/model_info
  ```
* **Response (例)**

  ```json
  {
    "name": "MORTM",
    "version": "4.1",
    "tasks": ["melody_generation", "arrangement"]
  }
  ```

---

### 2. `/pre_train_generate`

MIDIファイルをアップロードし、事前学習済みモデルで生成を行います。

* **Method**: `POST`

* **Parameters**

    * `midi` : アップロードするMIDIファイル (必須)
    * `model_type` : モデルの種類 (例: "melody", "arrange")
    * `temperature` : サンプリング温度 (デフォルト=1.0)
    * `p` : nucleus sampling (デフォルト=0.95)

* **Request (例: Linux/macOS)**

  ```bash
  curl -X POST http://127.0.0.1:8000/pre_train_generate \
    -F "midi=@example.mid" \
    -F "model_type=melody" \
    -F "temperature=1.0" \
    -F "p=0.95"
  ```

* **Response (例)**

  ```json
  {
    "saved": "data/saves/20250913/a1b2c3d4e5f6",
    "model_type": "melody",
    "temperature": 1.0,
    "p": 0.95
  }
  ```

---

## 📂 保存先

生成に使うファイルは以下に保存されます:

```
data/saves/{日付}/{ランダムID}/input.mid
```

---

## ⚠️ 注意点

* `CONTROLLER` が初期化されていない場合、`/model_info` はエラーになります。
  `python app.py` で起動した場合は自動初期化されますが、
  `uvicorn app:app --reload` を使う場合は `@app.on_event("startup")` で初期化処理を追加してください。
* 対応MIDIフォーマット:

    * `audio/midi`
    * `audio/x-midi`
    * `application/x-midi`
    * `application/octet-stream`

---

## 🛠 今後のTODO

* 生成処理の実装（現在はダミーレスポンス）
* Docker対応
* 生成結果の保存形式やログ機能の追加

```

---

このREADMEは最小限ですが、もし **Docker対応の起動方法** や **実際の生成処理のサンプルコード** も追記した方がいいですか？
```
