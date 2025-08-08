# 📅 Google Calendar & Notability Integration

## 🎯 Overview

This integration provides seamless lesson management by connecting Google Calendar with Notability notes through Google Drive backup. The system automatically creates calendar events with proper color coding and organizes notes in a structured folder hierarchy.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TutorBot      │    │  Google Calendar│    │  Google Drive   │
│                 │    │                 │    │                 │
│  - Lesson       │───▶│  - Events       │    │  - Lessen/      │
│  - Scheduling   │    │  - Color Coding │    │  - Student      │
│  - Notes        │    │  - Status Mgmt  │    │  - Folders      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Notability     │    │  Backup         │
                       │                 │    │                 │
                       │  - Notes        │    │  - Auto-sync    │
                       │  - Templates    │    │  - Organization │
                       └─────────────────┘    └─────────────────┘
```

## 📆 Calendar Structure

### 🎨 Color Coding

| Color | Status | Usage |
|-------|--------|-------|
| 🟨 Yellow | `definitief` | Confirmed lessons (paid) |
| 🔴 Red | `voorstel` | Lesson proposals (awaiting confirmation) |
| 🔵 Blue | `proefles` / `intake` | Trial lessons and intake sessions |
| 🟢 Green | `schoolles` | School-related lessons |
| ⚫ Gray | `vervanging` | Substitution lessons |
| 🟣 Purple | `follow-up` | Reminders and follow-ups |

### 📝 Event Title Format

```
[Student Name] – [Lesson Type] – [Status] – [Location]
```

**Examples:**
- `Naomi – Wiskunde – definitief – Zoom`
- `Amelie – Intake – Douwe Egberts`
- `Stijls – voorstel – wacht bevestiging`
- `Pierre Paolo – schoolles – 4V`

### 🔄 Status Workflow

```
voorstel → definitief (payment confirmed)
proefles → definitief (converted to regular)
intake → definitief (converted to regular)
definitief → vervanging (substitution needed)
definitief → follow-up (reminder added)
```

## 📁 Notes Organization

### 🗂️ Folder Structure

```
Google Drive/
└── Lessen/
    ├── [Student Name 1]/
    │   ├── 2025-01-15 - [Student] - Wiskunde Breuken
    │   ├── 2025-01-20 - [Student] - Intake Session
    │   └── 2025-01-25 - [Student] - Trial Lesson
    ├── [Student Name 2]/
    │   └── ...
    └── [Student Name N]/
        └── ...
```

### 📄 Naming Convention

```
YYYY-MM-DD - [Student Name] - [Topic]
```

**Examples:**
- `2025-01-15 - Naomi - Breuken oefenen`
- `2025-01-20 - Amelie - Intake Session`
- `2025-01-25 - Pierre Paolo - Wiskunde A`

## 🔧 Module Structure

### 📅 Calendar Module (`modules/calendar/`)

#### `calendar_manager.py`
- **CalendarManager**: Main calendar operations
- **Features**:
  - Create lesson events with proper formatting
  - Update event status and colors
  - Get available time slots
  - Handle timezone management

#### `event_creator.py`
- **EventCreator**: Specific event creation
- **Features**:
  - `create_trial_lesson()`: 30-minute trial lessons
  - `create_intake_session()`: 45-minute intake sessions
  - `create_regular_lesson()`: 60-minute regular lessons
  - `create_school_lesson()`: School-related lessons
  - `create_substitution_lesson()`: Substitution handling
  - `create_follow_up_reminder()`: Reminders and follow-ups

#### `status_manager.py`
- **StatusManager**: Status transitions and workflow
- **Features**:
  - Status change methods (`confirm_lesson()`, `mark_as_proposal()`, etc.)
  - Workflow management (`get_status_workflow()`)
  - Status summaries and pending actions

### 📝 Notes Module (`modules/notes/`)

#### `notes_manager.py`
- **NotesManager**: Google Drive integration
- **Features**:
  - Create student folders automatically
  - Create lesson notes with templates
  - Get notes links for calendar integration
  - List and organize student notes
  - Backup Notability files

#### `drive_backup.py`
- **DriveBackup**: Backup operations
- **Features**:
  - Automatic backup setup
  - Batch file backup
  - Backup status monitoring
  - Cleanup old backups
  - Sync local Notability folders

#### `note_organizer.py`
- **NoteOrganizer**: Note structure and templates
- **Features**:
  - Filename formatting and parsing
  - Note templates (regular, intake, trial)
  - Note organization by student
  - Statistics and reporting

### 🔗 Integration Module (`modules/integration/`)

#### `lesson_manager.py`
- **LessonManager**: Complete workflow integration
- **Features**:
  - `schedule_trial_lesson()`: Complete trial lesson setup
  - `schedule_intake_session()`: Complete intake setup
  - `schedule_regular_lesson()`: Complete regular lesson setup
  - `confirm_lesson()`: Status management
  - `get_lesson_summary()`: Comprehensive student overview
  - `backup_lesson_files()`: File backup integration

## 🚀 Usage Examples

### 1. Schedule a Trial Lesson

```python
from modules.integration import LessonManager

