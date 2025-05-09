"""
Todoist API client for MCP Todoist.

This module provides an async wrapper around the Todoist API SDK,
with proper error handling and configuration.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, cast

from todoist_api_python.api import TodoistAPI
# endpoints import removed: no longer needed or available in latest SDK
from todoist_api_python.models import (
    Task, Project, Label, Comment, Section, Collaborator
)

from .config import get_config
from .utils import (
    get_logger,
    handle_exceptions,
    TodoistError,
    AuthenticationError,
)

# Get configuration
config = get_config()

# Set up logging
logger = get_logger(__name__)


class TodoistClient:
    """
    Async wrapper for the Todoist API client.
    
    This class provides async methods for interacting with the Todoist API,
    with proper error handling and configuration.
    """
    
    def __init__(self, api_token: Optional[str] = None) -> None:
        """
        Initialize the Todoist client.
        
        Args:
            api_token: The Todoist API token. If not provided, it will be loaded from config.
        """
        self.api_token = api_token or config.todoist.api_token
        
        if not self.api_token:
            logger.error("Todoist API token not provided")
            raise AuthenticationError("Todoist API token not provided")
        
        # Initialize the Todoist API client
        self.api = TodoistAPI(self.api_token)
        logger.debug("Todoist API client initialized")
    
    @handle_exceptions
    async def get_tasks(
        self,
        project_id: Optional[str] = None,
        section_id: Optional[str] = None,
        label_id: Optional[str] = None,
        filter_string: Optional[str] = None,
        lang: Optional[str] = None,
        ids: Optional[List[str]] = None,
    ) -> List[Task]:
        """
        Get tasks from Todoist.
        
        Args:
            project_id: Filter tasks by project ID
            section_id: Filter tasks by section ID
            label_id: Filter tasks by label ID
            filter_string: Filter tasks using Todoist's filter syntax
            lang: Language for parsing filter strings
            ids: List of task IDs to retrieve
            
        Returns:
            List of Task objects
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(
            f"Getting tasks with filters: project_id={project_id}, "
            f"section_id={section_id}, label_id={label_id}, "
            f"filter_string={filter_string}, ids={ids}"
        )
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            tasks = await loop.run_in_executor(
                None,
                lambda: self.api.get_tasks(
                    project_id=project_id,
                    section_id=section_id,
                    label_id=label_id,
                    filter=filter_string,
                    lang=lang,
                    ids=ids,
                ),
            )
            logger.debug(f"Retrieved {len(tasks)} tasks")
            return tasks
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get tasks: {str(e)}")
            raise TodoistError(f"Failed to get tasks: {str(e)}") from e
    
    @handle_exceptions
    async def get_task(self, task_id: str) -> Task:
        """
        Get a specific task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Task object
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Getting task with ID: {task_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            task = await loop.run_in_executor(
                None,
                lambda: self.api.get_task(task_id),
            )
            logger.debug(f"Retrieved task: {task.content}")
            return task
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get task {task_id}: {str(e)}")
            raise TodoistError(f"Failed to get task: {str(e)}") from e
    
    @handle_exceptions
    async def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        section_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        order: Optional[int] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[int] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None,
        due_datetime: Optional[str] = None,
        due_lang: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> Task:
        """
        Create a new task in Todoist.
        
        Args:
            content: Task content (title)
            description: Task description
            project_id: Project ID for the task
            section_id: Section ID for the task
            parent_id: Parent task ID (for subtasks)
            order: Task order
            labels: List of label names
            priority: Task priority (1-4)
            due_string: Due date as a string (e.g., "tomorrow")
            due_date: Due date as YYYY-MM-DD
            due_datetime: Due datetime as RFC3339
            due_lang: Language for parsing due_string
            assignee_id: User ID to assign the task to
            
        Returns:
            Created Task object
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Creating task: {content}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            task = await loop.run_in_executor(
                None,
                lambda: self.api.add_task(
                    content=content,
                    description=description,
                    project_id=project_id,
                    section_id=section_id,
                    parent_id=parent_id,
                    order=order,
                    labels=labels,
                    priority=priority,
                    due_string=due_string,
                    due_date=due_date,
                    due_datetime=due_datetime,
                    due_lang=due_lang,
                    assignee_id=assignee_id,
                ),
            )
            logger.debug(f"Created task with ID: {task.id}")
            return task
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to create task: {str(e)}")
            raise TodoistError(f"Failed to create task: {str(e)}") from e
    
    @handle_exceptions
    async def update_task(
        self,
        task_id: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        section_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        order: Optional[int] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[int] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None,
        due_datetime: Optional[str] = None,
        due_lang: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> bool:
        """
        Update an existing task in Todoist.
        
        Args:
            task_id: ID of the task to update
            content: New task content (title)
            description: New task description
            project_id: New project ID
            section_id: New section ID
            parent_id: New parent task ID
            order: New task order
            labels: New list of label names
            priority: New task priority (1-4)
            due_string: New due date as a string
            due_date: New due date as YYYY-MM-DD
            due_datetime: New due datetime as RFC3339
            due_lang: Language for parsing due_string
            assignee_id: New user ID to assign the task to
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Updating task with ID: {task_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.update_task(
                    task_id=task_id,
                    content=content,
                    description=description,
                    project_id=project_id,
                    section_id=section_id,
                    parent_id=parent_id,
                    order=order,
                    labels=labels,
                    priority=priority,
                    due_string=due_string,
                    due_date=due_date,
                    due_datetime=due_datetime,
                    due_lang=due_lang,
                    assignee_id=assignee_id,
                ),
            )
            logger.debug(f"Updated task with ID: {task_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise TodoistError(f"Failed to update task: {str(e)}") from e
    
    @handle_exceptions
    async def close_task(self, task_id: str) -> bool:
        """
        Close (complete) a task.
        
        Args:
            task_id: ID of the task to close
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Closing task with ID: {task_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.close_task(task_id),
            )
            logger.debug(f"Closed task with ID: {task_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to close task {task_id}: {str(e)}")
            raise TodoistError(f"Failed to close task: {str(e)}") from e
    
    @handle_exceptions
    async def reopen_task(self, task_id: str) -> bool:
        """
        Reopen a completed task.
        
        Args:
            task_id: ID of the task to reopen
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Reopening task with ID: {task_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.reopen_task(task_id),
            )
            logger.debug(f"Reopened task with ID: {task_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to reopen task {task_id}: {str(e)}")
            raise TodoistError(f"Failed to reopen task: {str(e)}") from e
    
    @handle_exceptions
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Deleting task with ID: {task_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.delete_task(task_id),
            )
            logger.debug(f"Deleted task with ID: {task_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            raise TodoistError(f"Failed to delete task: {str(e)}") from e
    
    @handle_exceptions
    async def get_projects(self) -> List[Project]:
        """
        Get all projects.
        
        Returns:
            List of Project objects
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug("Getting all projects")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            projects = await loop.run_in_executor(
                None,
                lambda: self.api.get_projects(),
            )
            logger.debug(f"Retrieved {len(projects)} projects")
            return projects
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get projects: {str(e)}")
            raise TodoistError(f"Failed to get projects: {str(e)}") from e
    
    @handle_exceptions
    async def get_project(self, project_id: str) -> Project:
        """
        Get a specific project by ID.
        
        Args:
            project_id: The ID of the project to retrieve
            
        Returns:
            Project object
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Getting project with ID: {project_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            project = await loop.run_in_executor(
                None,
                lambda: self.api.get_project(project_id),
            )
            logger.debug(f"Retrieved project: {project.name}")
            return project
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise TodoistError(f"Failed to get project: {str(e)}") from e
    
    @handle_exceptions
    async def create_project(
        self,
        name: str,
        parent_id: Optional[str] = None,
        color: Optional[str] = None,
        favorite: bool = False,
    ) -> Project:
        """
        Create a new project.
        
        Args:
            name: Project name
            parent_id: Parent project ID (for sub-projects)
            color: Project color (e.g., "berry_red", "blue")
            favorite: Whether the project is a favorite
            
        Returns:
            Created Project object
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Creating project: {name}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            project = await loop.run_in_executor(
                None,
                lambda: self.api.add_project(
                    name=name,
                    parent_id=parent_id,
                    color=color,
                    favorite=favorite,
                ),
            )
            logger.debug(f"Created project with ID: {project.id}")
            return project
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to create project: {str(e)}")
            raise TodoistError(f"Failed to create project: {str(e)}") from e
    
    @handle_exceptions
    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        favorite: Optional[bool] = None,
    ) -> bool:
        """
        Update an existing project.
        
        Args:
            project_id: ID of the project to update
            name: New project name
            color: New project color
            favorite: Whether the project is a favorite
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Updating project with ID: {project_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.update_project(
                    project_id=project_id,
                    name=name,
                    color=color,
                    favorite=favorite,
                ),
            )
            logger.debug(f"Updated project with ID: {project_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to update project {project_id}: {str(e)}")
            raise TodoistError(f"Failed to update project: {str(e)}") from e
    
    @handle_exceptions
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: ID of the project to delete
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Deleting project with ID: {project_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.delete_project(project_id),
            )
            logger.debug(f"Deleted project with ID: {project_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            raise TodoistError(f"Failed to delete project: {str(e)}") from e
    
    @handle_exceptions
    async def get_labels(self) -> List[Label]:
        """
        Get all labels.
        
        Returns:
            List of Label objects
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug("Getting all labels")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            labels = await loop.run_in_executor(
                None,
                lambda: self.api.get_labels(),
            )
            logger.debug(f"Retrieved {len(labels)} labels")
            return labels
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get labels: {str(e)}")
            raise TodoistError(f"Failed to get labels: {str(e)}") from e
    
    @handle_exceptions
    async def get_label(self, label_id: str) -> Label:
        """
        Get a specific label by ID.
        
        Args:
            label_id: The ID of the label to retrieve
            
        Returns:
            Label object
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Getting label with ID: {label_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            label = await loop.run_in_executor(
                None,
                lambda: self.api.get_label(label_id),
            )
            logger.debug(f"Retrieved label: {label.name}")
            return label
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to get label {label_id}: {str(e)}")
            raise TodoistError(f"Failed to get label: {str(e)}") from e
    
    @handle_exceptions
    async def create_label(
        self,
        name: str,
        color: Optional[str] = None,
        favorite: bool = False,
    ) -> Label:
        """
        Create a new label.
        
        Args:
            name: Label name
            color: Label color (e.g., "berry_red", "blue")
            favorite: Whether the label is a favorite
            
        Returns:
            Created Label object
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Creating label: {name}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            label = await loop.run_in_executor(
                None,
                lambda: self.api.add_label(
                    name=name,
                    color=color,
                    favorite=favorite,
                ),
            )
            logger.debug(f"Created label with ID: {label.id}")
            return label
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to create label: {str(e)}")
            raise TodoistError(f"Failed to create label: {str(e)}") from e
    
    @handle_exceptions
    async def update_label(
        self,
        label_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        favorite: Optional[bool] = None,
    ) -> bool:
        """
        Update an existing label.
        
        Args:
            label_id: ID of the label to update
            name: New label name
            color: New label color
            favorite: Whether the label is a favorite
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Updating label with ID: {label_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.update_label(
                    label_id=label_id,
                    name=name,
                    color=color,
                    favorite=favorite,
                ),
            )
            logger.debug(f"Updated label with ID: {label_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to update label {label_id}: {str(e)}")
            raise TodoistError(f"Failed to update label: {str(e)}") from e
    
    @handle_exceptions
    async def delete_label(self, label_id: str) -> bool:
        """
        Delete a label.
        
        Args:
            label_id: ID of the label to delete
            
        Returns:
            True if successful
            
        Raises:
            TodoistError: If the API call fails
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Deleting label with ID: {label_id}")
        
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(
                None,
                lambda: self.api.delete_label(label_id),
            )
            logger.debug(f"Deleted label with ID: {label_id}")
            return success
        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error(f"Authentication failed: {str(e)}")
                raise AuthenticationError("Invalid or expired Todoist API token") from e
            logger.error(f"Failed to delete label {label_id}: {str(e)}")
            raise TodoistError(f"Failed to delete label: {str(e)}") from e
