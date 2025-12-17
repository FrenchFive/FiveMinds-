/**
 * Five Minds UI - Main JavaScript
 * Handles WebSocket connection and common functionality
 */

// Global state
let socket = null;
let connected = false;
let state = {};
let selectedRepoPath = '';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCommandBar();
    updateFooterTime();
    setInterval(updateFooterTime, 1000);
    
    // Load saved repo path
    const savedRepo = localStorage.getItem('selectedRepoPath');
    if (savedRepo) {
        setRepoPath(savedRepo);
    }
});

/**
 * Initialize WebSocket connection
 */
function initializeSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = io(window.location.origin, {
        transports: ['websocket', 'polling']
    });

    socket.on('connect', function() {
        connected = true;
        updateConnectionStatus(true);
        console.log('Connected to Five Minds server');
        socket.emit('request_state');
    });

    socket.on('disconnect', function() {
        connected = false;
        updateConnectionStatus(false);
        console.log('Disconnected from Five Minds server');
    });

    socket.on('state_update', function(data) {
        state = data;
        if (typeof onStateUpdate === 'function') {
            onStateUpdate(data);
        }
        // Check for completion
        checkForCompletion(data);
    });

    socket.on('objective_update', function(data) {
        if (typeof onObjectiveUpdate === 'function') {
            onObjectiveUpdate(data);
        }
    });

    socket.on('status_update', function(data) {
        if (typeof onStatusUpdate === 'function') {
            onStatusUpdate(data);
        }
        // Handle task queue processing when status becomes idle
        handleStatusChangeForQueue(data);
        // Check for completion
        if (data === 'completed') {
            showSuccessModal();
        }
    });

    socket.on('progress_update', function(data) {
        if (typeof onProgressUpdate === 'function') {
            onProgressUpdate(data);
        }
    });

    socket.on('cost_update', function(data) {
        if (typeof onCostUpdate === 'function') {
            onCostUpdate(data);
        }
    });

    socket.on('tickets_update', function(data) {
        if (typeof onTicketsUpdate === 'function') {
            onTicketsUpdate(data);
        }
    });

    socket.on('ticket_update', function(data) {
        if (typeof onTicketUpdate === 'function') {
            onTicketUpdate(data);
        }
    });

    socket.on('runner_update', function(data) {
        if (typeof onRunnerUpdate === 'function') {
            onRunnerUpdate(data);
        }
    });

    socket.on('runner_log', function(data) {
        if (typeof onRunnerLog === 'function') {
            onRunnerLog(data);
        }
    });

    socket.on('runner_files', function(data) {
        if (typeof onRunnerFiles === 'function') {
            onRunnerFiles(data);
        }
    });

    socket.on('runner_complete', function(data) {
        if (typeof onRunnerComplete === 'function') {
            onRunnerComplete(data);
        }
    });

    socket.on('active_jobs_update', function(data) {
        if (typeof onActiveJobsUpdate === 'function') {
            onActiveJobsUpdate(data);
        }
    });

    socket.on('headmaster_update', function(data) {
        if (typeof onHeadmasterUpdate === 'function') {
            onHeadmasterUpdate(data);
        }
    });

    socket.on('headmaster_reasoning', function(data) {
        if (typeof onHeadmasterReasoning === 'function') {
            onHeadmasterReasoning(data);
        }
    });

    socket.on('dependencies_update', function(data) {
        if (typeof onDependenciesUpdate === 'function') {
            onDependenciesUpdate(data);
        }
    });

    socket.on('review_update', function(data) {
        if (typeof onReviewUpdate === 'function') {
            onReviewUpdate(data);
        }
    });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(isConnected) {
    const indicator = document.getElementById('connection-status');
    const statusText = document.getElementById('system-status');
    
    if (indicator) {
        indicator.classList.toggle('connected', isConnected);
        indicator.classList.toggle('disconnected', !isConnected);
    }
    
    if (statusText) {
        statusText.textContent = isConnected ? 'Connected' : 'Disconnected';
    }
}

