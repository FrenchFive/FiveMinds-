/**
 * Five Minds UI - Runner Detail Page JavaScript
 */

let runnerData = null;
let ticketData = null;
let runtimeInterval = null;

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    if (data.runners && data.runners[RUNNER_ID]) {
        runnerData = data.runners[RUNNER_ID];
        renderRunnerDetail(runnerData);
        
        // Find ticket data
        if (data.tickets) {
            ticketData = data.tickets.find(t => t.id === runnerData.ticket_id);
            if (ticketData) {
                renderTicketDetails(ticketData);
            }
        }
    }
}

/**
 * Handle runner update
 */
function onRunnerUpdate(runner) {
    if (runner.id === RUNNER_ID) {
        runnerData = runner;
        renderRunnerDetail(runner);
    }
}

/**
 * Handle runner log
 */
function onRunnerLog(data) {
    if (data.runner_id === RUNNER_ID) {
        addLogEntry(data.log);
    }
}

/**
 * Handle runner files
 */
function onRunnerFiles(data) {
    if (data.runner_id === RUNNER_ID) {
        renderFiles(data.files);
    }
}

/**
 * Handle runner complete
 */
function onRunnerComplete(data) {
    if (data.runner_id === RUNNER_ID) {
        const statusBadge = document.getElementById('runner-status');
        if (statusBadge) {
            const status = data.result.success ? 'completed' : 'failed';
            statusBadge.textContent = status;
            statusBadge.className = `value status-badge ${status}`;
        }
        
        const cancelBtn = document.getElementById('cancel-btn');
        if (cancelBtn) {
            cancelBtn.disabled = true;
        }
        
        if (runtimeInterval) {
            clearInterval(runtimeInterval);
        }
    }
}

/**
 * Render runner detail
 */
function renderRunnerDetail(runner) {
    // Update status
    const statusBadge = document.getElementById('runner-status');
    if (statusBadge) {
        statusBadge.textContent = runner.status;
        statusBadge.className = `value status-badge ${formatStatusClass(runner.status)}`;
    }
    
    // Update start time
    const startTimeEl = document.getElementById('start-time');
    if (startTimeEl) {
        startTimeEl.textContent = formatTimestamp(runner.start_time);
    }
    
    // Start runtime timer
    if (runner.status === 'running') {
        startRuntimeTimer(runner.start_time);
    } else if (runner.end_time) {
        const runtimeEl = document.getElementById('runtime-value');
        if (runtimeEl) {
            runtimeEl.textContent = formatDuration(runner.start_time, runner.end_time);
        }
    }
    
    // Update cancel button
    const cancelBtn = document.getElementById('cancel-btn');
    if (cancelBtn) {
        cancelBtn.disabled = runner.status !== 'running';
    }
    
    // Render logs
    if (runner.logs) {
        renderLogs(runner.logs);
    }
    
    // Render files
    if (runner.files_touched) {
        renderFiles(runner.files_touched);
    }
}

/**
 * Render ticket details
 */
function renderTicketDetails(ticket) {
    const ticketIdEl = document.getElementById('ticket-id');
    const titleEl = document.getElementById('ticket-title');
    const descEl = document.getElementById('ticket-description');
    const priorityEl = document.getElementById('ticket-priority');
    const criteriaEl = document.getElementById('acceptance-criteria');
    
    if (ticketIdEl) ticketIdEl.textContent = ticket.id;
    if (titleEl) titleEl.textContent = ticket.title;
    if (descEl) descEl.textContent = ticket.description;
    
    if (priorityEl) {
        priorityEl.textContent = ticket.priority || 'medium';
        priorityEl.className = `value badge priority-${ticket.priority || 'medium'}`;
    }
    
    if (criteriaEl && ticket.acceptance_criteria) {
        criteriaEl.innerHTML = ticket.acceptance_criteria.map(c => `
            <li class="${c.met ? 'met' : 'unmet'}">
                ${escapeHtml(c.description)}
            </li>
        `).join('');
    }
}

/**
 * Start runtime timer
 */
function startRuntimeTimer(startTime) {
    const runtimeEl = document.getElementById('runtime-value');
    if (!runtimeEl) return;
    
    if (runtimeInterval) {
        clearInterval(runtimeInterval);
    }
    
    function updateRuntime() {
        runtimeEl.textContent = formatDuration(startTime);
    }
    
    updateRuntime();
    runtimeInterval = setInterval(updateRuntime, 1000);
}

/**
 * Render logs
 */
function renderLogs(logs) {
    const container = document.getElementById('logs-container');
    const countEl = document.getElementById('log-count');
    
    if (!container) return;
    
    if (logs.length === 0) {
        container.innerHTML = '<div class="logs-empty">Waiting for logs...</div>';
    } else {
        container.innerHTML = logs.map(log => `
            <div class="log-entry">
                <span class="log-time">${formatTimestamp(log.timestamp)}</span>
                <span class="log-message">${escapeHtml(log.message)}</span>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    }
    
    if (countEl) {
        countEl.textContent = `${logs.length} entr${logs.length !== 1 ? 'ies' : 'y'}`;
    }
}

/**
 * Add log entry
 */
function addLogEntry(log) {
    const container = document.getElementById('logs-container');
    const countEl = document.getElementById('log-count');
    
    if (!container) return;
    
    // Remove empty state
    const emptyState = container.querySelector('.logs-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${formatTimestamp(log.timestamp)}</span>
        <span class="log-message">${escapeHtml(log.message)}</span>
    `;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
    
    if (countEl) {
        const count = container.querySelectorAll('.log-entry').length;
        countEl.textContent = `${count} entr${count !== 1 ? 'ies' : 'y'}`;
    }
}

/**
 * Render files
 */
function renderFiles(files) {
    const container = document.getElementById('files-list');
    const countEl = document.getElementById('files-count');
    
    if (!container) return;
    
    if (files.length === 0) {
        container.innerHTML = '<li class="files-empty">No files modified yet</li>';
    } else {
        container.innerHTML = files.map(file => `
            <li>${escapeHtml(file)}</li>
        `).join('');
    }
    
    if (countEl) {
        countEl.textContent = `${files.length} file${files.length !== 1 ? 's' : ''}`;
    }
}

/**
 * Cancel runner
 */
async function cancelRunner() {
    if (!confirm(`Are you sure you want to cancel runner ${RUNNER_ID}?`)) {
        return;
    }
    
    try {
        const result = await apiRequest(`/api/cancel/${RUNNER_ID}`, 'POST');
        if (result.success) {
            alert('Runner cancelled successfully');
        } else {
            alert(`Failed to cancel runner: ${result.message}`);
        }
    } catch (error) {
        alert(`Error cancelling runner: ${error.message}`);
    }
}
