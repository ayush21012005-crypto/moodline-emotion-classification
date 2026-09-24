# 🧠 Moodline — Emotion Classification using BiGRU

An end-to-end Deep Learning project that detects human emotions from text using a Bidirectional GRU (BiGRU) neural network.

The project includes a trained TensorFlow/Keras model, FastAPI backend, and an interactive HTML/CSS/JavaScript frontend.

---

## 🚀 Project Overview

Moodline is a text emotion classification application that predicts one of six emotions from user-provided text.

### Supported Emotions

- 😢 Sadness
- 😄 Joy
- ❤️ Love
- 😠 Anger
- 😨 Fear
- 😲 Surprise

---

## 🏗️ Project Architecture

```text
User
  │
  ▼
HTML / CSS / JavaScript
  │
  │ HTTP POST /predict
  ▼
FastAPI Backend
  │
  ▼
Text Preprocessing
  │
  ▼
Tokenizer
  │
  ▼
Padding
  │
  ▼
BiGRU Deep Learning Model
  │
  ▼
Emotion Prediction
  │
  ▼
Emotion + Confidence + Probabilities
