"""
星形五角形専用AI数学チューター Webアプリケーション
リアルタイム解法推定・支援システム
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from modules.solution_engine import SolutionEngine
from modules.hint_generator import HintGenerator
from modules.problem_database import ProblemDatabase
from modules.handwriting_recognizer import HandwritingRecognizer, DigitalWhiteboard
from modules.star_pentagon_engine import StarPentagonEngine
from modules.star_pentagon_database import StarPentagonDatabase
from modules.realtime_support import RealTimeSupportSystem

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)

# Gemini APIの設定
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 従来のアプリケーションコンポーネント（後方互換性のため）
solution_engine = SolutionEngine(model)
hint_generator = HintGenerator(model)
problem_db = ProblemDatabase()
handwriting_recognizer = HandwritingRecognizer(model)
digital_whiteboard = DigitalWhiteboard(handwriting_recognizer)

# 星形五角形専用システム
star_engine = StarPentagonEngine(os.getenv('GEMINI_API_KEY'))
star_database = StarPentagonDatabase()
realtime_support = RealTimeSupportSystem(os.getenv('GEMINI_API_KEY'))

# アクティブセッション管理
active_sessions = {}

@app.route('/')
def index():
    """メインページ - 星形五角形専用チューター"""
    timestamp = str(int(time.time()))
    return render_template('star_pentagon_index.html', timestamp=timestamp)

# 星形五角形専用エンドポイント

@app.route('/api/star/start_session', methods=['POST'])
def start_star_session():
    """星形五角形学習セッション開始"""
    try:
        data = request.json or {}
        session_id = str(uuid.uuid4())
        
        # ユーザー設定
        user_config = {
            "support_level": data.get("support_level", "adaptive"),
            "difficulty": data.get("difficulty", "standard"),
            "hint_frequency": data.get("hint_frequency", "moderate")
        }
        
        # セッション開始
        result = realtime_support.start_session(session_id, user_config)
        
        # アクティブセッションに追加
        active_sessions[session_id] = {
            "start_time": datetime.now().isoformat(),
            "config": user_config
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'セッション開始エラー: {str(e)}'}), 500

@app.route('/api/star/update_step', methods=['POST'])
def update_star_step():
    """ステップ更新とリアルタイム分析"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'セッションが見つかりません'}), 400
        
        # ステップデータの準備
        step_data = {
            "user_input": data.get("user_input", ""),
            "image_data": data.get("image_data"),
            "time_spent": data.get("time_spent", 30),
            "retry_count": data.get("retry_count", 0),
            "action_type": data.get("action_type", "input")
        }
        
        # リアルタイム分析
        result = realtime_support.update_step(session_id, step_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'ステップ更新エラー: {str(e)}'}), 500

@app.route('/api/star/get_hint', methods=['POST'])
def get_star_hint():
    """星形五角形専用ヒント生成"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'セッションが見つかりません'}), 400
        
        # 適応的ヒントシーケンス取得
        hints = star_database.get_adaptive_hint_sequence(session_id)
        
        return jsonify({
            'hints': hints,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'ヒント生成エラー: {str(e)}'}), 500

@app.route('/api/star/solution_examples', methods=['GET'])
def get_solution_examples():
    """解答例の取得"""
    try:
        examples = star_database.get_solution_examples()
        return jsonify({
            'examples': examples,
            'total_count': len(examples),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'解答例取得エラー: {str(e)}'}), 500

@app.route('/api/star/analyze_progression', methods=['POST'])
def analyze_progression():
    """解法進行の分析"""
    try:
        data = request.json
        solution_id = data.get('solution_id')
        current_step = data.get('current_step')
        
        # 解法進行の分析
        analysis = star_engine.analyze_step_images(solution_id, current_step)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'進行分析エラー: {str(e)}'}), 500

@app.route('/api/star/get_struggle_support', methods=['POST'])
def get_struggle_support():
    """躓き検出と支援"""
    try:
        data = request.json
        session_id = data.get('session_id')
        struggle_data = data.get('struggle_indicators', [])
        
        # 躓きポイントの分析
        support_suggestions = star_engine.detect_struggle_points(session_id, struggle_data)
        
        return jsonify({
            'support_suggestions': support_suggestions,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'支援生成エラー: {str(e)}'}), 500

@app.route('/api/star/end_session', methods=['POST'])
def end_star_session():
    """セッション終了"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id in active_sessions:
            # セッション終了
            result = realtime_support.end_session(session_id)
            
            # アクティブセッションから削除
            del active_sessions[session_id]
            
            return jsonify(result)
        else:
            return jsonify({'error': 'セッションが見つかりません'}), 400
            
    except Exception as e:
        return jsonify({'error': f'セッション終了エラー: {str(e)}'}), 500

