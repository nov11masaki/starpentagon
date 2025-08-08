"""
手書き数式認識とLaTeX変換モジュール
Gemini Vision APIを使用して手書き数式をLaTeXに変換
"""

import base64
import io
from PIL import Image
import google.generativeai as genai
from typing import Dict, Any, Optional

class HandwritingRecognizer:
    def __init__(self, model):
        self.model = model
    
    def image_to_latex(self, image_data: str) -> Dict[str, Any]:
        """
        手書き画像をLaTeXに変換
        
        Args:
            image_data: Base64エンコードされた画像データ
            
        Returns:
            変換結果辞書
        """
        try:
            # Base64画像をPIL Imageに変換
            image = self._decode_base64_image(image_data)
            
            # Gemini Vision APIで手書き数式を認識
            latex_result = self._recognize_math_expression(image)
            
            return {
                'success': True,
                'latex': latex_result['latex'],
                'confidence': latex_result['confidence'],
                'interpretation': latex_result['interpretation'],
                'suggestions': latex_result.get('suggestions', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'手書き認識中にエラーが発生しました: {str(e)}',
                'latex': '',
                'confidence': 0.0
            }
    
    def _decode_base64_image(self, image_data: str) -> Image.Image:
        """Base64画像をPIL Imageに変換"""
        # data:image/png;base64, プレフィックスを除去
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Base64デコード
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        return image
    
    def _recognize_math_expression(self, image: Image.Image) -> Dict[str, Any]:
        """Gemini Vision APIで数式認識"""
        prompt = """
        この手書き数式画像を分析して、以下の形式でJSONレスポンスを返してください：

        {
            "latex": "認識された数式のLaTeX表記",
            "confidence": 0.0-1.0の信頼度,
            "interpretation": "数式の意味や内容の説明（日本語）",
            "suggestions": ["代替的な解釈1", "代替的な解釈2"]
        }

        注意点：
        1. LaTeX記法は正確に記述してください
        2. 日本語の説明も含めてください
        3. 不明確な部分があれば代替案も提示してください
        4. 数学記号は適切にエスケープしてください

        例：
        手書きで "x^2 + 2x + 1" が書かれている場合
        {
            "latex": "x^2 + 2x + 1",
            "confidence": 0.95,
            "interpretation": "xの2次式で、完全平方式 (x+1)^2 に因数分解できます",
            "suggestions": ["x² + 2x + 1", "(x+1)²"]
        }
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            
            # レスポンステキストからJSONを抽出
            response_text = response.text.strip()
            
            # JSONブロックを抽出（```json ... ``` で囲まれている場合）
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
            elif '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_text = response_text[start:end]
            else:
                json_text = response_text
            
            # JSONパース
            import json
            result = json.loads(json_text)
            
            # 必要なフィールドの確認
            required_fields = ['latex', 'confidence', 'interpretation']
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)
            
            return result
            
        except json.JSONDecodeError:
            # JSONパースに失敗した場合、テキストから直接LaTeXを抽出
            return self._fallback_text_extraction(response.text)
        except Exception as e:
            raise Exception(f"Gemini Vision API呼び出しエラー: {str(e)}")
    
    def _get_default_value(self, field: str) -> Any:
        """デフォルト値を取得"""
        defaults = {
            'latex': '',
            'confidence': 0.5,
            'interpretation': '数式を認識しました',
            'suggestions': []
        }
        return defaults.get(field, '')
    
    def _fallback_text_extraction(self, response_text: str) -> Dict[str, Any]:
        """フォールバック：テキストからLaTeXを抽出"""
        return {
            'latex': response_text.strip(),
            'confidence': 0.7,
            'interpretation': '手書き数式を認識しました',
            'suggestions': []
        }
    
    def validate_latex(self, latex_expression: str) -> Dict[str, Any]:
        """LaTeX式の妥当性を検証"""
        try:
            # 基本的なLaTeX構文チェック
            validation_result = self._basic_latex_validation(latex_expression)
            
            if validation_result['valid']:
                # Gemini APIでさらに詳細な検証
                detailed_validation = self._advanced_latex_validation(latex_expression)
                return detailed_validation
            else:
                return validation_result
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'LaTeX検証エラー: {str(e)}',
                'suggestions': []
            }
    
    def _basic_latex_validation(self, latex: str) -> Dict[str, Any]:
        """基本的なLaTeX構文検証"""
        errors = []
        
        # 括弧のバランスチェック
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in latex:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    errors.append(f"閉じ括弧 '{char}' に対応する開き括弧がありません")
                else:
                    last_open = stack.pop()
                    if brackets[last_open] != char:
                        errors.append(f"括弧の種類が一致しません: '{last_open}' と '{char}'")
        
        if stack:
            errors.append(f"開き括弧 {stack} に対応する閉じ括弧がありません")
        
        # 基本的な数学コマンドの存在チェック
        common_commands = ['\\frac', '\\sqrt', '\\sum', '\\int', '\\lim', '\\sin', '\\cos', '\\tan']
        used_commands = [cmd for cmd in common_commands if cmd in latex]
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'detected_commands': used_commands
        }
    
    def _advanced_latex_validation(self, latex: str) -> Dict[str, Any]:
        """Gemini APIを使用した高度なLaTeX検証"""
        prompt = f"""
        以下のLaTeX数式の妥当性を検証してください：

        {latex}

        以下の形式でJSONレスポンスを返してください：
        {{
            "valid": true/false,
            "errors": ["エラー1", "エラー2"],
            "suggestions": ["修正案1", "修正案2"],
            "interpretation": "数式の意味説明"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            import json
            
            response_text = response.text.strip()
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text
            
            return json.loads(json_text)
        except:
            return {
                'valid': True,
                'errors': [],
                'suggestions': [],
                'interpretation': 'LaTeX式は基本的に有効です'
            }

class DigitalWhiteboard:
    """デジタルホワイトボード機能"""
    
    def __init__(self, recognizer: HandwritingRecognizer):
        self.recognizer = recognizer
        self.session_history = []
    
    def process_drawing(self, drawing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        描画データを処理してLaTeXに変換
        
        Args:
            drawing_data: 描画データ（画像、ストローク情報等）
            
        Returns:
            処理結果
        """
        try:
            # 画像データから数式認識
            if 'image' in drawing_data:
                recognition_result = self.recognizer.image_to_latex(drawing_data['image'])
                
                if recognition_result['success']:
                    # セッション履歴に追加
                    self.session_history.append({
                        'timestamp': drawing_data.get('timestamp'),
                        'latex': recognition_result['latex'],
                        'confidence': recognition_result['confidence']
                    })
                    
                    return {
                        'success': True,
                        'latex': recognition_result['latex'],
                        'rendered_html': self._latex_to_html(recognition_result['latex']),
                        'confidence': recognition_result['confidence'],
                        'interpretation': recognition_result['interpretation'],
                        'session_id': len(self.session_history)
                    }
                else:
                    return recognition_result
                    
            else:
                return {
                    'success': False,
                    'error': '画像データが見つかりません'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'描画処理エラー: {str(e)}'
            }
    
    def _latex_to_html(self, latex: str) -> str:
        """LaTeXをHTML（MathJax用）に変換"""
        # MathJax用のデリミターを追加
        return f"$${latex}$$"
    
    def get_session_history(self) -> list:
        """セッション履歴を取得"""
        return self.session_history
    
    def clear_session(self):
        """セッションをクリア"""
        self.session_history = []

    def recognize_handwriting_from_base64(self, base64_data: str) -> str:
        """
        Base64エンコードされた画像から手書きテキストを認識
        
        Args:
            base64_data: Base64エンコードされた画像データ
            
        Returns:
            認識されたテキスト
        """
        try:
            # Base64データをデコード
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            import base64
            image_bytes = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return self.recognize_handwriting(image)
            
        except Exception as e:
            print(f"Base64手書き認識エラー: {e}")
            return "認識できませんでした"
