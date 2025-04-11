# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
import base64
import logging

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the SimFin Analysis API"}

def test_analysis_valid_ticker():
    response = client.get("/analysis/AMZN")
    assert response.status_code == 200
    assert "data" in response.json()
    assert "image" in response.json()

def test_analysis_invalid_ticker():
    response = client.get("/analysis/INVALID")
    assert response.status_code == 404

def test_analysis_empty_ticker():
    response = client.get("/analysis/")
    assert response.status_code == 404  # או 400, תלוי בהגדרה של FastAPI

def test_analysis_invalid_characters():
    response = client.get("/analysis/!@#")
    assert response.status_code == 400
    assert "detail" in response.json()

def test_analysis_valid_image():
    response = client.get("/analysis/AMZN")
    assert response.status_code == 200
    image_data = response.json()["image"]
    # ודא שהמחרוזת היא Base64 תקינה
    try:
        base64.b64decode(image_data)
    except Exception as e:
        pytest.fail(f"Invalid Base64 string: {e}")

def test_logging_on_error(caplog):
    caplog.set_level(logging.INFO)
    response = client.get("/analysis/INVALID")
    assert response.status_code == 500
    assert "Error processing ticker INVALID" in caplog.text