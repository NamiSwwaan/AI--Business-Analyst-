# src/core/ui_components.py
"""
UI components for the Task Manager application.
Renders the six-step workflow in Streamlit.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
from src.agents import run_ba_agent, load_employees, batch_task_processing
from src.services.task_matcher import get_similarity_scores
from src.core.task_processing import check_employees_for_task, assign_subtasks_to_employees
from src.utils.utils import parse_json_output
from src.core.navigation import go_to_next_step, go_to_previous_step, reset_to_step, save_state_to_history
from src.config import HOURS_PER_DAY, MAX_EMPLOYEES_PER_TASK, DEBUG

logger = logging.getLogger(__name__)

# Constants
STEPS = ["CEO Input", "Technical Spec", "Task Planning", "Task Assignment", "Sub-tasks", "Project Report"]

def render_step_1_ceo_input() -> None:
    """Render Step 1: Collect and analyze CEO input."""
    st.subheader("👩‍💼 CEO Input")
    ceo_input = st.text_area(
        "Describe your startup requirement:",
        st.session_state.get("ceo_input", ""),
        height=150,
        placeholder="e.g., Build a vendor dashboard",
        key="ceo_input_text",
        help="Enter a brief project description for analysis."
    )
    if ceo_input != st.session_state.get("ceo_input"):
        st.session_state.ceo_input = ceo_input
        save_state_to_history()

    if st.button("Analyze Requirement", help="Analyze the input with AI"):
        if not ceo_input.strip():
            st.error("Please enter a requirement.", icon="⚠️")
            return
        with st.spinner("Analyzing requirement..."):
            result = run_ba_agent(ceo_input)
            if result is None:
                st.error("Analysis failed. Please try again or check logs.", icon="❌")
                logger.error(f"BA agent failed for input: {ceo_input}")
            else:
                output = parse_json_output(result)
                st.session_state.output = output
                save_state_to_history()
                st.success("Analysis complete!", icon="✅")
                go_to_next_step()

def render_step_2_technical_spec() -> None:
    """Render Step 2: Display and edit technical specification."""
    st.subheader("📝 Technical Specification")
    output = st.session_state.get("output")
    if not output:
        st.error("Please complete CEO Input first.", icon="⚠️")
        if st.button("Return to CEO Input"):
            reset_to_step(1)
        return

    tech_spec = output.get("technical_spec", "")
    if isinstance(tech_spec, dict):
        tech_spec = tech_spec.get("overview", "")
        output["technical_spec"] = tech_spec

    updated_tech_spec = st.text_area(
        "Technical Specification",
        value=tech_spec,
        height=300,
        key="tech_spec_text",
        help="Edit the AI-generated technical specification.",
    )
    if updated_tech_spec != tech_spec:
        st.session_state.output["technical_spec"] = updated_tech_spec
        save_state_to_history()
        st.info("Technical specification updated.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Specification"):
            st.success("Specification saved!", icon="💾")
    with col2:
        if st.button("Proceed to Task Planning"):
            go_to_next_step()
    if st.button("Back to CEO Input"):
        go_to_previous_step()

def render_step_3_task_planning() -> None:
    """Render Step 3: Plan tasks, skills, dependencies, and resources."""
    st.subheader("📌 Task & Skill Breakdown")
    output = st.session_state.get("output")
    if not output:
        st.error("Please complete previous steps.", icon="⚠️")
        if st.button("Return to Technical Spec"):
            reset_to_step(2)
        return

    tasks = output.setdefault("tasks", [])
    if tasks and not isinstance(tasks[0], dict):
        tasks = [{"task": t, "priority": "Medium"} for t in tasks if isinstance(t, str)]
        output["tasks"] = tasks

    tasks_df = pd.DataFrame(tasks or [{"task": "", "priority": "Medium"}])
    edited_tasks = st.data_editor(
        tasks_df,
        num_rows="dynamic",
        key="tasks_editor",
        column_config={
            "task": st.column_config.TextColumn("Task", required=True),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High"], default="Medium"),
        },
    )
    if not edited_tasks.equals(tasks_df):
        output["tasks"] = [row for row in edited_tasks.to_dict("records") if row["task"].strip()]
        save_state_to_history()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Dependencies")
        deps_df = pd.DataFrame(output.setdefault("dependencies", []), columns=["Dependency"])
        edited_deps = st.data_editor(deps_df, num_rows="dynamic", key="deps_editor")
        if not edited_deps.equals(deps_df):
            output["dependencies"] = edited_deps["Dependency"].tolist()
            save_state_to_history()
    with col2:
        st.markdown("#### Skills")
        skills_df = pd.DataFrame(output.setdefault("skills", []), columns=["Skill"])
        edited_skills = st.data_editor(skills_df, num_rows="dynamic", key="skills_editor")
        if not edited_skills.equals(skills_df):
            output["skills"] = edited_skills["Skill"].tolist()
            save_state_to_history()

    st.markdown("#### Resources")
    resources = output.setdefault("resources", {"tech": [], "legal": [], "finance": [], "marketing": []})
    tabs = st.tabs(list(resources.keys()))
    for tab, key in zip(tabs, resources.keys()):
        with tab:
            df = pd.DataFrame({"Resource": resources[key]})
            edited = st.data_editor(df, num_rows="dynamic", key=f"{key}_editor")
            if not edited.equals(df):
                resources[key] = edited["Resource"].tolist()
                save_state_to_history()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Task Planning"):
            st.success("Task planning saved!", icon="💾")
    with col2:
        if output["tasks"] and st.button("Proceed to Task Assignment"):
            go_to_next_step()
        elif not output["tasks"]:
            st.warning("Please add at least one task.", icon="⚠️")
    if st.button("Back to Technical Spec"):
        go_to_previous_step()

def render_step_4_task_assignment() -> None:
    """Render Step 4: Assign tasks to employees."""
    st.subheader("👥 Task Assignment")
    output = st.session_state.get("output")
    task_board = st.session_state.get("task_board", [])
    if not output or not output.get("tasks"):
        st.error("Please complete Task Planning first.", icon="⚠️")
        if st.button("Return to Task Planning"):
            reset_to_step(3)
        return

    employees = load_employees()
    if not employees:
        st.error("No employees available. Check employees.json.", icon="❌")
        return

    with st.expander("Available Employees", expanded=DEBUG):
        st.dataframe(pd.DataFrame([{"Name": e["name"], "Role": e["role"]} for e in employees]))

    assignment_responses = st.session_state.setdefault("assignment_responses", {})
    for task_entry in output["tasks"]:
        task = task_entry["task"]
        priority = task_entry.get("priority", "Medium")

        with st.container():
            st.markdown(f"### 📋 Task: `{task}` (Priority: {priority})")
            duration, sub_tasks = batch_task_processing(task)
            adjusted_duration = max(2.0, duration * 0.75)
            days_needed = max(1, (adjusted_duration + HOURS_PER_DAY - 1) // HOURS_PER_DAY)

            st.write(f"Estimated Duration: {adjusted_duration:.1f} hours (~{days_needed} day{'s' if days_needed > 1 else ''})")

            col1, col2 = st.columns(2)
            with col1:
                duration_input = st.number_input(
                    "Adjust Duration (hours)",
                    min_value=1.0,
                    max_value=160.0,
                    value=float(adjusted_duration),
                    step=0.5,
                    key=f"duration_{task}",
                )
            with col2:
                deadline = st.date_input(
                    "Set Deadline",
                    value=datetime.today() + timedelta(days=days_needed),
                    min_value=datetime.today(),
                    key=f"deadline_{task}",
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"AI Suggest Employees", key=f"suggest_{task}", help="Use AI to suggest team"):
                    with st.spinner("Finding matches..."):
                        scored_employees = get_similarity_scores(task, employees)
                        assigned, responses = check_employees_for_task(task, employees, scored_employees, MAX_EMPLOYEES_PER_TASK)
                        if assigned:
                            task_entry = {
                                "task": task,
                                "employees": [e["name"] for e in assigned],
                                "emails": [e["email"] for e in assigned],
                                "deadline": deadline.strftime("%Y-%m-%d"),
                                "duration": duration_input,
                                "days_needed": max(1, (duration_input + HOURS_PER_DAY - 1) // HOURS_PER_DAY),
                                "priority": priority,
                            }
                            idx = next((i for i, t in enumerate(task_board) if t["task"] == task), None)
                            if idx is not None:
                                task_board[idx] = task_entry
                            else:
                                task_board.append(task_entry)
                            st.session_state.task_board = task_board
                            st.session_state.sub_tasks[task] = assign_subtasks_to_employees(sub_tasks, assigned)
                            assignment_responses[task] = responses
                            save_state_to_history()
                            st.success(f"Assigned {len(assigned)} employees!", icon="✅")
                            logger.info(f"AI assigned {len(assigned)} employees to '{task}'")

            with col2:
                existing_assigned = next((t["employees"] for t in task_board if t["task"] == task), [])
                selected_employees = st.multiselect(
                    "Select Employees",
                    options=[e["name"] for e in employees],
                    default=existing_assigned,
                    key=f"manual_{task}",
                    max_selections=MAX_EMPLOYEES_PER_TASK,
                    help="Manually select team members",
                )
                if selected_employees != existing_assigned and selected_employees:
                    assigned = [e for e in employees if e["name"] in selected_employees]
                    task_entry = {
                        "task": task,
                        "employees": selected_employees,
                        "emails": [e["email"] for e in assigned],
                        "deadline": deadline.strftime("%Y-%m-%d"),
                        "duration": duration_input,
                        "days_needed": max(1, (duration_input + HOURS_PER_DAY - 1) // HOURS_PER_DAY),
                        "priority": priority,
                    }
                    idx = next((i for i, t in enumerate(task_board) if t["task"] == task), None)
                    if idx is not None:
                        task_board[idx] = task_entry
                    else:
                        task_board.append(task_entry)
                    st.session_state.task_board = task_board
                    st.session_state.sub_tasks[task] = assign_subtasks_to_employees(sub_tasks, assigned)
                    save_state_to_history()
                    st.success(f"Manually assigned {len(selected_employees)} employees!", icon="✅")
                    logger.info(f"Manually assigned {len(selected_employees)} employees to '{task}'")

            if task in assignment_responses:
                with st.expander(f"Responses for '{task}'"):
                    st.markdown("\n".join(assignment_responses[task]))

    if task_board:
        st.subheader("Current Task Board")
        st.dataframe(pd.DataFrame(task_board)[["task", "employees", "deadline", "duration", "priority"]])
        approval = st.checkbox("Scrum Master Approval", value=st.session_state.get("scrum_master_approval", False))
        if approval != st.session_state.get("scrum_master_approval"):
            st.session_state.scrum_master_approval = approval
            save_state_to_history()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Task Planning"):
                go_to_previous_step()
        with col2:
            if approval and st.button("Proceed to Sub-tasks"):
                go_to_next_step()
            elif not approval:
                st.warning("Scrum Master approval required.", icon="⚠️")

def render_step_5_subtasks() -> None:
    """Render Step 5: Manage sub-tasks for assigned tasks."""
    st.subheader("🔍 Sub-tasks Management")
    task_board = st.session_state.get("task_board", [])
    if not task_board:
        st.error("No tasks assigned yet.", icon="⚠️")
        if st.button("Return to Task Assignment"):
            reset_to_step(4)
        return

    tabs = st.tabs([t["task"] for t in task_board])
    for tab, task_entry in zip(tabs, task_board):
        with tab:
            task = task_entry["task"]
            st.markdown(f"### Sub-tasks for: {task}")
            st.write(f"**Deadline:** {task_entry['deadline']} | **Team:** {', '.join(task_entry['employees'])}")
            sub_tasks = st.session_state.get("sub_tasks", {}).get(task, [])
            sub_tasks_df = pd.DataFrame(sub_tasks)
            edited_sub_tasks = st.data_editor(
                sub_tasks_df,
                num_rows="dynamic",
                key=f"subtasks_edit_{task}",
                column_config={
                    "sub_task": "Sub-Task",
                    "help": "Help Text",
                    "assigned": st.column_config.SelectboxColumn("Assigned", options=[""] + task_entry["employees"]),
                },
            )
            if not edited_sub_tasks.equals(sub_tasks_df):
                st.session_state.sub_tasks[task] = edited_sub_tasks.to_dict("records")
                save_state_to_history()
            if st.button(f"Save Sub-tasks", key=f"save_subtasks_{task}"):
                st.success(f"Sub-tasks saved for '{task}'!", icon="💾")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Task Assignment"):
            go_to_previous_step()
    with col2:
        if st.button("Start Project"):
            st.success("🎉 Project started!")
    with col3:
        if st.button("Proceed to Project Report"):
            go_to_next_step()

def render_step_6_project_report() -> None:
    """Render Step 6: Generate and export project report."""
    st.subheader("📊 Project Report")
    task_board = st.session_state.get("task_board", [])
    if not task_board:
        st.error("No tasks assigned yet.", icon="⚠️")
        if st.button("Return to Sub-tasks"):
            reset_to_step(5)
        return

    report = [
        f"Project: {st.session_state.get('ceo_input', 'Unnamed Project')}",
        f"Technical Specification: {json.dumps(st.session_state.get('output', {}).get('technical_spec', ''), indent=2)}",
        "\nResources:",
    ]
    for category, items in st.session_state.get("output", {}).get("resources", {}).items():
        report.append(f"  {category.capitalize()}: {', '.join(items) or 'None'}")
    report.append("\nTasks and Assignments:")
    for task_entry in task_board:
        report.extend([
            f"- Task: {task_entry['task']}",
            f"  Employees: {', '.join(task_entry['employees'])}",
            f"  Deadline: {task_entry['deadline']}",
            f"  Duration: {task_entry['duration']} hours",
            f"  Priority: {task_entry['priority']}",
        ])
        if task_entry["task"] in st.session_state.get("sub_tasks", {}):
            report.append("  Sub-tasks:")
            report.extend([
                f"    - {st['sub_task']} (Assigned: {st['assigned']})"
                for st in st.session_state["sub_tasks"][task_entry["task"]]
            ])

    st.text_area("Full Project Report", "\n".join(report), height=400, key="project_report_text")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Sub-tasks"):
            go_to_previous_step()
    with col2:
        if st.button("Export Project Plan"):
            project_plan = {
                "project": st.session_state.get("ceo_input", ""),
                "technical_spec": st.session_state.get("output", {}).get("technical_spec", ""),
                "tasks": task_board,
                "sub_tasks": st.session_state.get("sub_tasks", {}),
                "resources": st.session_state.get("output", {}).get("resources", {}),
            }
            st.download_button(
                "Download JSON",
                data=json.dumps(project_plan, indent=2),
                file_name="project_plan.json",
                mime="application/json",
            )
            logger.info("Exported project plan")