# ホワイトボード機能
@app.route('/api/star/whiteboard/stroke', methods=['POST'])
def add_whiteboard_stroke():
    """ホワイトボードストローク追加"""
    try:
        data = request.json
        session_id = data.get('session_id')
        stroke_data = data.get('stroke_data')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'セッションが見つかりません'}), 400
        
        # ストロークデータを処理
        digital_whiteboard.add_stroke(session_id, stroke_data)
        
        # リアルタイム手書き認識
        if data.get('auto_recognize', False):
            canvas_data = data.get('canvas_data')
            if canvas_data:
                recognized_text = handwriting_recognizer.recognize_handwriting_from_base64(canvas_data)
                
                # 認識結果を解法分析に送信
                step_data = {
                    "user_input": recognized_text,
                    "image_data": canvas_data,
                    "time_spent": data.get("time_spent", 30),
                    "action_type": "handwriting"
                }
                
                analysis_result = realtime_support.update_step(session_id, step_data)
                
                return jsonify({
                    'recognized_text': recognized_text,
                    'analysis': analysis_result,
                    'status': 'success'
                })
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': f'ホワイトボードエラー: {str(e)}'}), 500

@app.route('/api/star/whiteboard/recognize', methods=['POST'])
def recognize_whiteboard():
    """ホワイトボード手書き認識"""
    try:
        data = request.json
        session_id = data.get('session_id')
        canvas_data = data.get('canvas_data')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': 'セッションが見つかりません'}), 400
        
        if not canvas_data:
            return jsonify({'error': 'キャンバスデータが必要です'}), 400
        
        # 手書き認識実行
        recognized_text = handwriting_recognizer.recognize_handwriting_from_base64(canvas_data)
        
        # 解法分析
        step_data = {
            "user_input": recognized_text,
            "image_data": canvas_data,
            "time_spent": data.get("time_spent", 60),
            "action_type": "handwriting_analysis"
        }
        
        analysis_result = realtime_support.update_step(session_id, step_data)
        
        return jsonify({
            'recognized_text': recognized_text,
            'analysis': analysis_result,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'認識エラー: {str(e)}'}), 500

