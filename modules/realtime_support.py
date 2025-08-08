"""
リアルタイム解法推定・支援システム
解いている最中に裏で解法を推定し、躓いた時に適切な支援を提供
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Callable
import threading
from datetime import datetime
import google.generativeai as genai
from .star_pentagon_engine import StarPentagonEngine
from .star_pentagon_database import StarPentagonDatabase

class RealTimeSupportSystem:
    def __init__(self, api_key: str, dataset_path: str = "dataset"):
        """
        リアルタイム支援システムの初期化
        
        Args:
            api_key: Gemini API キー
            dataset_path: データセットのパス
        """
        self.engine = StarPentagonEngine(api_key, dataset_path)
        self.database = StarPentagonDatabase(dataset_path)
        
        # 現在のセッション管理
        self.active_sessions = {}
        self.support_callbacks = {}
        
        # 支援システムの設定
        self.support_config = {
            "struggle_detection_threshold": 60,  # 60秒で躓き検出
            "hint_cooldown": 30,  # ヒント間のクールダウン30秒
            "max_consecutive_hints": 3,  # 連続ヒントの最大数
            "pattern_confidence_threshold": 0.7,  # 解法パターン確信度
            "intervention_modes": ["hint", "alternative_method", "step_back"]
        }
    
    def start_session(self, session_id: str, user_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        新しい学習セッションを開始
        
        Args:
            session_id: セッションID
            user_config: ユーザー設定（難易度、支援レベルなど）
            
        Returns:
            セッション情報
        """
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "user_config": user_config or {},
            "current_step": 0,
            "steps_history": [],
            "estimated_pattern": None,
            "confidence_level": 0.0,
            "last_hint_time": 0,
            "hint_count": 0,
            "struggle_indicators": [],
            "intervention_history": [],
            "status": "active"
        }
        
        self.active_sessions[session_id] = session_data
        
        # バックグラウンド監視を開始
        self._start_background_monitoring(session_id)
        
        return {
            "session_id": session_id,
            "status": "started",
            "problem": self.database.get_problem(),
            "support_level": user_config.get("support_level", "adaptive"),
            "message": "星形五角形の問題を開始します。解法を進めてください。"
        }
    
    def update_step(self, session_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ステップ更新と分析
        
        Args:
            session_id: セッションID
            step_data: ステップデータ（画像、テキスト、時間など）
            
        Returns:
            分析結果と支援情報
        """
        if session_id not in self.active_sessions:
            return {"error": "セッションが見つかりません"}
        
        session = self.active_sessions[session_id]
        
        # ステップデータを追加
        step_data["timestamp"] = datetime.now().isoformat()
        step_data["step_number"] = session["current_step"] + 1
        session["steps_history"].append(step_data)
        session["current_step"] += 1
        
        # 解法パターンの推定
        pattern_analysis = self._analyze_solution_pattern(session["steps_history"])
        session["estimated_pattern"] = pattern_analysis["pattern"]
        session["confidence_level"] = pattern_analysis["confidence"]
        
        # 躓き検出
        struggle_detected = self._detect_struggle(step_data, session)
        
        # 支援の判定
        support_action = None
        if struggle_detected:
            support_action = self._determine_support_action(session)
        
        # データベースに進捗を記録
        progress_result = self.database.track_student_progress(session_id, step_data)
        
        response = {
            "step_number": session["current_step"],
            "estimated_pattern": session["estimated_pattern"],
            "confidence": session["confidence_level"],
            "progress_rate": progress_result.get("completion_rate", 0),
            "struggle_detected": struggle_detected,
            "support_action": support_action,
            "next_suggestion": progress_result.get("suggested_action"),
            "status": "success"
        }
        
        # 支援アクションがある場合は実行
        if support_action:
            support_result = self._execute_support_action(session_id, support_action)
            response["support_message"] = support_result
        
        return response
    
    def _analyze_solution_pattern(self, steps_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解法パターンの分析"""
        step_count = len(steps_history)
        
        if step_count < 3:
            return {"pattern": "初期段階", "confidence": 0.3}
        
        # 時間パターンの分析
        recent_times = [step.get("time_spent", 30) for step in steps_history[-5:]]
        avg_time = sum(recent_times) / len(recent_times)
        
        # 入力パターンの分析
        input_complexity = self._analyze_input_complexity(steps_history)
        
        # パターン推定
        if avg_time < 25 and input_complexity < 0.5:
            pattern = "三角形分解法"
            confidence = 0.8
        elif avg_time < 45 and step_count < 35:
            pattern = "ブーメラン法"
            confidence = 0.7
        elif step_count > 30 and input_complexity > 0.6:
            if step_count < 60:
                pattern = "蝶々法"
            else:
                pattern = "五角形分解法"
            confidence = 0.6
        else:
            pattern = "外角利用法"
            confidence = 0.5
        
        return {"pattern": pattern, "confidence": confidence}
    
    def _analyze_input_complexity(self, steps_history: List[Dict[str, Any]]) -> float:
        """入力の複雑度を分析"""
        if not steps_history:
            return 0.0
        
        complexity_indicators = []
        
        for step in steps_history[-5:]:  # 直近5ステップを分析
            user_input = step.get("user_input", "")
            
            # テキストの長さ
            text_complexity = min(len(user_input) / 100, 1.0)
            
            # 数学記号の使用
            math_symbols = ["∠", "°", "α", "β", "γ", "△", "∵", "∴"]
            symbol_usage = sum(1 for symbol in math_symbols if symbol in user_input) / len(math_symbols)
            
            # 計算の存在
            has_calculation = any(op in user_input for op in ["+", "-", "×", "÷", "="])
            
            step_complexity = (text_complexity + symbol_usage + (0.3 if has_calculation else 0)) / 2.3
            complexity_indicators.append(step_complexity)
        
        return sum(complexity_indicators) / len(complexity_indicators) if complexity_indicators else 0.0
    
    def _detect_struggle(self, step_data: Dict[str, Any], session: Dict[str, Any]) -> bool:
        """躓きの検出"""
        time_spent = step_data.get("time_spent", 0)
        retry_count = step_data.get("retry_count", 0)
        
        # 時間による検出
        time_struggle = time_spent > self.support_config["struggle_detection_threshold"]
        
        # 再試行による検出
        retry_struggle = retry_count > 2
        
        # パターンからの逸脱による検出
        pattern_deviation = self._detect_pattern_deviation(session)
        
        # 入力の停滞による検出
        input_stagnation = self._detect_input_stagnation(session["steps_history"])
        
        struggle_detected = time_struggle or retry_struggle or pattern_deviation or input_stagnation
        
        if struggle_detected:
            struggle_info = {
                "timestamp": step_data["timestamp"],
                "type": "time" if time_struggle else "retry" if retry_struggle else "pattern" if pattern_deviation else "stagnation",
                "severity": self._calculate_struggle_severity(time_spent, retry_count, pattern_deviation),
                "step_number": session["current_step"]
            }
            session["struggle_indicators"].append(struggle_info)
        
        return struggle_detected
    
    def _detect_pattern_deviation(self, session: Dict[str, Any]) -> bool:
        """パターンからの逸脱を検出"""
        if session["confidence_level"] < 0.6:
            return False
        
        expected_progress = self._calculate_expected_progress(session["estimated_pattern"], session["current_step"])
        actual_progress = session["current_step"]
        
        return abs(actual_progress - expected_progress) > 10
    
    def _detect_input_stagnation(self, steps_history: List[Dict[str, Any]]) -> bool:
        """入力の停滞を検出"""
        if len(steps_history) < 3:
            return False
        
        recent_inputs = [step.get("user_input", "") for step in steps_history[-3:]]
        
        # 類似度による停滞検出
        similarity_count = 0
        for i in range(len(recent_inputs) - 1):
            if self._calculate_text_similarity(recent_inputs[i], recent_inputs[i + 1]) > 0.8:
                similarity_count += 1
        
        return similarity_count >= 2
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """テキストの類似度を計算"""
        if not text1 or not text2:
            return 0.0
        
        # 簡単な類似度計算（実際にはより詳細な計算が必要）
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_expected_progress(self, pattern: str, current_step: int) -> float:
        """期待される進捗を計算"""
        pattern_expectations = {
            "三角形分解法": current_step * 0.8,  # 早い進行
            "ブーメラン法": current_step * 1.0,  # 標準的進行
            "蝶々法": current_step * 1.2,  # やや慎重な進行
            "五角形分解法": current_step * 1.5,  # 慎重な進行
            "外角利用法": current_step * 1.7  # 最も慎重
        }
        
        return pattern_expectations.get(pattern, current_step)
    
    def _calculate_struggle_severity(self, time_spent: int, retry_count: int, pattern_deviation: bool) -> str:
        """躓きの深刻度を計算"""
        severity_score = 0
        
        if time_spent > 120:
            severity_score += 3
        elif time_spent > 60:
            severity_score += 2
        
        if retry_count > 3:
            severity_score += 2
        elif retry_count > 1:
            severity_score += 1
        
        if pattern_deviation:
            severity_score += 1
        
        if severity_score >= 4:
            return "high"
        elif severity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _determine_support_action(self, session: Dict[str, Any]) -> Optional[str]:
        """支援アクションの決定"""
        current_time = time.time()
        last_hint_time = session["last_hint_time"]
        hint_count = session["hint_count"]
        
        # クールダウンチェック
        if current_time - last_hint_time < self.support_config["hint_cooldown"]:
            return None
        
        # 最大ヒント数チェック
        if hint_count >= self.support_config["max_consecutive_hints"]:
            return "alternative_method"
        
        # 躓きの深刻度に基づく判定
        if session["struggle_indicators"]:
            latest_struggle = session["struggle_indicators"][-1]
            severity = latest_struggle["severity"]
            
            if severity == "high":
                return "step_back"
            elif severity == "medium":
                return "hint"
            else:
                return "gentle_nudge"
        
        return "hint"
    
    def _execute_support_action(self, session_id: str, action: str) -> str:
        """支援アクションの実行"""
        session = self.active_sessions[session_id]
        
        support_messages = {
            "hint": self._generate_contextual_hint(session),
            "alternative_method": self._suggest_alternative_method(session),
            "step_back": self._suggest_step_back(session),
            "gentle_nudge": self._generate_gentle_nudge(session)
        }
        
        message = support_messages.get(action, "支援を準備中です...")
        
        # 支援履歴に記録
        intervention = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "message": message,
            "step_number": session["current_step"]
        }
        session["intervention_history"].append(intervention)
        
        # ヒントの場合はカウントを更新
        if action == "hint":
            session["hint_count"] += 1
            session["last_hint_time"] = time.time()
        
        return message
    
    def _generate_contextual_hint(self, session: Dict[str, Any]) -> str:
        """文脈に応じたヒント生成"""
        pattern = session["estimated_pattern"]
        step_count = session["current_step"]
        
        # パターンと進捗に基づくヒント
        if pattern == "三角形分解法":
            if step_count < 5:
                return "星形の5つの先端に注目してみましょう。それぞれで三角形ができませんか？"
            elif step_count < 10:
                return "1つの三角形の内角の和は180°です。星形には何個の三角形がありますか？"
            else:
                return "5つの先端角をすべて足すと答えになります。"
        
        elif pattern == "ブーメラン法":
            if step_count < 10:
                return "ブーメランのような補助線を引いてみましょう。"
            elif step_count < 20:
                return "対頂角は等しいという性質を思い出してください。"
            else:
                return "角度を1つの三角形に集めて180°で計算してみましょう。"
        
        # 他のパターンも同様
        return "現在の解法を確認して、次のステップを考えてみてください。"
    
    def _suggest_alternative_method(self, session: Dict[str, Any]) -> str:
        """代替手法の提案"""
        current_pattern = session["estimated_pattern"]
        
        alternatives = {
            "三角形分解法": "ブーメラン法を試してみませんか？補助線を使った別のアプローチです。",
            "ブーメラン法": "三角形分解法はいかがでしょう？より直接的な方法です。",
            "蝶々法": "三角形分解法から始めてみましょう。基本的なアプローチです。",
            "五角形分解法": "まず三角形分解法で基本を理解してから挑戦しましょう。",
            "外角利用法": "三角形分解法で基本概念を確認してから進めましょう。"
        }
        
        return alternatives.get(current_pattern, "別のアプローチを考えてみましょう。")
    
    def _suggest_step_back(self, session: Dict[str, Any]) -> str:
        """一歩戻ることの提案"""
        return "少し立ち止まって考えてみましょう。星形五角形の基本的な性質から始めませんか？正五角形の性質を思い出してください。"
    
    def _generate_gentle_nudge(self, session: Dict[str, Any]) -> str:
        """軽いナッジの生成"""
        nudges = [
            "いい感じで進んでいますね。このまま続けてみてください。",
            "順調に解法が進んでいます。次のステップを考えてみましょう。",
            "良いアプローチです。もう少し詳しく考えてみてください。"
        ]
        return nudges[session["current_step"] % len(nudges)]
    
    def _start_background_monitoring(self, session_id: str):
        """バックグラウンド監視の開始"""
        def monitor():
            while session_id in self.active_sessions and self.active_sessions[session_id]["status"] == "active":
                time.sleep(30)  # 30秒ごとにチェック
                self._periodic_check(session_id)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _periodic_check(self, session_id: str):
        """定期的なチェック"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # 長時間の非活動チェック
        if session["steps_history"]:
            last_step_time = session["steps_history"][-1]["timestamp"]
            last_time = datetime.fromisoformat(last_step_time)
            time_diff = (datetime.now() - last_time).total_seconds()
            
            if time_diff > 300:  # 5分間非活動
                self._send_gentle_reminder(session_id)
    
    def _send_gentle_reminder(self, session_id: str):
        """軽いリマインダーの送信"""
        if session_id in self.support_callbacks:
            callback = self.support_callbacks[session_id]
            callback({
                "type": "reminder",
                "message": "問題に取り組み続けていますか？お手伝いが必要でしたらお知らせください。"
            })
    
    def register_callback(self, session_id: str, callback: Callable):
        """支援コールバックの登録"""
        self.support_callbacks[session_id] = callback
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """セッションの終了"""
        if session_id not in self.active_sessions:
            return {"error": "セッションが見つかりません"}
        
        session = self.active_sessions[session_id]
        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()
        
        # セッション統計の生成
        stats = self._generate_session_stats(session)
        
        # セッションデータを保存
        self._save_session_data(session_id, session)
        
        # アクティブセッションから削除
        del self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": "completed",
            "statistics": stats,
            "message": "セッションが完了しました。お疲れ様でした！"
        }
    
    def _generate_session_stats(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """セッション統計の生成"""
        total_time = (datetime.fromisoformat(session.get("end_time", datetime.now().isoformat())) - 
                     datetime.fromisoformat(session["start_time"])).total_seconds()
        
        return {
            "total_time": total_time,
            "total_steps": session["current_step"],
            "estimated_pattern": session["estimated_pattern"],
            "confidence_level": session["confidence_level"],
            "hints_used": session["hint_count"],
            "struggles_detected": len(session["struggle_indicators"]),
            "interventions_made": len(session["intervention_history"])
        }
    
    def _save_session_data(self, session_id: str, session: Dict[str, Any]):
        """セッションデータの保存"""
        os.makedirs("sessions", exist_ok=True)
        filename = f"sessions/{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