lesson_manager = LessonManager()

# Schedule complete trial lesson
result = lesson_manager.schedule_trial_lesson(
    student_name="Naomi",
    start_time=datetime(2025, 1, 20, 14, 0),  # 2:00 PM
    duration_minutes=30,
    location="Zoom",
    description="Trial lesson for mathematics",
    auto_create_notes=True
)

if result['success']:
    print(f"✅ Trial lesson scheduled!")
    print(f"   Calendar Event: {result['calendar_event_id']}")
    print(f"   Notes Link: {result['notes_link']}")
    print(f"   Note Template: {result['note_template_id']}")
else:
    print(f"❌ Errors: {result['errors']}")
```

### 2. Schedule an Intake Session

```python
result = lesson_manager.schedule_intake_session(
    student_name="Amelie",
    start_time=datetime(2025, 1, 22, 15, 30),  # 3:30 PM
    duration_minutes=45,
    location="Douwe Egberts",
    description="Initial intake session"
)
```

### 3. Schedule a Regular Lesson

```python
result = lesson_manager.schedule_regular_lesson(
    student_name="Pierre Paolo",
    lesson_topic="Wiskunde A",
    start_time=datetime(2025, 1, 25, 16, 0),  # 4:00 PM
    duration_minutes=60,
    location="Zoom",
    description="Regular mathematics lesson",
    is_confirmed=True  # Payment received
)
```

### 4. Confirm a Lesson

```python
# Change status from "voorstel" to "definitief"
success = lesson_manager.confirm_lesson("calendar_event_id_here")
if success:
    print("✅ Lesson confirmed!")
```

### 5. Get Student Summary

```python
summary = lesson_manager.get_lesson_summary("Naomi")
print(f"Student: {summary['student_name']}")
print(f"Total Lessons: {summary['total_lessons']}")
print(f"Notes Link: {summary['notes_link']}")
print(f"Recent Notes: {len(summary['recent_notes'])}")
```

### 6. Backup Lesson Files

```python
file_ids = lesson_manager.backup_lesson_files(
    student_name="Naomi",
    lesson_date=datetime(2025, 1, 20),
    lesson_topic="Breuken oefenen",
    file_paths=[
        "/path/to/notability/file1.pdf",
        "/path/to/notability/file2.pdf"
    ]
)
print(f"✅ Backed up {len(file_ids)} files")
```

## 🔧 Configuration

### Environment Variables

```bash
# Google Calendar
GCAL_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
GCAL_CALENDAR_ID=primary

