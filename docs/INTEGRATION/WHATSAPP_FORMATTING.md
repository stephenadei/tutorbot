# WhatsApp Formatting Guide

WhatsApp supports a set of advanced text formatting options using simple inline symbols. Here's a complete overview of what's available:

## ✅ Basic Formatting

| Format | Syntax | Example Input | Output |
|--------|--------|---------------|---------|
| **Bold** | `*text*` | `*hello*` | **hello** |
| *Italic* | `_text_` | `_hello_` | *hello* |
| ~~Strikethrough~~ | `~text~` | `~hello~` | ~~hello~~ |
| `Monospace` | `` `text` `` | `` `hello` `` | `hello` (in monospace font) |

## 🔤 Combined Formatting

Yes, you can combine styles, for example:

`*_bold and italic_*`

Becomes: **_bold and italic_**

You can even nest formatting carefully like:

`~*_strikethrough, bold & italic_*~`

→ ~~**_strikethrough, bold & italic_**~~

## 📄 Lists & Indentation (Fake Formatting)

WhatsApp doesn't support true bullet lists or indentation, but you can simulate it:

### Bulleted list
```
• Item one  
• Item two
```

### Numbered list
```
1. First point  
2. Second point
```

### Indented text (fake with spaces or emojis)
```
➤ Sub-point  
   ➤ Sub-sub-point
```

## 🧩 Quote & Code Blocks

### Quote a message:
Type `>` followed by a space before the text:

> This is a quote

### `Code block` with backticks

But multi-line blocks are not officially supported like in Slack/Discord.

## 🖋️ Special Tips

- On iOS/Android, long press your typed message → tap Format (you'll get options to bold, italic, etc.)
- Emojis, arrows (→), and symbols (✔, ✨, ⚠) often enhance clarity in structured messages
- Use line breaks (Shift+Enter on desktop) to structure longer messages

## 🎯 Best Practices for Bot Messages

### Structured Responses
```
*Welcome to TutorBot!* 👋

Here's how I can help you:

• 🎯 *Schedule a lesson* - Book your tutoring session
• ℹ️ *Get information* - Learn about rates and services  
• 👨‍🏫 *Speak to Stephen* - Connect directly with your tutor

What would you like to do?
```

### Confirmation Messages
```
✅ *Lesson Confirmed!*

📅 **Date:** Monday, August 12th  
⏰ **Time:** 14:00 - 15:00  
📍 **Location:** Science Park 904  
👤 **Student:** Maria

📧 I'll send you a confirmation email shortly.
```

### Error Messages
```
❌ *Oops! Something went wrong*

I couldn't process your request. Please try again or contact Stephen directly.

👨‍🏫 *Need help?* Stephen is available at +31 6 47357426
```

### Information Lists
```
💰 *Our Rates:*

📚 **Higher Education:**
• Single lesson: €80
• Package of 2: €135  
• Package of 4: €250

🎓 **Secondary Education:**
• Single lesson: €60-75
• Package of 2: €100-130
• Package of 4: €200-230
```

## 🔧 Implementation Notes

When implementing these formats in your bot:

1. **Escape special characters** when needed
2. **Test on multiple devices** - formatting may vary
3. **Keep it simple** - complex formatting can break
4. **Use emojis strategically** - they enhance readability
5. **Maintain consistency** - use the same formatting patterns throughout

## 📱 Device Compatibility

- **iOS/Android**: Full formatting support
- **Web/Desktop**: Most formatting works, some variations
- **Business API**: All formatting supported
- **Third-party clients**: May vary

---

*Need help implementing these formats in your bot? Check the main documentation for code examples.* 