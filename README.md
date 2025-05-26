---
```markdown
# Task Manager for Startup Crew AI

A Streamlit-based application designed to streamline project management for startups by leveraging AI agents to analyze requirements, plan tasks, assign employees, and generate project reports.

## Overview

This tool assists CEOs and Scrum Masters in managing startup projects by:
- Collecting high-level requirements from the CEO.
- Generating technical specifications and task breakdowns using AI.
- Assigning tasks to employees based on skills and availability.
- Managing sub-tasks and tracking project progress.
- Producing detailed project reports.

## Project Structure

```

│
├── .env                  # Environment variables (API keys, configuration)<br>
├── README.md             # Project documentation (this file)<br>
├── data/                 # Data files<br>
│   └── employees.json    # Employee details (name, role, email, skills)<br>
├── src/                  # Source code<br>
│   ├── agents/           # AI agent implementations<br>
│   │   ├── __init__.py<br>
│   │   ├── ba_agent.py   # Business Analyst agent<br>
│   │   ├── base_agent.py # Base agent class<br>
│   │   ├── employee_agent.py # Employee evaluation agent<br>
│   │   └── task_agent.py # Task processing agent<br>
│   ├── config/           # Configuration files<br>
│   │   ├── __init__.py<br>
│   │   ├── config.py     # General app constants<br>
│   │   └── llm_config.py # LLM configuration<br>
│   ├── core/             # Core application logic<br>
│   │   ├── __init__.py<br>
│   │   ├── app.py        # Main Streamlit app<br>
│   │   ├── navigation.py # Navigation and progress tracking<br>
│   │   ├── state_management.py # Session state handling<br>
│   │   ├── task_processing.py # Task estimation and sub-task generation<br>
│   │   └── ui_components.py # UI components for each step<br>
│   ├── services/         # External service integrations<br>
│   │   ├── __init__.py<br>
│   │   ├── email_service.py # Email notification service<br>
│   │   └── task_matcher.py # Task-employee matching logic<br>
│   └── utils/            # Utility functions<br>
│       └── utils.py      # JSON parsing, retry logic, etc.<br>
└── session_data/         # Auto-generated session state storage (not in repo)<br>

```

## Prerequisites

- **Python 3.9+**
- **Dependencies**: Install via `pip install -r requirements.txt` (create this file if needed)
  - `streamlit`
  - `crewai`
  - `python-dotenv`
  - `pandas`
  - `scikit-learn`
  - `litellm`
  - `tenacity`
- **Groq API Key**: Obtain from [Groqcloud](https://groqcloud.com) and add to `.env`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd task-manager
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Copy `.env.example` (if provided) to `.env` or create `.env` based on the template in `.env` section above.
   - Update `LLM_API_KEY` with your Groq API key.

4. **Run the Application**:
   ```bash
   streamlit run src/core/app.py
   ```

## Usage

1. **CEO Input**: Enter your project requirement (e.g., "Build a vendor dashboard").
2. **Technical Specification**: Review and edit the AI-generated spec.
3. **Task Planning**: Define tasks, skills, dependencies, and resources.
4. **Task Assignment**: Assign tasks to employees manually or via AI suggestions.
5. **Sub-tasks**: Manage detailed sub-tasks for each assignment.
6. **Project Report**: Export the final plan as JSON.

Progress is saved automatically in `session_data/` using a unique session ID.

## Environment Variables

See `.env` for details:
- `DEBUG`: Enable debug mode.
- `LOG_LEVEL`: Set logging level.
- `EMPLOYEES_FILE`: Path to employee data.
- `SESSION_DIR`: Session state directory.
- `LLM_*`: LLM configuration (API key, model, etc.).
- `EMAIL_*`: (Future) Email service settings.

**Note**: Keep `.env` out of version control by adding it to `.gitignore`.

## Contributing

- Fork the repo, create a branch, and submit a pull request.
- Follow Python PEP 8 style guidelines.
- Add tests in a future `tests/` directory (TBD).

## Future Improvements

- Email notifications for task assignments.
- Real-time collaboration features.
- Enhanced AI task estimation accuracy.
- Unit tests and CI/CD integration.
```

### Improvements and Rationale:
1. **Clarity**: Provides a clear overview of the project’s purpose and functionality.
2. **Structure**: Reflects the new directory structure you’ve outlined, making it easy to navigate the codebase.
3. **Setup Instructions**: Includes detailed steps to get the app running, referencing the `.env` file we just optimized.
4. **Usage Guide**: Mirrors the UI flow (CEO Input → Project Report) to maintain the same UX while explaining it to users.
5. **Security**: Emphasizes keeping `.env` private.
6. **Expandability**: Leaves room for future features (e.g., email, tests) and contributions.
7. **No Bugs**: As a documentation file, it has no executable code to optimize, but it aligns with the refactored structure.

### Functionality Check:
- This file doesn’t affect runtime behavior but ensures users can set up and use the app correctly.
- It assumes a `requirements.txt` file (we can create one later if needed).
