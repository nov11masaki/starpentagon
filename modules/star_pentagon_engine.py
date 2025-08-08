"""
星形五角形専用の解法推定・分析エンジン
"""

import json
import re
import os
from typing import Dict, List, Any, Tuple, Optional
import google.generativeai as genai
from PIL import Image
import io
import base64

class StarPentagonEngine:
    def __init__(self, api_key: str, dataset_path: str = "dataset"):
        """
        星形五角形専用エンジンの初期化
        
        Args:
            api_key: Gemini API キー
            dataset_path: データセットのパス
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.dataset_path = dataset_path
        
        # データセットの読み込み
        self.dataset = self._load_dataset()
        self.solution_types = self._load_solution_types()
        
        # 星形五角形の実際の12+1解法パターン（データセットベース）
        self.solution_patterns = {
            "三角形5つと内部の五角形に着目": {
                "keywords": ["三角形", "5つ", "内部", "五角形", "先端", "180度", "外角"],
                "steps": ["星形の先端にできる5つの三角形の内角の和を求める（1つあたり180度 × 5）", "五角形の外側に広がる角度（外角）を2つ分として差し引いて求める"],
                "difficulty": "初級",
                "description": "基本的な三角形分解と五角形の関係を利用"
            },
            "ブーメラン形と三角形の内角の和に着目": {
                "keywords": ["ブーメラン", "補助線", "対頂角", "三角形", "内角", "180度"],
                "steps": ["ブーメランの形に似た補助線を使って先端の角の和を求める", "その角度を対頂角の性質で1つの三角形に集めてまとめる", "その三角形の内角の和（180度）と比較して求める"],
                "difficulty": "中級",
                "description": "ブーメラン型補助線による対頂角の活用"
            },
            "ちょうちょ形と三角の内角の和に着目": {
                "keywords": ["ちょうちょ", "対称", "底角", "対頂角", "等しい", "180度"],
                "steps": ["対称なちょうちょ形をつくり、対頂角の性質から対応する底角の和が等しくなることを利用する", "その三角形の内角の和（180度）を活用して、等しい角度を使って求める"],
                "difficulty": "中級",
                "description": "対称性を利用した蝶型図形分析"
            },
            "内側の五角形の外角の和と外側の五角形の内角の和に着目": {
                "keywords": ["内側", "外側", "五角形", "外角", "内角", "540度", "360度"],
                "steps": ["外側の五角形の内角の和（540度）を求める", "内部の五角形の外角の1つが、余分な三角形の外角の和に相当する", "外側の五角形の外角の和（360度）から内側の外角分を引いて求める"],
                "difficulty": "上級",
                "description": "内外五角形の角度関係による分析"
            },
            "内側と外側の五角形の内角の和，三角形の内角の和に着目": {
                "keywords": ["内側", "外側", "五角形", "内角", "三角形", "540度", "180度"],
                "steps": ["余分な三角形5つ分の内角の和（180度 × 5）を求める", "内部の五角形の内角の和（540度）を求める", "外部の五角形の内角の和から、内部との関係で不要な角を差し引いて求める"],
                "difficulty": "上級",
                "description": "内外五角形と三角形の複合的分析"
            },
            "ブーメラン形と五角形の内角の和に着目": {
                "keywords": ["ブーメラン", "五角形", "内角", "対頂角", "移動", "3回", "540度"],
                "steps": ["5つのブーメラン形の先端角の和を文字などで表現する", "それらの角は五角形の内角として対頂角で移動する（対応させる）", "五角形の内角の和はそれらの角度を3回ずつ加えたものに等しくなる", "その合計を3で割ることで1つ分の角度を求める"],
                "difficulty": "上級",
                "description": "ブーメラン型と五角形内角の代数的関係"
            },
            "三角形の外角の和と三角形の内角の和に着目": {
                "keywords": ["三角形", "外角", "内角", "360度", "180度", "補助線"],
                "steps": ["2つの三角形の外角の和（360度）を求める", "角度が1つの三角形に集まるように補助線で構成し、内角の和（180度）との関係を使って求める"],
                "difficulty": "中級",
                "description": "三角形の外角と内角の性質利用"
            },
            "三角形5つの内角の和と五角形の内角の和に着目し,連立する": {
                "keywords": ["三角形", "5つ", "内角", "五角形", "連立", "180度", "540度"],
                "steps": ["5つの三角形の内角の和（180度 × 5）を求める", "各三角形の1つの角は五角形の内角の1つとして含まれていることを意識する", "三角形の合計から五角形の内角の和を引いたものが、求める角度を2回ずつ足したものに対応する", "その結果を2で割ることで1つ分の角度を求める"],
                "difficulty": "上級",
                "description": "三角形と五角形の角度関係を連立方程式で解決"
            },
            "三角形4つの内角の和と五角形の外角の和に着目する": {
                "keywords": ["三角形", "4つ", "内角", "五角形", "外角", "180度", "360度"],
                "steps": ["4つの三角形の内角の和（180度 × 4）を求める", "余分な部分が五角形の外角の和（360度）と一直線に並んで構成されていると見なす", "三角形の合計から余分な角度（外角）を差し引いて求める"],
                "difficulty": "上級",
                "description": "4つの三角形と五角形外角の関係分析"
            },
            "五角形の外角の和に着目する": {
                "keywords": ["五角形", "外角", "360度", "2回", "先端角"],
                "steps": ["五角形の外角の和（360度）を求める", "5つの先端角がそれぞれ2回ずつ加えられているという構造に着目する", "合計から2で割って1つ分の角度を求める"],
                "difficulty": "中級",
                "description": "五角形外角の和の性質を直接利用"
            },
            "五角形の内角の和に着目する": {
                "keywords": ["五角形", "内角", "540度", "三角形", "180度", "外角"],
                "steps": ["5つ分の三角形の内角の和（180度 × 5）を求める", "内部の五角形に相当する外角の和が1つ分含まれていることを意識する", "それが2つ分あると見なし、合計から2つ分の外角を引くことで答えを求める"],
                "difficulty": "中級",
                "description": "五角形内角の和の性質を利用"
            },
            "ブーメラン形と三角形の外角の和に着目": {
                "keywords": ["ブーメラン", "三角形", "外角", "一直線", "先端角"],
                "steps": ["ブーメラン形の先端の角の和を計算する", "ブーメラン以外の角度が三角形の外角として使われている構造を意識する", "外角が一直線上に並ぶ性質から計算して求める"],
                "difficulty": "上級",
                "description": "ブーメラン型と三角形外角の複合分析"
            },
            "その他": {
                "keywords": ["独自", "組み合わせ", "その他", "混合", "特殊"],
                "steps": ["解法を分析", "適切な手法を適用", "結果を確認"],
                "difficulty": "可変",
                "description": "上記12パターン以外の解法や複合的な手法"
            }
        }
    
    def _load_dataset(self) -> Dict:
        """データセットの読み込み"""
        try:
            with open(os.path.join(self.dataset_path, 'dataset.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"データセットファイルが見つかりません: {self.dataset_path}/dataset.json")
            return {}
    
    def _load_solution_types(self) -> Dict:
        """解法タイプの読み込み"""
        try:
            with open(os.path.join(self.dataset_path, 'solution_types.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"解法タイプファイルが見つかりません: {self.dataset_path}/solution_types.json")
            return {}
    
    def analyze_step_images(self, solution_id: str, current_step: int = None) -> Dict[str, Any]:
        """
        ステップ画像を分析して解法を推定
        
        Args:
            solution_id: 解答IDパターン（例: "solution_02_01"）
            current_step: 現在のステップ（Noneの場合は全体を分析）
            
        Returns:
            解法分析結果
        """
        if solution_id not in self.dataset:
            return {"error": "指定された解答IDが見つかりません"}
        
        steps = self.dataset[solution_id]["steps"]
        
        if current_step is None:
            # 全ステップを分析
            return self._analyze_full_solution(solution_id, steps)
        else:
            # 特定のステップまでを分析
            return self._analyze_partial_solution(solution_id, steps[:current_step + 1])
    
    def _analyze_full_solution(self, solution_id: str, steps: List[str]) -> Dict[str, Any]:
        """完全な解答の分析"""
        # 最終的な画像を分析
        final_image_path = f"dataset/final/final_{solution_id.split('_')[1]}_{solution_id.split('_')[2]}.jpeg"
        
        # 解法パターンの推定
        estimated_pattern = self._estimate_solution_pattern(steps)
        
        # 進捗評価
        progress = {
            "completion_rate": 1.0,
            "current_stage": "完了",
            "estimated_pattern": estimated_pattern,
            "total_steps": len(steps),
            "key_insights": self._extract_key_insights(estimated_pattern)
        }
        
        return {
            "solution_id": solution_id,
            "analysis_type": "complete",
            "progress": progress,
            "pattern": estimated_pattern,
            "status": "success"
        }
    
    def _analyze_partial_solution(self, solution_id: str, partial_steps: List[str]) -> Dict[str, Any]:
        """部分的な解答の分析"""
        total_steps = len(self.dataset[solution_id]["steps"])
        current_step_count = len(partial_steps)
        
        # 現在の進捗を推定
        estimated_pattern = self._estimate_solution_pattern(partial_steps)
        current_stage = self._determine_current_stage(partial_steps, estimated_pattern)
        
        progress = {
            "completion_rate": current_step_count / total_steps,
            "current_stage": current_stage,
            "estimated_pattern": estimated_pattern,
            "completed_steps": current_step_count,
            "total_steps": total_steps,
            "next_suggestion": self._get_next_step_suggestion(estimated_pattern, current_stage)
        }
        
        return {
            "solution_id": solution_id,
            "analysis_type": "partial",
            "progress": progress,
            "pattern": estimated_pattern,
            "status": "success"
        }
    
    def _estimate_solution_pattern(self, steps: List[str]) -> str:
        """ステップ数と解答IDから解法パターンを推定（実際のパターン名使用）"""
        step_count = len(steps)
        
        # ステップ数による大まかな分類（実際のデータセットパターン名）
        if step_count < 15:
            return "三角形5つと内部の五角形に着目"
        elif step_count < 25:
            return "ブーメラン形と三角形の内角の和に着目"
        elif step_count < 35:
            return "ちょうちょ形と三角の内角の和に着目"
        elif step_count < 45:
            return "五角形の外角の和に着目する"
        elif step_count < 55:
            return "五角形の内角の和に着目する"
        elif step_count < 65:
            return "内側の五角形の外角の和と外側の五角形の内角の和に着目"
        else:
            return "三角形5つの内角の和と五角形の内角の和に着目し,連立する"
    
    def _determine_current_stage(self, steps: List[str], pattern: str) -> str:
        """現在の解答段階を判定（実際のパターンベース）"""
        step_count = len(steps)
        
        if "三角形5つと内部" in pattern:
            if step_count < 5:
                return "問題理解・図形認識"
            elif step_count < 10:
                return "三角形分解の準備"
            elif step_count < 15:
                return "角度計算"
            else:
                return "最終計算・確認"
        
        elif "ブーメラン形" in pattern:
            if step_count < 8:
                return "ブーメラン補助線の描画"
            elif step_count < 16:
                return "対頂角の関係分析"
            elif step_count < 24:
                return "三角形内角計算"
            else:
                return "結果導出・検証"
        
        elif "ちょうちょ形" in pattern:
            if step_count < 7:
                return "対称図形の構成"
            elif step_count < 14:
                return "底角の等価関係確認"
            elif step_count < 21:
                return "内角計算"
            else:
                return "答えの導出"
        
        elif "連立" in pattern:
            if step_count < 10:
                return "方程式の設定"
            elif step_count < 20:
                return "連立方程式の構築"
            elif step_count < 30:
                return "方程式の解法"
            else:
                return "解の検証・結論"
        
        else:
            # その他のパターン
            progress_ratio = step_count / 50  # 想定最大ステップ
            if progress_ratio < 0.3:
                return "初期段階・構想"
            elif progress_ratio < 0.6:
                return "計算・解法実行"
            elif progress_ratio < 0.9:
                return "検証・調整"
            else:
                return "完成・確認"
    
    def _get_next_step_suggestion(self, pattern: str, current_stage: str) -> str:
        """次のステップの提案"""
        suggestions = {
            "三角形5つと内部の五角形に着目": {
                "問題理解・図形認識": "星形を5つの三角形に分けることを考えてみましょう",
                "三角形分解の準備": "各三角形の頂点がどこにあるか確認しましょう",
                "角度計算": "1つの三角形の内角の和は180°です",
                "最終計算・確認": "5つの三角形の先端角の合計を求めましょう"
            },
            "ブーメラン形と三角形の内角の和に着目": {
                "ブーメラン補助線の描画": "ブーメランのような補助線を考えてみましょう",
                "対頂角の関係分析": "対頂角を作る線を引いてみましょう",
                "三角形内角計算": "対頂角の性質（等しい角）を見つけましょう",
                "結果導出・検証": "三角形の内角の和180°を利用しましょう"
            },
            "ちょうちょ形と三角の内角の和に着目": {
                "対称図形の構成": "ちょうちょのような対称な図形を考えてみましょう",
                "底角の等価関係確認": "対称な補助線を引いてみましょう",
                "内角計算": "対応する角の等しさを確認しましょう",
                "答えの導出": "三角形の内角の和を利用して計算しましょう"
            },
            "五角形の外角の和に着目する": {
                "問題理解・図形認識": "星形の外角に注目してみましょう",
                "計算・解法実行": "外角の和は360°になることを利用しましょう",
                "検証・調整": "各外角を特定して合計を求めましょう",
                "完成・確認": "外角から内角（先端角）を求めましょう"
            },
            "五角形の内角の和に着目する": {
                "問題理解・図形認識": "内側と外側の五角形に注目してみましょう",
                "計算・解法実行": "五角形の内角の和（540°）を思い出しましょう",
                "検証・調整": "内角と外角の関係を考えましょう",
                "完成・確認": "すべての角度関係を統合して答えを求めましょう"
            }
        }
        
        return suggestions.get(pattern, {}).get(current_stage, "次のステップを考えてみましょう")
    
    def _extract_key_insights(self, pattern: str) -> List[str]:
        """解法パターンの重要なポイント"""
        insights = {
            "三角形5つと内部の五角形に着目": [
                "星形は5つの三角形に分解できる",
                "各三角形の内角の和は180°",
                "先端角の合計は5×36°=180°"
            ],
            "ブーメラン形と三角形の内角の和に着目": [
                "対頂角の性質を利用する",
                "補助線により三角形を作る",
                "角度の移動と集約が鍵"
            ],
            "ちょうちょ形と三角の内角の和に着目": [
                "対称性を利用する",
                "等しい角の関係を見つける",
                "視覚的に分かりやすい方法"
            ],
            "五角形の外角の和に着目する": [
                "外角の和は常に360°",
                "外角から内角を求める",
                "直接的なアプローチ"
            ],
            "五角形の内角の和に着目する": [
                "五角形の内角の和は540°",
                "内角と外角の関係を利用",
                "基本的な多角形の性質"
            ],
            "内側の五角形の外角の和と外側の五角形の内角の和に着目": [
                "内外五角形の関係性",
                "複合的な角度分析",
                "高度な図形理解が必要"
            ]
        }
        
        return insights.get(pattern, [])
    
    def generate_hint(self, solution_id: str, current_step: int, difficulty_level: str = "adaptive") -> Dict[str, Any]:
        """
        現在の進捗に応じたヒント生成
        
        Args:
            solution_id: 解答ID
            current_step: 現在のステップ
            difficulty_level: ヒントの難易度 ("easy", "medium", "hard", "adaptive")
            
        Returns:
            生成されたヒント
        """
        # 現在の状況を分析
        analysis = self.analyze_step_images(solution_id, current_step)
        
        if "error" in analysis:
            return analysis
        
        pattern = analysis["progress"]["estimated_pattern"]
        current_stage = analysis["progress"]["current_stage"]
        completion_rate = analysis["progress"]["completion_rate"]
        
        # 難易度レベルの決定
        if difficulty_level == "adaptive":
            if completion_rate < 0.3:
                hint_level = "easy"
            elif completion_rate < 0.7:
                hint_level = "medium"
            else:
                hint_level = "hard"
        else:
            hint_level = difficulty_level
        
        # ヒント生成
        hint = self._generate_contextual_hint(pattern, current_stage, hint_level)
        
        return {
            "hint": hint,
            "pattern": pattern,
            "stage": current_stage,
            "completion_rate": completion_rate,
            "difficulty": hint_level,
            "next_suggestion": analysis["progress"].get("next_suggestion", ""),
            "status": "success"
        }
    
    def _generate_contextual_hint(self, pattern: str, stage: str, difficulty: str) -> str:
        """文脈に応じたヒント生成"""
        hints = {
            "三角形5つと内部の五角形に着目": {
                "easy": {
                    "問題理解・図形認識": "星形の先端は5つありますね。それぞれの先端で三角形ができそうです。",
                    "三角形分解の準備": "星形の1つの先端に注目してみましょう。そこでできる三角形を見つけられますか？",
                    "角度計算": "三角形の内角の和は何度でしたか？180度でしたね。",
                    "最終計算・確認": "5つの三角形の先端角を全て足すと答えになります。"
                },
                "medium": {
                    "問題理解・図形認識": "星形を5つの合同な三角形に分解することを考えてみましょう。",
                    "三角形分解の準備": "各三角形の先端角（求めたい角）はどれでしょうか？",
                    "角度計算": "1つの三角形で先端角をα、他の2つの角をβ、γとすると、α+β+γ=180°です。",
                    "最終計算・確認": "すべての先端角の合計は5α度になります。"
                },
                "hard": {
                    "問題理解・図形認識": "星形の幾何学的性質を利用した分解を考えてください。",
                    "三角形分解の準備": "合同な三角形への分割と、角度の対称性を考察してください。",
                    "角度計算": "三角形の内角の和定理を星形全体に適用してください。",
                    "最終計算・確認": "5つの先端角の合計から星形五角形の性質を導出してください。"
                }
            },
            "ブーメラン形と三角形の内角の和に着目": {
                "easy": {
                    "ブーメラン補助線の描画": "ブーメランのような補助線を引いてみましょう。",
                    "対頂角の関係分析": "対頂角は等しくなることを思い出してください。",
                    "三角形内角計算": "三角形の内角の和は180度です。",
                    "結果導出・検証": "計算結果を確認してみましょう。"
                }
            }
        }
        
        pattern_hints = hints.get(pattern, {})
        difficulty_hints = pattern_hints.get(difficulty, {})
        return difficulty_hints.get(stage, "現在の段階に適したヒントを考え中です...")
    
    def detect_struggle_points(self, solution_id: str, step_analysis: List[int]) -> List[Dict[str, Any]]:
        """
        学習者の躓きポイントを検出
        
        Args:
            solution_id: 解答ID
            step_analysis: ステップごとの時間分析や再試行回数
            
        Returns:
            躓きポイントの分析結果
        """
        struggle_points = []
        
        # ステップごとの分析
        for i, time_spent in enumerate(step_analysis):
            if time_spent > 60:  # 60秒以上かかった場合
                analysis = self.analyze_step_images(solution_id, i)
                pattern = analysis["progress"]["estimated_pattern"]
                stage = analysis["progress"]["current_stage"]
                
                struggle_point = {
                    "step": i,
                    "stage": stage,
                    "pattern": pattern,
                    "time_spent": time_spent,
                    "difficulty_reason": self._identify_difficulty_reason(pattern, stage),
                    "targeted_hint": self._generate_targeted_hint(pattern, stage),
                    "alternative_approach": self._suggest_alternative_approach(pattern)
                }
                struggle_points.append(struggle_point)
        
        return struggle_points
    
    def _identify_difficulty_reason(self, pattern: str, stage: str) -> str:
        """困難の理由を特定"""
        difficulty_reasons = {
            "三角形5つと内部の五角形に着目": {
                "問題理解・図形認識": "星形の構造理解が難しい",
                "三角形分解の準備": "分解方法の発想が困難",
                "角度計算": "内角の和の適用が不明確",
                "最終計算・確認": "計算ミスや統合が困難"
            },
            "ブーメラン形と三角形の内角の和に着目": {
                "ブーメラン補助線の描画": "補助線の引き方が不明",
                "対頂角の関係分析": "対頂角の性質理解が困難",
                "三角形内角計算": "角度の移動が理解困難",
                "結果導出・検証": "結果の検証方法が不明"
            }
        }
        
        return difficulty_reasons.get(pattern, {}).get(stage, "不明な困難")
    
    def _generate_targeted_hint(self, pattern: str, stage: str) -> str:
        """困難に特化したヒント"""
        return self._generate_contextual_hint(pattern, stage, "easy")
    
    def _suggest_alternative_approach(self, pattern: str) -> str:
        """代替アプローチの提案"""
        alternatives = {
            "三角形5つと内部の五角形に着目": "ブーメラン形と三角形の内角の和に着目してみませんか？補助線を使った別のアプローチです。",
            "ブーメラン形と三角形の内角の和に着目": "ちょうちょ形と三角の内角の和に着目はいかがでしょう？対称性を利用した視覚的な方法です。",
            "ちょうちょ形と三角の内角の和に着目": "三角形5つと内部の五角形に着目に戻って、シンプルに考えてみましょう。",
            "五角形の外角の和に着目する": "まずは三角形5つと内部の五角形に着目で基本を理解してから挑戦しましょう。",
            "五角形の内角の和に着目する": "三角形5つと内部の五角形に着目から始めて、段階的に理解を深めましょう。"
        }
        
        return alternatives.get(pattern, "別のアプローチを考えてみましょう。")
