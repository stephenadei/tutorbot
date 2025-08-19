# 🎯 Prefill Confirmation Flow

## Overview

The prefill confirmation flow is a **critical component** of TutorBot that ensures users can verify and confirm information extracted from their initial messages. This flow was recently fixed to properly display interactive menu buttons in WhatsApp.

## 🔄 Flow Overview

```
User sends message → OpenAI extracts info → Show confirmation menu → User confirms → Show action menu
```

### Step-by-Step Process

1. **Message Reception**: User sends initial message with information
2. **OpenAI Analysis**: `prefill_intake_from_message()` extracts structured data
3. **Confirmation Display**: `show_prefill_action_menu()` shows extracted info + menu
4. **User Confirmation**: User selects confirmation option
5. **Action Menu**: `show_prefill_action_menu_after_confirmation()` shows next steps

## 🎯 Critical Functions

### `show_prefill_action_menu(cid, contact_id, lang)`

**Purpose**: Primary entry point for prefill confirmation flow

**What it does**:
- Sends confirmation question as text message
- Sends interactive menu with confirmation options
- Sets `pending_intent` to "prefill_confirmation"

**Critical Implementation Details**:
```python
# Step 1: Send confirmation question
confirmation_text = t("prefill_confirmation_question", lang)
send_text_with_duplicate_check(cid, confirmation_text)

# Step 2: Send interactive menu (CRITICAL FOR WHATSAPP BUTTONS)
menu_options = [
    (t("prefill_confirm_all", lang), "confirm_all"),
    (t("prefill_correct_all", lang), "correct_all"),
    (t("prefill_correct_partial", lang), "correct_partial")
]
send_input_select_only(cid, menu_title, menu_options)
```

### `send_input_select_only(conversation_id, text, options)`

**Purpose**: Send interactive menu buttons in WhatsApp

**Critical Features**:
- Uses `ChatwootAPI.send_message()` for proper SSL handling
- Prevents SSL errors that were causing menu failures
- Ensures WhatsApp displays interactive buttons, not just text

**Implementation**:
```python
# CRITICAL: Use ChatwootAPI instead of direct HTTP requests
success = ChatwootAPI.send_message(
    conversation_id, 
    text, 
    "input_select", 
    content_attributes
)
```

## 🚨 Important Notes

### Why This Flow Was Critical to Fix

1. **SSL Errors**: Direct HTTP requests were causing SSL errors and worker crashes
2. **Menu Display**: Text-only messages don't show interactive buttons in WhatsApp
3. **User Experience**: Users couldn't confirm information without proper menu buttons

### What Was Fixed

1. **SSL Handling**: Switched from direct HTTP requests to `ChatwootAPI.send_message()`
2. **Menu Functionality**: Ensured `send_input_select_only()` is called for menu display
3. **Error Prevention**: Added proper error handling and logging

### Flow Validation

The correct flow is now:
```
show_prefill_action_menu() → send_input_select_only() → WhatsApp displays buttons
```

**NOT**:
```
show_prefill_action_menu() → text message only → No buttons displayed
```

## 📋 Menu Options

### Confirmation Menu Options

1. **✅ "Ja, klopt!"** (`confirm_all`)
   - User confirms all extracted information is correct
   - Proceeds to action menu

2. **❌ "Nee, aanpassen"** (`correct_all`)
   - User indicates information needs correction
   - Triggers correction flow

3. **🤔 "Deels correct"** (`correct_partial`)
   - User indicates partial information is correct
   - Triggers partial correction flow

### Action Menu Options (After Confirmation)

**For New Customers**:
- 📅 "Eerst proefles" (`plan_trial_lesson`)
- 📋 "Meer informatie" (`go_to_main_menu`)
- 👨‍🏫 "Met Stephen spreken" (`handoff`)

**For Existing Customers**:
- 📅 "Alle lessen inplannen" (`plan_all_lessons`)
- 📅 "Eerst proefles" (`plan_trial_lesson`)
- 📋 "Meer informatie" (`go_to_main_menu`)
- 👨‍🏫 "Met Stephen spreken" (`handoff`)

## 🔧 Technical Implementation

### Required Environment Variables

```bash
CW_URL=https://crm.stephenadei.nl
CW_ACC_ID=1
CW_ADMIN_TOKEN=your_admin_token
```

### Dependencies

- `scripts/cw_api.py` - ChatwootAPI class for SSL-safe requests
- `main.py` - Core flow functions
- Translation system (`t()` function) for multilingual support

### Error Handling

```python
try:
    set_conv_attrs(cid, {"pending_intent": "prefill_confirmation"})
except Exception as e:
    print(f"⚠️ SSL error setting pending_intent: {e}")
    # Continue anyway - not critical
```

## 🧪 Testing

### Manual Testing

1. Send message: "Mijn dochter Maria zit in Havo 5..."
2. Verify confirmation message appears
3. Verify interactive menu buttons appear
4. Test each button option
5. Verify action menu appears after confirmation

### Log Verification

Look for these log messages:
```
🎯 Showing prefill confirmation menu in nl
📤 Sending input_select menu with 3 items...
✅ Chatwoot input_select sent successfully (3 options)
🎯 Prefill confirmation menu send result: True
```

### Common Issues

1. **No menu buttons**: Check if `send_input_select_only()` is being called
2. **SSL errors**: Verify `ChatwootAPI.send_message()` is being used
3. **Menu not appearing**: Check WhatsApp formatting rules in function

## 📚 Related Documentation

- [Project Organization](PROJECT_ORGANIZATION.md)
- [WhatsApp Formatting](INTEGRATION/WHATSAPP_FORMATTING.md)
- [Integration Roadmap](INTEGRATION/INTEGRATION_ROADMAP.md)

---

*Last Updated: December 2024*
*Status: Fully Implemented and Tested*
