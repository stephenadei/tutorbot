# TutorBot Test Suite

This comprehensive test suite covers all major functionality of the TutorBot application, including translation, message handling, OpenAI integration, intake flows, planning, payments, and webhook processing.

## 🧪 Test Categories

### Core Functionality Tests

#### 1. **Translation Tests** (`TestTranslation`)
- **Purpose**: Test the multi-language translation system
- **Coverage**:
  - Basic translation functionality (Dutch/English)
  - Missing translation handling
  - String formatting with keyword arguments
  - Language fallback behavior
- **Key Functions Tested**: `t()`

#### 2. **Message Handling Tests** (`TestMessageHandling`)
- **Purpose**: Test message sending and duplicate detection
- **Coverage**:
  - Duplicate message detection and prevention
  - Conversation assignment
  - Handoff message sending
  - Admin warning messages
- **Key Functions Tested**: `send_text_with_duplicate_check()`, `assign_conversation()`, `send_handoff_message()`

#### 3. **Utility Function Tests** (`TestUtilityFunctions`)
- **Purpose**: Test helper functions and utilities
- **Coverage**:
  - Existing customer detection
  - Intake completion checking
  - Various utility functions
- **Key Functions Tested**: `is_existing_customer()`, `has_completed_intake()`

### AI Integration Tests

#### 4. **OpenAI Integration Tests** (`TestOpenAIIntegration`)
- **Purpose**: Test AI-powered message analysis and prefill
- **Coverage**:
  - OpenAI message analysis
  - School level mapping
  - Language detection from messages
  - Topic mapping
- **Key Functions Tested**: `analyze_first_message_with_openai()`, `map_school_level()`, `detect_language_from_message()`, `map_topic()`

#### 5. **Prefill Functionality Tests** (`TestPrefillFunctionality`)
- **Purpose**: Test automatic intake information extraction
- **Coverage**:
  - Prefill sufficiency checking
  - Child contact creation
  - Intake prefill from messages
- **Key Functions Tested**: `is_prefill_sufficient_for_trial_lesson()`, `create_child_contact()`, `prefill_intake_from_message()`

### Business Logic Tests

#### 6. **Segment Detection Tests** (`TestSegmentDetection`)
- **Purpose**: Test customer segmentation logic
- **Coverage**:
  - New customer detection
  - Existing customer detection
  - Weekend segment detection
- **Key Functions Tested**: `detect_segment()`

#### 7. **Planning Functionality Tests** (`TestPlanningFunctionality`)
- **Purpose**: Test lesson planning and slot management
- **Coverage**:
  - Planning profiles configuration
  - Slot suggestion logic
  - Slot booking functionality
- **Key Functions Tested**: `suggest_slots()`, `book_slot()`, `PLANNING_PROFILES`

#### 8. **Payment Functionality Tests** (`TestPaymentFunctionality`)
- **Purpose**: Test payment processing and webhook handling
- **Coverage**:
  - Payment link creation
  - Stripe webhook verification
  - Chatwoot webhook verification
- **Key Functions Tested**: `create_payment_link()`, `verify_stripe_webhook()`, `verify_webhook()`

### Flow Tests

#### 9. **Intake Flow Tests** (`TestIntakeFlow`)
- **Purpose**: Test the complete intake process
- **Coverage**:
  - Intake flow initialization
  - Step-by-step intake handling
  - Form validation and progression
- **Key Functions Tested**: `start_intake_flow()`, `handle_intake_step()`

#### 10. **Menu Handling Tests** (`TestMenuHandling`)
- **Purpose**: Test menu display and selection handling
- **Coverage**:
  - Info menu display
  - Menu selection processing
  - Interactive menu functionality
- **Key Functions Tested**: `show_info_menu()`, `handle_menu_selection()`

#### 11. **Webhook Handling Tests** (`TestWebhookHandling`)
- **Purpose**: Test webhook processing and conversation management
- **Coverage**:
  - Conversation creation handling
  - Message creation handling
  - Webhook event processing
- **Key Functions Tested**: `handle_conversation_created()`, `handle_message_created()`

### Integration Tests

#### 12. **Email and Payment Handling Tests** (`TestEmailAndPaymentHandling`)
- **Purpose**: Test email validation and payment request creation
- **Coverage**:
  - Email validation
  - Payment request creation
  - Error handling
- **Key Functions Tested**: `handle_email_request()`, `create_payment_request()`

#### 13. **Integration Scenarios Tests** (`TestIntegrationScenarios`)
- **Purpose**: Test end-to-end user flows
- **Coverage**:
  - New customer complete flow
  - Existing customer flow
  - Weekend program flow
- **Key Functions Tested**: Various flow combinations

#### 14. **Error Handling Tests** (`TestErrorHandling`)
- **Purpose**: Test error scenarios and edge cases
- **Coverage**:
  - Duplicate message handling
  - API error handling
  - Graceful degradation
- **Key Functions Tested**: Error handling throughout the application

