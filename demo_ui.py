#!/usr/bin/env python3
"""
Demo script to showcase the Five Minds UI system
"""

import time
import threading
from fiveminds.ui import UIServer


def populate_demo_data(server: UIServer):
    """Populate the UI with demo data."""
    time.sleep(1)
    
    # Set objective
    server.set_objective({
        "description": "Create a REST API for user management",
        "requirements": [
            "Implement user CRUD operations",
            "Add authentication middleware",
            "Create API documentation",
            "Write integration tests"
        ],
        "constraints": [
            "Use Flask framework",
            "Follow REST best practices"
        ],
        "success_metrics": [
            "All endpoints work correctly",
            "100% test coverage"
        ]
    })
    
    time.sleep(0.5)
    
    # Add HeadMaster reasoning
    server.add_headmaster_reasoning("Analyzing repository structure...")
    time.sleep(0.3)
    server.add_headmaster_reasoning("Detected Python project with Flask framework")
    time.sleep(0.3)
    server.add_headmaster_reasoning("Decomposing objective into 4 tickets")
    
    # Set tickets
    tickets = [
        {
            "id": "TKT-001",
            "title": "Implement user CRUD operations",
            "description": "Create endpoints for Create, Read, Update, Delete user operations",
            "acceptance_criteria": [
                {"description": "POST /users creates new user", "met": True},
                {"description": "GET /users returns all users", "met": True},
                {"description": "PUT /users/:id updates user", "met": True},
                {"description": "DELETE /users/:id removes user", "met": True}
            ],
            "status": "completed",
            "priority": "high",
            "dependencies": [],
            "assigned_runner": "R1"
        },
        {
            "id": "TKT-002",
            "title": "Add authentication middleware",
            "description": "Implement JWT-based authentication for API endpoints",
            "acceptance_criteria": [
                {"description": "JWT token generation", "met": True},
                {"description": "Token validation middleware", "met": True},
                {"description": "Protected routes require auth", "met": False}
            ],
            "status": "in_progress",
            "priority": "high",
            "dependencies": ["TKT-001"],
            "assigned_runner": "R2"
        },
        {
            "id": "TKT-003",
            "title": "Create API documentation",
            "description": "Generate OpenAPI/Swagger documentation for all endpoints",
            "acceptance_criteria": [
                {"description": "OpenAPI spec generated", "met": False},
                {"description": "Swagger UI accessible", "met": False}
            ],
            "status": "pending",
            "priority": "medium",
            "dependencies": ["TKT-001", "TKT-002"]
        },
        {
            "id": "TKT-004",
            "title": "Write integration tests",
            "description": "Create comprehensive test suite for all API endpoints",
            "acceptance_criteria": [
                {"description": "Tests for CRUD operations", "met": False},
                {"description": "Tests for authentication", "met": False},
                {"description": "100% code coverage", "met": False}
            ],
            "status": "pending",
            "priority": "medium",
            "dependencies": ["TKT-001", "TKT-002"]
        }
    ]
    
    server.set_tickets(tickets)
    
    # Set dependencies
    dependencies = [
        {"from": "TKT-001", "to": "TKT-002"},
        {"from": "TKT-001", "to": "TKT-003"},
        {"from": "TKT-002", "to": "TKT-003"},
        {"from": "TKT-001", "to": "TKT-004"},
        {"from": "TKT-002", "to": "TKT-004"}
    ]
    server.set_dependencies(dependencies)
    
    # Add runners
    server.add_runner("R1", "TKT-001")
    server.update_runner_log("R1", "Starting ticket execution...")
    server.update_runner_log("R1", "Creating sandbox environment")
    server.update_runner_log("R1", "Implementing user CRUD operations")
    server.update_runner_log("R1", "Creating user model")
    server.update_runner_log("R1", "Implementing POST /users endpoint")
    server.update_runner_log("R1", "Implementing GET /users endpoint")
    server.update_runner_log("R1", "Running tests...")
    server.update_runner_files("R1", ["models/user.py", "routes/users.py", "tests/test_users.py"])
    
    server.add_runner("R2", "TKT-002")
    server.update_runner_log("R2", "Starting authentication implementation...")
    server.update_runner_log("R2", "Creating JWT utilities")
    server.update_runner_log("R2", "Implementing auth middleware")
    server.update_runner_files("R2", ["auth/jwt.py", "middleware/auth.py"])
    
    # Complete R1
    server.complete_runner("R1", {
        "ticket_id": "TKT-001",
        "success": True,
        "diff": """diff --git a/models/user.py b/models/user.py
new file mode 100644
--- /dev/null
+++ b/models/user.py
@@ -0,0 +1,15 @@
+from dataclasses import dataclass
+from typing import Optional
+
+@dataclass
+class User:
+    id: int
+    username: str
+    email: str
+    password_hash: str
+    created_at: str
+
+def create_user(username: str, email: str, password: str) -> User:
+    # Implementation
+    pass""",
        "logs": ["Test suite passed", "All criteria met"],
        "test_results": {"total": 12, "passed": 12, "failed": 0, "skipped": 0},
        "execution_time": 45.2
    })
    
    # Add review
    server.add_review({
        "ticket_id": "TKT-001",
        "approved": True,
        "feedback": "✓ Review passed - ticket approved\nAcceptance criteria: 4/4 met\nTests: 12/12 passed\nAlignment score: 0.95\nChanges: +85 -0 lines",
        "alignment_score": 0.95,
        "follow_up_tickets": [],
        "suggestions": [
            "Consider adding input validation",
            "Add rate limiting to endpoints"
        ]
    })
    
    # Update cost
    server.update_cost(tokens=15000, api_calls=25, cost=0.45)
    
    # Update status
    server.set_status("executing")
    server.update_headmaster("integration_status", "pending")
    
    print("Demo data populated!")


def main():
    print("\n🧠 Five Minds UI Demo")
    print("=" * 50)
    print("Starting UI server at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop\n")
    
    server = UIServer(host="127.0.0.1", port=5000)
    
    # Populate demo data in background
    thread = threading.Thread(target=populate_demo_data, args=(server,))
    thread.daemon = True
    thread.start()
    
    # Start server (blocking)
    server.start(background=False)


if __name__ == "__main__":
    main()
