"""Prototype login contract: actual router/model, stubbed CLI/database boundary."""
import importlib.util
import sys
import types
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.common.errors import AccountError, EmailMismatchError, InvalidPasswordError


@pytest.fixture
def login_module(monkeypatch):
    stub = types.ModuleType("src.core.login_logic")
    stub.api_login = lambda **kwargs: (kwargs["input_email"], 7, b"SERVER-KEY-NEVER-SEND")
    monkeypatch.setitem(sys.modules, "src.core.login_logic", stub)
    path = Path(__file__).resolve().parents[2] / "src/api/routers/auth/login.py"
    spec = importlib.util.spec_from_file_location("prototype_login_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def client(login_module):
    app = FastAPI()
    app.include_router(login_module.login_router)
    with TestClient(app) as client:
        yield client


def test_safe_response_and_parameter_mapping(client, login_module, monkeypatch):
    calls = []
    def verify(**kwargs):
        calls.append(kwargs)
        return kwargs["input_email"], 7, b"SERVER-KEY-NEVER-SEND"
    monkeypatch.setattr(login_module, "api_login", verify)
    response = client.post("/auth/login", json={"email":"qa@example.invalid", "password":"Fictional-test-password!"})
    assert response.status_code == 200
    assert response.json() == {"verified":True,"session_created":False,"user":{"id":"7","email":"qa@example.invalid"}}
    assert calls == [{"input_email":"qa@example.invalid", "input_password":"Fictional-test-password!"}]
    assert "SERVER-KEY" not in response.text
    assert "Fictional-test-password" not in response.text
    assert "set-cookie" not in response.headers
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("error_type", [AccountError, EmailMismatchError, InvalidPasswordError])
def test_generic_401(client, login_module, monkeypatch, error_type):
    def fail(**kwargs):
        raise error_type("PRIVATE DEBUG DETAIL")
    monkeypatch.setattr(login_module, "api_login", fail)
    response = client.post("/auth/login", json={"email":"qa@example.invalid", "password":"Wrong-test-password"})
    assert response.status_code == 401
    assert response.json() == {"detail":"Invalid email or password."}
    assert response.headers["cache-control"] == "no-store"


def test_validation_and_fixed_route(client, login_module, monkeypatch):
    def must_not_run(**kwargs):
        raise AssertionError("Verification must not run")
    monkeypatch.setattr(login_module, "api_login", must_not_run)
    assert client.post("/auth/login", json={"email":"qa@example.invalid"}).status_code == 422
    assert client.post("/auth/something-else", json={"email":"qa@example.invalid", "password":"test"}).status_code == 404
