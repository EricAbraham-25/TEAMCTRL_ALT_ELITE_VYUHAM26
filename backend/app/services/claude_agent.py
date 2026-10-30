
import os
import json

import anthropic
from dotenv import load_dotenv

from app.services.agent_tools import (
    search_employees,
    get_employee_attendance,
    get_employee_tasks,
    list_projects,
    get_project_details,
    get_department_employees,
)

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")

TOOLS = [
    {
        "name": "search_employees",
        "description": "Search employees by name or employee code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_employee_attendance",
        "description": "Retrieve attendance records for a specific employee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"}
            },
            "required": ["employee_name"],
        },
    },
    {
        "name": "get_employee_tasks",
        "description": "Retrieve tasks assigned to a specific employee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"}
            },
            "required": ["employee_name"],
        },
    },
    {
        "name": "list_projects",
        "description": "List company projects, optionally filtered by status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"}
            },
        },
    },
    {
        "name": "get_project_details",
        "description": "Retrieve project information, team members, roles and tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string"}
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "get_department_employees",
        "description": "Find all employees in a department. ALWAYS use this tool when a manager asks who works in a department or asks for employees grouped by department.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department_name": {"type": "string"}
            },
            "required": ["department_name"],
        },
    },
]


def run_agent(db, question: str):
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing from .env")

    client = anthropic.Anthropic(api_key=api_key)

    available_functions = {
        "search_employees": lambda **args: search_employees(db, **args),
        "get_employee_attendance": lambda **args: get_employee_attendance(db, **args),
        "get_employee_tasks": lambda **args: get_employee_tasks(db, **args),
        "list_projects": lambda **args: list_projects(db, **args),
        "get_project_details": lambda **args: get_project_details(db, **args),
        "get_department_employees": lambda **args: get_department_employees(db, **args),
    }

    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]

    system_prompt = """
You are OrgMind AI, an AI assistant for company managers.

You must use the appropriate database tool for company-related factual questions.

IMPORTANT TOOL RULES:
- For department questions such as "Who works in Development?",
  ALWAYS call get_department_employees.
- Do not use search_employees to search for department names.
- For employee attendance, call get_employee_attendance.
- For employee tasks, call get_employee_tasks.
- For project team questions, call get_project_details.
- For project listing and status, call list_projects.

Never invent company information.
Only report facts returned by the database.
If a tool returns an error, explain it honestly.
Never claim to know an employee's live location.
Keep answers concise and clear.
"""

    for _ in range(4):
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            answer = [
                block.text
                for block in response.content
                if block.type == "text"
            ]
            return "\n".join(answer)

        messages.append({
            "role": "assistant",
            "content": response.content,
        })

        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            function = available_functions.get(block.name)

            if function is None:
                result = {"error": "Unknown tool"}
            else:
                try:
                    result = function(**block.input)
                except Exception as error:
                    print(f"Tool error ({block.name}): {error}")
                    result = {
                        "error": f"Database tool {block.name} failed."
                    }

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, default=str),
            })

        if not tool_results:
            break

        messages.append({
            "role": "user",
            "content": tool_results,
        })

    return "I couldn't complete that request. Please try again."
