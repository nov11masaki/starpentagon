"""
ヒント生成システム
学習者の進捗とつまづきに応じて段階的なヒントを生成
"""

from typing import Dict, List, Any
import google.generativeai as genai

class HintGenerator:
    def __init__(self, model):
        self.model = model
        self.hint_templates = {
            'problem_understanding': [
                "まず問題文を整理してみましょう。何を求めているか明確にしてください。",
                "与えられた条件をリストアップしてみてください。",
                "図やグラフを描いて問題を視覚化してみましょう。"
            ],
            'approach_selection': [
                "この問題にはどのような解法が考えられるでしょうか？",
                "似たような問題を解いたことはありませんか？",
                "使えそうな公式や定理を思い出してみましょう。"
            ],
            'calculation_progress': [
                "計算を一歩ずつ確認してみましょう。",
                "符号や計算ミスがないか確認してください。",
                "別の方法でも計算してみて、答えが合うか確認しましょう。"
            ]
        }
    
    def generate_hints(self, problem_content: str, user_input: str, solution_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        分析結果に基づいてヒントを生成
        """
        hints = []
        
        # 新しい分析結果構造に対応
        progress_stage = solution_analysis.get('progress_stage', '問題理解段階')
        correctness = solution_analysis.get('correctness', 'unknown')
        detailed_eval = solution_analysis.get('detailed_evaluation', {})
        
        # 段階別の基本ヒント
        basic_hint = self._get_basic_hint_from_progress(progress_stage)
        if basic_hint:
            hints.append({
                'type': 'basic',
                'content': basic_hint,
                'level': 1
            })
        
        # 正誤状況に応じたヒント
        correctness_hint = self._get_correctness_based_hint(correctness, detailed_eval)
        if correctness_hint:
            hints.append({
                'type': 'correctness_based',
                'content': correctness_hint,
                'level': 2
            })
        
        # AIによる個別ヒント
        ai_hint = self._generate_ai_hint(problem_content, user_input, solution_analysis)
        if ai_hint:
            hints.append({
                'type': 'ai_generated',
                'content': ai_hint,
                'level': 3
            })
        
        return hints
    
    def get_progressive_hint(self, problem_content: str, user_input: str, hint_level: int) -> str:
        """
        段階的なヒントを取得（レベルが上がるほど具体的）
        """
        if hint_level == 1:
            return self._get_encouraging_hint(user_input)
        elif hint_level == 2:
            return self._get_directional_hint(problem_content, user_input)
        elif hint_level == 3:
            return self._get_specific_hint(problem_content, user_input)
        else:
            return self._get_detailed_solution_hint(problem_content, user_input)
    
    def _get_basic_hint(self, current_stage: str) -> str:
        """段階別の基本ヒント"""
        if current_stage in self.hint_templates:
            templates = self.hint_templates[current_stage]
            return templates[0]  # 最初のテンプレートを使用
        return None
    
    def _get_basic_hint_from_progress(self, progress_stage: str) -> str:
        """進捗段階から基本ヒントを取得"""
        stage_hints = {
            '問題理解段階': "まず問題文をよく読んで、何を求めているのかを明確にしましょう。",
            '方針決定段階': "問題を解くためにどの公式や解法を使うか考えてみましょう。",
            '計算実行段階': "計算を進めているところですね。符号や計算ミスに注意してください。",
            '答え導出段階': "もう少しで答えに到達できそうです。最終的な答えの形を確認しましょう。",
            '解答完了段階': "よくできました！答えが正しいか最終確認をしてみましょう。"
        }
        
        for key, hint in stage_hints.items():
            if key in progress_stage or progress_stage in key:
                return hint
        
        return "この調子で解き進めていきましょう！"
    
    def _get_correctness_based_hint(self, correctness: str, detailed_eval: Dict[str, bool]) -> str:
        """正誤状況に基づくヒント"""
        if correctness == 'correct':
            return "素晴らしい！正解です。解法もよく理解できていますね。"
        elif correctness == 'partial':
            # 詳細評価から具体的なアドバイス
            issues = []
            if not detailed_eval.get('problem_understanding', True):
                issues.append("問題の理解をもう一度確認してみましょう")
            if not detailed_eval.get('method_selection', True):
                issues.append("解法の選択を見直してみましょう")
            if not detailed_eval.get('calculation_accuracy', True):
                issues.append("計算をもう一度チェックしてください")
            if not detailed_eval.get('final_answer', True):
                issues.append("最終答えの形を確認してみましょう")
            
            if issues:
                return f"部分的に正しいです。特に{issues[0]}。"
            else:
                return "いい方向で進んでいます。もう少しで完璧です！"
        elif correctness == 'incorrect':
            return "解法を見直してみましょう。基本的な公式や条件を再確認してください。"
        else:
            return "解答を続けてください。分からない部分があれば、基本に戻って考えてみましょう。"
    
    def _generate_ai_hint(self, problem_content: str, user_input: str, solution_analysis: Dict[str, Any]) -> str:
        """AIによる個別ヒント生成"""
        approach = solution_analysis.get('approach', '不明')
        progress_stage = solution_analysis.get('progress_stage', '不明')
        correctness = solution_analysis.get('correctness', 'unknown')
        feedback = solution_analysis.get('feedback', '')
        
        prompt = f"""
数学問題の個別指導をしてください：

【問題】
{problem_content}

【学習者の回答】
{user_input}

【分析結果】
- 解法アプローチ: {approach}
- 進捗段階: {progress_stage}
- 正誤判定: {correctness}
- フィードバック: {feedback}

学習者の自己解決力を育むため、以下のルールでヒントを提供してください：
1. 答えを直接教えるのではなく、考え方の方向性を示す
2. 学習者が既に理解していることを認めて励ます
3. 次の一歩を踏み出すための具体的な行動を提案する
4. 簡潔で分かりやすい表現を使う（100文字以内）

建設的なヒント:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"ヒント生成エラー: {str(e)}")
            return "もう一度問題を確認して、一歩ずつ解き進めてみましょう。"
    
    def _check_for_errors(self, user_input: str, solution_analysis: Dict[str, Any]) -> str:
        """誤りの検出とヒント"""
        # 基本的な数学的誤りをチェック
        errors = []
        
        # 符号の誤りチェック
        if '+-' in user_input or '-+' in user_input:
            errors.append("符号の計算を確認してみてください。")
        
        # 括弧のチェック
        open_brackets = user_input.count('(')
        close_brackets = user_input.count(')')
        if open_brackets != close_brackets:
            errors.append("括弧の開閉を確認してください。")
        
        if errors:
            return "計算を確認してみましょう：" + " ".join(errors)
        
        return None
    
    def _get_encouraging_hint(self, user_input: str) -> str:
        """励ましのヒント（レベル1）"""
        if len(user_input.strip()) < 10:
            return "良いスタートです！もう少し詳しく書いてみましょう。どんな方法で解こうと思いますか？"
        else:
            return "いい感じで進んでいますね！この調子で続けてみてください。"
    
    def _get_directional_hint(self, problem_content: str, user_input: str) -> str:
        """方向性のヒント（レベル2）"""
        prompt = f"""
        以下の問題に対する学習者の回答に、方向性を示すヒントを提供してください：

        【問題】{problem_content}
        【学習者の回答】{user_input}

        答えは教えず、考える方向性だけを示してください。50文字以内で簡潔に。
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "もう一度問題を読み返して、使えそうな条件や公式を探してみましょう。"
    
    def _get_specific_hint(self, problem_content: str, user_input: str) -> str:
        """具体的なヒント（レベル3）"""
        prompt = f"""
        以下の問題に対する学習者の回答に、より具体的なヒントを提供してください：

        【問題】{problem_content}
        【学習者の回答】{user_input}

        次に取るべき具体的なアクションを示してください。答えは教えず、手順だけを説明してください。
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "計算を一歩ずつ確認して、使える公式や条件を整理してみましょう。"
    
    def _get_detailed_solution_hint(self, problem_content: str, user_input: str) -> str:
        """詳細な解法ヒント（レベル4+）"""
        prompt = f"""
        以下の問題に対する詳細な解法の方向性を示してください：

        【問題】{problem_content}
        【学習者の現在の回答】{user_input}

        解法の手順を段階的に示してください。ただし、最終的な数値計算は学習者に任せてください。
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "解法の全体像を整理して、各ステップを順番に進めてみましょう。分からない部分があれば、基本的な公式に戻って考えてみてください。"
