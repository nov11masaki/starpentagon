# 🧮 AI数学チューター Webアプリケーション

高校数学の学習者向けの個別指導AIチューターWebアプリケーションです。学習者の思考プロセスを推定し、個別最適なヒントを提供することで、自己解決能力の育成を支援します。

## 🎯 プロジェクト概要

### 主な特徴
- **個別最適な指導**: 学習者の思考プロセスを分析し、個人に合わせたヒントを生成
- **段階的支援**: レベル別のヒントシステムで段階的な学習をサポート
- **解法多様性対応**: 複数の解法アプローチを認識・対応
- **リアルタイム分析**: Google Gemini APIを活用した高精度な思考分析

### 対象分野
- ベクトル（内積、成分計算、図形的解釈）
- 図形と方程式（円、直線、軌跡）

## 🛠️ 技術スタック

- **バックエンド**: Python, Flask
- **AI/ML**: Google Gemini API
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **数式レンダリング**: MathJax
- **開発環境**: Visual Studio Code

## 📋 システム要件

- Python 3.8以上
- Google Gemini API キー
- モダンなWebブラウザ (Chrome, Firefox, Safari, Edge)

## 🚀 セットアップ手順

### 1. リポジトリのクローンと依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd "AI math/mathmatic"

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\\Scripts\\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
# .env.example をコピー
cp .env.example .env

# .env ファイルを編集してGemini API キーを設定
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Gemini API キーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. 新しいAPIキーを作成
3. `.env`ファイルに設定

### 4. アプリケーションの起動

```bash
python app.py
```

アプリケーションは `http://localhost:5000` で起動します。

## 📖 使用方法

### 基本的な使い方

1. **問題選択**: 用意されている数学問題から一つを選択
2. **解答入力**: 思考プロセスを自由にテキストエリアに記述
3. **思考チェック**: 「思考チェック」ボタンで分析を実行
4. **ヒント活用**: 表示されるヒントを参考に学習を継続

### ヒントシステム

- **レベル1**: 励ましのヒント - 学習者を励まし、方向性を示唆
- **レベル2**: 方向性のヒント - 解法の大まかな方向を提示
- **レベル3**: 具体的なヒント - より具体的なアクションを提案
- **レベル4+**: 詳細な解法ヒント - 解法の詳細な手順を説明

## 🏗️ プロジェクト構造

```
AI math/mathmatic/
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存関係
├── .env.example          # 環境変数テンプレート
├── .env                  # 環境変数（要作成）
├── modules/              # アプリケーションモジュール
│   ├── __init__.py
│   ├── solution_engine.py    # 解法推定エンジン
│   ├── hint_generator.py     # ヒント生成システム
│   └── problem_database.py   # 問題データベース
├── templates/            # HTMLテンプレート
│   └── index.html
├── static/              # 静的ファイル
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── .github/             # GitHub設定
│   └── copilot-instructions.md
└── README.md
```

## 🔧 開発

### 新しい問題の追加

`modules/problem_database.py` の `_initialize_problems` メソッドに新しい問題を追加できます：

```python
new_problem_id: {
    'id': new_problem_id,
    'title': '問題タイトル',
    'category': 'vector' or 'geometry',
    'difficulty': 'basic', 'intermediate', or 'advanced',
    'content': 'LaTeX記法での問題文',
    'solution_patterns': [...],
    'hints': {...}
}
```

### APIエンドポイント

- `GET /api/problems` - 問題一覧の取得
- `GET /api/problem/<id>` - 特定の問題の取得  
- `POST /api/check-thinking` - 思考チェック
- `POST /api/get-hint` - 段階的ヒント取得

## 📊 分析機能

### 解法推定
- **問題タイプ判定**: ベクトル、図形と方程式などの分類
- **アプローチ推定**: 学習者が選択している解法方針の特定
- **進捗段階判定**: 現在の解答段階の評価

### ヒント生成
- **個別最適化**: 学習者の理解度と進捗に応じたヒント
- **段階的支援**: 答えを教えずに思考をガイド
- **エラー検出**: 計算ミスや論理的誤りの指摘

## 🎨 UI/UX特徴

- **レスポンシブデザイン**: PC・タブレット対応
- **数式美麗表示**: MathJaxによる高品質な数式レンダリング
- **直感的操作**: 学習を妨げないシンプルなインターフェース
- **リアルタイムフィードバック**: 即座に分析結果を表示

## 🔒 セキュリティ

- API キーの環境変数管理
- 入力値のサニタイゼーション
- XSS攻撃対策の実装

## 📈 今後の開発予定

### フェーズ2の機能拡張
- デジタルホワイトボードUI
- 手書き数式認識
- リアルタイム思考追跡
- より多くの数学分野への対応

## 🤝 貢献

プロジェクトへの貢献を歓迎します。バグレポート、機能要求、プルリクエストをお気軽にお送りください。

## 📄 ライセンス

MIT License

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesをご利用ください。

---

**教育は未来への投資です。このAI数学チューターが、すべての学習者の数学的思考力向上に貢献できることを願っています。** 🌟
