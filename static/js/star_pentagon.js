/**
 * 星形五角形 AI数学チューター
 * フロントエンド JavaScript
 */

class StarPentagonTutor {
    constructor() {
        this.sessionId = null;
        this.analysisTimer = null;
        this.lastAnalysisTime = 0;
        this.settings = {
            supportLevel: 'adaptive',
            difficulty: 'standard',
            hintFrequency: 'moderate',
            analysisSensitivity: 5,
            autoAnalysisInterval: 10
        };
        
        // ホワイトボード設定
        this.whiteboard = null;
        this.ctx = null;
        this.isDrawing = false;
        this.isErasing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.strokes = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupWhiteboard();
        this.loadSettings();
        this.loadSolutionExamples();
    }

    setupWhiteboard() {
        this.whiteboard = document.getElementById('whiteboard');
        this.ctx = this.whiteboard.getContext('2d');
        
        // 描画設定
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        
        // ホワイトボードイベント
        this.whiteboard.addEventListener('mousedown', this.startDrawing.bind(this));
        this.whiteboard.addEventListener('mousemove', this.draw.bind(this));
        this.whiteboard.addEventListener('mouseup', this.stopDrawing.bind(this));
        this.whiteboard.addEventListener('mouseout', this.stopDrawing.bind(this));
        
        // タッチイベント
        this.whiteboard.addEventListener('touchstart', this.handleTouch.bind(this));
        this.whiteboard.addEventListener('touchmove', this.handleTouch.bind(this));
        this.whiteboard.addEventListener('touchend', this.stopDrawing.bind(this));
        
        // 描画ツール
        document.getElementById('penSize').addEventListener('input', (e) => {
            this.ctx.lineWidth = e.target.value;
        });
        
        document.getElementById('penColor').addEventListener('change', (e) => {
            this.ctx.strokeStyle = e.target.value;
            this.isErasing = false;
        });
        
        document.getElementById('eraserBtn').addEventListener('click', () => {
            this.toggleEraser();
        });
        
        document.getElementById('clearCanvasBtn').addEventListener('click', () => {
            this.clearCanvas();
        });
        
        document.getElementById('recognizeBtn').addEventListener('click', () => {
            this.recognizeHandwriting();
        });
        
        // 初期設定
        this.ctx.lineWidth = 3;
        this.ctx.strokeStyle = '#2c3e50';
    }

    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.whiteboard.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
        
