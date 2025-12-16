/**
 * Five Minds UI - Main JavaScript
 * Handles WebSocket connection and common functionality
 */

// Global state
let socket = null;
let connected = false;
let state = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    updateFooterTime();
    setInterval(updateFooterTime, 1000);
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
