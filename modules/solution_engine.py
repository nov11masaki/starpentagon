"""
解法推定エンジン
学習者の入力から解法アプローチを推定し、進捗段階を判定する
"""

import re
import json
from typing import Dict, List, Any
import google.generativeai as genai

class SolutionEngine:
    def __init__(self, model):
        self.model = model
        self.solution_patterns = {
            'vector': {
                'keywords': ['ベクトル', '内積', '外積', '成分', '単位ベクトル', '正規化'],
                'approaches': ['成分計算', '内積利用', '図形的解釈', 'ベクトル方程式']
            },
            'geometry': {
                'keywords': ['円', '直線', '放物線', '楕円', '双曲線', '座標', '距離'],
                'approaches': ['座標設定', '方程式設定', '判別式利用', '図形的性質']
            }
        }
    
    def analyze_solution(self, problem_content: str, user_input: str) -> Dict[str, Any]:
        """
        学習者の入力を分析し、解法アプローチと進捗段階を推定
        """
        try:
            # Gemini APIを使用した包括的な解法分析
            ai_evaluation = self._get_comprehensive_analysis(problem_content, user_input)
            
            # 基本的な問題分析
            problem_type = self._identify_problem_type(problem_content)
            approach = self._estimate_approach(user_input, problem_type)
            
            # AI分析結果から詳細情報を抽出
            return {
                'approach': ai_evaluation.get('approach', approach),
                'progress_stage': ai_evaluation.get('progress_stage', '解法開始段階'),
                'feedback': ai_evaluation.get('feedback', '解法を確認しています'),
                'correctness': ai_evaluation.get('correctness', 'partial'),
                'correctness_score': ai_evaluation.get('correctness_score', 0.5),
                'detailed_evaluation': ai_evaluation.get('detailed_evaluation', {}),
                'suggestions': ai_evaluation.get('suggestions', []),
                'confidence': ai_evaluation.get('confidence', 0.7)
            }
        except Exception as e:
            # エラー時のフォールバック
            return {
                'approach': 'エラーが発生しました',
                'progress_stage': '分析中',
                'feedback': f'分析中にエラーが発生しました: {str(e)[:100]}',
                'correctness': 'unknown',
                'correctness_score': 0.0,
                'detailed_evaluation': {},
                'suggestions': [],
                'confidence': 0.0
            }
    
    def _get_comprehensive_analysis(self, problem_content: str, user_input: str) -> Dict[str, Any]:
        """
        Gemini APIを使用した包括的な解法分析と正誤判定
        """
        prompt = f"""
あなたは高校数学の専門教師です。以下の問題と学習者の解答を分析して、詳細な評価を行ってください。

【問題】
{problem_content}

【学習者の解答・作業】
{user_input}

以下の項目について分析し、JSON形式で回答してください：

1. 解法アプローチ（どの解法を使っているか）
2. 進捗段階（問題理解 → 方針決定 → 計算実行 → 答え導出のどの段階か）
3. 正誤判定（correct/partial/incorrect/unknown）
4. 正解度スコア（0.0-1.0）
5. 詳細評価（各ステップの正確性）
6. フィードバック（具体的な指導内容）
7. 改善提案（次のステップへの提案）
8. 信頼度（分析結果の確信度 0.0-1.0）

回答形式：
{{
    "approach": "使用している解法名",
    "progress_stage": "現在の進捗段階",
    "correctness": "correct/partial/incorrect/unknown",
    "correctness_score": 0.0-1.0の数値,
    "detailed_evaluation": {{
        "problem_understanding": true/false,
        "method_selection": true/false,
        "calculation_accuracy": true/false,
        "final_answer": true/false,
        "presentation": true/false
    }},
    "feedback": "具体的なフィードバック内容",
    "suggestions": ["改善提案1", "改善提案2", "改善提案3"],
    "confidence": 0.0-1.0の数値
}}

特に以下に注意して分析してください：
- 数学的概念の理解度
- 計算の正確性
- 解法の適切性
- 論理的思考の流れ
- 最終答えの妥当性
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSON形式の応答を解析
            response_text = response.text.strip()
            
            # JSON部分を抽出（```json ``` で囲まれている場合）
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            analysis_result = json.loads(json_text)
            
            # デフォルト値の設定
            default_analysis = {
                'approach': '解法分析中',
                'progress_stage': '分析中',
                'correctness': 'unknown',
                'correctness_score': 0.5,
                'detailed_evaluation': {
                    'problem_understanding': False,
                    'method_selection': False,
                    'calculation_accuracy': False,
                    'final_answer': False,
                    'presentation': False
                },
                'feedback': 'AI分析を実行しています',
                'suggestions': ['解法を確認してください'],
                'confidence': 0.5
            }
            
            # 結果をマージ
            for key, default_value in default_analysis.items():
                if key not in analysis_result:
                    analysis_result[key] = default_value
            
            return analysis_result
            
        except Exception as e:
            print(f"AI分析エラー: {str(e)}")
            return {
                'approach': '分析エラー',
                'progress_stage': 'エラー発生',
                'correctness': 'unknown',
                'correctness_score': 0.0,
                'detailed_evaluation': {
                    'problem_understanding': False,
                    'method_selection': False,
                    'calculation_accuracy': False,
                    'final_answer': False,
                    'presentation': False
                },
                'feedback': f'AI分析中にエラーが発生しました: {str(e)[:100]}',
                'suggestions': ['手動で解法を確認してください'],
                'confidence': 0.0
            }
    
    def _identify_problem_type(self, problem_content: str) -> str:
        """問題タイプの判定"""
        vector_keywords = ['ベクトル', '内積', '外積', '成分']
        geometry_keywords = ['円', '直線', '放物線', '座標', '軌跡']
        
        if any(keyword in problem_content for keyword in vector_keywords):
            return 'vector'
        elif any(keyword in problem_content for keyword in geometry_keywords):
            return 'geometry'
        else:
            return 'unknown'
    
    def _estimate_approach(self, user_input: str, problem_type: str) -> str:
        """解法アプローチの推定"""
        if problem_type not in self.solution_patterns:
            return 'unknown'
        
        approaches = self.solution_patterns[problem_type]['approaches']
        
        # キーワードマッチングによる推定
        for approach in approaches:
            if approach in user_input:
                return approach
        
        # より詳細な分析（正規表現などを使用）
        if problem_type == 'vector':
            if re.search(r'\([0-9\-,\s]+\)', user_input):  # 成分表現
                return '成分計算'
            elif '内積' in user_input or '・' in user_input:
                return '内積利用'
        
        return 'unidentified'
