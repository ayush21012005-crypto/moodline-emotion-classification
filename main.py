# ============================================================
# IMPORTS
# ============================================================

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

import numpy as np
import pickle
import re
import os


# ============================================================
# 1. BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# 2. PATHS
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "Artifacts",
    "BiGRU_Model.keras"
)

TOKENIZER_PATH = os.path.join(
    BASE_DIR,
    "Artifacts",
    "tokenizer.pkl"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

INDEX_FILE = os.path.join(
    STATIC_DIR,
    "index.html"
)


# ============================================================
# 3. MODEL SETTINGS
# ============================================================

MAX_SEQUENCE_LENGTH = 50


# ============================================================
# 4. EMOTION LABELS
# ============================================================

emotion_labels = [
    "sadness",
    "joy",
    "love",
    "anger",
    "fear",
    "surprise"
]


# ============================================================
# 5. EMOTION EMOJIS
# ============================================================

EMOTION_EMOJIS = {
    "sadness": "😢",
    "joy": "😄",
    "love": "❤️",
    "anger": "😠",
    "fear": "😨",
    "surprise": "😲"
}


# ============================================================
# 6. TEXT PREPROCESSING
# ============================================================

def preprocess_text(text: str) -> str:

    text = text.lower()

    # Remove apostrophes
    text = re.sub(
        r"'",
        "",
        text
    )

    # Remove special characters
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# 7. REQUEST MODEL
# ============================================================

class TextInput(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text for emotion prediction",
        json_schema_extra={
            "example": "I feel very happy today"
        }
    )


# ============================================================
# 8. RESPONSE MODEL
# ============================================================

class PredictionResponse(BaseModel):

    text: str

    predicted_emotion: str

    emoji: str

    confidence: float

    all_probabilities: dict[str, float]


# ============================================================
# 9. HEALTH RESPONSE
# ============================================================

class HealthResponse(BaseModel):

    status: str

    model_loaded: bool


# ============================================================
# 10. MODEL STORAGE
# ============================================================

dl_model = {
    "BiGRU": None,
    "Tokenizer": None
}


# ============================================================
# 11. LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print()
    print("==========================================")
    print("Starting FastAPI application...")
    print("==========================================")

    print()
    print("Base directory:")
    print(BASE_DIR)

    print()
    print("Model path:")
    print(MODEL_PATH)

    print()
    print("Tokenizer path:")
    print(TOKENIZER_PATH)

    # --------------------------------------------------------
    # Check model
    # --------------------------------------------------------

    if not os.path.isfile(MODEL_PATH):

        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    print("Model file found.")

    # --------------------------------------------------------
    # Check tokenizer
    # --------------------------------------------------------

    if not os.path.isfile(TOKENIZER_PATH):

        raise FileNotFoundError(
            f"Tokenizer file not found: {TOKENIZER_PATH}"
        )

    print("Tokenizer file found.")

    # --------------------------------------------------------
    # Check static
    # --------------------------------------------------------

    os.makedirs(
        STATIC_DIR,
        exist_ok=True
    )

    if os.path.isfile(INDEX_FILE):

        print("index.html found.")

    else:

        print(
            "WARNING: static/index.html not found."
        )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    try:

        print()
        print("Loading BiGRU model...")

        dl_model["BiGRU"] = load_model(
            MODEL_PATH
        )

        print(
            "BiGRU model loaded successfully."
        )

        # ----------------------------------------------------
        # Load tokenizer
        # ----------------------------------------------------

        print()
        print("Loading tokenizer...")

        with open(
            TOKENIZER_PATH,
            "rb"
        ) as file:

            dl_model["Tokenizer"] = pickle.load(
                file
            )

        print(
            "Tokenizer loaded successfully."
        )

        print()
        print("==========================================")
        print("Model and tokenizer loaded successfully.")
        print("Server is ready.")
        print("==========================================")
        print()

    except Exception as e:

        print()
        print("ERROR WHILE LOADING MODEL/TOKENIZER")
        print(str(e))

        raise

    yield

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    print()
    print("Shutting down server...")

    dl_model["BiGRU"] = None
    dl_model["Tokenizer"] = None

    print(
        "Model and tokenizer removed from memory."
    )


# ============================================================
# 12. CREATE FASTAPI APP
# ============================================================

app = FastAPI(

    title="BiGRU Emotion Prediction API",

    description=(
        "Deep Learning based Emotion "
        "Prediction using BiGRU"
    ),

    version="1.0.0",

    lifespan=lifespan
)


# ============================================================
# 13. CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# 14. STATIC DIRECTORY
# ============================================================

os.makedirs(
    STATIC_DIR,
    exist_ok=True
)


# ============================================================
# 15. STATIC FILES
# ============================================================

app.mount(

    "/static",

    StaticFiles(
        directory=STATIC_DIR
    ),

    name="static"

)


# ============================================================
# 16. HOME PAGE
# ============================================================

@app.get(
    "/",
    include_in_schema=False
)
async def home():

    if not os.path.isfile(INDEX_FILE):

        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Moodline API</title>
            </head>

            <body>

                <h1>
                    Moodline API is running
                </h1>

                <p>
                    index.html was not found.
                </p>

                <a href="/docs">
                    Open API Documentation
                </a>

            </body>
            </html>
            """
        )

    return FileResponse(
        INDEX_FILE
    )


# ============================================================
# 17. HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse
)
async def health_check():

    model_loaded = (

        dl_model["BiGRU"] is not None

        and

        dl_model["Tokenizer"] is not None

    )

    return HealthResponse(

        status="Server is running",

        model_loaded=model_loaded

    )


# ============================================================
# 18. PREDICT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
async def predict_emotion(
    text_input: TextInput
):

    # --------------------------------------------------------
    # Get model
    # --------------------------------------------------------

    BiGRU_model = dl_model["BiGRU"]

    tokenizer_model = dl_model["Tokenizer"]

    # --------------------------------------------------------
    # Check model
    # --------------------------------------------------------

    if (
        BiGRU_model is None
        or
        tokenizer_model is None
    ):

        raise HTTPException(

            status_code=503,

            detail=(
                "Model is not loaded. "
                "Please try again later."
            )

        )

    # --------------------------------------------------------
    # Original text
    # --------------------------------------------------------

    original_text = text_input.text

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    cleaned_text = preprocess_text(
        original_text
    )

    if not cleaned_text:

        raise HTTPException(

            status_code=400,

            detail="Please enter valid text."

        )

    # --------------------------------------------------------
    # Tokenization
    # --------------------------------------------------------

    tokenized_text = (
        tokenizer_model.texts_to_sequences(
            [cleaned_text]
        )
    )

    # --------------------------------------------------------
    # Padding
    # --------------------------------------------------------

    padded_sequence = pad_sequences(

        tokenized_text,

        maxlen=MAX_SEQUENCE_LENGTH,

        padding="post",

        truncating="post"

    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    try:

        probabilities = (
            BiGRU_model.predict(
                padded_sequence,
                verbose=0
            )[0]
        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=f"Prediction failed: {str(e)}"

        )

    # --------------------------------------------------------
    # Convert probabilities
    # --------------------------------------------------------

    probabilities = np.asarray(

        probabilities,

        dtype=float

    )

    # --------------------------------------------------------
    # Validate output
    # --------------------------------------------------------

    if len(probabilities) != len(
        emotion_labels
    ):

        raise HTTPException(

            status_code=500,

            detail=(
                "Model output size does not "
                "match emotion labels."
            )

        )

    # --------------------------------------------------------
    # Find top emotion
    # --------------------------------------------------------

    top_emotion_index = int(

        np.argmax(
            probabilities
        )

    )

    predicted_emotion = (

        emotion_labels[
            top_emotion_index
        ]

    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = float(

        probabilities[
            top_emotion_index
        ]

    )

    # --------------------------------------------------------
    # All probabilities
    # --------------------------------------------------------

    all_probabilities = {

        label: float(probability)

        for label, probability

        in zip(
            emotion_labels,
            probabilities
        )

    }

    # --------------------------------------------------------
    # Emoji
    # --------------------------------------------------------

    emoji = EMOTION_EMOJIS.get(

        predicted_emotion,

        ""

    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return PredictionResponse(

        text=original_text,

        predicted_emotion=predicted_emotion,

        emoji=emoji,

        confidence=confidence,

        all_probabilities=all_probabilities

    )


# ============================================================
# 19. API INFO
# ============================================================

@app.get(
    "/api-info",
    include_in_schema=False
)
async def api_info():

    return {

        "project":
            "BiGRU Emotion Prediction",

        "status":
            "running",

        "model_loaded":
            dl_model["BiGRU"] is not None,

        "tokenizer_loaded":
            dl_model["Tokenizer"] is not None,

        "endpoints": {

            "home": "/",

            "health": "/health",

            "predict": "/predict",

            "docs": "/docs"

        }

    }