"""
問題データベース
数学問題とその解法パターンを管理
"""

from typing import Dict, List, Any

class ProblemDatabase:
    def __init__(self):
        self.problems = self._initialize_problems()
    
    def _initialize_problems(self) -> Dict[int, Dict[str, Any]]:
        """初期問題データの設定"""
        return {
            # 数学I - 数と式
            1: {
                'id': 1,
                'title': '二次方程式の解の公式',
                'category': 'algebra',
                'subject': '数学I',
                'unit': '数と式',
                'difficulty': 'basic',
                'content': '''
                二次方程式 $2x^2 - 5x + 2 = 0$ を解け。
                ''',
                'solution_patterns': [
                    {'approach': '解の公式', 'steps': ['判別式の計算', '解の公式の適用']},
                    {'approach': '因数分解', 'steps': ['因数分解の試行', '解の読み取り']},
                    {'approach': '平方完成', 'steps': ['平方完成', '平方根の計算']}
                ],
                'expected_methods': ['解の公式', '因数分解', '平方完成'],
                'answer': 'x = 2, 1/2'
            },

            # 数学I - 二次関数
            2: {
                'id': 2,
                'title': '二次関数の最大値・最小値',
                'category': 'functions',
                'subject': '数学I',
                'unit': '二次関数',
                'difficulty': 'intermediate',
                'content': '''
                関数 $f(x) = x^2 - 4x + 3$ について、区間 $[0, 3]$ における最大値と最小値を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '平方完成', 'steps': ['平方完成', '頂点の確認', '区間での値の比較']},
                    {'approach': '微分利用', 'steps': ['導関数の計算', '極値の発見', '端点での値']},
                    {'approach': 'グラフ作成', 'steps': ['グラフの概形', '区間での最大最小']}
                ],
                'expected_methods': ['平方完成', '微分', 'グラフ'],
                'answer': '最大値: 3, 最小値: -1'
            },

            # 数学A - 場合の数
            3: {
                'id': 3,
                'title': '順列と組み合わせ',
                'category': 'combinatorics',
                'subject': '数学A',
                'unit': '場合の数と確率',
                'difficulty': 'basic',
                'content': '''
                5人の中から3人を選んで一列に並べる方法は何通りあるか。
                ''',
                'solution_patterns': [
                    {'approach': '順列の公式', 'steps': ['P(5,3)の計算']},
                    {'approach': '樹形図', 'steps': ['場合分けの図示', '計数']},
                    {'approach': '段階的計算', 'steps': ['1番目5通り', '2番目4通り', '3番目3通り']}
                ],
                'expected_methods': ['順列公式', '樹形図', '段階的思考'],
                'answer': '60通り'
            },

            # 数学A - 図形の性質
            4: {
                'id': 4,
                'title': '三角形の外心',
                'category': 'geometry',
                'subject': '数学A',
                'unit': '図形の性質',
                'difficulty': 'intermediate',
                'content': '''
                三角形ABCにおいて、A(1, 0), B(5, 0), C(3, 4)のとき、外心の座標を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '垂直二等分線', 'steps': ['各辺の垂直二等分線', '交点の計算']},
                    {'approach': '距離の等式', 'steps': ['外心をO(x,y)として', 'OA=OB=OCの連立']},
                    {'approach': '円の方程式', 'steps': ['3点を通る円の方程式', '中心の読み取り']}
                ],
                'expected_methods': ['垂直二等分線', '距離の等式', '円の方程式'],
                'answer': '(3, 1)'
            },

            # 数学II - 図形と方程式
            5: {
                'id': 5,
                'title': '円と直線の位置関係',
                'category': 'analytic_geometry',
                'subject': '数学II',
                'unit': '図形と方程式',
                'difficulty': 'intermediate',
                'content': '''
                円 $x^2 + y^2 - 4x + 2y - 5 = 0$ と直線 $x + y - 1 = 0$ の交点を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '連立方程式', 'steps': ['直線の式を円に代入', '二次方程式を解く']},
                    {'approach': '中心と距離', 'steps': ['円の標準形', '中心から直線までの距離', '交点の計算']},
                    {'approach': 'パラメータ表示', 'steps': ['直線のパラメータ表示', '円の式に代入']}
                ],
                'expected_methods': ['連立方程式', '距離の公式', 'パラメータ'],
                'answer': '(3, -2), (-1, 2)'
            },

            # 数学II - 三角関数
            6: {
                'id': 6,
                'title': '三角関数の合成',
                'category': 'trigonometry',
                'subject': '数学II',
                'unit': '三角関数',
                'difficulty': 'advanced',
                'content': '''
                $f(x) = \\sin x + \\sqrt{3}\\cos x$ の最大値と、そのときの $x$ の値を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '三角関数の合成', 'steps': ['$a\\sin x + b\\cos x = R\\sin(x + \\alpha)$', '係数の決定']},
                    {'approach': 'ベクトル利用', 'steps': ['$(1, \\sqrt{3})$との内積', '角度の計算']},
                    {'approach': '微分利用', 'steps': ['導関数を0にする', '極値の確認']}
                ],
                'expected_methods': ['合成公式', 'ベクトル', '微分'],
                'answer': '最大値: 2, x = π/3 + 2nπ'
            },

            # 数学II - 指数・対数
            7: {
                'id': 7,
                'title': '指数方程式',
                'category': 'exponential',
                'subject': '数学II',
                'unit': '指数関数・対数関数',
                'difficulty': 'intermediate',
                'content': '''
                $2^{2x+1} - 5 \\cdot 2^x + 2 = 0$ を解け。
                ''',
                'solution_patterns': [
                    {'approach': '置換', 'steps': ['$t = 2^x$とおく', '二次方程式に変換', '元の変数に戻す']},
                    {'approach': '因数分解', 'steps': ['共通因数$2^x$でまとめる', '因数分解']},
                    {'approach': 'グラフ利用', 'steps': ['左辺をグラフ化', 'x軸との交点']}
                ],
                'expected_methods': ['置換', '因数分解', 'グラフ'],
                'answer': 'x = 0, 1'
            },

            # 数学B - ベクトル
            8: {
                'id': 8,
                'title': '空間ベクトルの内積',
                'category': 'vector',
                'subject': '数学B',
                'unit': 'ベクトル',
                'difficulty': 'advanced',
                'content': '''
                四面体OABCにおいて、$\\vec{OA} = \\vec{a}$, $\\vec{OB} = \\vec{b}$, $\\vec{OC} = \\vec{c}$ とする。
                $|\\vec{a}| = |\\vec{b}| = |\\vec{c}| = 1$, $\\vec{a} \\cdot \\vec{b} = \\vec{b} \\cdot \\vec{c} = \\vec{c} \\cdot \\vec{a} = \\frac{1}{2}$ のとき、
                四面体OABCの体積を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': 'スカラー三重積', 'steps': ['$\\vec{a} \\cdot (\\vec{b} \\times \\vec{c})$の計算', '体積公式の適用']},
                    {'approach': '行列式', 'steps': ['座標設定', '行列式による体積計算']},
                    {'approach': '幾何学的考察', 'steps': ['角度の計算', '高さと底面積']}
                ],
                'expected_methods': ['スカラー三重積', '行列式', '幾何学'],
                'answer': '$\\frac{\\sqrt{2}}{12}$'
            },

            # 数学B - 数列
            9: {
                'id': 9,
                'title': '漸化式の解法',
                'category': 'sequence',
                'subject': '数学B',
                'unit': '数列',
                'difficulty': 'advanced',
                'content': '''
                数列 $\\{a_n\\}$ が $a_1 = 1$, $a_{n+1} = 3a_n + 2$ を満たすとき、一般項 $a_n$ を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '特性方程式', 'steps': ['特性方程式の解', '一般解の形', '初期条件による決定']},
                    {'approach': '変数変換', 'steps': ['$b_n = a_n + k$の形に変換', '等比数列に帰着']},
                    {'approach': '数学的帰納法', 'steps': ['一般項の推測', '数学的帰納法による証明']}
                ],
                'expected_methods': ['特性方程式', '変数変換', '数学的帰納法'],
                'answer': '$a_n = 2 \\cdot 3^{n-1} - 1$'
            },

            # 数学III - 極限
            10: {
                'id': 10,
                'title': '関数の極限',
                'category': 'limit',
                'subject': '数学III',
                'unit': '極限',
                'difficulty': 'advanced',
                'content': '''
                $\\lim_{x \\to 0} \\frac{\\sin 3x}{\\tan 2x}$ を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '基本極限利用', 'steps': ['$\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$の利用', '変数変換']},
                    {'approach': 'ロピタルの定理', 'steps': ['0/0型の確認', 'ロピタルの定理の適用']},
                    {'approach': 'テイラー展開', 'steps': ['各関数のテイラー展開', '主要項の比較']}
                ],
                'expected_methods': ['基本極限', 'ロピタル', 'テイラー展開'],
                'answer': '$\\frac{3}{2}$'
            },

            # 数学III - 微分法
            11: {
                'id': 11,
                'title': '陰関数の微分',
                'category': 'differentiation',
                'subject': '数学III',
                'unit': '微分法',
                'difficulty': 'advanced',
                'content': '''
                $x^2 + y^2 = 4$ で表される円上の点 $(\\sqrt{2}, \\sqrt{2})$ における接線の方程式を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '陰関数微分', 'steps': ['両辺をxで微分', 'dy/dxを求める', '接線の方程式']},
                    {'approach': '幾何学的性質', 'steps': ['円の中心と接点', '法線ベクトル', '接線の方程式']},
                    {'approach': 'パラメータ表示', 'steps': ['円のパラメータ表示', '微分による接線']}
                ],
                'expected_methods': ['陰関数微分', '幾何学', 'パラメータ'],
                'answer': '$x + y = 2\\sqrt{2}$'
            },

            # 数学III - 積分法
            12: {
                'id': 12,
                'title': '部分積分の応用',
                'category': 'integration',
                'subject': '数学III',
                'unit': '積分法',
                'difficulty': 'advanced',
                'content': '''
                $\\int x^2 e^x dx$ を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '部分積分の反復', 'steps': ['2回の部分積分', '係数の整理']},
                    {'approach': '表による部分積分', 'steps': ['部分積分の表作成', '符号の確認']},
                    {'approach': '漸化式', 'steps': ['$I_n = \\int x^n e^x dx$の漸化式', '解の導出']}
                ],
                'expected_methods': ['部分積分', '表形式', '漸化式'],
                'answer': '$e^x(x^2 - 2x + 2) + C$'
            },

            # 数学C - 複素数平面
            13: {
                'id': 13,
                'title': '複素数の回転',
                'category': 'complex',
                'subject': '数学C',
                'unit': '複素数平面',
                'difficulty': 'advanced',
                'content': '''
                複素数 $z = 1 + i$ を原点中心に $60°$ 回転した点を表す複素数を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': '複素数の積', 'steps': ['回転の複素数$e^{i\\pi/3}$', '積の計算']},
                    {'approach': '極形式利用', 'steps': ['極形式への変換', '偏角の加算', '直交形式に戻す']},
                    {'approach': '回転行列', 'steps': ['回転行列の適用', '座標変換']}
                ],
                'expected_methods': ['複素数の積', '極形式', '回転行列'],
                'answer': '$\\frac{1-\\sqrt{3}}{2} + \\frac{1+\\sqrt{3}}{2}i$'
            },

            # 数学C - 平面上の曲線
            14: {
                'id': 14,
                'title': 'サイクロイドの長さ',
                'category': 'curves',
                'subject': '数学C',
                'unit': '平面上の曲線',
                'difficulty': 'advanced',
                'content': '''
                半径 $a$ の円が直線上を滑らずに転がるとき、円周上の一点が描く軌跡（サイクロイド）について、
                一周期分の弧長を求めよ。
                ''',
                'solution_patterns': [
                    {'approach': 'パラメータ表示', 'steps': ['サイクロイドの方程式', '弧長公式の適用']},
                    {'approach': '幾何学的考察', 'steps': ['円の転がり', '軌跡の性質', '対称性の利用']},
                    {'approach': '積分変換', 'steps': ['適切な変数変換', '積分の計算']}
                ],
                'expected_methods': ['パラメータ', '幾何学', '積分変換'],
                'answer': '$8a$'
            },

            # 数学C - 統計的推測
            15: {
                'id': 15,
                'title': '信頼区間の推定',
                'category': 'statistics',
                'subject': '数学C',
                'unit': '統計的推測',
                'difficulty': 'intermediate',
                'content': '''
                ある母集団から大きさ25の標本を取り、標本平均が52.4、標本標準偏差が8.2であった。
                母平均の95%信頼区間を求めよ。（t分布表を使用）
                ''',
                'solution_patterns': [
                    {'approach': 't分布利用', 'steps': ['自由度の確認', 't値の読み取り', '信頼区間の計算']},
                    {'approach': '正規分布近似', 'steps': ['標本サイズの確認', '正規分布による近似']},
                    {'approach': 'ブートストラップ', 'steps': ['リサンプリング', '経験分布による推定']}
                ],
                'expected_methods': ['t分布', '正規近似', 'ブートストラップ'],
                'answer': '$[49.05, 55.75]$ (概算)'
            }
        }
    
    def get_all_problems(self) -> List[Dict[str, Any]]:
        """全問題の一覧を取得"""
        return [
            {
                'id': problem['id'],
                'title': problem['title'], 
                'category': problem['category'],
                'subject': problem.get('subject', '未分類'),
                'unit': problem.get('unit', ''),
                'difficulty': problem['difficulty']
            }
            for problem in self.problems.values()
        ]
    
    def get_problem(self, problem_id: int) -> Dict[str, Any]:
        """特定の問題を取得"""
        return self.problems.get(problem_id)
    
    def get_problems_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """教科別の問題を取得"""
        return [
            problem for problem in self.problems.values()
            if problem.get('subject') == subject
        ]
    
    def get_problems_by_category(self, category: str) -> List[Dict[str, Any]]:
        """カテゴリ別の問題を取得"""
        return [
            problem for problem in self.problems.values()
            if problem['category'] == category
        ]
    
    def get_problems_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """難易度別の問題を取得"""
        return [
            problem for problem in self.problems.values()
            if problem['difficulty'] == difficulty
        ]
    
    def add_problem(self, problem_data: Dict[str, Any]) -> int:
        """新しい問題を追加"""
        new_id = max(self.problems.keys()) + 1
        problem_data['id'] = new_id
        self.problems[new_id] = problem_data
        return new_id
    
    def get_solution_patterns(self, problem_id: int) -> List[Dict[str, Any]]:
        """問題の解法パターンを取得"""
        problem = self.get_problem(problem_id)
        if problem:
            return problem.get('solution_patterns', [])
        return []
    
    def get_hints(self, problem_id: int, level: int = 1) -> str:
        """問題のヒントを取得"""
        problem = self.get_problem(problem_id)
        if problem and 'hints' in problem:
            hint_key = f'level{level}'
            return problem['hints'].get(hint_key, problem['hints'].get('level1', ''))
        return ''
