"""
Integration Module

Ties together calendar and notes functionality
for seamless lesson management.
"""

from .lesson_manager import LessonManager
from .workflow_manager import WorkflowManager

__all__ = ['LessonManager', 'WorkflowManager']
