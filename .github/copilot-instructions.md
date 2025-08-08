<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI数学チューター Webアプリケーション

このプロジェクトは、高校数学の学習者向けの個別指導AIチューターWebアプリケーションです。

## プロジェクトの目的
- 学習者の思考プロセスを推定し、個別最適なヒントを提供
- 解法の多様性に対応（特にベクトル、図形と方程式）
- 段階的な学習支援を通じて自己解決能力を育成

## 技術スタック
- **バックエンド**: Python Flask
- **AI/ML**: Google Gemini API
- **フロントエンド**: HTML, CSS, JavaScript, MathJax
- **数式処理**: LaTeX記法、MathJax

## コーディング規約とベストプラクティス

### Python (バックエンド)
- PEP 8に準拠したコードスタイル
- 型ヒントを積極的に使用
- docstringは日本語で記述
- エラーハンドリングを適切に実装
- Gemini APIのレート制限を考慮した実装

### JavaScript (フロントエンド)
- ES6+ の機能を活用
- async/await を使用した非同期処理
- クラスベースの設計
- DOM操作の最適化
- MathJax との連携を考慮

### 数学的コンテンツ
- LaTeX記法での数式表現
- MathJaxでの適切なレンダリング
- ユニコード数学記号の適切な使用
- 数学的概念の正確な表現

### UI/UX設計
- レスポンシブデザインの実装
- アクセシビリティの配慮
- 学習者にとって直感的なインターフェース
- フィードバックの明確な表示

## 主要コンポーネント

### 解法推定エンジン (modules/solution_engine.py)
- 学習者の入力から解法アプローチを推定
- 進捗段階の判定
- Gemini APIとの連携

### ヒント生成システム (modules/hint_generator.py)
- 段階的ヒントの生成
- 個別最適化されたアドバイス
- 自己解決力を促進する指導

### 問題データベース (modules/problem_database.py)
- 数学問題とメタデータの管理
- 解法パターンの格納
- カテゴリ別の問題分類

## 開発時の注意点

1. **数学的正確性**: 数式や解法の正確性を最優先
2. **教育的配慮**: 答えを直接教えず、思考プロセスを支援
3. **エラーハンドリング**: Gemini API のエラーや制限に対する適切な対応
4. **パフォーマンス**: 3秒以内の応答時間を目標
5. **拡張性**: 新しい問題や解法パターンの追加が容易な設計

## セキュリティ
- API キーの適切な管理
- 入力値のサニタイゼーション
- XSS対策の実装

## テスト
- 数学的解法の正確性テスト
- UI/UXの使いやすさテスト
- API統合テスト