        // 新しいストローク開始
        this.strokes.push({
            points: [{ x: this.lastX, y: this.lastY }],
            color: this.ctx.strokeStyle,
            width: this.ctx.lineWidth,
            isEraser: this.isErasing
        });
    }

    draw(e) {
        if (!this.isDrawing) return;
        
        const rect = this.whiteboard.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(currentX, currentY);
        
        if (this.isErasing) {
            this.ctx.globalCompositeOperation = 'destination-out';
            this.ctx.strokeStyle = 'rgba(0,0,0,1)';
        } else {
            this.ctx.globalCompositeOperation = 'source-over';
        }
        
        this.ctx.stroke();
        
        // ストロークに点を追加
        const currentStroke = this.strokes[this.strokes.length - 1];
        if (currentStroke) {
            currentStroke.points.push({ x: currentX, y: currentY });
        }
        
        this.lastX = currentX;
        this.lastY = currentY;
    }

    stopDrawing() {
        if (!this.isDrawing) return;
        this.isDrawing = false;
        
        // ストローク完了の通知
        if (this.sessionId) {
            this.sendStrokeData();
        }
    }

    handleTouch(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                        e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        this.whiteboard.dispatchEvent(mouseEvent);
    }

    toggleEraser() {
        this.isErasing = !this.isErasing;
        const eraserBtn = document.getElementById('eraserBtn');
        
        if (this.isErasing) {
            eraserBtn.classList.add('active');
            eraserBtn.textContent = '✏️ ペン';
            this.whiteboard.style.cursor = 'grab';
        } else {
            eraserBtn.classList.remove('active');
            eraserBtn.textContent = '🧽 消しゴム';
            this.whiteboard.style.cursor = 'crosshair';
        }
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.whiteboard.width, this.whiteboard.height);
        this.strokes = [];
        document.getElementById('recognizedText').style.display = 'none';
        
        if (this.sessionId) {
            this.clearWhiteboardSession();
        }
    }

    async sendStrokeData() {
        try {
            const strokeData = {
                session_id: this.sessionId,
                stroke_data: this.strokes[this.strokes.length - 1],
                timestamp: Date.now()
            };
            
            await fetch('/api/star/whiteboard/stroke', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(strokeData)
            });
            
        } catch (error) {
            console.error('Stroke data send error:', error);
        }
    }

    async recognizeHandwriting() {
        if (!this.sessionId) {
            this.showNotification('セッションを開始してください', 'warning');
            return;
        }
        
        try {
            const canvasData = this.whiteboard.toDataURL('image/png');
            
            const response = await fetch('/api/star/whiteboard/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    canvas_data: canvasData,
                    time_spent: 60
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                this.showNotification('認識エラー: ' + result.error, 'error');
                return;
            }
            
            // 認識結果を表示
            const recognizedTextDiv = document.getElementById('recognizedText');
            recognizedTextDiv.textContent = result.recognized_text;
            recognizedTextDiv.classList.add('active');
            
            // 分析結果を更新
            if (result.analysis) {
                this.updateAnalysisDisplay(
                    result.analysis.estimated_pattern || '分析中',
                    result.analysis.progress_stage || '認識完了',
                    result.analysis.estimated_difficulty || '-',
                    result.analysis.confidence_score || 0
                );
                
                if (result.analysis.auto_hints) {
                    this.displayHints(result.analysis.auto_hints);
                }
            }
            
            this.showNotification('手書きを認識しました', 'success');
            
        } catch (error) {
            console.error('Handwriting recognition error:', error);
            this.showNotification('手書き認識に失敗しました', 'error');
        }
    }

    async clearWhiteboardSession() {
        try {
            await fetch('/api/star/whiteboard/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
        } catch (error) {
            console.error('Clear whiteboard error:', error);
        }
    }

    setupEventListeners() {
        // セッション開始
        document.getElementById('startSessionBtn').addEventListener('click', () => {
            this.startSession();
        });

        // 解法分析
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeCurrentInput();
        });

        // ヒント取得
        document.getElementById('hintBtn').addEventListener('click', () => {
            this.getHints();
        });

        // 設定・ヘルプモーダル
        this.setupModalHandlers();

        // 自動分析タイマー
        this.startAutoAnalysis();
    }

    setupModalHandlers() {
        // 設定モーダル
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsModal = document.getElementById('settingsModal');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');
        const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');

        settingsBtn.addEventListener('click', () => {
            this.openSettingsModal();
        });

        saveSettingsBtn.addEventListener('click', () => {
            this.saveSettings();
        });

        cancelSettingsBtn.addEventListener('click', () => {
            this.closeModal(settingsModal);
        });

        // ヘルプモーダル
        const helpBtn = document.getElementById('helpBtn');
        const helpModal = document.getElementById('helpModal');

        helpBtn.addEventListener('click', () => {
            helpModal.classList.add('active');
        });

        // モーダル閉じる
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal);
            });
        });

        // モーダル外クリックで閉じる
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }

    async startSession() {
        try {
            const config = {
                support_level: document.getElementById('supportLevel').value,
                difficulty: document.getElementById('difficulty').value,
                hint_frequency: document.getElementById('hintFrequency').value
            };

            const response = await fetch('/api/star/start_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();

            if (result.error) {
                this.showNotification('セッション開始エラー: ' + result.error, 'error');
                return;
            }

            this.sessionId = result.session_id;
            this.settings = { ...this.settings, ...config };

            // UI切り替え
            document.getElementById('sessionStart').classList.remove('active');
            document.getElementById('problemSolving').classList.add('active');

            this.showNotification('セッションを開始しました！', 'success');
            this.updateAnalysisDisplay('解法を入力してください', '開始', '-', 0);

        } catch (error) {
            console.error('Session start error:', error);
            this.showNotification('セッション開始に失敗しました', 'error');
        }
    }

    async onUserInput() {
        // ホワイトボードベースなので、手書き認識で処理
        // 自動認識は無効化（手動認識ボタンを使用）
        return;
    }

    async analyzeCurrentInput() {
        if (!this.sessionId) {
            this.showNotification('セッションを開始してください', 'warning');
            return;
        }

        // 手書き認識を実行してから分析
        await this.recognizeHandwriting();
    }

    async getHints() {
        if (!this.sessionId) {
            this.showNotification('セッションを開始してください', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/star/get_hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const result = await response.json();

            if (result.error) {
                this.showNotification('ヒント取得エラー: ' + result.error, 'error');
                return;
            }

            this.displayHints(result.hints);
            this.showNotification('ヒントを表示しました', 'info');

        } catch (error) {
            console.error('Hint error:', error);
            this.showNotification('ヒント取得に失敗しました', 'error');
        }
    }

    async loadSolutionExamples() {
        try {
            const response = await fetch('/api/star/solution_examples');
            const result = await response.json();

            if (result.error) {
                console.error('Examples load error:', result.error);
                return;
            }

            this.displaySolutionExamples(result.examples);

        } catch (error) {
            console.error('Examples error:', error);
        }
    }

    displaySolutionExamples(examples) {
        const container = document.getElementById('solutionExamples');
        
        if (!examples || examples.length === 0) {
            container.innerHTML = '<p class="hint-placeholder">解答例を読み込み中...</p>';
            return;
        }

        const examplesHtml = examples.map(example => `
            <div class="example-item" onclick="window.starTutor.selectExample('${example.pattern}')">
                <div class="example-title">${example.pattern}</div>
                <div class="example-description">${example.description}</div>
            </div>
        `).join('');

        container.innerHTML = examplesHtml;
    }

    selectExample(pattern) {
        const userInput = document.getElementById('userInput');
        const currentValue = userInput.value;
        
        if (!currentValue.trim()) {
            userInput.value = `${pattern}で解いてみます。\n\n`;
        } else {
            userInput.value += `\n\n参考: ${pattern}のアプローチ\n`;
        }
        
        userInput.focus();
        this.onUserInput();
    }

    updateAnalysisDisplay(pattern, stage, difficulty, confidence) {
        document.getElementById('currentPattern').textContent = pattern;
        document.getElementById('progressStage').textContent = stage;
        document.getElementById('estimatedDifficulty').textContent = difficulty;
        
        const confidenceBar = document.getElementById('confidenceLevel');
        confidenceBar.style.width = `${Math.max(0, Math.min(100, confidence * 100))}%`;
    }

    displayHints(hints) {
        const container = document.getElementById('hintsContent');
        
        if (!hints || hints.length === 0) {
            container.innerHTML = '<p class="hint-placeholder">ヒントはありません</p>';
            return;
        }

        const hintsHtml = hints.map(hint => {
            const priorityClass = `hint-priority-${hint.priority || 'medium'}`;
            return `
                <div class="hint-item ${priorityClass}">
                    <strong>${hint.type || 'ヒント'}:</strong>
                    <p>${hint.content}</p>
                    ${hint.explanation ? `<small>${hint.explanation}</small>` : ''}
                </div>
            `;
        }).join('');

        container.innerHTML = hintsHtml;
    }

    handleStruggleDetection(suggestions) {
        if (!suggestions || suggestions.length === 0) return;

        const urgentHints = suggestions.filter(s => s.urgency === 'high');
        if (urgentHints.length > 0) {
            this.displayHints(urgentHints);
            this.showNotification('追加のサポートを表示しました', 'info');
        }
    }

    clearWorkspace() {
        this.clearCanvas();
        document.getElementById('hintsContent').innerHTML = 
            '<p class="hint-placeholder">手書きで解法を描いて認識ボタンを押してください。</p>';
        this.updateAnalysisDisplay('分析中...', '初期段階', '-', 0);
    }

    startAutoAnalysis() {
        if (this.analysisTimer) {
            clearInterval(this.analysisTimer);
        }

        // ホワイトボードベースなので自動分析は無効化
        // 手動認識ボタンを使用
        this.analysisTimer = setInterval(() => {
            // ストロークがある場合の軽微な分析のみ
            if (this.strokes.length > 0 && this.sessionId) {
                // 簡単な進捗更新のみ
                this.updateAnalysisDisplay('手書き入力中', '描画中', '-', 0);
            }
        }, this.settings.autoAnalysisInterval * 1000);
    }

    openSettingsModal() {
        const modal = document.getElementById('settingsModal');
        
        // 現在の設定を反映
        document.getElementById('modalSupportLevel').value = this.settings.supportLevel;
        document.getElementById('analysisSensitivity').value = this.settings.analysisSensitivity;
        document.getElementById('autoAnalysisInterval').value = this.settings.autoAnalysisInterval;
        
        // レンジ値の表示更新
        const sensitivityRange = document.getElementById('analysisSensitivity');
        const sensitivityValue = sensitivityRange.nextElementSibling;
        sensitivityValue.textContent = sensitivityRange.value;
        
        sensitivityRange.addEventListener('input', (e) => {
            sensitivityValue.textContent = e.target.value;
        });

        modal.classList.add('active');
    }

    saveSettings() {
        this.settings.supportLevel = document.getElementById('modalSupportLevel').value;
        this.settings.analysisSensitivity = parseInt(document.getElementById('analysisSensitivity').value);
        this.settings.autoAnalysisInterval = parseInt(document.getElementById('autoAnalysisInterval').value);

        // ローカルストレージに保存
        localStorage.setItem('starPentagonSettings', JSON.stringify(this.settings));

        // 自動分析間隔を更新
        this.startAutoAnalysis();

        this.closeModal(document.getElementById('settingsModal'));
        this.showNotification('設定を保存しました', 'success');
    }

    loadSettings() {
        const saved = localStorage.getItem('starPentagonSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }

    closeModal(modal) {
        modal.classList.remove('active');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        // 自動削除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    async endSession() {
        if (!this.sessionId) return;

        try {
            const response = await fetch('/api/star/end_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const result = await response.json();
            
            if (!result.error) {
                this.showNotification('セッションを終了しました', 'info');
            }

        } catch (error) {
            console.error('Session end error:', error);
        }

        this.sessionId = null;
        
        // タイマークリア
        if (this.analysisTimer) {
            clearInterval(this.analysisTimer);
            this.analysisTimer = null;
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.starTutor = new StarPentagonTutor();
});

// ページ離脱時の処理
window.addEventListener('beforeunload', () => {
    if (window.starTutor) {
        window.starTutor.endSession();
    }
});
