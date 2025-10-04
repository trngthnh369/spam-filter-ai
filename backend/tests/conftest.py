"""
Test configuration and fixtures
"""

import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    os.environ["TESTING"] = "1"
    yield
    del os.environ["TESTING"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])