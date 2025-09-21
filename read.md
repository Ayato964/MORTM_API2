# MORTM API v2

このプロジェクトは、AIによる音楽生成モデルをFastAPIでラッピングし、Web APIとして提供するものです。

## 🚀 アーキテクチャ

本APIは、柔軟性と拡張性を重視した設計パターンを採用しています。

1.  **FastAPI Webサーバー (`app.py`)**:
    *   HTTPリクエストを受け付けるAPIの窓口です。
    *   リクエストのバリデーションを行い、`ModelController`に処理を委譲します。

2.  **モデル管理 (`model.py`)**:
    *   `ModelController`クラスが、APIのビジネスロジックを管理します。
    *   起動時に `data/models` ディレクトリをスキャンし、利用可能なモデルを自動で認識します。
    *   `ModelRapperFactory` を通じて、リクエストに応じたモデル処理クラス（Rapper）を動的に生成します。

3.  **モデル処理の抽象化 (`rapper.py`)**:
    *   **Strategyパターン**と**Factoryパターン**を採用しています。
    *   `AbstractModelRapper`: モデル固有の処理（読み込み、前処理、生成、後処理）のインターフェースを定義する抽象基底クラスです。
    *   `ModelRapperFactory`: モデル名に応じて、適切な `Rapper` のインスタンスを生成するクラスです。
    *   この設計により、モデルの内部実装を `ModelController` から完全に分離し、新しいモデルアーキテクチャの追加を容易にしています。

## ▶️ 使い方

### 1. サーバーの起動

以下のコマンドでAPIサーバーを起動します。

```bash
python app.py
```

サーバーは `http://0.0.0.0:8000` でリクエストを待ち受けます。

### 2. モデルの配置

`data/models` ディレクトリ以下に、各モデルを格納したフォルダを配置します。各モデルフォルダには、モデルのメタデータを記述した `data.json` を含める必要があります。

```
data/
└── models/
    ├── mortm-sax-v1/
    │   ├── model_weights.pth
    │   └── data.json  <-- メタデータファイル
    └── mortm-pro-v2/
        ├── model_weights.pth
        └── data.json
```

## 📖 APIエンドポイント

### モデル情報の取得

利用可能なすべてのモデルのメタデータを取得します。

-   **URL**: `/model_info`
-   **Method**: `POST`
-   **Response**:
    ```json
    {
      "0": {
        "model_name": "MORTM4.1-SAX",
        "description": "Alto Saxophone model",
        "model_folder_path": "/path/to/data/models/MORTM4.1-SAX"
      },
      "1": {
        "model_name": "MORTM4.1Pro-SAX",
        "description": "Professional Alto Saxophone model",
        "model_folder_path": "/path/to/data/models/MORTM4.1Pro-SAX"
      }
    }
    ```

### 音楽の生成

指定したモデルとパラメータで新しいファイルを生成します。

-   **URL**: `/generate`
-   **Method**: `POST`
-   **Request Body**: `multipart/form-data`
    -   `midi`: (`file`) 生成のベースとなるMIDIファイル。
    -   `meta_json`: (`string`) 生成パラメータを記述したJSON文字列。

#### `meta_json` の構造

`GenerateMeta`モデルに基づきます。

| フィールド        | 型             | 説明                                           | デフォルト値 |
| ----------------- | -------------- | ---------------------------------------------- | ------------ |
| `model_type`      | `string`       | 使用するモデル名 (`model_name`)。              | **必須**     |
| `program`         | `List[int]`    | MIDIのプログラムチェンジ番号。                 | **必須**     |
| `tempo`           | `int`          | 生成するMIDIのテンポ (BPM)。                   | **必須**     |
| `task`            | `string`       | モデルに与えるタスク。                         | **必須**     |
| `p`               | `float`        | Nucleus samplingのp値。                        | `0.95`       |
| `temperature`     | `float`        | 生成の多様性を制御する温度。                   | `1.0`        |
| `chord_item`      | `List[string]` | (任意) コード進行のリスト。                    | `None`       |
| `chord_times`     | `List[float]`  | (任意) 各コードの開始時間。                    | `None`       |
| `split_measure`   | `int`          | (任意) 処理を分割する小節数。                  | `999`        |

#### cURLリクエスト例

以下のコマンドは、生成されたファイルを `generated.mid` という名前で保存します。

```bash
curl -X POST "http://localhost:8000/generate" \
     -F "midi=@/path/to/your/input.mid" \
     -F "meta_json={\"model_type\": \"MORTM4.1-SAX\", \"program\": [56], \"tempo\": 120, \"task\": \"generate\", \"p\": 0.96}" \
     -o generated.mid
```

#### 成功レスポンス

-   **Status Code**: `200 OK`
-   **Content-Type**: レスポンスヘッダーには、生成されたファイルの形式に応じた`Content-Type`が設定されます。
    -   `.mid` ファイルの場合: `audio/midi`
    -   `.txt` ファイルの場合: `text/plain`
    -   その他の場合: `application/octet-stream`
-   **Response Body**: 生成されたファイル（MIDIやテキストなど）そのものが返されます。

## ✨ 新しいモデルの追加方法

新しいアーキテクチャのモデルを追加する手順は以下の通りです。

1.  **Rapperクラスの作成**:
    *   `rapper.py` の `AbstractModelRapper` を継承した、新しいRapperクラス（例: `NewModelRapper`）を作成します。
    *   `_load_model`, `preprocessing`, `generate`, `postprocessing` の各メソッドに、そのモデル固有の処理を実装します。

2.  **Rapperの登録**:
    *   `model.py` の `ModelController._register_rappers` メソッド内で、新しいRapperを登録します。
    *   モデル名に含まれるユニークなキーワードと、作成したRapperクラスを結びつけます。

    ```python
    # model.py
    class ModelController:
        def _register_rappers(self):
            # ... 既存の登録
            self.rapper_factory.register_rapper("NewModelKeyword", NewModelRapper)
    ```

3.  **モデルの配置**:
    *   `data/models` に新しいモデルのフォルダを配置します。フォルダ内の `data.json` の `model_name` に、登録したキーワード（例: `NewModelKeyword-v1`）が含まれていることを確認してください。

以上の手順で、APIは新しいモデルを自動的に認識し、生成リクエストに対応できるようになります。
