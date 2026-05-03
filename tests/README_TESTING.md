"""
Unit Testing Guide for ReviewPilot

This document provides information about the unit tests for the ReviewPilot application.

## Test Structure

The tests follow the same directory structure as the main app/ directory for easy navigation:

```
tests/
├── conftest.py                          # Pytest fixtures and configuration
├── core/
│   ├── api/
│   │   └── test_client.py              # APIClient tests
│   ├── services/
│   │   ├── test_review_service.py      # ReviewService tests
│   │   ├── test_github_service.py      # GithubService tests
│   │   ├── test_embedding_service.py   # EmbeddingService tests
│   │   └── test_chatbot_service.py     # ChatbotService tests
│   └── utils/
│       └── (utility tests)
├── workers/
│   ├── test_review_worker.py           # review_worker tests
│   └── test_chatbot_worker.py          # chatbot_worker tests
└── webhook/
    ├── test_event_dispatcher.py         # WebhookEventDispatcher tests
    └── event_handlers/
        ├── test_pull_request_event_handler.py
        └── test_issue_comment_event_handler.py
```

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-mock pytest-asyncio
```

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/core/services/test_review_service.py
```

### Run Specific Test Class
```bash
pytest tests/core/services/test_review_service.py::TestReviewService
```

### Run Specific Test
```bash
pytest tests/core/services/test_review_service.py::TestReviewService::test_init
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Tests with Print Statements
```bash
pytest -s
```

## Test Coverage by Module

### Core Services Tests
- **ReviewService** (test_review_service.py)
  - Initialization
  - Successful PR review flow
  - Error handling (diff retrieval, context fetch)
  - Multi-file PR handling

- **GithubService** (test_github_service.py)
  - PR file retrieval
  - PR diff generation
  - Comment posting
  - Error handling for API calls

- **EmbeddingService** (test_embedding_service.py)
  - Repository embeddings creation
  - Chunk embedding generation
  - Context retrieval from vectorstore
  - Code summary generation

- **ChatbotService** (test_chatbot_service.py)
  - Query processing
  - PR context integration
  - Response formatting with sender mentions

### Workers Tests
- **review_worker** (test_review_worker.py)
  - Successful task execution
  - Multiple concurrent reviews
  - Error handling and retries
  - Correct service initialization

- **chatbot_worker** (test_chatbot_worker.py)
  - Chat message processing
  - Query handling
  - Multiple conversations
  - Special character handling

### Webhook Tests
- **EventDispatcher** (test_event_dispatcher.py)
  - Event routing to correct handlers
  - Unknown event handling
  - Multiple events in sequence

- **PullRequestEventHandler** (test_pull_request_event_handler.py)
  - PR opened event (review queued)
  - PR synchronize event
  - PR reopened event
  - PR closed/merged event
  - Payload validation

- **IssueCommentEventHandler** (test_issue_comment_event_handler.py)
  - Comment on PR handling
  - Query extraction from comments
  - Installation ID handling
  - Task queueing

### API Client Tests
- **APIClient** (test_client.py)
  - HTTP request methods (GET, POST, etc.)
  - Response parsing (JSON and text)
  - Error handling (HTTP errors)
  - Retry strategy configuration
  - Custom headers and timeouts

## Fixtures (conftest.py)

The following fixtures are available for use in tests:

- `mock_github_service`: Mocked GithubService with typical GitHub API responses
- `mock_embedding_service`: Mocked EmbeddingService with context/embeddings
- `mock_llm`: Mocked language model
- `mock_vectorstore_service`: Mocked vector database service
- `mock_github_client`: Mocked GitHub API client
- `sample_pr_payload`: Sample GitHub PR webhook payload
- `sample_issue_comment_payload`: Sample GitHub issue comment webhook payload

## Key Testing Patterns

### 1. Service Initialization Tests
All services are tested for correct initialization with required dependencies.

### 2. Happy Path Tests
Main success flow is tested to ensure correct behavior.

### 3. Error Handling Tests
Exception handling and error propagation is verified.

### 4. Integration Pattern Tests
How multiple components work together is validated.

### 5. Edge Cases
Special characters, multiple instances, boundary values are tested.

## Mocking Strategy

Tests use `unittest.mock` to:
- Mock external API calls
- Mock database operations
- Mock Celery task creation
- Avoid real HTTP requests and file operations

## Running in CI/CD

Add to your CI/CD pipeline:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

## Test Statistics

Total Test Cases: 80+
- Core Services: 25+ tests
- Workers: 15+ tests
- Webhooks: 30+ tests
- API Client: 15+ tests

## Adding New Tests

When adding new features:
1. Create tests in the corresponding test module
2. Use existing fixtures when applicable
3. Follow the naming convention: `test_<functionality>`
4. Include docstrings explaining what is tested
5. Use descriptive assertion messages

## Known Limitations

- Async/await functionality may need pytest-asyncio for proper handling
- Some LangChain components may require additional mocking
- Redis client interactions are mocked (real Redis not needed for tests)
- OpenAI API calls are mocked (no actual API calls in tests)

## Troubleshooting

### Issue: Tests fail with import errors
- Ensure PYTHONPATH includes the project root
- Check that all dependencies are installed

### Issue: Mock fixtures not working
- Verify patch paths match the actual import paths
- Check fixture scope (function/class/module)

### Issue: Timeout in tests
- Increase timeout for async operations
- Check for blocking calls in mock setup

## Future Improvements

- Integration tests with real services (optional)
- Performance/load tests for critical paths
- Contract tests for external API integrations
- Mutation testing for test quality assessment
"""

# Make this a valid Python module
pass

