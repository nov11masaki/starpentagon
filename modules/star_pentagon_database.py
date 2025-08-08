"""
星形五角形専用問題データベース
解いている最中の段階的支援システム
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import cv2
import numpy as np

class StarPentagonDatabase:
    def __init__(self, dataset_path: str = "dataset"):
        """
        星形五角形問題データベースの初期化
        
        Args:
            dataset_path: データセットのパス
        """
        self.dataset_path = dataset_path
        self.dataset = self._load_dataset()
        self.solution_types = self._load_solution_types()
        
        # 星形五角形の基本問題を定義
        self.base_problem = {
            "id": "star_pentagon_01",
            "title": "星形五角形の内角の和",
            "description": "正五角形の各頂点を2つおきに結んでできる星形五角形において、5つの先端角の和を求めなさい。",
            "image_path": "problems/star_pentagon.png",
            "answer": 180,
            "unit": "度",
            "difficulty": "標準",
            "solution_patterns": [
                "三角形分解法",
                "ブーメラン法", 
                "蝶々法",
                "五角形分解法",
                "外角利用法"
            ]
        }
    
    def _load_dataset(self) -> Dict:
        """データセットの読み込み"""
        try:
            with open(os.path.join(self.dataset_path, 'dataset.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_solution_types(self) -> Dict:
        """解法タイプの読み込み"""
        try:
            with open(os.path.join(self.dataset_path, 'solution_types.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_problem(self) -> Dict[str, Any]:
        """星形五角形問題を取得"""
        return self.base_problem
    
    def get_solution_examples(self) -> List[Dict[str, Any]]:
        """解答例の一覧を取得（solution_types.jsonベース）"""
        try:
            # solution_types.jsonから実際の解法パターンを読み込み
            solution_types_path = os.path.join(self.dataset_path, "solution_types.json")
            if os.path.exists(solution_types_path):
                with open(solution_types_path, 'r', encoding='utf-8') as f:
                    solution_types = json.load(f)
                
                examples = []
                for pattern_id, pattern_info in solution_types.items():
                    examples.append({
                        "pattern": pattern_info["name"],
                        "description": self._format_steps_description(pattern_info["steps"]),
                        "steps": pattern_info["steps"],
                        "pattern_id": pattern_id,
                        "difficulty": self._estimate_pattern_difficulty(pattern_info),
                        "keywords": self._extract_keywords(pattern_info)
                    })
                
                return examples
            else:
                # フォールバック: データセットの解答例
                return self._get_dataset_examples()
                
        except Exception as e:
            print(f"解答例読み込みエラー: {e}")
            return self._get_dataset_examples()

    def _format_steps_description(self, steps: List[str]) -> str:
        """ステップリストから説明文を生成"""
        if len(steps) >= 2:
            return f"{steps[0]} → {steps[1]}..."
        elif len(steps) == 1:
            return steps[0]
        else:
            return "解法手順の詳細"

    def _estimate_pattern_difficulty(self, pattern_info: Dict) -> str:
        """解法パターンの難易度を推定"""
        steps_count = len(pattern_info.get("steps", []))
        name = pattern_info.get("name", "")
        
        # パターン名に基づく難易度判定
        if "連立" in name or ("外角" in name and "内角" in name):
            return "上級"
        elif "ブーメラン" in name or "ちょうちょ" in name:
            return "中級"
        elif steps_count >= 4:
            return "上級"
        elif steps_count <= 2:
            return "初級"
        else:
            return "中級"

    def _extract_keywords(self, pattern_info: Dict) -> List[str]:
        """解法パターンからキーワードを抽出"""
        name = pattern_info.get("name", "")
        steps = pattern_info.get("steps", [])
        
        keywords = []
        # 名前からキーワード抽出
        if "三角形" in name:
            keywords.extend(["三角形", "内角", "180度"])
        if "五角形" in name:
            keywords.extend(["五角形", "540度", "360度"])
        if "ブーメラン" in name:
            keywords.extend(["ブーメラン", "補助線", "対頂角"])
        if "ちょうちょ" in name:
            keywords.extend(["ちょうちょ", "対称", "底角"])
        if "外角" in name:
            keywords.extend(["外角", "360度"])
        if "内角" in name:
            keywords.extend(["内角", "和"])
        
        return list(set(keywords))  # 重複除去

    def get_solution_patterns(self) -> Dict[str, Any]:
        """解法パターンの一覧を取得"""
        patterns = {}
        
        # solution_types.jsonから実際のパターンを読み込み
        if self.solution_types:
            for pattern_id, pattern_info in self.solution_types.items():
                pattern_name = pattern_info.get("name", pattern_id)
                patterns[pattern_name] = {
                    "id": pattern_id,
                    "name": pattern_name,
                    "steps": pattern_info.get("steps", []),
                    "description": self._format_steps_description(pattern_info.get("steps", [])),
                    "difficulty": self._estimate_pattern_difficulty(pattern_info),
                    "keywords": self._extract_keywords(pattern_info)
                }
        
        # "その他"パターンを追加
        if "その他" not in patterns:
            patterns["その他"] = {
                "id": "other",
                "name": "その他",
                "steps": ["独自の解法を適用", "結果を確認"],
                "description": "上記パターン以外の解法",
                "difficulty": "可変",
                "keywords": ["独自", "その他", "混合"]
            }
        
        return patterns

    def _get_dataset_examples(self) -> List[Dict[str, Any]]:
        """データセットから解答例を取得（フォールバック）"""
        examples = []
        
        for solution_id, data in self.dataset.items():
            if solution_id.startswith("solution_"):
                # solution_02_01 -> 02_01
                parts = solution_id.split('_')
                if len(parts) >= 3:
                    example_id = f"{parts[1]}_{parts[2]}"
                    
                    examples.append({
                        "solution_id": solution_id,
                        "example_id": example_id,
                        "step_count": len(data["steps"]),
                        "final_image": f"dataset/final/final_{example_id}.jpeg",
                        "steps_images": [f"dataset/steps/{step}" for step in data["steps"]],
                        "estimated_pattern": self._estimate_pattern_from_steps(len(data["steps"])),
                        "difficulty_level": self._estimate_difficulty(len(data["steps"]))
                    })
        
        return sorted(examples, key=lambda x: x["step_count"])
    
    def _estimate_pattern_from_steps(self, step_count: int) -> str:
        """ステップ数から解法パターンを推定（実際のパターン名使用）"""
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
    
    def _estimate_difficulty(self, step_count: int) -> str:
        """ステップ数から難易度を推定"""
        if step_count < 25:
            return "初級"
        elif step_count < 55:
            return "中級"
        else:
            return "上級"
    
    def get_step_sequence(self, solution_id: str) -> Optional[List[str]]:
        """指定された解答のステップシーケンスを取得"""
        if solution_id in self.dataset:
            return self.dataset[solution_id]["steps"]
        return None
    
    def get_solution_type_info(self, type_id: str) -> Optional[Dict[str, Any]]:
        """解法タイプの詳細情報を取得"""
        return self.solution_types.get(type_id, None)
    
    def track_student_progress(self, session_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        学習者の進捗を追跡
        
        Args:
            session_id: セッションID
            step_data: ステップデータ（画像、時間、解法など）
            
        Returns:
            進捗分析結果
        """
        progress_file = f"progress/{session_id}.json"
        
        # 既存の進捗データを読み込み
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
        else:
            progress = {
                "session_id": session_id,
                "start_time": step_data.get("timestamp"),
                "steps": [],
                "current_pattern": None,
                "struggle_points": [],
                "hints_used": []
            }
        
        # 新しいステップを追加
        progress["steps"].append(step_data)
        
        # 現在の解法パターンを更新
        current_pattern = self._analyze_current_pattern(progress["steps"])
        progress["current_pattern"] = current_pattern
        
        # 躓きポイントの検出
        if self._detect_struggle(step_data):
            struggle_point = {
                "step_number": len(progress["steps"]),
                "timestamp": step_data.get("timestamp"),
                "pattern": current_pattern,
                "difficulty_type": self._identify_struggle_type(step_data),
                "suggested_help": self._suggest_help(current_pattern, step_data)
            }
            progress["struggle_points"].append(struggle_point)
        
        # 進捗データを保存
        os.makedirs("progress", exist_ok=True)
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        return {
            "current_step": len(progress["steps"]),
            "estimated_pattern": current_pattern,
            "completion_rate": self._calculate_completion_rate(progress["steps"], current_pattern),
            "recent_struggle": len(progress["struggle_points"]) > 0 and 
                             progress["struggle_points"][-1]["step_number"] == len(progress["steps"]),
            "suggested_action": self._suggest_next_action(progress),
            "status": "success"
        }
    
    def _analyze_current_pattern(self, steps: List[Dict[str, Any]]) -> str:
        """現在のステップから解法パターンを分析"""
        step_count = len(steps)
        
        # 時間の傾向から分析
        if step_count > 3:
            recent_times = [step.get("time_spent", 30) for step in steps[-3:]]
            avg_time = sum(recent_times) / len(recent_times)
            
            if avg_time < 20:  # 早い進行
                return "三角形分解法"
            elif avg_time < 40:  # 中程度
                if step_count < 30:
                    return "ブーメラン法"
                else:
                    return "蝶々法"
            else:  # 慎重な進行
                if step_count > 50:
                    return "外角利用法"
                else:
                    return "五角形分解法"
        
        # デフォルトの推定
        return self._estimate_pattern_from_steps(step_count)
    
    def _detect_struggle(self, step_data: Dict[str, Any]) -> bool:
        """躓きを検出"""
        time_spent = step_data.get("time_spent", 0)
        retry_count = step_data.get("retry_count", 0)
        
        return time_spent > 60 or retry_count > 2
    
    def _identify_struggle_type(self, step_data: Dict[str, Any]) -> str:
        """躓きの種類を特定"""
        time_spent = step_data.get("time_spent", 0)
        retry_count = step_data.get("retry_count", 0)
        user_input = step_data.get("user_input", "")
        
        if retry_count > 2:
            return "conceptual_difficulty"  # 概念的困難
        elif time_spent > 120:
            return "decision_paralysis"  # 判断麻痺
        elif len(user_input) < 10:
            return "lack_of_direction"  # 方向性の欠如
        else:
            return "calculation_struggle"  # 計算困難
    
    def _suggest_help(self, pattern: str, step_data: Dict[str, Any]) -> str:
        """困っている学習者への支援提案"""
        struggle_type = self._identify_struggle_type(step_data)
        
        help_suggestions = {
            "conceptual_difficulty": f"{pattern}の基本概念を確認しましょう。別のアプローチも考えてみませんか？",
            "decision_paralysis": "一歩ずつ進めましょう。まず図形の基本的な性質から考えてみてください。",
            "lack_of_direction": f"{pattern}では、まず補助線を引くことから始めましょう。",
            "calculation_struggle": "計算に集中しましょう。三角形の内角の和（180°）を思い出してください。"
        }
        
        return help_suggestions.get(struggle_type, "ヒントが必要でしたら「ヒント」ボタンを押してください。")
    
    def _calculate_completion_rate(self, steps: List[Dict[str, Any]], pattern: str) -> float:
        """完了率を計算"""
        step_count = len(steps)
        
        # パターンごとの平均ステップ数
        average_steps = {
            "三角形分解法": 15,
            "ブーメラン法": 30,
            "蝶々法": 45,
            "五角形分解法": 65,
            "外角利用法": 85
        }
        
        expected = average_steps.get(pattern, 40)
        return min(step_count / expected, 1.0)
    
    def _suggest_next_action(self, progress: Dict[str, Any]) -> str:
        """次のアクションを提案"""
        current_pattern = progress["current_pattern"]
        step_count = len(progress["steps"])
        recent_struggle = len(progress["struggle_points"]) > 0
        
        if recent_struggle:
            return "hint_request"  # ヒントを提案
        elif step_count < 5:
            return "continue_exploration"  # 探索を継続
        elif step_count > 60:
            return "consider_simplification"  # 簡略化を検討
        else:
            return "continue_current_approach"  # 現在のアプローチを継続
    
    def get_adaptive_hint_sequence(self, session_id: str) -> List[Dict[str, Any]]:
        """
        適応的ヒントシーケンスを生成
        学習者の進捗に応じて段階的にヒントを提供
        """
        progress_file = f"progress/{session_id}.json"
        
        if not os.path.exists(progress_file):
            return [{"error": "セッションが見つかりません"}]
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        current_pattern = progress["current_pattern"]
        step_count = len(progress["steps"])
        hints_used = len(progress["hints_used"])
        
        # ヒントレベルの決定
        if hints_used == 0:
            hint_level = "gentle"
        elif hints_used < 3:
            hint_level = "moderate"
        else:
            hint_level = "direct"
        
        # パターンごとのヒントシーケンス
        hint_sequences = {
            "三角形分解法": {
                "gentle": ["星形には5つの先端がありますね", "三角形を作ることができそうです"],
                "moderate": ["5つの三角形に分解してみましょう", "各三角形の内角の和は180°です"],
                "direct": ["星形を5つの三角形に分け、各先端角をαとすると5α=180°です"]
            },
            "ブーメラン法": {
                "gentle": ["補助線を引くとブーメランのような形ができます", "対頂角に注目してみてください"],
                "moderate": ["ブーメラン形の補助線を引いて対頂角を利用しましょう", "角度を1つの三角形に集めてみます"],
                "direct": ["補助線により対頂角を利用し、先端角を三角形の内角として180°で計算できます"]
            }
            # 他のパターンも同様に定義
        }
        
        return hint_sequences.get(current_pattern, {}).get(hint_level, ["現在の進捗に適したヒントを準備中です"])
    
    def analyze_image_progression(self, image_sequence: List[str]) -> Dict[str, Any]:
        """
        画像シーケンスから解法の進行を分析
        
        Args:
            image_sequence: 画像ファイルパスのリスト
            
        Returns:
            進行分析結果
        """
        if not image_sequence:
            return {"error": "画像が提供されていません"}
        
        analysis = {
            "total_steps": len(image_sequence),
            "progression_stages": [],
            "detected_patterns": [],
            "key_moments": [],
            "estimated_solution_type": None
        }
        
        # 画像シーケンスから特徴抽出
        for i, image_path in enumerate(image_sequence):
            stage_analysis = self._analyze_single_step(image_path, i)
            analysis["progression_stages"].append(stage_analysis)
            
            # キーとなる瞬間を検出
            if stage_analysis.get("is_key_moment", False):
                analysis["key_moments"].append({
                    "step": i,
                    "description": stage_analysis["description"],
                    "significance": stage_analysis["significance"]
                })
        
        # 全体的な解法パターンを推定
        analysis["estimated_solution_type"] = self._estimate_overall_pattern(analysis["progression_stages"])
        
        return analysis
    
    def _analyze_single_step(self, image_path: str, step_index: int) -> Dict[str, Any]:
        """単一ステップの画像分析"""
        # 実際の画像分析はここで実装
        # 現在は基本的な情報を返す
        return {
            "step_index": step_index,
            "image_path": image_path,
            "estimated_action": "図形操作",
            "complexity_level": min(step_index // 10 + 1, 5),
            "is_key_moment": step_index % 15 == 0,  # 15ステップごとにキーとなる瞬間と仮定
            "description": f"ステップ {step_index + 1}: 解法進行中",
            "significance": "progress" if step_index % 15 != 0 else "milestone"
        }
    
    def _estimate_overall_pattern(self, stages: List[Dict[str, Any]]) -> str:
        """全体的な解法パターンの推定"""
        total_steps = len(stages)
        return self._estimate_pattern_from_steps(total_steps)
