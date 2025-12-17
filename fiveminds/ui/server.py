"""
Five Minds UI Server - Flask-based web server with WebSocket support
"""

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

logger = logging.getLogger(__name__)


class UIServer:
    """
    Web-based UI server for Five Minds system.
    
    Provides:
    - Dashboard View: objective, status, progress timeline, cost usage, active jobs
    - Runner View: ticket details, live logs, files touched, runtime, cancel control
    - HeadMaster View: reasoning log, ticket graph, dependency view, integration status
    - Review View: diff viewer, acceptance checklist, risk list, follow-up ticket buttons
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Initialize the UI server.

        Args:
            host: Host address to bind to
            port: Port number to bind to
        """
        self.host = host
        self.port = port
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static")
        )
        # Use environment variable for secret key, fallback to generated key
        import os
        import secrets
        self.app.config['SECRET_KEY'] = os.environ.get('FIVEMINDS_SECRET_KEY', secrets.token_hex(32))
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # State management
        self._state: Dict[str, Any] = {
            "objective": None,
            "status": "idle",
            "start_time": None,
            "progress": [],
            "cost_usage": {"tokens": 0, "api_calls": 0, "estimated_cost": 0.0},
            "active_jobs": [],
            "tickets": [],
            "runners": {},
            "headmaster": {
                "reasoning_log": [],
                "ticket_graph": [],
                "dependencies": [],
                "integration_status": "pending"
            },
            "reviews": [],
            "results": {}
        }
        self._lock = threading.Lock()
        self._cancel_callbacks: Dict[str, Callable] = {}
        self._server_thread: Optional[threading.Thread] = None
        self._running = False
        
        self._setup_routes()
        self._setup_socketio_handlers()
        
        logger.info(f"UI Server initialized at {host}:{port}")

    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard view."""
            return render_template('dashboard.html')
        
        @self.app.route('/runner')
        def runner_view():
            """Runner view."""
            return render_template('runner.html')
        
        @self.app.route('/runner/<runner_id>')
        def runner_detail(runner_id):
            """Runner detail view."""
            return render_template('runner_detail.html', runner_id=runner_id)
        
        @self.app.route('/headmaster')
        def headmaster_view():
            """HeadMaster view."""
            return render_template('headmaster.html')
        
        @self.app.route('/review')
        def review_view():
            """Review view."""
            return render_template('review.html')
        
        @self.app.route('/review/<ticket_id>')
        def review_detail(ticket_id):
            """Review detail view."""
            return render_template('review_detail.html', ticket_id=ticket_id)
        
        @self.app.route('/settings')
        def settings_view():
            """Settings view for API keys and model configuration."""
            return render_template('settings.html')
        
        # API endpoints
        @self.app.route('/api/state')
        def get_state():
            """Get current system state."""
            with self._lock:
                return jsonify(self._state)
        
        @self.app.route('/api/tickets')
        def get_tickets():
            """Get all tickets."""
            with self._lock:
                return jsonify(self._state["tickets"])
        
        @self.app.route('/api/runners')
        def get_runners():
            """Get all runners."""
            with self._lock:
                return jsonify(self._state["runners"])
        
        @self.app.route('/api/reviews')
        def get_reviews():
            """Get all reviews."""
            with self._lock:
                return jsonify(self._state["reviews"])
        
        @self.app.route('/api/headmaster')
        def get_headmaster():
            """Get headmaster state."""
            with self._lock:
                return jsonify(self._state["headmaster"])
        
        @self.app.route('/api/settings', methods=['GET'])
        def get_settings():
            """Get current settings (without exposing full API keys)."""
            with self._lock:
                settings = self._state.get("settings", {})
                # Return safe version without full API keys
                safe_settings = {
                    "api_keys": {
                        "openai_configured": bool(settings.get("api_keys", {}).get("openai_key")),
                        "anthropic_configured": bool(settings.get("api_keys", {}).get("anthropic_key")),
                        "google_configured": bool(settings.get("api_keys", {}).get("google_key")),
                        "cohere_configured": bool(settings.get("api_keys", {}).get("cohere_key")),
                        "custom_endpoint": settings.get("api_keys", {}).get("custom_endpoint", "")
                    },
                    "models": settings.get("models", {
                        "headmaster": "gpt-4",
                        "runner": "gpt-4",
                        "reviewer": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    })
                }
                return jsonify(safe_settings)
        
        @self.app.route('/api/settings', methods=['POST'])
        def save_settings():
            """Save settings."""
            data = request.json
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400
            
            with self._lock:
                if "settings" not in self._state:
                    self._state["settings"] = {}
                
                # Update API keys (only if provided - don't overwrite with empty)
                if "api_keys" in data:
                    if "api_keys" not in self._state["settings"]:
                        self._state["settings"]["api_keys"] = {}
                    
                    for key in ["openai_key", "anthropic_key", "google_key", "cohere_key"]:
                        if data["api_keys"].get(key):
                            self._state["settings"]["api_keys"][key] = data["api_keys"][key]
                    
                    # Custom endpoint can be empty
                    if "custom_endpoint" in data["api_keys"]:
                        self._state["settings"]["api_keys"]["custom_endpoint"] = data["api_keys"]["custom_endpoint"]
                
                # Update model configuration
                if "models" in data:
                    self._state["settings"]["models"] = data["models"]
            
            self._emit_update("settings_update", {"updated": True})
            return jsonify({"success": True, "message": "Settings saved successfully"})
        
        @self.app.route('/api/settings/reset', methods=['POST'])
        def reset_settings():
            """Reset settings to defaults."""
            with self._lock:
                self._state["settings"] = {
                    "api_keys": {},
                    "models": {
                        "headmaster": "gpt-4",
                        "runner": "gpt-4",
                        "reviewer": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                }
            
            self._emit_update("settings_update", {"reset": True})
            return jsonify({"success": True, "message": "Settings reset to defaults"})
        
        @self.app.route('/api/cancel/<runner_id>', methods=['POST'])
        def cancel_runner(runner_id):
            """Cancel a runner."""
            callback = self._cancel_callbacks.get(runner_id)
            if callback:
                try:
                    callback()
                    return jsonify({"success": True, "message": f"Runner {runner_id} cancelled"})
                except Exception as e:
                    return jsonify({"success": False, "message": str(e)}), 500
            return jsonify({"success": False, "message": f"Runner {runner_id} not found"}), 404
        
        @self.app.route('/api/follow-up', methods=['POST'])
        def create_follow_up():
            """Create a follow-up ticket."""
            data = request.json
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400
            
            # Add to tickets list
            with self._lock:
                self._state["tickets"].append(data)
            
            self._emit_update("tickets_update", self._state["tickets"])
            return jsonify({"success": True, "message": "Follow-up ticket created"})
        
        @self.app.route('/api/objective', methods=['POST'])
        def submit_objective():
            """Submit a new objective."""
            data = request.json
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400
            
            # Validate objective data
            if not data.get("description"):
                return jsonify({"success": False, "message": "Objective description is required"}), 400
            
            # Store objective
            objective = {
                "description": data.get("description", ""),
                "requirements": data.get("requirements", []),
                "constraints": data.get("constraints", []),
                "success_metrics": data.get("success_metrics", ["All acceptance criteria met", "All tests pass"])
            }
            
            # Update state
            with self._lock:
                self._state["objective"] = objective
                self._state["status"] = "analyzing"
                self._state["start_time"] = datetime.now().isoformat()
                self._add_progress("New objective submitted: " + objective["description"])
            
            # Emit updates
            self._emit_update("objective_update", self._state["objective"])
            self._emit_update("status_update", self._state["status"])
            
            logger.info(f"New objective submitted: {objective['description']}")
            
            return jsonify({"success": True, "message": "Objective submitted successfully"})

    def _setup_socketio_handlers(self):
        """Setup WebSocket handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info("Client connected to UI")
            with self._lock:
                emit('state_update', self._state)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info("Client disconnected from UI")
        
        @self.socketio.on('request_state')
        def handle_request_state():
            """Handle state request from client."""
            with self._lock:
                emit('state_update', self._state)

    def _emit_update(self, event: str, data: Any):
        """
        Emit an update to all connected clients.
        
        Args:
            event: Event name
            data: Event data
        """
        self.socketio.emit(event, data)

    # State update methods
    def set_objective(self, objective: Dict[str, Any]):
        """
        Set the current objective.
        
        Args:
            objective: Objective data
        """
        with self._lock:
            self._state["objective"] = objective
            self._state["status"] = "analyzing"
            self._state["start_time"] = datetime.now().isoformat()
            self._add_progress("Objective set: " + objective.get("description", ""))
        self._emit_update("objective_update", self._state["objective"])
        self._emit_update("status_update", self._state["status"])

    def set_status(self, status: str):
        """
        Set the current status.
        
        Args:
            status: Status string
        """
        with self._lock:
            self._state["status"] = status
            self._add_progress(f"Status changed to: {status}")
        self._emit_update("status_update", status)

    def _add_progress(self, message: str):
        """
        Add a progress entry (internal, must hold lock).
        
        Args:
            message: Progress message
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        self._state["progress"].append(entry)
        self._emit_update("progress_update", entry)

    def add_progress(self, message: str):
        """
        Add a progress entry.
        
        Args:
            message: Progress message
        """
        with self._lock:
            self._add_progress(message)

    def update_cost(self, tokens: int = 0, api_calls: int = 0, cost: float = 0.0):
        """
        Update cost usage.
        
        Args:
            tokens: Number of tokens used
            api_calls: Number of API calls made
            cost: Estimated cost in USD
        """
        with self._lock:
            self._state["cost_usage"]["tokens"] += tokens
            self._state["cost_usage"]["api_calls"] += api_calls
            self._state["cost_usage"]["estimated_cost"] += cost
        self._emit_update("cost_update", self._state["cost_usage"])

    def set_tickets(self, tickets: List[Dict[str, Any]]):
        """
        Set all tickets.
        
        Args:
            tickets: List of ticket data
        """
        with self._lock:
            self._state["tickets"] = tickets
            self._add_progress(f"Created {len(tickets)} tickets")
        self._emit_update("tickets_update", tickets)

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]):
        """
        Update a specific ticket.
        
        Args:
            ticket_id: Ticket ID
            updates: Updates to apply
        """
        with self._lock:
            for ticket in self._state["tickets"]:
                if ticket.get("id") == ticket_id:
                    ticket.update(updates)
                    break
        self._emit_update("ticket_update", {"id": ticket_id, "updates": updates})

    def add_runner(self, runner_id: str, ticket_id: str, cancel_callback: Optional[Callable] = None):
        """
        Add a runner.
        
        Args:
            runner_id: Runner ID
            ticket_id: Ticket being executed
            cancel_callback: Callback to cancel the runner
        """
        runner_data = {
            "id": runner_id,
            "ticket_id": ticket_id,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "logs": [],
            "files_touched": [],
            "runtime": 0
        }
        with self._lock:
            self._state["runners"][runner_id] = runner_data
            self._state["active_jobs"].append({
                "runner_id": runner_id,
                "ticket_id": ticket_id,
                "status": "running"
            })
            if cancel_callback:
                self._cancel_callbacks[runner_id] = cancel_callback
            self._add_progress(f"Runner {runner_id} started on ticket {ticket_id}")
        self._emit_update("runner_update", runner_data)
        self._emit_update("active_jobs_update", self._state["active_jobs"])

    def update_runner_log(self, runner_id: str, log_entry: str):
        """
        Add a log entry to a runner.
        
        Args:
            runner_id: Runner ID
            log_entry: Log entry to add
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "message": log_entry
        }
        with self._lock:
            if runner_id in self._state["runners"]:
                self._state["runners"][runner_id]["logs"].append(log_data)
        self._emit_update("runner_log", {"runner_id": runner_id, "log": log_data})

    def update_runner_files(self, runner_id: str, files: List[str]):
        """
        Update files touched by a runner.
        
        Args:
            runner_id: Runner ID
            files: List of file paths
        """
        with self._lock:
            if runner_id in self._state["runners"]:
                self._state["runners"][runner_id]["files_touched"] = files
        self._emit_update("runner_files", {"runner_id": runner_id, "files": files})

    def complete_runner(self, runner_id: str, result: Dict[str, Any]):
        """
        Mark a runner as complete.
        
        Args:
            runner_id: Runner ID
            result: Runner result data
        """
        with self._lock:
            if runner_id in self._state["runners"]:
                self._state["runners"][runner_id]["status"] = "completed"
                self._state["runners"][runner_id]["result"] = result
                self._state["runners"][runner_id]["end_time"] = datetime.now().isoformat()
            
            # Update active jobs
            self._state["active_jobs"] = [
                job for job in self._state["active_jobs"]
                if job["runner_id"] != runner_id
            ]
            
            # Store result
            self._state["results"][runner_id] = result
            
            # Remove cancel callback
            self._cancel_callbacks.pop(runner_id, None)
            
            self._add_progress(f"Runner {runner_id} completed")
        
        self._emit_update("runner_complete", {"runner_id": runner_id, "result": result})
        self._emit_update("active_jobs_update", self._state["active_jobs"])

    def update_headmaster(self, key: str, value: Any):
        """
        Update headmaster state.
        
        Args:
            key: State key to update
            value: New value
        """
        with self._lock:
            self._state["headmaster"][key] = value
        self._emit_update("headmaster_update", {key: value})

    def add_headmaster_reasoning(self, reasoning: str):
        """
        Add a reasoning entry to headmaster.
        
        Args:
            reasoning: Reasoning message
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": reasoning
        }
        with self._lock:
            self._state["headmaster"]["reasoning_log"].append(entry)
        self._emit_update("headmaster_reasoning", entry)

    def set_dependencies(self, dependencies: List[Dict[str, Any]]):
        """
        Set dependency data.
        
        Args:
            dependencies: List of dependency relationships
        """
        with self._lock:
            self._state["headmaster"]["dependencies"] = dependencies
        self._emit_update("dependencies_update", dependencies)

    def add_review(self, review: Dict[str, Any]):
        """
        Add a review.
        
        Args:
            review: Review data
        """
        with self._lock:
            self._state["reviews"].append(review)
            self._add_progress(f"Review added for ticket {review.get('ticket_id', 'unknown')}")
        self._emit_update("review_update", review)

    def get_state(self) -> Dict[str, Any]:
        """
        Get current state.
        
        Returns:
            Current state dictionary
        """
        with self._lock:
            return dict(self._state)

    def start(self, background: bool = True):
        """
        Start the UI server.
        
        Args:
            background: Run in background thread if True
        """
        if background:
            self._running = True
            self._server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"UI Server started in background at http://{self.host}:{self.port}")
        else:
            self._run_server()

    def _run_server(self):
        """Run the server (internal)."""
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=False,
            use_reloader=False,
            log_output=False
        )

    def stop(self):
        """Stop the UI server."""
        self._running = False
        logger.info("UI Server stopped")
