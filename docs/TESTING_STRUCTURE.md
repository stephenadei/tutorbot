# Testing Structure - Tests vs Scripts/Testing

## 📁 **Directory Structure**

```
tutorbot/
├── tests/                    # 🧪 AUTOMATED TESTS
│   ├── run_tests.py          # Test runner
│   ├── test_main.py          # Unit tests for main.py
│   ├── test_config.py        # Configuration tests
│   ├── test_setup.py         # Setup tests
│   ├── test_prefill_overview.py # Prefill functionality tests
│   └── test_api_connection.py # API connection tests
└── scripts/testing/          # 🔧 MANUAL TESTING TOOLS
    ├── test_bot.py           # Manual bot testing
    ├── test_chatwoot_api.py  # Manual API testing
    ├── test_input_select.py  # Input select testing
    ├── test_real_message.py  # Real message testing
    ├── test_real_conversation.py # Real conversation testing
    └── show_prefill_overview.py # Prefill overview utility
```

## 🧪 **`tests/` - Automated Tests**

### **Purpose:**
- **Unit tests** en **integration tests** voor de applicatie
- **Automated testing** via test runner
- **CI/CD integration** voor GitHub Actions
- **Code quality assurance**

### **Usage:**
```bash
# Run all tests
python3 tests/run_tests.py

# Run specific test categories
python3 tests/run_tests.py --category core
python3 tests/run_tests.py --category api

# Run single test
python3 tests/run_tests.py --test TestTranslation.test_basic_translation
```

### **Test Categories:**
- **core** - Core functionality tests
- **flow** - User flow tests
- **api** - API integration tests
- **translation** - Translation system tests
- **message** - Message handling tests
- **openai** - OpenAI integration tests
- **prefill** - Prefill functionality tests
- **segment** - Segment detection tests
- **planning** - Planning functionality tests
- **payment** - Payment functionality tests
- **intake** - Intake flow tests
- **menu** - Menu handling tests
- **webhook** - Webhook handling tests
- **utility** - Utility function tests
- **email** - Email and payment handling tests
- **integration** - Integration scenario tests
- **error** - Error handling tests

---

## 🔧 **`scripts/testing/` - Manual Testing Tools**

### **Purpose:**
- **Manual testing** en **debugging tools**
- **Development utilities** voor handmatige tests
- **Real-world scenario testing**
- **Troubleshooting** en **diagnostics**

### **Usage:**
```bash
# Manual bot testing
python3 scripts/testing/test_bot.py

# Manual API testing
python3 scripts/testing/test_chatwoot_api.py

# Real message testing
python3 scripts/testing/test_real_message.py

# Show prefill overview
python3 scripts/testing/show_prefill_overview.py
```

### **Tools:**
- **`test_bot.py`** - Test bot functionality manually
- **`test_chatwoot_api.py`** - Test Chatwoot API manually
- **`test_input_select.py`** - Test input selection manually
- **`test_real_message.py`** - Test with real messages
- **`test_real_conversation.py`** - Test with real conversations
- **`show_prefill_overview.py`** - Show prefill overview for debugging

---

## 🎯 **Key Differences**

| Aspect | `tests/` | `scripts/testing/` |
|--------|----------|-------------------|
| **Purpose** | Automated testing | Manual testing tools |
| **Execution** | Via test runner | Direct execution |
| **Output** | Pass/fail results | Debug information |
| **Use Case** | CI/CD, quality assurance | Development, debugging |
| **Frequency** | Run regularly | Run as needed |
| **Scope** | Comprehensive coverage | Specific scenarios |

---

## 🚀 **When to Use Which**

### **Use `tests/` when:**
- ✅ Running automated test suites
- ✅ Checking code quality
- ✅ CI/CD pipeline
- ✅ Regression testing
- ✅ Comprehensive functionality testing

### **Use `scripts/testing/` when:**
- 🔧 Debugging specific issues
- 🔧 Testing real-world scenarios
- 🔧 Manual verification
- 🔧 Development troubleshooting
- 🔧 Quick functionality checks

---

## 📋 **Recommended Workflow**

### **Development Workflow:**
1. **Write code** in main.py
2. **Run automated tests:** `python3 tests/run_tests.py`
3. **If issues:** Use `scripts/testing/` tools for debugging
4. **Fix issues** and repeat

### **Debugging Workflow:**
1. **Identify issue** in production/logs
2. **Use relevant tool** from `scripts/testing/`
3. **Debug and fix** the issue
4. **Add automated test** to `tests/` if needed

---

## 🔄 **Potential Improvements**

### **Option 1: Keep Current Structure**
- ✅ Clear separation of concerns
- ✅ Different purposes for each directory
- ✅ No breaking changes needed

### **Option 2: Consolidate**
- 🔄 Move all testing to `tests/`
- 🔄 Create subdirectories: `tests/unit/`, `tests/integration/`, `tests/manual/`
- ⚠️ Requires updating all references

### **Option 3: Rename for Clarity**
- 🔄 Rename `scripts/testing/` to `scripts/debug/` or `scripts/tools/`
- 🔄 Keep `tests/` for automated tests only
- ⚠️ Requires updating documentation

---

## 📚 **Related Documentation**

- `tests/README.md` - Automated testing documentation
- `scripts/README.md` - Scripts organization documentation
- `docs/INTEGRATION_ROADMAP.md` - Integration testing plan

---

*Last Updated: August 7, 2025*
*Status: Current structure documented* 