"""Command-line health check diagnostic script.

Usage:
    python -m app.health
"""

import json
import sys

from app.bootstrap import create_platform_service


def run_diagnostics() -> int:
    try:
        service = create_platform_service()
        health = service.health_check()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        service.close()
        return 0 if health["status"] == "healthy" else 1
    except Exception as e:
        error_output = {
            "status": "unhealthy",
            "error": str(e),
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(run_diagnostics())
