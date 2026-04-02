/* ========================================
   AI活用タイプ診断 - Quiz Logic (MBTI風)
   ======================================== */

(function () {
    "use strict";

    // --- State ---
    var currentQuestion = 0;
    var scores = {
        assistant: 0,
        creator: 0,
        researcher: 0,
        partner: 0,
        innovator: 0,
    };
    var isTransitioning = false;

    // --- DOM Elements ---
    var startScreen = document.getElementById("start-screen");
    var quizScreen = document.getElementById("quiz-screen");
    var loadingScreen = document.getElementById("loading-screen");
    var startBtn = document.getElementById("start-btn");
    var questionArea = document.getElementById("question-area");
    var progressFill = document.getElementById("progress-fill");
    var progressText = document.getElementById("progress-text");

    // --- Init ---
    if (startBtn) {
        startBtn.addEventListener("click", startQuiz);
    }

    function startQuiz() {
        startScreen.classList.remove("active");
        quizScreen.classList.add("active");
        renderQuestion(0);
    }

    // --- Render Question (MBTI style) ---
    function renderQuestion(index) {
        if (!window.questions || index >= window.questions.length) return;

        var q = window.questions[index];
        var opts = window.answerOptions;
        var total = window.questions.length;
        var pct = ((index + 1) / total) * 100;

        progressFill.style.width = pct + "%";
        progressText.textContent = (index + 1) + " / " + total;

        var html =
            '<div class="question-wrapper">' +
            '  <div class="question-number">Q' + q.id + '</div>' +
            '  <h2 class="question-text">' + escapeHtml(q.text) + '</h2>' +
            '  <div class="likert-choices">';

        for (var i = 0; i < opts.length; i++) {
            html +=
                '<button class="likert-btn" data-score="' + opts[i].score + '">' +
                escapeHtml(opts[i].label) +
                '</button>';
        }

        html += '  </div></div>';

        questionArea.innerHTML = html;

        // Attach click handlers
        var buttons = questionArea.querySelectorAll(".likert-btn");
        for (var j = 0; j < buttons.length; j++) {
            buttons[j].addEventListener("click", onLikertClick);
        }
    }

    // --- Likert Click Handler ---
    function onLikertClick(e) {
        if (isTransitioning) return;
        isTransitioning = true;

        var btn = e.currentTarget;
        var rawScore = parseInt(btn.getAttribute("data-score"), 10);
        var q = window.questions[currentQuestion];

        // 逆転項目: スコアを反転 (3→0, 2→1, 1→2, 0→3)
        var score = q.reverse ? (3 - rawScore) : rawScore;

        // Visual: mark selected
        btn.classList.add("selected");

        // Accumulate score for the primary type
        scores[q.primary] += score;

        // Wait, then advance
        setTimeout(function () {
            currentQuestion++;

            if (currentQuestion >= window.questions.length) {
                showLoading();
            } else {
                transitionToNext();
            }
        }, 400);
    }

    // --- Transition Animation ---
    function transitionToNext() {
        var wrapper = questionArea.querySelector(".question-wrapper");
        if (wrapper) {
            wrapper.classList.add("fade-out");
        }

        setTimeout(function () {
            renderQuestion(currentQuestion);
            isTransitioning = false;
        }, 250);
    }

    // --- Loading & Redirect ---
    function showLoading() {
        quizScreen.classList.remove("active");
        loadingScreen.classList.add("active");

        setTimeout(function () {
            var maxType = "assistant";
            var maxScore = -1;
            var types = Object.keys(scores);
            for (var i = 0; i < types.length; i++) {
                if (scores[types[i]] > maxScore) {
                    maxScore = scores[types[i]];
                    maxType = types[i];
                }
            }
            window.location.href = "/result/" + maxType;
        }, 1500);
    }

    // --- Utility ---
    function escapeHtml(str) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }
})();

/* ========================================
   Copy to Clipboard (Result Page)
   ======================================== */

function copyPrompt(button) {
    var text = button.getAttribute("data-text");
    if (!text) return;

    var tmp = document.createElement("textarea");
    tmp.innerHTML = text;
    var decoded = tmp.value;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(decoded).then(function () {
            showCopied(button);
        });
    } else {
        tmp.value = decoded;
        tmp.style.position = "fixed";
        tmp.style.left = "-9999px";
        document.body.appendChild(tmp);
        tmp.select();
        try {
            document.execCommand("copy");
            showCopied(button);
        } catch (_) {}
        document.body.removeChild(tmp);
    }
}

function showCopied(button) {
    var label = button.querySelector(".copy-label");
    var icon = button.querySelector(".copy-icon");
    if (label) label.textContent = "OK!";
    if (icon) icon.textContent = "\u2714";
    button.classList.add("copied");

    setTimeout(function () {
        if (label) label.textContent = "\u30B3\u30D4\u30FC";
        if (icon) icon.textContent = "\uD83D\uDCCB";
        button.classList.remove("copied");
    }, 2000);
}
