# Main.py Refactoring Analysis

## Current State Analysis (January 2025)

### 📊 **Function Count Overview**
- **Total functions in main.py**: 32 active functions
- **Module aliases at bottom**: 26 functions
- **Total lines**: 2145

### 🏗️ **Architecture Status**
- ✅ **Configuration**: Moved to `modules/core/config.py`
- ✅ **Core handlers**: Aliased to modules (conversation, intake, planning, menu)
- ✅ **OpenAI integration**: Moved to `modules/integrations/openai_service.py`
- ✅ **Routes**: Delegated to `modules/routes/`
- ⚠️ **Business logic**: Still 32 functions in main.py that should be moved

---

## 📋 **Functions That Need To Be Moved**

### 🎯 **Priority 1: Core Business Logic (High Impact)**

#### **Contact Management (1 function)**
- `create_child_contact()` → `modules/handlers/contact.py`
  - Complex contact creation logic
  - Parent-child relationship handling
  - Should be with other contact operations

#### **Calendar Integration (3 functions)**
- `suggest_slots()` → `modules/integrations/calendar_integration.py`
- `suggest_slots_mock()` → `modules/integrations/calendar_integration.py`
- `book_slot()` → `modules/integrations/calendar_integration.py`
  - Real calendar integration logic
  - Slot suggestion algorithms
  - Booking functionality

#### **Payment Integration (2 functions)**
- `create_payment_link()` → Already delegated to module ✅
- `verify_stripe_webhook()` → Already delegated to module ✅

#### **Webhook Handling (1 function)**
- `verify_webhook()` → Already delegated to module ✅

### 🎯 **Priority 2: Menu & Flow Handlers (Medium Impact)**

#### **Info Menu System (4 functions)**
- `show_info_menu()` → `modules/handlers/menu.py`
- `handle_info_menu_selection()` → `modules/handlers/menu.py`
- `show_info_follow_up_menu()` → `modules/handlers/menu.py`
- `show_detailed_info_menu()` → `modules/handlers/menu.py`

#### **Handoff Menu System (1 function)**
- `handle_handoff_menu_selection()` → `modules/handlers/menu.py`

#### **Segment Menu System (1 function)**
- `show_segment_menu()` → `modules/handlers/menu.py`

### 🎯 **Priority 3: Prefill System (Medium Impact)**

#### **Prefill Confirmation Flow (7 functions)**
- `handle_prefill_confirmation()` → `modules/handlers/intake.py`
- `show_prefill_action_menu()` → `modules/handlers/intake.py`
- `show_prefill_action_menu_after_confirmation()` → `modules/handlers/intake.py`
- `process_corrections_and_reconfirm()` → `modules/handlers/intake.py`
- `show_prefill_summary_with_corrections()` → `modules/handlers/intake.py`
- `handle_corrected_prefill_confirmation()` → `modules/handlers/intake.py`
- `handle_prefill_confirmation_yes()` → `modules/handlers/intake.py`
- `handle_prefill_confirmation_no()` → `modules/handlers/intake.py`

### 🎯 **Priority 4: Planning System (Low Impact)**

#### **Trial Lesson Planning (2 functions)**
- `ask_trial_lesson_mode()` → `modules/handlers/planning.py`
- `handle_trial_lesson_mode_selection()` → `modules/handlers/planning.py`

#### **Preferences & Slots (3 functions)**
- `ask_for_preferences_and_suggest_slots()` → `modules/handlers/planning.py`
- `suggest_available_slots()` → `modules/handlers/planning.py`
- `process_preferences_and_suggest_slots()` → `modules/handlers/planning.py`

#### **Post-Trial Flow (3 functions)**
- `check_trial_booking_time_and_show_menu()` → `modules/handlers/planning.py`
- `show_post_trial_menu()` → `modules/handlers/planning.py`
- `create_payment_request()` → `modules/handlers/planning.py`

#### **Email Handling (1 function)**
- `handle_email_request()` → `modules/handlers/planning.py`

### 🎯 **Priority 5: Utility Functions (Low Impact)**

#### **Bot State (1 function)**
- `is_bot_disabled()` → `modules/utils/bot_state.py`

#### **FAQ Handling (1 function)**
- `handle_faq_request()` → Already delegated to module ✅

---

## 📊 **Refactoring Impact Analysis**

### **High Impact Moves (Should do first)**
1. **Contact Management** (1 function) - Core business logic
2. **Calendar Integration** (3 functions) - Complex integration logic
3. **Menu Systems** (6 functions) - Core UI flow

### **Medium Impact Moves**
4. **Prefill System** (7 functions) - Important but self-contained
5. **Planning System** (9 functions) - Already partially modularized

### **Low Impact Moves**
6. **Utility Functions** (2 functions) - Simple utilities

---

## 🎯 **Recommended Refactoring Order**

### **Phase 1: Core Business Logic**
1. Move contact management to `modules/handlers/contact.py`
2. Move calendar integration to `modules/integrations/calendar_integration.py`
3. Move menu systems to `modules/handlers/menu.py`

### **Phase 2: Flow Systems**
4. Move prefill system to `modules/handlers/intake.py`
5. Move planning system to `modules/handlers/planning.py`

### **Phase 3: Utilities & Cleanup**
6. Move utility functions
7. Clean up imports
8. Remove redundant aliases

### **Phase 4: Architecture Improvements**
9. Create app factory pattern
10. Optimize module structure

---

## 📈 **Expected Outcomes**

After complete refactoring:
- **main.py size**: ~200-300 lines (from 2145)
- **Function count**: ~5-10 functions (from 32)
- **Module organization**: Clear separation of concerns
- **Maintainability**: Much easier to work with specific features
- **Testing**: Easier to unit test individual modules

---

## 🚨 **Dependencies & Risks**

### **High-Risk Functions** (Need careful testing)
- `create_child_contact()` - Complex contact relationships
- `suggest_slots()` - Calendar integration dependencies
- `handle_prefill_confirmation()` - Core intake flow

### **Import Dependencies**
- Many functions import from each other
- Some circular dependencies may exist
- Need to be careful with module imports

### **Testing Requirements**
- Update tests to use new module paths
- Test backward compatibility aliases
- Ensure no broken imports

