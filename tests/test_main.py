# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

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