@app.route('/api/star/whiteboard/clear', methods=['POST'])
def clear_whiteboard():
    """ホワイトボードクリア"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id in active_sessions:
            digital_whiteboard.clear_session(session_id)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'セッションが見つかりません'}), 400
            
    except Exception as e:
        return jsonify({'error': f'クリアエラー: {str(e)}'}), 500

# 静的ファイル配信（画像など）
@app.route('/dataset/<path:filename>')
def dataset_files(filename):
    """データセット画像の配信"""
    return send_from_directory('dataset', filename)

# 従来のエンドポイント（後方互換性のため）

@app.route('/api/problems')
def get_problems():
    """問題リストの取得（従来版）"""
    problems = problem_db.get_all_problems()
    return jsonify(problems)

@app.route('/api/problem/<int:problem_id>')
def get_problem(problem_id):
    """特定の問題の取得（従来版）"""
    problem = problem_db.get_problem(problem_id)
    if problem:
        return jsonify(problem)
    return jsonify({'error': '問題が見つかりません'}), 404

@app.route('/api/problems/subject/<subject>')
def get_problems_by_subject(subject):
    """教科別問題の取得"""
    problems = problem_db.get_problems_by_subject(subject)
    return jsonify(problems)

@app.route('/api/problems/difficulty/<difficulty>')
def get_problems_by_difficulty(difficulty):
    """難易度別問題の取得"""
    problems = problem_db.get_problems_by_difficulty(difficulty)
    return jsonify(problems)

@app.route('/api/check-thinking', methods=['POST'])
def check_thinking():
    """思考チェック機能"""
    data = request.json
    problem_id = data.get('problem_id')
    user_input = data.get('user_input')
    
    if not problem_id or not user_input:
        return jsonify({'error': '必要な情報が不足しています'}), 400
    
    try:
        # 問題情報の取得
        problem = problem_db.get_problem(problem_id)
        if not problem:
            return jsonify({'error': '問題が見つかりません'}), 404
        
        # 解法推定
        solution_analysis = solution_engine.analyze_solution(
            problem['content'], 
            user_input
        )
        
        # ヒント生成
        hints = hint_generator.generate_hints(
            problem['content'],
            user_input,
            solution_analysis
        )
        
        return jsonify({
            'solution_analysis': solution_analysis,
            'hints': hints,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/get-hint', methods=['POST'])
def get_hint():
    """段階的ヒントの取得"""
    data = request.json
    problem_id = data.get('problem_id')
    user_input = data.get('user_input')
    hint_level = data.get('hint_level', 1)
    
    try:
        problem = problem_db.get_problem(problem_id)
        if not problem:
            return jsonify({'error': '問題が見つかりません'}), 404
        
        hint = hint_generator.get_progressive_hint(
            problem['content'],
            user_input,
            hint_level
        )
        
        return jsonify({
            'hint': hint,
            'hint_level': hint_level,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'ヒント生成中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/recognize_handwriting', methods=['POST'])
def recognize_handwriting_js():
    """手書き数式認識（JavaScript用）"""
    data = request.json
    image_data = data.get('image_data')
    
    if not image_data:
        return jsonify({'error': '画像データが必要です', 'success': False}), 400
    
    try:
        # まずは簡単なテスト応答を返す
        if not hasattr(handwriting_recognizer, 'image_to_latex'):
            # モジュールが正しく実装されていない場合のフォールバック
            return jsonify({
                'success': True,
                'latex': 'x^2 + 2x + 1',
                'confidence': 0.8,
                'interpretation': 'テスト用の認識結果です',
                'suggestions': []
            })
        
        # 手書き画像をLaTeXに変換
        recognition_result = handwriting_recognizer.image_to_latex(image_data)
        
        return jsonify(recognition_result)
            
    except Exception as e:
        print(f"手書き認識エラー: {str(e)}")  # デバッグ用
        return jsonify({
            'error': f'手書き認識中にエラーが発生しました: {str(e)}', 
            'success': False
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_thinking():
    """思考プロセス分析"""
    data = request.json
    problem_id = data.get('problem_id')
    user_input = data.get('user_input')
    
    if not problem_id or not user_input:
        return jsonify({'error': '必要な情報が不足しています'}), 400
    
    try:
        # 問題情報の取得
        problem = problem_db.get_problem(problem_id)
        if not problem:
            return jsonify({'error': '問題が見つかりません'}), 404
        
        # 解法推定
        solution_analysis = solution_engine.analyze_solution(
            problem['content'], 
            user_input
        )
        
        return jsonify({
            'approach': solution_analysis.get('approach', '解法を分析中'),
            'progress_stage': solution_analysis.get('progress_stage', '初期段階'),
            'feedback': solution_analysis.get('feedback', 'よい方向で進んでいます'),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/hint', methods=['POST'])
def get_hint_js():
    """ヒント生成（JavaScript用）"""
    data = request.json
    problem_id = data.get('problem_id')
    current_analysis = data.get('current_analysis')
    hint_level = data.get('hint_level', 1)
    
    try:
        problem = problem_db.get_problem(problem_id)
        if not problem:
            return jsonify({'error': '問題が見つかりません'}), 404
        
        # current_analysisから学習者の入力を取得
        user_input = ''
        if current_analysis:
            user_input = current_analysis.get('user_input', '')
        
        hint_content = hint_generator.get_progressive_hint(
            problem['content'],
            user_input,
            hint_level
        )
        
        return jsonify({
            'type': f'レベル{hint_level}ヒント',
            'content': hint_content,
            'hint_level': hint_level,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'ヒント生成中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/recognize-handwriting', methods=['POST'])
def recognize_handwriting():
    """手書き数式認識"""
    data = request.json
    image_data = data.get('image')
    timestamp = data.get('timestamp')
    
    if not image_data:
        return jsonify({'error': '画像データが必要です'}), 400
    
    try:
        # 手書き画像をLaTeXに変換
        recognition_result = handwriting_recognizer.image_to_latex(image_data)
        
        if recognition_result['success']:
            # デジタルホワイトボードで処理
            drawing_data = {
                'image': image_data,
                'timestamp': timestamp
            }
            
            whiteboard_result = digital_whiteboard.process_drawing(drawing_data)
            
            return jsonify(whiteboard_result)
        else:
            return jsonify(recognition_result), 400
            
    except Exception as e:
        return jsonify({'error': f'手書き認識中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/validate-latex', methods=['POST'])
def validate_latex():
    """LaTeX式の検証"""
    data = request.json
    latex_expression = data.get('latex')
    
    if not latex_expression:
        return jsonify({'error': 'LaTeX式が必要です'}), 400
    
    try:
        validation_result = handwriting_recognizer.validate_latex(latex_expression)
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({'error': f'LaTeX検証中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/whiteboard/history')
def get_whiteboard_history():
    """ホワイトボードセッション履歴の取得"""
    try:
        history = digital_whiteboard.get_session_history()
        return jsonify({
            'history': history,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': f'履歴取得中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/whiteboard/clear', methods=['POST'])
def clear_whiteboard_session():
    """ホワイトボードセッションのクリア"""
    try:
        digital_whiteboard.clear_session()
        return jsonify({
            'message': 'セッションをクリアしました',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': f'セッションクリア中にエラーが発生しました: {str(e)}'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))  # デフォルトを5002に変更
    app.run(debug=True, host='0.0.0.0', port=port)
