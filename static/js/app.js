// AI数学チューター - 左右分割レイアウト用 JavaScript

class MathTutor {
    constructor() {
        this.selectedProblem = null;
        this.currentAnalysis = null;
        this.hintHistory = [];
        this.digitalWhiteboard = null;
        this.handwritingRecognizer = null;
        this.currentSubject = 'all';
        this.currentDifficulty = 'all';
        this.allProblems = [];
        
        this.init();
    }
    
    init() {
        this.loadProblems();
        this.initEventListeners();
        this.initWhiteboard();
        this.initMathJax();
    }
    
    initEventListeners() {
        // 問題フィルターのイベントリスナー
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = e.target.dataset.filter;
                this.filterBySubject(filter);
            });
        });
        
        const difficultySelect = document.getElementById('difficultySelect');
        if (difficultySelect) {
            difficultySelect.addEventListener('change', (e) => this.filterByDifficulty(e.target.value));
        }
        
        // ホワイトボード制御ボタン
        const clearButton = document.getElementById('clearCanvas');
        const undoButton = document.getElementById('undoStroke');
        const redoButton = document.getElementById('redoStroke');
        const recognizeButton = document.getElementById('recognizeContent');
        const analyzeButton = document.getElementById('analyzeProgress');
        
        if (clearButton) clearButton.addEventListener('click', () => this.clearCanvas());
        if (undoButton) undoButton.addEventListener('click', () => this.undoCanvas());
        if (redoButton) redoButton.addEventListener('click', () => this.redoCanvas());
        
        // 認識ボタンは自動分析を実行（Shiftキーで認識のみ）
        if (recognizeButton) {
            recognizeButton.addEventListener('click', (e) => {
                if (e.shiftKey) {
                    this.recognizeHandwritingOnly();
                } else {
                    this.recognizeHandwriting();
                }
            });
        }
        
        // 分析ボタンは手動分析を実行
        if (analyzeButton) analyzeButton.addEventListener('click', () => this.analyzeThinking());
        
        // 描画ツール制御
        const penTool = document.getElementById('penTool');
        const eraserTool = document.getElementById('eraserTool');
        const brushSizeSlider = document.getElementById('brushSize');
        
        if (penTool) penTool.addEventListener('click', () => this.setDrawMode());
        if (eraserTool) eraserTool.addEventListener('click', () => this.setEraseMode());
        if (brushSizeSlider) {
            brushSizeSlider.addEventListener('input', (e) => this.setBrushSize(e.target.value));
            this.updateBrushSizeDisplay(brushSizeSlider.value);
        }
        
        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.analyzeThinking();
                } else if (e.key === 'h') {
                    e.preventDefault();
                    this.getHint();
                } else if (e.key === 'z' && !e.shiftKey) {
                    e.preventDefault();
                    this.undoCanvas();
                } else if (e.key === 'z' && e.shiftKey) {
                    e.preventDefault();
                    this.redoCanvas();
                }
            }
        });
    }
    
    initMathJax() {
        if (window.MathJax) {
            MathJax.config.tex = {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']]
            };
        }
    }
    
    async loadProblems() {
        try {
            this.showLoading('問題一覧を読み込み中...');
            const response = await fetch('/api/problems');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const problems = await response.json();
            this.allProblems = problems;
            this.displayProblems(problems);
            console.log('問題を読み込みました:', problems.length, '件');
        } catch (error) {
            this.showError('問題の読み込みに失敗しました: ' + error.message);
            console.error('Error loading problems:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    filterBySubject(subject) {
        this.currentSubject = subject;
        
        // タブの状態を更新
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        const activeTab = document.querySelector(`[data-filter="${subject}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        this.applyFilters();
    }
    
    filterByDifficulty(difficulty) {
        this.currentDifficulty = difficulty;
        this.applyFilters();
    }
    
    applyFilters() {
        if (!this.allProblems) return;
        
        let filteredProblems = this.allProblems.filter(problem => {
            const subjectMatch = this.currentSubject === 'all' || problem.subject === this.currentSubject;
            const difficultyMatch = this.currentDifficulty === 'all' || problem.difficulty === this.currentDifficulty;
            return subjectMatch && difficultyMatch;
        });
        
        this.displayProblems(filteredProblems);
        console.log('フィルター適用:', {
            subject: this.currentSubject,
            difficulty: this.currentDifficulty,
            results: filteredProblems.length
        });
    }
    
    displayProblems(problems) {
        const problemList = document.getElementById('problemList');
        if (!problemList) {
            console.error('Problem list element not found');
            return;
        }
        
        problemList.innerHTML = '';
        
        if (problems.length === 0) {
            problemList.innerHTML = '<p class="no-problems">条件に合う問題がありません。</p>';
            return;
        }
        
        problems.forEach(problem => {
            const problemElement = document.createElement('div');
            problemElement.className = 'problem-item';
            problemElement.dataset.problemId = problem.id;
            
            problemElement.innerHTML = `
                <div class="problem-title">${problem.title}</div>
                <div class="problem-meta">
                    <span class="subject-tag">${problem.subject}</span>
                    <span class="unit-tag">${problem.unit}</span>
                    <span class="difficulty-tag">${problem.difficulty}</span>
                </div>
            `;
            
            problemElement.addEventListener('click', () => this.selectProblem(problem));
            problemList.appendChild(problemElement);
        });
    }
    
    async selectProblem(problem) {
        try {
            // 前の選択を解除
            const previousSelected = document.querySelector('.problem-item.selected');
            if (previousSelected) {
                previousSelected.classList.remove('selected');
            }
            
            // 新しい問題を選択
            const selectedElement = document.querySelector(`[data-problem-id="${problem.id}"]`);
            if (selectedElement) {
                selectedElement.classList.add('selected');
            }
            
            // 問題の詳細を取得
            const response = await fetch(`/api/problem/${problem.id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const problemDetail = await response.json();
            
            this.selectedProblem = problemDetail;
            this.displaySelectedProblem(problemDetail);
            this.clearAnalysis();
            this.clearHints();
            this.clearRecognitionResults();
            
            if (this.digitalWhiteboard) {
                this.digitalWhiteboard.clear();
            }
        } catch (error) {
            this.showError('問題の詳細取得に失敗しました: ' + error.message);
            console.error('Error selecting problem:', error);
        }
    }
    
    displaySelectedProblem(problem) {
        const problemDisplay = document.getElementById('problemDisplay');
        const problemContent = document.getElementById('problemContent');
        const problemInfo = document.getElementById('problemInfo');
        
        if (!problemDisplay || !problemContent || !problemInfo) {
            console.error('Problem display elements not found');
            return;
        }
        
        // 問題内容を表示
        problemContent.innerHTML = `
            <h3>${problem.title}</h3>
            <div class="problem-text">
                ${problem.content}
            </div>
        `;
        
        // 問題情報を表示
        problemInfo.innerHTML = `
            <div class="problem-meta">
                <span class="meta-item"><strong>科目:</strong> ${problem.subject}</span>
                <span class="meta-item"><strong>単元:</strong> ${problem.unit}</span>
                <span class="meta-item"><strong>難易度:</strong> ${problem.difficulty}</span>
            </div>
        `;
        
        // 問題表示エリアを表示
        problemDisplay.style.display = 'block';
        
        // MathJaxで数式をレンダリング
        if (window.MathJax) {
            MathJax.typesetPromise([problemContent, problemInfo]).catch(console.error);
        }
        
        console.log('問題を表示しました:', problem.title);
    }
    
    initWhiteboard() {
        try {
            this.digitalWhiteboard = new DigitalWhiteboard('drawingCanvas');
            this.handwritingRecognizer = new HandwritingRecognizer();
            console.log('ホワイトボードを初期化しました');
        } catch (error) {
            console.error('ホワイトボード初期化エラー:', error);
        }
    }
    
    setDrawMode() {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.setDrawMode();
        }
        const penTool = document.getElementById('penTool');
        const eraserTool = document.getElementById('eraserTool');
        if (penTool) penTool.classList.add('active');
        if (eraserTool) eraserTool.classList.remove('active');
    }
    
    setEraseMode() {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.setEraseMode();
        }
        const penTool = document.getElementById('penTool');
        const eraserTool = document.getElementById('eraserTool');
        if (eraserTool) eraserTool.classList.add('active');
        if (penTool) penTool.classList.remove('active');
    }
    
    setBrushSize(size) {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.setBrushSize(size);
        }
        this.updateBrushSizeDisplay(size);
    }
    
    updateBrushSizeDisplay(size) {
        const display = document.getElementById('brushSizeDisplay');
        if (display) {
            display.textContent = `${size}px`;
        }
    }
    
    clearCanvas() {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.clear();
        }
        this.clearRecognitionResults();
    }
    
    undoCanvas() {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.undo();
        }
    }
    
    redoCanvas() {
        if (this.digitalWhiteboard) {
            this.digitalWhiteboard.redo();
        }
    }
    
    async recognizeHandwriting() {
        if (!this.digitalWhiteboard) {
            this.showError('ホワイトボードが初期化されていません。');
            return null;
        }
        
        if (this.digitalWhiteboard.isEmpty()) {
            this.showError('何も描かれていません。手書きで解答を書いてください。');
            return null;
        }
        
        try {
            this.showLoading('手書き内容を認識中...');
            const imageData = this.digitalWhiteboard.getImageData();
            
            console.log('手書き認識開始:', imageData.substring(0, 50) + '...');
            
            const response = await fetch('/api/recognize_handwriting', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_data: imageData })
            });
            
            console.log('API応答ステータス:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API エラー応答:', errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const recognition = await response.json();
            console.log('認識結果:', recognition);
            
            this.displayRecognitionResult(recognition);
            
            // 認識が成功した場合、自動的に解法推定と正誤判定を実行
            if (recognition.success && recognition.latex && this.selectedProblem) {
                this.hideLoading(); // 認識のローディングを終了
                await this.performAutomaticAnalysis(recognition);
            }
            
            return recognition;
        } catch (error) {
            this.showError('手書き認識に失敗しました: ' + error.message);
            console.error('Error recognizing handwriting:', error);
            return null;
        } finally {
            this.hideLoading();
        }
    }
    
    async performAutomaticAnalysis(recognition) {
        if (!this.selectedProblem || !recognition.latex) {
            return;
        }
        
        try {
            this.showLoading('解法推定と正誤判定を実行中...');
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    problem_id: this.selectedProblem.id,
                    user_input: recognition.latex
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const analysis = await response.json();
            console.log('自動分析結果:', analysis);
            
            this.currentAnalysis = analysis;
            this.displayAnalysis(analysis);
            
            // 分析結果に基づいて適切なフィードバックを表示
            this.showAnalysisNotification(analysis);
            
        } catch (error) {
            console.error('自動分析エラー:', error);
            // エラーがあっても認識結果は表示されているので、重大なエラー表示はしない
            this.showTemporaryMessage('自動分析でエラーが発生しましたが、認識結果は表示されています。');
        } finally {
            this.hideLoading();
        }
    }
    
    showAnalysisNotification(analysis) {
        // 詳細な分析結果を含む通知メッセージを表示
        const notification = document.createElement('div');
        notification.className = 'analysis-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(analysis.correctness)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 350px;
            font-size: 14px;
            line-height: 1.4;
        `;
        
        const scoreText = analysis.correctness_score ? 
            `${Math.round(analysis.correctness_score * 100)}点` : '評価中';
        
        notification.innerHTML = `
            <strong>📊 自動分析完了</strong><br>
            正誤判定: ${this.getCorrectnessIcon(analysis.correctness)} ${this.getCorrectnessText(analysis.correctness)}<br>
            解法: ${analysis.approach}<br>
            スコア: ${scoreText}
        `;
        
        document.body.appendChild(notification);
        
        // 6秒後に自動的に削除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 6000);
    }
    
    getNotificationColor(correctness) {
        switch (correctness) {
            case 'correct': return '#16a34a';
            case 'partial': return '#d97706';
            case 'incorrect': return '#dc2626';
            default: return '#6b7280';
        }
    }
    
    showTemporaryMessage(message) {
        const tempMessage = document.createElement('div');
        tempMessage.className = 'temp-message';
        tempMessage.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff9800;
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            z-index: 999;
            max-width: 250px;
            font-size: 13px;
        `;
        tempMessage.textContent = message;
        
        document.body.appendChild(tempMessage);
        
        setTimeout(() => {
            if (tempMessage.parentNode) {
                tempMessage.parentNode.removeChild(tempMessage);
            }
        }, 3000);
    }
    
    displayRecognitionResult(recognition) {
        const resultDiv = document.getElementById('recognitionResults');
        const resultContent = document.getElementById('recognitionContent');
        
        if (!resultDiv || !resultContent) {
            console.error('Recognition results elements not found');
            return;
        }
        
        if (recognition.success) {
            resultContent.innerHTML = `
                <div class="latex-display">
                    <strong>認識結果:</strong> ${recognition.latex || '（認識できませんでした）'}
                </div>
                <div class="recognition-confidence confidence-${this.getConfidenceLevel(recognition.confidence)}">
                    信頼度: ${Math.round((recognition.confidence || 0) * 100)}%
                </div>
                ${recognition.interpretation ? `<div class="interpretation"><strong>解釈:</strong> ${recognition.interpretation}</div>` : ''}
            `;
            
            resultDiv.style.display = 'block';
            
            // MathJaxで数式をレンダリング
            if (window.MathJax && recognition.latex) {
                MathJax.typesetPromise([resultContent]).catch(console.error);
            }
        } else {
            resultContent.innerHTML = `
                <p>手書き内容を認識できませんでした。より明確に書き直してお試しください。</p>
                <p>エラー詳細: ${recognition.error || '不明なエラー'}</p>
                <div class="recognition-tips">
                    <strong>認識のコツ:</strong>
                    <ul>
                        <li>文字は大きくはっきりと書く</li>
                        <li>数式の各要素の間に適度な間隔を空ける</li>
                        <li>背景は白で、ペンは濃い色を使う</li>
                    </ul>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
    }
    
    getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.6) return 'medium';
        return 'low';
    }
    
    async recognizeHandwritingOnly() {
        if (!this.digitalWhiteboard) {
            this.showError('ホワイトボードが初期化されていません。');
            return null;
        }
        
        if (this.digitalWhiteboard.isEmpty()) {
            this.showError('何も描かれていません。手書きで解答を書いてください。');
            return null;
        }
        
        try {
            this.showLoading('手書き内容を認識中...');
            const imageData = this.digitalWhiteboard.getImageData();
            
            console.log('手書き認識のみ実行:', imageData.substring(0, 50) + '...');
            
            const response = await fetch('/api/recognize_handwriting', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_data: imageData })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const recognition = await response.json();
            console.log('認識結果（分析なし）:', recognition);
            
            this.displayRecognitionResult(recognition);
            return recognition;
        } catch (error) {
            this.showError('手書き認識に失敗しました: ' + error.message);
            console.error('Error recognizing handwriting:', error);
            return null;
        } finally {
            this.hideLoading();
        }
    }
    
    async analyzeThinking() {
        if (!this.selectedProblem) {
            this.showError('問題を選択してください。');
            return;
        }
        
        // 手書き認識を実行
        const recognition = await this.recognizeHandwriting();
        if (!recognition || !recognition.success || !recognition.latex) {
            this.showError('手書き内容を認識できませんでした。再度描き直してお試しください。');
            return;
        }
        
        try {
            this.showLoading('思考プロセスを分析中...');
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    problem_id: this.selectedProblem.id,
                    user_input: recognition.latex
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const analysis = await response.json();
            this.currentAnalysis = analysis;
            this.displayAnalysis(analysis);
        } catch (error) {
            this.showError('分析に失敗しました: ' + error.message);
            console.error('Error analyzing thinking:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    displayAnalysis(analysis) {
        const analysisDisplay = document.getElementById('analysisPanel');
        const analysisContent = document.getElementById('analysisContent');
        
        if (!analysisDisplay || !analysisContent) {
            console.error('Analysis panel elements not found');
            return;
        }
        
        // 正誤判定のスタイルを決定
        const correctnessClass = this.getCorrectnessClass(analysis.correctness);
        const correctnessIcon = this.getCorrectnessIcon(analysis.correctness);
        const scorePercentage = Math.round((analysis.correctness_score || 0.5) * 100);
        
        // 詳細評価の表示
        const detailedEval = analysis.detailed_evaluation || {};
        const evalItems = [
            { key: 'problem_understanding', label: '問題理解', value: detailedEval.problem_understanding },
            { key: 'method_selection', label: '解法選択', value: detailedEval.method_selection },
            { key: 'calculation_accuracy', label: '計算正確性', value: detailedEval.calculation_accuracy },
            { key: 'final_answer', label: '最終答え', value: detailedEval.final_answer },
            { key: 'presentation', label: '表現・記述', value: detailedEval.presentation }
        ];
        
        analysisContent.innerHTML = `
            <div class="analysis-header">
                <h3>🎯 AI解法分析・評価結果</h3>
                <div class="correctness-summary">
                    <div class="correctness-indicator ${correctnessClass}">
                        ${correctnessIcon} ${this.getCorrectnessText(analysis.correctness)}
                    </div>
                    <div class="score-display">
                        <div class="score-bar">
                            <div class="score-fill ${correctnessClass}" style="width: ${scorePercentage}%"></div>
                        </div>
                        <span class="score-text">${scorePercentage}点</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-main">
                <div class="analysis-section">
                    <div class="analysis-item primary">
                        <div class="analysis-label">📝 解法アプローチ</div>
                        <div class="analysis-value">${analysis.approach}</div>
                    </div>
                    <div class="analysis-item primary">
                        <div class="analysis-label">📊 進捗段階</div>
                        <div class="analysis-value">${analysis.progress_stage}</div>
                    </div>
                </div>
                
                <div class="analysis-section">
                    <h4>📋 詳細評価</h4>
                    <div class="evaluation-grid">
                        ${evalItems.map(item => `
                            <div class="eval-item ${item.value ? 'correct' : 'incorrect'}">
                                <span class="eval-icon">${item.value ? '✅' : '❌'}</span>
                                <span class="eval-label">${item.label}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="analysis-section">
                    <div class="analysis-item feedback">
                        <div class="analysis-label">💭 詳細フィードバック</div>
                        <div class="analysis-value">${analysis.feedback}</div>
                    </div>
                </div>
                
                ${analysis.suggestions && analysis.suggestions.length > 0 ? `
                <div class="analysis-section">
                    <h4>💡 改善提案</h4>
                    <ul class="suggestions-list">
                        ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <div class="analysis-section">
                    <div class="confidence-display">
                        <span class="confidence-label">🎯 分析信頼度:</span>
                        <span class="confidence-value">${Math.round((analysis.confidence || 0.5) * 100)}%</span>
                    </div>
                </div>
            </div>
            
            <div class="hint-controls">
                <h4>💡 追加ヒントが必要な場合</h4>
                <div class="hint-buttons">
                    <button class="btn btn-hint hint-basic" onclick="mathTutor.getHint(1)">基本ヒント</button>
                    <button class="btn btn-hint hint-detailed" onclick="mathTutor.getHint(2)">詳細ヒント</button>
                    <button class="btn btn-hint hint-solution" onclick="mathTutor.getHint(3)">解法ヒント</button>
                </div>
            </div>
        `;
        
        analysisDisplay.style.display = 'block';
        
        // MathJaxで数式をレンダリング
        if (window.MathJax) {
            MathJax.typesetPromise([analysisContent]).catch(console.error);
        }
    }
    
    getCorrectnessClass(correctness) {
        switch (correctness) {
            case 'correct': return 'correct';
            case 'partial': return 'partial';
            case 'incorrect': return 'incorrect';
            default: return 'neutral';
        }
    }
    
    getCorrectnessIcon(correctness) {
        switch (correctness) {
            case 'correct': return '✅';
            case 'partial': return '🟡';
            case 'incorrect': return '❌';
            default: return '📝';
        }
    }
    
    getCorrectnessText(correctness) {
        switch (correctness) {
            case 'correct': return '正解です！';
            case 'partial': return '部分的に正しいです';
            case 'incorrect': return '再確認が必要です';
            default: return '分析完了';
        }
    }
    
    async getHint(level = 1) {
        if (!this.selectedProblem) {
            this.showError('問題を選択してください。');
            return;
        }
        
        try {
            this.showLoading('ヒントを生成中...');
            
            // 現在の認識結果を取得
            let currentInput = '';
            const recognitionResults = document.getElementById('recognitionContent');
            if (recognitionResults) {
                const latexDisplay = recognitionResults.querySelector('.latex-display');
                if (latexDisplay) {
                    currentInput = latexDisplay.textContent.replace('認識結果:', '').trim();
                }
            }
            
            const response = await fetch('/api/hint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    problem_id: this.selectedProblem.id,
                    current_analysis: {
                        ...this.currentAnalysis,
                        user_input: currentInput
                    },
                    hint_level: level
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const hint = await response.json();
            this.displayHint(hint, level);
            this.hintHistory.push(hint);
        } catch (error) {
            this.showError('ヒント生成に失敗しました: ' + error.message);
            console.error('Error getting hint:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    displayHint(hint, level) {
        const hintsDisplay = document.getElementById('hintsPanel');
        const hintsContent = document.getElementById('hintsContent');
        
        if (!hintsDisplay || !hintsContent) {
            console.error('Hints panel elements not found');
            return;
        }
        
        hintsContent.innerHTML = `
            <div class="hint-item">
                <div class="hint-level">レベル${level}</div>
                <div class="hint-type">${hint.type}</div>
                <div class="hint-content">${hint.content}</div>
            </div>
        `;
        
        hintsDisplay.style.display = 'block';
        
        // MathJaxで数式をレンダリング
        if (window.MathJax) {
            MathJax.typesetPromise([hintsContent]).catch(console.error);
        }
    }
    
    clearAnalysis() {
        const analysisDisplay = document.getElementById('analysisPanel');
        if (analysisDisplay) {
            analysisDisplay.style.display = 'none';
        }
        this.currentAnalysis = null;
    }
    
    clearHints() {
        const hintsDisplay = document.getElementById('hintsPanel');
        if (hintsDisplay) {
            hintsDisplay.style.display = 'none';
        }
        this.hintHistory = [];
    }
    
    clearRecognitionResults() {
        const resultsDisplay = document.getElementById('recognitionResults');
        if (resultsDisplay) {
            resultsDisplay.style.display = 'none';
        }
    }
    
    showLoading(message = '処理中...') {
        let loadingDiv = document.getElementById('loadingDisplay');
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'loadingDisplay';
            loadingDiv.className = 'loading';
            document.body.appendChild(loadingDiv);
        }
        
        loadingDiv.innerHTML = `
            <div class="spinner"></div>
            <p>${message}</p>
        `;
        loadingDiv.style.display = 'flex';
    }
    
    hideLoading() {
        const loadingDiv = document.getElementById('loadingDisplay');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
    
    showError(message) {
        let errorDiv = document.getElementById('errorDisplay');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'errorDisplay';
            errorDiv.className = 'error-display';
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `
            <div class="error-content">
                <h3>エラー</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="mathTutor.hideError()">閉じる</button>
            </div>
        `;
        errorDiv.style.display = 'flex';
        
        console.error('Error:', message);
    }
    
    hideError() {
        const errorDiv = document.getElementById('errorDisplay');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }
}

// デジタルホワイトボードクラス（強化版）
class DigitalWhiteboard {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            throw new Error(`Canvas element with id "${canvasId}" not found`);
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.isErasing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.strokeHistory = [];
        this.currentStroke = [];
        this.undoHistory = [];
        this.brushSize = 3;
        
        this.setupCanvas();
        this.initEventListeners();
    }
    
    setupCanvas() {
        // レスポンシブなキャンバスサイズの設定
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // 描画設定
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.setDrawMode();
        this.clear();
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const containerWidth = Math.max(400, container.clientWidth - 40); // パディング考慮
        const containerHeight = Math.min(500, Math.max(300, window.innerHeight * 0.5));
        
        // 既存の描画を保存
        const imageData = this.strokeHistory.length > 0 ? this.canvas.toDataURL() : null;
        
        this.canvas.width = containerWidth;
        this.canvas.height = containerHeight;
        this.canvas.style.width = containerWidth + 'px';
        this.canvas.style.height = containerHeight + 'px';
        
        // 描画設定を再適用
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.setDrawMode();
        
        // 背景を白に設定
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 既存の描画を復元
        if (imageData && this.strokeHistory.length > 0) {
            const img = new Image();
            img.onload = () => {
                this.ctx.drawImage(img, 0, 0);
            };
            img.src = imageData;
        }
    }
    
    initEventListeners() {
        // マウスイベント
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseleave', () => this.stopDrawing());
        
        // タッチイベント（モバイル対応）
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.startDrawing(mouseEvent);
        });
        
        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.draw(mouseEvent);
        });
        
        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopDrawing();
        });
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.canvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
        
        this.currentStroke = [{
            x: this.lastX, 
            y: this.lastY, 
            isErasing: this.isErasing,
            brushSize: this.brushSize
        }];
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.ctx.globalCompositeOperation = this.isErasing ? 'destination-out' : 'source-over';
        this.ctx.lineWidth = this.brushSize;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(currentX, currentY);
        this.ctx.stroke();
        
        this.currentStroke.push({
            x: currentX, 
            y: currentY, 
            isErasing: this.isErasing,
            brushSize: this.brushSize
        });
        
        this.lastX = currentX;
        this.lastY = currentY;
    }
    
    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            if (this.currentStroke.length > 0) {
                this.strokeHistory.push([...this.currentStroke]);
                this.currentStroke = [];
                this.undoHistory = []; // 新しいストロークが追加されたらredo履歴をクリア
            }
        }
    }
    
    setDrawMode() {
        this.isErasing = false;
        this.ctx.strokeStyle = '#2563eb';
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    setEraseMode() {
        this.isErasing = true;
        this.ctx.globalCompositeOperation = 'destination-out';
    }
    
    setBrushSize(size) {
        this.brushSize = parseInt(size);
        this.ctx.lineWidth = this.brushSize;
    }
    
    clear() {
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.strokeHistory = [];
        this.undoHistory = [];
    }
    
    undo() {
        if (this.strokeHistory.length > 0) {
            const lastStroke = this.strokeHistory.pop();
            this.undoHistory.push(lastStroke);
            this.redrawCanvas();
        }
    }
    
    redo() {
        if (this.undoHistory.length > 0) {
            const strokeToRedo = this.undoHistory.pop();
            this.strokeHistory.push(strokeToRedo);
            this.redrawCanvas();
        }
    }
    
    redrawCanvas() {
        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.strokeHistory.forEach(stroke => {
            if (stroke.length > 1) {
                this.ctx.globalCompositeOperation = stroke[0].isErasing ? 'destination-out' : 'source-over';
                this.ctx.lineWidth = stroke[0].brushSize;
                this.ctx.strokeStyle = '#2563eb';
                
                this.ctx.beginPath();
                this.ctx.moveTo(stroke[0].x, stroke[0].y);
                for (let i = 1; i < stroke.length; i++) {
                    this.ctx.lineTo(stroke[i].x, stroke[i].y);
                }
                this.ctx.stroke();
            }
        });
    }
    
    isEmpty() {
        return this.strokeHistory.length === 0;
    }
    
    getImageData() {
        return this.canvas.toDataURL('image/png');
    }
}

// 手書き認識クラス
class HandwritingRecognizer {
    constructor() {
        this.apiEndpoint = '/api/recognize_handwriting';
    }
    
    async recognizeFromCanvas(canvasElement) {
        const imageData = canvasElement.toDataURL('image/png');
        return await this.recognize(imageData);
    }
    
    async recognize(imageData) {
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_data: imageData })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Handwriting recognition error:', error);
            return { success: false, error: error.message };
        }
    }
}

// アプリケーション初期化
let mathTutor;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing MathTutor...');
    try {
        mathTutor = new MathTutor();
        console.log('MathTutor initialized successfully');
    } catch (error) {
        console.error('Failed to initialize MathTutor:', error);
    }
});
