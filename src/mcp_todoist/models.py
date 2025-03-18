"""
Data models for MCP Todoist.

This module defines Pydantic models for working with Todoist data,
providing validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field, validator


class TodoistColor(str, Enum):
    """Valid Todoist color names."""
    
    BERRY_RED = "berry_red"
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    OLIVE_GREEN = "olive_green"
    LIME_GREEN = "lime_green"
    GREEN = "green"
    MINT_GREEN = "mint_green"
    TEAL = "teal"
    SKY_BLUE = "sky_blue"
    LIGHT_BLUE = "light_blue"
    BLUE = "blue"
    GRAPE = "grape"
    VIOLET = "violet"
    LAVENDER = "lavender"
    MAGENTA = "magenta"
    SALMON = "salmon"
    CHARCOAL = "charcoal"
    GREY = "grey"
    TAUPE = "taupe"


class TodoistPriority(int, Enum):
    """Valid Todoist priority levels (1 = lowest, 4 = highest)."""
    
    P1 = 1  # Low priority
    P2 = 2  # Normal priority
    P3 = 3  # Medium priority
    P4 = 4  # High priority


class TaskDue(BaseModel):
    """Due date information for a task."""
    
    date: Optional[str] = None
    string: Optional[str] = None
    datetime: Optional[str] = None
    recurring: Optional[bool] = None
    
    @validator("date")
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format."""
        if v and not v.startswith("20"):  # Simple check for YYYY-MM-DD
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class TaskMCPInput(BaseModel):
    """Model for task input from MCP."""
    
    content: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # For convenience, will look up project ID
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    labels: Optional[List[str]] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    due_string: Optional[str] = None
    due_date: Optional[str] = None
    due_datetime: Optional[str] = None
    due_lang: Optional[str] = None
    assignee_id: Optional[str] = None


class TaskMCPOutput(BaseModel):
    """Model for task output to MCP."""
    
    id: str
    content: str
    description: str = ""
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    labels: List[str] = Field(default_factory=list)
    priority: int = 1
    due: Optional[TaskDue] = None
    url: str
    comment_count: int = 0
    created_at: datetime
    is_completed: bool = False
    creator_id: Optional[str] = None
    assignee_id: Optional[str] = None
    
    @classmethod
    def from_todoist(cls, task: Any) -> "TaskMCPOutput":
        """Convert a Todoist API task to a TaskMCPOutput."""
        due = None
        if hasattr(task, 'due') and task.due:
            due = TaskDue(
                date=getattr(task.due, 'date', None),
                string=getattr(task.due, 'string', None),
                datetime=getattr(task.due, 'datetime', None),
                recurring=getattr(task.due, 'recurring', None),
            )
        
        created_at_value = getattr(task, 'created_at', None)
        if isinstance(created_at_value, str):
            try:
                created_at = datetime.fromisoformat(created_at_value.replace('Z', '+00:00'))
            except ValueError:
                created_at = datetime.now()
        else:
            created_at = datetime.now()
        
        return cls(
            id=task.id,
            content=task.content,
            description=getattr(task, 'description', "") or "",
            project_id=getattr(task, 'project_id', None),
            section_id=getattr(task, 'section_id', None),
            parent_id=getattr(task, 'parent_id', None),
            labels=getattr(task, 'labels', []) or [],
            priority=getattr(task, 'priority', 1),
            due=due,
            url=getattr(task, 'url', f"https://todoist.com/app/task/{task.id}"),
            comment_count=getattr(task, 'comment_count', 0),
            created_at=created_at,
            is_completed=False,  # API doesn't return completed tasks
            creator_id=getattr(task, 'creator_id', None),
            assignee_id=getattr(task, 'assignee_id', None),
        )


class ProjectMCPInput(BaseModel):
    """Model for project input from MCP."""
    
    name: str
    parent_id: Optional[str] = None
    color: Optional[str] = None
    favorite: Optional[bool] = False
    
    @validator("color")
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color name."""
        if v and v not in [c.value for c in TodoistColor]:
            valid_colors = ", ".join([c.value for c in TodoistColor])
            raise ValueError(f"Color must be one of: {valid_colors}")
        return v


class ProjectMCPOutput(BaseModel):
    """Model for project output to MCP."""
    
    id: str
    name: str
    color: str
    parent_id: Optional[str] = None
    order: Optional[int] = None
    comment_count: int = 0
    is_shared: bool = False
    is_favorite: bool = False
    is_inbox_project: bool = False
    is_team_inbox: bool = False
    view_style: str = "list"
    url: str
    
    @classmethod
    def from_todoist(cls, project: Any) -> "ProjectMCPOutput":
        """Convert a Todoist API project to a ProjectMCPOutput."""
        return cls(
            id=project.id,
            name=project.name,
            color=getattr(project, 'color', 'grey'),
            parent_id=getattr(project, 'parent_id', None),
            order=getattr(project, 'order', None),
            comment_count=getattr(project, 'comment_count', 0),
            is_shared=getattr(project, 'is_shared', False),
            is_favorite=getattr(project, 'is_favorite', False),
            is_inbox_project=getattr(project, 'is_inbox_project', False),
            is_team_inbox=getattr(project, 'is_team_inbox', False),
            view_style=getattr(project, 'view_style', 'list'),
            url=getattr(project, 'url', f"https://todoist.com/app/project/{project.id}"),
        )


class LabelMCPInput(BaseModel):
    """Model for label input from MCP."""
    
    name: str
    color: Optional[str] = None
    favorite: Optional[bool] = False
    
    @validator("color")
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color name."""
        if v and v not in [c.value for c in TodoistColor]:
            valid_colors = ", ".join([c.value for c in TodoistColor])
            raise ValueError(f"Color must be one of: {valid_colors}")
        return v


class LabelMCPOutput(BaseModel):
    """Model for label output to MCP."""
    
    id: str
    name: str
    color: str
    order: Optional[int] = None
    is_favorite: bool = False
    
    @classmethod
    def from_todoist(cls, label: Any) -> "LabelMCPOutput":
        """Convert a Todoist API label to a LabelMCPOutput."""
        return cls(
            id=label.id,
            name=label.name,
            color=getattr(label, 'color', 'grey'),
            order=getattr(label, 'order', None),
            is_favorite=getattr(label, 'is_favorite', False),
        )


class TaskFilterMCPInput(BaseModel):
    """Model for task filtering from MCP."""
    
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # For convenience, will look up project ID
    section_id: Optional[str] = None
    label_id: Optional[str] = None
    label_name: Optional[str] = None  # For convenience, will look up label ID
    filter_string: Optional[str] = None
    due_today: Optional[bool] = None
    due_upcoming: Optional[bool] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None
    limit: Optional[int] = Field(None, ge=1, le=100)
