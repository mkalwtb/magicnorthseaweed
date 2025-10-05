# Magic North Seaweed Test Suite

This directory contains comprehensive tests for the Magic North Seaweed surf forecasting system.

## Test Structure

### Test Files

- **`test_spots.py`** - Tests for spot definitions, data processing, and spot-related functionality
- **`test_models.py`** - Tests for ML model functionality, training, and prediction
- **`test_stormglass.py`** - Tests for weather data API integration (with minimal API calls)
- **`test_webtables.py`** - Tests for HTML table generation and web interface
- **`test_django_views.py`** - Tests for Django web interface and views
- **`test_alert_system.py`** - Tests for email alert system and notifications
- **`test_surffeedback.py`** - Tests for surf feedback data processing
- **`test_plotting.py`** - Tests for data visualization and plotting
- **`test_integration.py`** - Integration tests for complete system workflows

### Configuration Files

- **`conftest.py`** - Pytest configuration, fixtures, and shared test utilities
- **`pytest.ini`** - Pytest settings and test markers
- **`README.md`** - This documentation file

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Files
```bash
pytest tests/test_spots.py
pytest tests/test_models.py
pytest tests/test_stormglass.py
```

### Run Tests by Category
```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Django tests only
pytest tests/ -m django

# Exclude slow tests
pytest tests/ -m "not slow"
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=data --cov=forecast --cov=alert
```

## Test Categories

### Unit Tests
- Individual function testing
- Data structure validation
- Error handling
- Edge cases

### Integration Tests
- Complete workflow testing
- Module interaction testing
- Data flow validation
- System configuration testing

### Django Tests
- Web interface testing
- URL routing
- View functionality
- Template rendering

## Test Features

### Mocking and Fixtures
- **Stormglass API mocking** - All external API calls are mocked to avoid rate limits
- **File system mocking** - File operations are mocked to avoid creating actual files
- **Database mocking** - Database operations are mocked for Django tests
- **Email mocking** - Email sending is mocked to avoid actual email delivery

### Test Data
- **Sample weather data** - Realistic weather forecast data for testing
- **Sample feedback data** - Surf feedback data for testing
- **Mock spots** - Test spot definitions
- **Mock models** - Test ML models

### Modern Testing Practices
- **Pytest fixtures** - Reusable test components
- **Parametrized tests** - Multiple test cases with different inputs
- **Async testing** - Support for asynchronous operations
- **Coverage reporting** - Code coverage analysis
- **Performance testing** - Performance characteristics validation

## Test Coverage

The test suite covers:

- **Core functionality** - All major functions and classes
- **Data processing** - Weather data, surf feedback, and forecast processing
- **Web interface** - Django views, templates, and URL routing
- **Alert system** - Email notifications and alert management
- **ML models** - Model training, prediction, and evaluation
- **API integration** - Stormglass API integration (mocked)
- **Error handling** - Error conditions and edge cases
- **Performance** - System performance characteristics

## Best Practices

### Test Organization
- Tests are organized by module/functionality
- Each test file focuses on a specific area
- Integration tests are separate from unit tests
- Django tests are clearly marked

### Test Data Management
- Test data is generated programmatically
- No external dependencies
- Realistic but controlled data
- Easy to modify and extend

### Mocking Strategy
- External APIs are mocked
- File operations are mocked
- Database operations are mocked
- Email sending is mocked
- Only 1-2 actual Stormglass API calls for integration testing

### Error Testing
- Invalid inputs are tested
- Edge cases are covered
- Error conditions are validated
- Graceful failure is ensured

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- **Fast execution** - Most tests complete quickly
- **No external dependencies** - All external services are mocked
- **Deterministic results** - Tests produce consistent results
- **Clear reporting** - Detailed test output and coverage reports

## Maintenance

### Adding New Tests
1. Create test functions with `test_` prefix
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Add test markers for categorization
5. Update documentation as needed

### Updating Tests
1. Keep tests synchronized with code changes
2. Update fixtures when data structures change
3. Maintain test coverage
4. Review and update test documentation

### Debugging Tests
1. Use `pytest -v` for verbose output
2. Use `pytest --tb=short` for shorter tracebacks
3. Use `pytest -s` to see print statements
4. Use `pytest --pdb` to drop into debugger on failures
