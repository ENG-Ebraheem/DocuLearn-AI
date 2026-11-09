from unittest.mock import patch
import pytest

from app.health import run_diagnostics


class TestPhase9Staging:

    @patch("app.health.create_platform_service")
    def test_run_diagnostics_healthy_returns_zero(self, mock_create):
        mock_service = mock_create.return_value
        mock_service.health_check.return_value = {
            "status": "healthy",
            "database": True,
            "vector_store": True,
            "embedding_provider": True,
            "llm_configured": True,
        }
        exit_code = run_diagnostics()
        assert exit_code == 0
        mock_service.close.assert_called_once()

    @patch("app.health.create_platform_service")
    def test_run_diagnostics_degraded_returns_one(self, mock_create):
        mock_service = mock_create.return_value
        mock_service.health_check.return_value = {
            "status": "degraded",
            "database": False,
            "vector_store": True,
            "embedding_provider": True,
            "llm_configured": False,
        }
        exit_code = run_diagnostics()
        assert exit_code == 1
