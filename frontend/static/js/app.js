class AstroFateApp {
    constructor() {
        this.currentQuestionIndex = 0;
        this.questions = [];
        this.choices = [];
        this.behaviors = [];
        this.questionStartTime = null;
        this.switchCount = 0;
        this.selectedOption = null;
        
        this.init();
    }

    init() {
        this.bindElements();
        this.bindEvents();
        this.initBackgroundStars();
        this.loadQuestions();
    }

    bindElements() {
        this.introScreen = document.getElementById('introScreen');
        this.questionScreen = document.getElementById('questionScreen');
        this.loadingScreen = document.getElementById('loadingScreen');
        this.resultScreen = document.getElementById('resultScreen');

        this.startBtn = document.getElementById('startBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.restartBtn = document.getElementById('restartBtn');

        this.questionText = document.getElementById('questionText');
        this.optionsContainer = document.getElementById('optionsContainer');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');

        this.fortuneText = document.getElementById('fortuneText');
        this.resultStarCanvas = document.getElementById('resultStarCanvas');
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startQuiz());
        this.prevBtn.addEventListener('click', () => this.prevQuestion());
        this.nextBtn.addEventListener('click', () => this.nextQuestion());
        this.restartBtn.addEventListener('click', () => this.restart());
    }

    initBackgroundStars() {
        const canvas = document.getElementById('starCanvas');
        const ctx = canvas.getContext('2d');
        
        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const stars = [];
        const starCount = 100;
        
        for (let i = 0; i < starCount; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1.5 + 0.5,
                opacity: Math.random() * 0.5 + 0.3,
                speed: Math.random() * 0.5 + 0.1
            });
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            stars.forEach(star => {
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(147, 197, 253, ${star.opacity})`;
                ctx.fill();
                
                star.opacity += Math.sin(Date.now() * 0.001 * star.speed) * 0.01;
                star.opacity = Math.max(0.1, Math.min(0.8, star.opacity));
            });
            
            requestAnimationFrame(animate);
        };

        animate();
    }

    async loadQuestions() {
        try {
            const response = await fetch('/api/questions');
            const data = await response.json();
            this.questions = data.questions;
        } catch (error) {
            console.error('Failed to load questions:', error);
        }
    }

    startQuiz() {
        this.currentQuestionIndex = 0;
        this.choices = [];
        this.behaviors = [];
        
        this.showScreen(this.questionScreen);
        this.showQuestion();
    }

    showScreen(screen) {
        document.querySelectorAll('.screen').forEach(s => {
            s.classList.remove('active');
        });
        screen.classList.add('active');
    }

    showQuestion() {
        if (this.questionStartTime !== null) {
            const duration = (Date.now() - this.questionStartTime) / 1000;
            const previousBehavior = this.behaviors[this.currentQuestionIndex];
            if (previousBehavior) {
                previousBehavior.duration_seconds = duration;
            }
        }

        const question = this.questions[this.currentQuestionIndex];
        this.questionText.textContent = question.text;

        this.progressFill.style.width = `${((this.currentQuestionIndex + 1) / this.questions.length) * 100}%`;
        this.progressText.textContent = `${this.currentQuestionIndex + 1} / ${this.questions.length}`;

        this.prevBtn.style.visibility = this.currentQuestionIndex === 0 ? 'hidden' : 'visible';
        this.nextBtn.textContent = this.currentQuestionIndex === this.questions.length - 1 ? '查看结果' : '下一题';

        this.optionsContainer.innerHTML = '';
        this.selectedOption = this.choices[this.currentQuestionIndex] || null;
        this.switchCount = 0;

        question.options.forEach((option, index) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            if (this.selectedOption === option.id) {
                btn.classList.add('selected');
            }
            btn.dataset.optionId = option.id;
            btn.innerHTML = `<span class="option-label">${option.id}</span> ${option.text}`;
            
            btn.addEventListener('click', () => this.selectOption(option.id, btn));
            
            this.optionsContainer.appendChild(btn);
        });

        this.nextBtn.disabled = this.selectedOption === null;
        this.questionStartTime = Date.now();
    }

    selectOption(optionId, btnElement) {
        if (this.selectedOption !== null && this.selectedOption !== optionId) {
            this.switchCount++;
        }

        this.selectedOption = optionId;

        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        btnElement.classList.add('selected');

        this.nextBtn.disabled = false;
    }

    prevQuestion() {
        if (this.currentQuestionIndex > 0) {
            const duration = (Date.now() - this.questionStartTime) / 1000;
            this.behaviors[this.currentQuestionIndex] = {
                question_id: this.currentQuestionIndex + 1,
                duration_seconds: duration,
                switch_count: this.switchCount,
                final_choice: this.selectedOption
            };
            this.choices[this.currentQuestionIndex] = this.selectedOption;

            this.currentQuestionIndex--;
            this.showQuestion();
        }
    }

    nextQuestion() {
        const duration = (Date.now() - this.questionStartTime) / 1000;
        this.behaviors[this.currentQuestionIndex] = {
            question_id: this.currentQuestionIndex + 1,
            duration_seconds: duration,
            switch_count: this.switchCount,
            final_choice: this.selectedOption
        };
        this.choices[this.currentQuestionIndex] = this.selectedOption;

        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            this.showQuestion();
        } else {
            this.submitAnswers();
        }
    }

    async submitAnswers() {
        this.showScreen(this.loadingScreen);

        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    behaviors: this.behaviors,
                    choices: this.choices
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showResult(data);
            } else {
                throw new Error(data.detail || '提交失败');
            }
        } catch (error) {
            console.error('Submit error:', error);
            alert('提交失败，请重试。');
            this.showScreen(this.questionScreen);
        }
    }

    showResult(data) {
        this.fortuneText.textContent = data.fortune;
        this.showScreen(this.resultScreen);
        
        setTimeout(() => {
            this.drawResultStars(data.star_count);
        }, 100);
    }

    drawResultStars(starCount) {
        const canvas = this.resultStarCanvas;
        const ctx = canvas.getContext('2d');
        
        const container = canvas.parentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;

        const stars = [];
        const colors = [
            '#6366f1', '#8b5cf6', '#a855f7', '#ec4899',
            '#3b82f6', '#14b8a6', '#f59e0b', '#ef4444'
        ];

        for (let i = 0; i < starCount; i++) {
            stars.push({
                x: Math.random() * (canvas.width - 60) + 30,
                y: Math.random() * (canvas.height - 60) + 30,
                baseRadius: Math.random() * 8 + 6,
                color: colors[Math.floor(Math.random() * colors.length)],
                pulseSpeed: Math.random() * 2 + 1,
                twinklePhase: Math.random() * Math.PI * 2
            });
        }

        const bgStars = [];
        const bgStarCount = 30;
        
        for (let i = 0; i < bgStarCount; i++) {
            bgStars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1 + 0.5,
                opacity: Math.random() * 0.3 + 0.1,
                twinkleSpeed: Math.random() * 0.002 + 0.001
            });
        }

        let animationId = null;
        const startTime = Date.now();

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            bgStars.forEach(star => {
                star.opacity += Math.sin(Date.now() * star.twinkleSpeed) * 0.01;
                star.opacity = Math.max(0.05, Math.min(0.4, star.opacity));
                
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(147, 197, 253, ${star.opacity})`;
                ctx.fill();
            });

            const elapsed = Date.now() - startTime;
            
            stars.forEach((star, index) => {
                const delay = index * 200;
                const appearProgress = Math.min(Math.max((elapsed - delay) / 1000, 0), 1);
                
                if (appearProgress > 0) {
                    const pulse = Math.sin((elapsed * 0.003 * star.pulseSpeed) + star.twinklePhase);
                    const radius = star.baseRadius + pulse * 3;
                    const glowRadius = radius * 3;

                    const gradient = ctx.createRadialGradient(
                        star.x, star.y, 0,
                        star.x, star.y, glowRadius
                    );
                    gradient.addColorStop(0, star.color + 'aa');
                    gradient.addColorStop(0.5, star.color + '40');
                    gradient.addColorStop(1, star.color + '00');

                    ctx.beginPath();
                    ctx.arc(star.x, star.y, glowRadius, 0, Math.PI * 2);
                    ctx.fillStyle = gradient;
                    ctx.globalAlpha = appearProgress;
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(star.x, star.y, radius, 0, Math.PI * 2);
                    ctx.fillStyle = star.color;
                    ctx.globalAlpha = appearProgress;
                    ctx.fill();

                    ctx.beginPath();
                    const coreRadius = radius * 0.3;
                    ctx.arc(star.x, star.y, coreRadius, 0, Math.PI * 2);
                    ctx.fillStyle = 'white';
                    ctx.globalAlpha = appearProgress * 0.8;
                    ctx.fill();

                    ctx.globalAlpha = 1;
                }
            });

            animationId = requestAnimationFrame(animate);
        };

        animate();

        const resizeHandler = () => {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        };

        window.addEventListener('resize', resizeHandler);
        
        const originalRestart = this.restart.bind(this);
        this.restart = () => {
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
            window.removeEventListener('resize', resizeHandler);
            this.restart = originalRestart;
            originalRestart();
        };
    }

    restart() {
        this.currentQuestionIndex = 0;
        this.choices = [];
        this.behaviors = [];
        this.questionStartTime = null;
        this.switchCount = 0;
        this.selectedOption = null;

        this.showScreen(this.introScreen);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AstroFateApp();
});
