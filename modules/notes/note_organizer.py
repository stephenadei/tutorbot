"""
Note Organizer

Handles organization and structure of notes
with proper naming conventions and metadata.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class NoteOrganizer:
    """Organizes notes with proper structure and naming"""
    
    def __init__(self):
        self.naming_convention = "YYYY-MM-DD - Student Name - Topic"
        self.folder_structure = {
            'root': 'Lessen',
            'students': 'Individual student folders',
            'templates': 'Note templates',
            'archives': 'Old notes'
        }
    
    def format_note_filename(self, 
                           student_name: str,
                           lesson_date: datetime,
                           lesson_topic: str) -> str:
        """
        Format filename according to naming convention
        
        Args:
            student_name: Name of the student
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            
        Returns:
            Formatted filename
        """
        date_str = lesson_date.strftime("%Y-%m-%d")
        return f"{date_str} - {student_name} - {lesson_topic}"
    
    def parse_note_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse filename to extract metadata
        
        Args:
            filename: Filename to parse
            
        Returns:
            Dictionary with parsed metadata
        """
        try:
            parts = filename.split(' - ')
            if len(parts) >= 3:
                date_str = parts[0]
                student_name = parts[1]
                topic = ' - '.join(parts[2:])  # Handle topics with dashes
                
                lesson_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                return {
                    'date': lesson_date,
                    'student_name': student_name,
                    'topic': topic,
                    'is_valid': True
                }
            else:
                return {'is_valid': False, 'error': 'Invalid format'}
                
        except Exception as e:
            return {'is_valid': False, 'error': str(e)}
    
    def create_note_template(self, 
                           student_name: str,
                           lesson_date: datetime,
                           lesson_topic: str,
                           lesson_type: str = "regular") -> str:
        """
        Create a note template with proper structure
        
        Args:
            student_name: Name of the student
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            lesson_type: Type of lesson (trial, intake, regular, etc.)
            
        Returns:
            Formatted note template
        """
        date_str = lesson_date.strftime("%Y-%m-%d")
        
        template = f"""
# {date_str} - {student_name} - {lesson_topic}

## Lesson Information
- **Student:** {student_name}
- **Date:** {date_str}
- **Topic:** {lesson_topic}
- **Type:** {lesson_type.title()}
- **Duration:** [Duration]

## Lesson Content
### What we covered:
- [Topic 1]
- [Topic 2]
- [Topic 3]

### Key Concepts:
- [Concept 1]
- [Concept 2]

## Student Progress
### Strengths:
- [Strength 1]
- [Strength 2]

### Areas for Improvement:
- [Area 1]
- [Area 2]

## Homework & Follow-up
### Assigned:
- [Homework 1]
- [Homework 2]

### Next Steps:
- [ ] [Action item 1]
- [ ] [Action item 2]

## Notes & Observations
[Additional notes and observations]

---
*Created by TutorBot - {datetime.now().strftime("%Y-%m-%d %H:%M")}*
        """.strip()
        
        return template
    
    def create_intake_template(self, 
                              student_name: str,
                              intake_date: datetime) -> str:
        """
        Create an intake session template
        
        Args:
            student_name: Name of the student
            intake_date: Date of the intake
            
        Returns:
            Formatted intake template
        """
        date_str = intake_date.strftime("%Y-%m-%d")
        
        template = f"""
# {date_str} - {student_name} - Intake Session

## Student Information
- **Name:** {student_name}
- **Date:** {date_str}
- **Session Type:** Intake

## Background Information
### Current Level:
- **School:** [School name]
- **Grade/Level:** [Grade/Level]
- **Current Performance:** [Performance level]

### Subjects & Topics:
- **Main Subject:** [Subject]
- **Specific Topics:** [Topics]
- **Goals:** [Learning goals]

## Assessment Results
### Strengths:
- [Strength 1]
- [Strength 2]

### Challenges:
- [Challenge 1]
- [Challenge 2]

### Learning Style:
- [Learning style observations]

## Recommendations
### Suggested Approach:
- [Approach 1]
- [Approach 2]

### Frequency:
- [Recommended frequency]

### Duration:
- [Recommended duration]

## Next Steps
- [ ] Schedule trial lesson
- [ ] Prepare materials
- [ ] Follow up with parent/student

## Notes
[Additional observations and notes]

---
*Created by TutorBot - {datetime.now().strftime("%Y-%m-%d %H:%M")}*
        """.strip()
        
        return template
    
    def create_trial_lesson_template(self,
                                    student_name: str,
                                    trial_date: datetime,
                                    lesson_topic: str) -> str:
        """
        Create a trial lesson template
        
        Args:
            student_name: Name of the student
            trial_date: Date of the trial lesson
            lesson_topic: Topic of the trial lesson
            
        Returns:
            Formatted trial lesson template
        """
        date_str = trial_date.strftime("%Y-%m-%d")
        
        template = f"""
# {date_str} - {student_name} - Trial Lesson

## Trial Lesson Information
- **Student:** {student_name}
- **Date:** {date_str}
- **Topic:** {lesson_topic}
- **Type:** Trial Lesson (30 minutes)

## Lesson Content
### What we covered:
- [Topic 1]
- [Topic 2]

### Teaching Approach:
- [Approach used]

## Student Assessment
### Engagement Level:
- [High/Medium/Low]

### Understanding:
- [Good/Fair/Needs improvement]

### Communication:
- [Observations about communication]

## Trial Lesson Evaluation
### Positive Aspects:
- [Positive 1]
- [Positive 2]

### Areas of Concern:
- [Concern 1]
- [Concern 2]

### Compatibility:
- [Assessment of student-teacher compatibility]

## Recommendations
### Continue with Regular Lessons:
- [Yes/No/Maybe]

### Suggested Frequency:
- [Recommendation]

### Special Considerations:
- [Any special needs or considerations]

## Follow-up Actions
- [ ] Send feedback to parent/student
- [ ] Schedule regular lessons (if applicable)
- [ ] Prepare materials for next session

## Notes
[Additional observations and notes]

---
*Created by TutorBot - {datetime.now().strftime("%Y-%m-%d %H:%M")}*
        """.strip()
        
        return template
    
    def organize_notes_by_student(self, notes_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize notes by student
        
        Args:
            notes_list: List of note dictionaries
            
        Returns:
            Dictionary organized by student name
        """
        organized = {}
        
        for note in notes_list:
            filename = note.get('name', '')
            parsed = self.parse_note_filename(filename)
            
            if parsed.get('is_valid'):
                student_name = parsed['student_name']
                if student_name not in organized:
                    organized[student_name] = []
                
                organized[student_name].append({
                    **note,
                    'parsed_metadata': parsed
                })
        
        # Sort notes by date for each student
        for student_name in organized:
            organized[student_name].sort(
                key=lambda x: x['parsed_metadata']['date'],
                reverse=True
            )
        
        return organized
    
    def get_note_statistics(self, notes_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about notes
        
        Args:
            notes_list: List of note dictionaries
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_notes': len(notes_list),
            'students': set(),
            'date_range': {'earliest': None, 'latest': None},
            'note_types': {},
            'recent_activity': []
        }
        
        for note in notes_list:
            filename = note.get('name', '')
            parsed = self.parse_note_filename(filename)
            
            if parsed.get('is_valid'):
                # Count students
                stats['students'].add(parsed['student_name'])
                
                # Track date range
                note_date = parsed['date']
                if not stats['date_range']['earliest'] or note_date < stats['date_range']['earliest']:
                    stats['date_range']['earliest'] = note_date
                if not stats['date_range']['latest'] or note_date > stats['date_range']['latest']:
                    stats['date_range']['latest'] = note_date
                
                # Count note types
                topic = parsed['topic'].lower()
                if 'intake' in topic:
                    note_type = 'intake'
                elif 'trial' in topic or 'proefles' in topic:
                    note_type = 'trial'
                else:
                    note_type = 'regular'
                
                stats['note_types'][note_type] = stats['note_types'].get(note_type, 0) + 1
                
                # Recent activity (last 30 days)
                if note_date >= datetime.now() - timedelta(days=30):
                    stats['recent_activity'].append({
                        'student': parsed['student_name'],
                        'date': note_date,
                        'topic': parsed['topic']
                    })
        
        # Convert set to list for JSON serialization
        stats['students'] = list(stats['students'])
        stats['students_count'] = len(stats['students'])
        
        return stats