# Google Drive (uses same service account)
# Automatically configured from GCAL_SERVICE_ACCOUNT_JSON
```

### Service Account Setup

1. **Create Google Cloud Project**
2. **Enable APIs**:
   - Google Calendar API
   - Google Drive API
3. **Create Service Account**:
   - Download JSON key file
   - Set `GCAL_SERVICE_ACCOUNT_JSON` environment variable
4. **Share Calendar**:
   - Share your Google Calendar with the service account email
5. **Share Drive Folder** (optional):
   - Share the "Lessen" folder with the service account email

## 📊 Workflow Integration

### 1. New Student Intake

```
1. Student contacts via WhatsApp
2. Bot analyzes message with OpenAI
3. Bot creates intake session:
   - Calendar event (blue, 45 min)
   - Notes template in Google Drive
   - Notes link added to calendar description
4. Student confirms appointment
5. After intake:
   - Status changes to "definitief"
   - Trial lesson scheduled
   - Notes updated with intake results
```

### 2. Trial Lesson

```
1. Trial lesson scheduled:
   - Calendar event (blue, 30 min)
   - Trial lesson template created
   - Notes link in calendar description
2. During lesson:
   - Notes taken in Notability
   - Files automatically backed up
3. After lesson:
   - Evaluation added to notes
   - Decision: continue or not
   - If continue: regular lessons scheduled
```

### 3. Regular Lessons

```
1. Regular lesson scheduled:
   - Calendar event (yellow if confirmed, red if proposal)
   - Regular lesson template created
2. Before lesson:
   - Previous notes reviewed
   - Materials prepared
3. During lesson:
   - Notes taken in Notability
   - Files backed up automatically
4. After lesson:
   - Notes updated with progress
   - Homework assigned
   - Next lesson scheduled
```

## 🔍 Monitoring & Maintenance

### Backup Status

```python
from modules.notes import NotesManager

notes_manager = NotesManager()
backup_status = notes_manager.get_backup_status("Student Name")
print(f"Total Notes: {backup_status['total_notes']}")
print(f"Last Backup: {backup_status['last_backup']}")
print(f"Folder Link: {backup_status['folder_link']}")
```

### Cleanup Old Backups

```python
from modules.notes import DriveBackup

drive_backup = DriveBackup(notes_manager)
cleaned_count = drive_backup.cleanup_old_backups(days_to_keep=365)
print(f"Cleaned up {cleaned_count} old files")
```

### Sync Local Notability Folder

```python
sync_results = drive_backup.sync_notability_folder("/path/to/notability/folder")
print(f"Synced {sync_results['synced_files']}/{sync_results['total_files']} files")
```

## 🎯 Benefits

### ✅ For Stephen
- **Automated Organization**: No manual folder creation
- **Consistent Structure**: Standardized naming and templates
- **Easy Access**: All notes in one place (Google Drive)
- **Calendar Integration**: Notes linked to calendar events
- **Backup Security**: Automatic backup of all notes
- **Status Tracking**: Clear lesson status management

### ✅ For Students
- **Professional Experience**: Well-organized lessons
- **Easy Follow-up**: Clear notes and homework tracking
- **Consistent Quality**: Standardized lesson structure
- **Progress Tracking**: Historical lesson records

### ✅ For Business
- **Scalability**: Easy to manage multiple students
- **Efficiency**: Automated workflows reduce manual work
- **Quality Control**: Standardized processes
- **Data Security**: Cloud backup prevents data loss
- **Analytics**: Easy to track lesson statistics

## 🚀 Future Enhancements

### Planned Features
- **Google Docs Integration**: Direct note editing in Google Docs
- **Automated Reminders**: Follow-up reminders for students
- **Progress Reports**: Automated progress summaries
- **Payment Integration**: Link payments to lesson confirmation
- **Mobile App**: Notability sync app for mobile devices

### Advanced Workflows
- **Batch Scheduling**: Schedule multiple lessons at once
- **Recurring Lessons**: Automatic recurring lesson creation
- **Substitution Management**: Automated substitution handling
- **Analytics Dashboard**: Comprehensive lesson analytics
- **Student Portal**: Student access to their notes and progress

---

*This integration provides a complete lesson management solution that seamlessly connects calendar scheduling with note-taking and organization, making Stephen's tutoring business more efficient and professional.*
