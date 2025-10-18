# Alex Backend Tests

Automated test suite for Alex Backend API.

## Setup

Install test dependencies:
```bash
pip3 install pytest pytest-cov
```

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_auth.py
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run tests by marker:
```bash
pytest -m auth  # Run only authentication tests
pytest -m api   # Run only API tests
```

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_auth.py` - Authentication endpoint tests
- `test_tasks.py` - Task API endpoint tests

## Markers

- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