/**
 * Update footer time
 */
function updateFooterTime() {
    const timeElement = document.getElementById('footer-time');
    if (timeElement) {
        timeElement.textContent = new Date().toLocaleTimeString();
    }
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

/**
 * Format duration
 */
function formatDuration(startTime, endTime) {
    if (!startTime) return '-';
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = Math.floor((end - start) / 1000);
    
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    const seconds = diff % 60;
    
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Format status for CSS class
 */
function formatStatusClass(status) {
    if (!status) return 'pending';
    return status.toLowerCase().replace(/_/g, '-');
}

/**
 * Make API request
 */
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    return response.json();
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format diff for display
 */
function formatDiff(diff) {
    if (!diff) return '<span class="diff-empty">No diff available</span>';
    
    const lines = diff.split('\n');
    return lines.map(line => {
        if (line.startsWith('+') && !line.startsWith('+++')) {
            return `<span class="diff-add">${escapeHtml(line)}</span>`;
        } else if (line.startsWith('-') && !line.startsWith('---')) {
            return `<span class="diff-remove">${escapeHtml(line)}</span>`;
        } else if (line.startsWith('@@')) {
            return `<span class="diff-info">${escapeHtml(line)}</span>`;
        }
        return escapeHtml(line);
    }).join('\n');
}

/**
 * Task Queue Management
 */
let taskQueue = [];

/**
 * Initialize command bar and autonomous mode
 */
function initializeCommandBar() {
    const chatForm = document.getElementById('objective-chat-form');
    const autonomousToggle = document.getElementById('autonomous-mode-toggle');
    
    if (chatForm) {
        chatForm.addEventListener('submit', handleObjectiveSubmit);
    }
    
    if (autonomousToggle) {
        autonomousToggle.addEventListener('change', handleAutonomousModeToggle);
        
        // Load saved state
        const savedState = localStorage.getItem('autonomousMode');
        if (savedState !== null) {
            autonomousToggle.checked = savedState === 'true';
        }
    }
}

/**
 * Select repository path
 */
function selectRepo() {
    // Prompt user for repository path (in a real app this would be a file picker)
    const path = prompt('Enter the path to your local repository:', selectedRepoPath || '/path/to/repo');
    
    if (path && path.trim()) {
        setRepoPath(path.trim());
        showNotification(`Repository set: ${path.trim()}`, 'success');
    }
}

/**
 * Set the repository path
 */
function setRepoPath(path) {
    selectedRepoPath = path;
    localStorage.setItem('selectedRepoPath', path);
    
    const repoPathEl = document.getElementById('repo-path');
    if (repoPathEl) {
        repoPathEl.textContent = path;
        repoPathEl.classList.add('selected');
    }
}

/**
 * Handle objective submission - direct submit without modal
 */
async function handleObjectiveSubmit(event) {
    event.preventDefault();
    
    const input = document.getElementById('objective-input');
    const objective = input.value.trim();
    
    if (!objective) {
        showNotification('Please enter an objective', 'error');
        return;
    }
    
    if (!selectedRepoPath) {
        showNotification('Please select a repository first', 'warning');
        selectRepo();
        return;
    }
    
    // Submit objective directly
    try {
        const response = await fetch('/api/objective', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: objective,
                requirements: [],
                constraints: [],
                success_metrics: ["All acceptance criteria met", "All tests pass"],
                repo_path: selectedRepoPath
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showNotification(`Started: ${objective}`, 'success');
            input.value = '';
        } else {
            showNotification(`Failed: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error submitting objective:', error);
        showNotification(`Error: ${error.message}`, 'error');
    }
}

/**
 * Submit the next task from queue
 */
async function submitNextTask() {
    if (taskQueue.length === 0) {
        return;
    }
    
    const task = taskQueue[0];
    task.status = 'submitting';
    
    try {
        const response = await fetch('/api/objective', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: task.description,
                requirements: task.requirements || [],
                constraints: task.constraints || [],
                success_metrics: task.success_metrics || ["All acceptance criteria met", "All tests pass"]
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Remove from queue
            taskQueue.shift();
            updateQueueIndicator();
            showNotification(`Task "${task.description}" started`);
        } else {
            task.status = 'failed';
            showNotification(`Failed to submit task: ${result.message}`, 'error');
        }
    } catch (error) {
        task.status = 'failed';
        console.error('Error submitting task:', error);
        showNotification(`Error submitting task: ${error.message}`, 'error');
    }
}

/**
 * Update task queue indicator
 */
function updateQueueIndicator() {
    const indicator = document.getElementById('task-queue-indicator');
    const countEl = document.getElementById('queue-count');
    
    if (indicator && countEl) {
        if (taskQueue.length > 0) {
            countEl.textContent = taskQueue.length;
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }
}

/**
 * Handle autonomous mode toggle
 */
function handleAutonomousModeToggle(event) {
    const enabled = event.target.checked;
    
    // Save to localStorage
    localStorage.setItem('autonomousMode', enabled);
    
    // Show notification
    if (enabled) {
        showNotification('🤖 Autonomous mode enabled - tasks will run automatically');
        
        // If there are queued tasks and system is idle, start processing
        if (taskQueue.length > 0 && (state.status === 'idle' || !state.status)) {
            submitNextTask();
        }
    } else {
        showNotification('⏸️ Autonomous mode disabled - tasks will queue until manually started');
    }
}

/**
 * Handle status changes for task queue processing
 */
function handleStatusChangeForQueue(status) {
    // If system becomes idle and autonomous mode is on, process next task
    const autonomousMode = document.getElementById('autonomous-mode-toggle')?.checked;
    
    if (status === 'idle' && autonomousMode && taskQueue.length > 0) {
        setTimeout(() => {
            submitNextTask();
        }, 2000); // Wait 2 seconds before submitting next task
    }
}

/**
 * Check for completion and show success modal
 */
function checkForCompletion(data) {
    if (data.status === 'completed' && data.objective) {
        // Store completion data for success modal
        window.lastCompletedObjective = data.objective;
        window.lastCompletedTickets = data.tickets || [];
        window.lastCompletedStartTime = data.start_time;
    }
}

/**
 * Show success modal
 */
function showSuccessModal() {
    const modal = document.getElementById('success-modal');
    const objectiveText = document.getElementById('success-objective-text');
    const ticketsCount = document.getElementById('success-tickets-count');
    const timeElapsed = document.getElementById('success-time-elapsed');
    
    if (!modal) return;
    
    // Populate modal with completion data
    if (objectiveText && window.lastCompletedObjective) {
        objectiveText.textContent = window.lastCompletedObjective.description || 'Objective';
    }
    
    if (ticketsCount && window.lastCompletedTickets) {
        const completed = window.lastCompletedTickets.filter(t => 
            t.status === 'completed' || t.status === 'COMPLETED'
        ).length;
        ticketsCount.textContent = completed;
    }
    
    if (timeElapsed && window.lastCompletedStartTime) {
        timeElapsed.textContent = formatDuration(window.lastCompletedStartTime);
    }
    
    modal.classList.add('active');
}

/**
 * Close success modal
 */
function closeSuccessModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Focus on objective input and scroll to it
 * This function is used by the "Set objective" button on dashboard
 */
function focusObjectiveInput() {
    const input = document.getElementById('objective-input');
    const commandBarContainer = document.querySelector('.command-bar-container');
    
    if (input) {
        input.focus();
        
        // Add a pulse animation to draw attention
        if (commandBarContainer) {
            commandBarContainer.classList.add('pulse-attention');
            setTimeout(() => {
                commandBarContainer.classList.remove('pulse-attention');
            }, 1000);
        }
    }
}

/**
 * Show notification (simple implementation)
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    
    // Add to document
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
