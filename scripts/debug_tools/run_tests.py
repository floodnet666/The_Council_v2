import pytest
import sys

if __name__ == "__main__":
    result = pytest.main(["backend/tests/test_api_e2e_true.py", "-v", "-s"])
    sys.exit(result)
