(() => {

    "use strict";


    // ============================================================
    // FASTAPI BACKEND URL
    // ============================================================

    // IMPORTANT:
    // Live Server runs on:
    // http://127.0.0.1:5500
    //
    // FastAPI runs on:
    // http://127.0.0.1:8000
    //
    // Therefore API requests MUST go to port 8000.

    const API_BASE_URL =
        "http://127.0.0.1:8000";


    // ============================================================
    // EMOJIS
    // ============================================================

    const EMOJI = {

        sadness: "😢",

        joy: "😄",

        love: "❤️",

        anger: "😠",

        fear: "😨",

        surprise: "😲"

    };


    // ============================================================
    // HTML ELEMENTS
    // ============================================================

    const el = {

        statusDot:
            document.getElementById(
                "statusDot"
            ),

        serverStatusText:
            document.getElementById(
                "serverStatusText"
            ),

        textInput:
            document.getElementById(
                "textInput"
            ),

        charCount:
            document.getElementById(
                "charCount"
            ),

        analyzeBtn:
            document.getElementById(
                "analyzeBtn"
            ),

        errorMsg:
            document.getElementById(
                "errorMsg"
            ),

        orb:
            document.getElementById(
                "orb"
            ),

        orbEmoji:
            document.getElementById(
                "orbEmoji"
            ),

        resultSection:
            document.getElementById(
                "resultSection"
            ),

        emotionWord:
            document.getElementById(
                "emotionWord"
            ),

        emotionEmoji:
            document.getElementById(
                "emotionEmoji"
            ),

        confidenceText:
            document.getElementById(
                "confidenceText"
            ),

        echoedText:
            document.getElementById(
                "echoedText"
            ),

        barsContainer:
            document.getElementById(
                "barsContainer"
            )

    };


    // ============================================================
    // MODEL STATUS
    // ============================================================

    let modelReady = false;


    // ============================================================
    // HEALTH CHECK
    // ============================================================

    async function checkHealth() {

        try {

            console.log(
                "Checking FastAPI:"
            );

            console.log(
                `${API_BASE_URL}/health`
            );


            const response =
                await fetch(
                    `${API_BASE_URL}/health`
                );


            if (!response.ok) {

                throw new Error(
                    `Health check failed: ${response.status}`
                );

            }


            const data =
                await response.json();


            console.log(
                "Health response:",
                data
            );


            modelReady =
                data.model_loaded === true;


            if (modelReady) {

                setStatus(
                    "live",
                    "model ready — say something"
                );

            }

            else {

                setStatus(
                    "warming",
                    "model is loading…"
                );


                setTimeout(
                    checkHealth,
                    3000
                );

            }


        }

        catch (error) {

            console.error(
                "Health check error:",
                error
            );


            modelReady = false;


            setStatus(
                "down",
                "can't reach FastAPI server"
            );


            setTimeout(
                checkHealth,
                5000
            );

        }


        syncButtonState();

    }


    // ============================================================
    // SERVER STATUS
    // ============================================================

    function setStatus(
        kind,
        text
    ) {

        el.statusDot.className =
            "brand-mark " + kind;


        el.serverStatusText.textContent =
            text;

    }


    // ============================================================
    // INPUT
    // ============================================================

    el.textInput.addEventListener(
        "input",
        () => {

            el.charCount.textContent =
                el.textInput.value.length;


            syncButtonState();

        }
    );


    // ============================================================
    // CTRL + ENTER
    // ============================================================

    el.textInput.addEventListener(
        "keydown",
        (event) => {

            if (
                (event.ctrlKey ||
                 event.metaKey) &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                runAnalysis();

            }

        }
    );


    // ============================================================
    // BUTTON STATE
    // ============================================================

    function syncButtonState() {

        const hasText =
            el.textInput.value.trim().length > 0;


        el.analyzeBtn.disabled =
            !hasText ||
            !modelReady;

    }


    // ============================================================
    // BUTTON CLICK
    // ============================================================

    el.analyzeBtn.addEventListener(
        "click",
        runAnalysis
    );


    // ============================================================
    // PREDICTION
    // ============================================================

    async function runAnalysis() {

        const text =
            el.textInput.value.trim();


        if (!text) {

            showError(
                "Please enter some text."
            );

            return;

        }


        if (!modelReady) {

            showError(
                "The model is not ready yet."
            );

            return;

        }


        hideError();

        enterThinking();


        try {

            console.log(
                "Sending text to FastAPI:",
                text
            );


            const response =
                await fetch(
                    `${API_BASE_URL}/predict`,
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body: JSON.stringify({

                            text: text

                        })

                    }
                );


            const data =
                await response.json();


            console.log(
                "Prediction response:",
                data
            );


            if (!response.ok) {

                throw new Error(

                    data.detail ||

                    `Request failed: ${response.status}`

                );

            }


            renderResult(
                data,
                text
            );

        }

        catch (error) {

            console.error(
                "Prediction error:",
                error
            );


            exitThinking(false);


            showError(
                error.message ||
                "Prediction failed."
            );

        }

    }


    // ============================================================
    // THINKING
    // ============================================================

    function enterThinking() {

        el.analyzeBtn.classList.add(
            "loading"
        );


        el.analyzeBtn
            .querySelector(
                ".btn-label"
            )
            .textContent =
                "Reading…";


        el.analyzeBtn.disabled =
            true;


        el.orb.classList.remove(
            "settled"
        );


        el.orb.classList.add(
            "thinking"
        );


        el.orbEmoji.style.opacity =
            "0";

    }


    // ============================================================
    // EXIT THINKING
    // ============================================================

    function exitThinking(
        success
    ) {

        el.analyzeBtn.classList.remove(
            "loading"
        );


        el.analyzeBtn
            .querySelector(
                ".btn-label"
            )
            .textContent =
                "Read the mood";


        el.orb.classList.remove(
            "thinking"
        );


        syncButtonState();


        if (!success) {

            el.orbEmoji.textContent =
                "✎";


            el.orbEmoji.style.opacity =
                "1";

        }

    }


    // ============================================================
    // DISPLAY RESULT
    // ============================================================

    function renderResult(
        data,
        originalText
    ) {

        console.log(
            "Rendering:",
            data
        );


        const emotion =
            data.predicted_emotion;


        const emoji =
            data.emoji ||
            EMOJI[emotion] ||
            "🙂";


        // Change page emotion color

        document.body.setAttribute(
            "data-emotion",
            emotion
        );


        // Orb

        el.orb.classList.add(
            "settled"
        );


        el.orbEmoji.textContent =
            emoji;


        el.orbEmoji.style.opacity =
            "1";


        exitThinking(true);


        // Emotion

        el.emotionWord.textContent =
            capitalize(
                emotion
            );


        el.emotionEmoji.textContent =
            emoji;


        // Confidence

        const confidence =
            Number(
                data.confidence
            );


        el.confidenceText.textContent =
            `${(
                confidence * 100
            ).toFixed(1)}% confidence`;


        // Original text

        el.echoedText.textContent =
            `“${originalText}”`;


        // IMPORTANT:
        // Correct backend property name

        renderBars(
            data.all_probabilities
        );


        // Show result

        el.resultSection.hidden =
            false;


        el.resultSection.classList.remove(
            "entering"
        );


        void el.resultSection.offsetWidth;


        el.resultSection.classList.add(
            "entering"
        );


        el.resultSection.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    }


    // ============================================================
    // PROBABILITY BARS
    // ============================================================

    function renderBars(
        probabilities
    ) {

        if (!probabilities) {

            console.error(
                "all_probabilities missing"
            );

            return;

        }


        const entries =
            Object.entries(
                probabilities
            ).sort(
                (a, b) =>
                    b[1] - a[1]
            );


        el.barsContainer.innerHTML =
            "";


        entries.forEach(
            ([label, value], index) => {

                const percentage =
                    Number(value) * 100;


                const row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    `bar-row bar-${label}`;


                row.innerHTML = `

                    <span class="bar-label">

                        ${EMOJI[label] || ""}

                        ${label}

                    </span>

                    <span class="bar-track">

                        <span class="bar-fill">
                        </span>

                    </span>

                    <span class="bar-pct">

                        ${percentage.toFixed(1)}%

                    </span>

                `;


                el.barsContainer.appendChild(
                    row
                );


                const fill =
                    row.querySelector(
                        ".bar-fill"
                    );


                setTimeout(
                    () => {

                        fill.style.width =
                            `${percentage}%`;

                    },
                    100 +
                    index * 100
                );

            }
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    function showError(
        message
    ) {

        el.errorMsg.textContent =
            message;


        el.errorMsg.hidden =
            false;

    }


    function hideError() {

        el.errorMsg.hidden =
            true;

    }


    // ============================================================
    // CAPITALIZE
    // ============================================================

    function capitalize(
        text
    ) {

        if (!text) {

            return "";

        }


        return (
            text.charAt(0).toUpperCase() +
            text.slice(1)
        );

    }


    // ============================================================
    // START
    // ============================================================

    checkHealth();

})();