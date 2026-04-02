/* ========================================
   AI活用タイプ診断 - Quiz Logic
   ======================================== */

(function () {
    "use strict";

    // --- State ---
    let currentQuestion = 0;
    const scores = {
        assistant: 0,
        creator: 0,
        researcher: 0,
        partner: 0,
        innovator: 0,
    };
    let isTransitioning = false;

    // --- DOM Elements ---
    const startScreen = document.getElementById("start-screen");
    const quizScreen = document.getElementById("quiz-screen");
    const loadingScreen = document.getElementById("loading-screen");
    const startBtn = document.getElementById("start-btn");
    const questionArea = document.getElementById("question-area");
    const progressFill = document.getElementById("progress-fill");
    const progressText = document.getElementById("progress-text");

    // --- Init ---
    if (startBtn) {
        startBtn.addEventListener("click", startQuiz);
    }

    function startQuiz() {
        startScreen.classList.remove("active");
        quizScreen.classList.add("active");
        renderQuestion(0);
    }

    // --- Render Question ---
    function renderQuestion(index) {
        if (!window.questions || index >= window.questions.length) return;

        const q = window.questions[index];
        const pct = ((index + 1) / window.questions.length) * 100;

        progressFill.style.width = pct + "%";
        progressText.textContent = (index + 1) + " / " + window.questions.length;

        const html =
            '<div class="question-wrapper">' +
            '  <div class="question-number">Q' + q.id + '</div>' +
            '  <h2 class="question-text">' + escapeHtml(q.text) + '</h2>' +
            '  <div class="choices">' +
            q.choices
                .map(function (c, i) {
                    return (
                        '<button class="choice-btn" data-index="' + i + '">' +
                        '  <span class="choice-label">' + c.label + '</span>' +
                        '  <span class="choice-text">' + escapeHtml(c.text) + '</span>' +
                        '</button>'
                    );
                })
                .join("") +
            '  </div>' +
            '</div>';

        questionArea.innerHTML = html;

        // Attach click handlers
        var buttons = questionArea.querySelectorAll(".choice-btn");
        for (var j = 0; j < buttons.length; j++) {
            buttons[j].addEventListener("click", onChoiceClick);
        }
    }

    // --- Choice Click Handler ---
    function onChoiceClick(e) {
        if (isTransitioning) return;
        isTransitioning = true;

        var btn = e.currentTarget;
        var choiceIndex = parseInt(btn.getAttribute("data-index"), 10);
        var q = window.questions[currentQuestion];
        var choice = q.choices[choiceIndex];

        // Visual: mark selected
        btn.classList.add("selected");

        // Accumulate scores
        var types = Object.keys(choice.scores);
        for (var i = 0; i < types.length; i++) {
            scores[types[i]] += choice.scores[types[i]];
        }

        // Wait, then advance
        setTimeout(function () {
            currentQuestion++;

            if (currentQuestion >= window.questions.length) {
                showLoading();
            } else {
                transitionToNext();
            }
        }, 500);
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
        }, 300);
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

    // Decode HTML entities
    var tmp = document.createElement("textarea");
    tmp.innerHTML = text;
    var decoded = tmp.value;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(decoded).then(function () {
            showCopied(button);
        });
    } else {
        // Fallback
        tmp.value = decoded;
        tmp.style.position = "fixed";
        tmp.style.left = "-9999px";
        document.body.appendChild(tmp);
        tmp.select();
        try {
            document.execCommand("copy");
            showCopied(button);
        } catch (_) {
            // silent fail
        }
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