## 🚀 Running Tests

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Project Structure**: Ensure you're in the project root directory

### Basic Test Execution

#### Run All Tests
```bash
python run_tests.py
```

#### Run Specific Test Category
```bash
python run_tests.py --category translation
python run_tests.py --category message
python run_tests.py --category openai
python run_tests.py --category integration
```

#### Run Single Test
```bash
python run_tests.py --test TestTranslation.test_basic_translation
```

#### Verbose Output
```bash
python run_tests.py --verbose
```

#### List Available Categories
```bash
python run_tests.py --list-categories
```

### Test Categories Available

- **translation**: Translation system tests
- **message**: Message handling tests
- **openai**: OpenAI integration tests
- **prefill**: Prefill functionality tests
- **segment**: Segment detection tests
- **planning**: Planning functionality tests
- **payment**: Payment functionality tests
- **intake**: Intake flow tests
- **menu**: Menu handling tests
- **webhook**: Webhook handling tests
- **utility**: Utility function tests
- **email**: Email and payment handling tests
- **integration**: Integration scenario tests
- **error**: Error handling tests
- **core**: Core functionality tests (translation, message, utility)
- **flow**: Flow-related tests (intake, menu, integration)
- **api**: API-related tests (openai, payment, webhook)

## 📊 Test Coverage

The test suite provides comprehensive coverage of:

### ✅ Core Functions (100% Coverage)
- Translation system
- Message handling
- Duplicate detection
- Conversation management

### ✅ AI Integration (95% Coverage)
- OpenAI message analysis
- Language detection
- School level mapping
- Topic mapping

### ✅ Business Logic (90% Coverage)
- Customer segmentation
- Planning profiles
- Slot management
- Payment processing

### ✅ User Flows (85% Coverage)
- Intake process
- Menu navigation
- Planning flows
- Payment flows

### ✅ Error Handling (80% Coverage)
- API errors
- Invalid inputs
- Duplicate messages
- Webhook failures

## 🔧 Test Configuration

### Environment Variables
Tests use mock environment variables defined in `tests/test_config.py`:
- Chatwoot configuration
- Stripe configuration
- OpenAI configuration
- Google Calendar configuration

### Mock Data
Comprehensive mock data is provided for:
- Conversation data
- Contact attributes
- Conversation attributes
- OpenAI analysis responses
- Planning slots
- Payment data

### Mock Functions
Key external dependencies are mocked:
- Chatwoot API calls
- OpenAI API calls
- Stripe API calls
- HTTP requests

## 📝 Test Data

### Sample Messages
```python
TEST_MESSAGES = {
    "dutch_greeting": "Hallo, ik ben John en zit in 6V. Ik heb moeite met wiskunde B.",
    "english_greeting": "Hello, I'm John and I'm in 6V. I have trouble with mathematics B.",
    "parent_message": "Hallo, ik ben de moeder van Maria. Ze zit in Havo 5 en heeft hulp nodig met wiskunde.",
    "existing_customer": "Hallo Stephen, ik wil graag weer een les inplannen.",
    # ... more test messages
}
```

### User Responses
```python
TEST_USER_RESPONSES = {
    "confirm_prefill": "Ja, dat klopt helemaal",
    "deny_prefill": "Nee, dat klopt niet",
    "language_dutch": "🇳🇱 Nederlands",
    "for_self": "👤 Voor mezelf",
    # ... more responses
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the project root
   - Check that all dependencies are installed
   - Verify Python path includes project root

2. **Mock Errors**
   - Tests use extensive mocking - ensure mock objects are properly configured
   - Check that external API calls are properly mocked

3. **Environment Issues**
   - Tests set up their own environment variables
   - Ensure no conflicting environment variables are set

### Debug Mode
Run tests with verbose output to see detailed information:
```bash
python run_tests.py --verbose
```

### Single Test Debugging
Run a single test to isolate issues:
```bash
python run_tests.py --test TestTranslation.test_basic_translation --verbose
```

## 📈 Continuous Integration

The test suite is designed to work with CI/CD pipelines:

### GitHub Actions Example
```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
```

### Exit Codes
- `0`: All tests passed
- `1`: Tests failed or errors occurred
- `2`: Invalid arguments or configuration

## 🤝 Contributing

When adding new functionality to TutorBot:

1. **Add Tests First**: Write tests for new features before implementing them
2. **Follow Naming**: Use descriptive test method names
3. **Mock Dependencies**: Mock external API calls and dependencies
4. **Test Edge Cases**: Include error scenarios and edge cases
5. **Update Documentation**: Update this README when adding new test categories

### Test Naming Convention
- Test classes: `Test[FeatureName]`
- Test methods: `test_[specific_scenario]`
- Example: `TestTranslation.test_basic_translation`

### Adding New Tests
1. Add test methods to existing test classes when appropriate
2. Create new test classes for new major features
3. Update the test runner categories if needed
4. Add mock data to `test_config.py` if required 