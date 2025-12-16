/**
 * Five Minds UI - Runner Page JavaScript
 */

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    if (data.runners) {
        renderRunners(data.runners);
    }
}

/**
 * Handle runner update
 */
function onRunnerUpdate(runner) {
    const container = document.getElementById('runners-container');
    if (!container) return;
    
    // Remove empty state
    const emptyState = container.querySelector('.runners-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Check if runner card exists
    let card = container.querySelector(`[data-runner-id="${runner.id}"]`);
    
    if (!card) {
        card = createRunnerCard(runner);
        container.appendChild(card);
    } else {
        updateRunnerCard(card, runner);
    }
}

/**
 * Handle runner log update
 */
function onRunnerLog(data) {
    const card = document.querySelector(`[data-runner-id="${data.runner_id}"]`);
    if (!card) return;
    
    const logsContainer = card.querySelector('.runner-logs');
    if (!logsContainer) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-time">${formatTimestamp(data.log.timestamp)}</span>
        <span class="log-message">${escapeHtml(data.log.message)}</span>
    `;
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

/**
 * Handle runner complete
 */
function onRunnerComplete(data) {
    const card = document.querySelector(`[data-runner-id="${data.runner_id}"]`);
    if (!card) return;
    
    const statusBadge = card.querySelector('.runner-status');
    if (statusBadge) {
        const status = data.result.success ? 'completed' : 'failed';
        statusBadge.textContent = status;
        statusBadge.className = `status-badge ${status}`;
    }
    
    const cancelBtn = card.querySelector('.cancel-btn');
    if (cancelBtn) {
        cancelBtn.disabled = true;
    }
}

/**
 * Render all runners
 */
function renderRunners(runners) {
    const container = document.getElementById('runners-container');
    if (!container) return;
    
    const runnerList = Object.values(runners);
    
    if (runnerList.length === 0) {
        container.innerHTML = `
            <div class="runners-empty card">
                <div class="empty-state">
                    <span class="empty-icon">🏃</span>
                    <h3>No Active Runners</h3>
                    <p>Runners will appear here when executing tickets</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    runnerList.forEach(runner => {
        const card = createRunnerCard(runner);
        container.appendChild(card);
    });
}

/**
 * Create runner card element
 */
function createRunnerCard(runner) {
    const card = document.createElement('div');
    card.className = 'card runner-card';
    card.dataset.runnerId = runner.id;
    
    const status = runner.status || 'running';
    const isCompleted = status === 'completed' || status === 'failed';
    
    card.innerHTML = `
        <div class="card-header runner-header">
            <h3>
                <span class="icon">🏃</span>
                ${escapeHtml(runner.id)}
            </h3>
            <span class="status-badge runner-status ${formatStatusClass(status)}">${status}</span>
        </div>
        <div class="card-body">
            <div class="detail-row">
                <span class="label">Ticket:</span>
                <span class="value">${escapeHtml(runner.ticket_id)}</span>
            </div>
            <div class="detail-row">
                <span class="label">Started:</span>
                <span class="value">${formatTimestamp(runner.start_time)}</span>
            </div>
            <div class="detail-row">
                <span class="label">Runtime:</span>
                <span class="value runner-runtime">${formatDuration(runner.start_time, runner.end_time)}</span>
            </div>
            <div class="runner-logs">
                ${renderRunnerLogs(runner.logs)}
            </div>
            <div class="runner-actions" style="margin-top: var(--spacing-md);">
                <a href="/runner/${runner.id}" class="btn btn-secondary">View Details</a>
                <button class="btn btn-danger cancel-btn" onclick="cancelRunner('${runner.id}')" ${isCompleted ? 'disabled' : ''}>
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    // Start runtime update if running
    if (!isCompleted) {
        startRuntimeUpdate(card, runner.start_time);
    }
    
    return card;
}

/**
 * Update runner card
 */
function updateRunnerCard(card, runner) {
    const statusBadge = card.querySelector('.runner-status');
    if (statusBadge) {
        statusBadge.textContent = runner.status;
        statusBadge.className = `status-badge runner-status ${formatStatusClass(runner.status)}`;
    }
}

/**
 * Render runner logs
 */
function renderRunnerLogs(logs) {
    if (!logs || logs.length === 0) {
        return '<div class="logs-empty">Waiting for logs...</div>';
    }
    
    return logs.map(log => `
        <div class="log-entry">
            <span class="log-time">${formatTimestamp(log.timestamp)}</span>
            <span class="log-message">${escapeHtml(log.message)}</span>
        </div>
    `).join('');
}

/**
 * Start runtime update interval
 */
function startRuntimeUpdate(card, startTime) {
    const runtimeEl = card.querySelector('.runner-runtime');
    if (!runtimeEl) return;
    
    const intervalId = setInterval(() => {
        const statusBadge = card.querySelector('.runner-status');
        if (statusBadge && (statusBadge.textContent === 'completed' || statusBadge.textContent === 'failed')) {
            clearInterval(intervalId);
            return;
        }
        runtimeEl.textContent = formatDuration(startTime);
    }, 1000);
}

/**
 * Cancel a runner
 */
async function cancelRunner(runnerId) {
    if (!confirm(`Are you sure you want to cancel runner ${runnerId}?`)) {
        return;
    }
    
    try {
        const result = await apiRequest(`/api/cancel/${runnerId}`, 'POST');
        if (result.success) {
            alert('Runner cancelled successfully');
        } else {
            alert(`Failed to cancel runner: ${result.message}`);
        }
    } catch (error) {
        alert(`Error cancelling runner: ${error.message}`);
    }
}
