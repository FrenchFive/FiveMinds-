/**
 * Five Minds UI - Dashboard JavaScript
 */

// Update interval for elapsed time
let elapsedInterval = null;

// Initialize stop button when page loads
document.addEventListener('DOMContentLoaded', function() {
    const stopBtn = document.getElementById('stop-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', handleStopClick);
    }
});

/**
 * Handle stop button click
 */
function handleStopClick() {
    const stopBtn = document.getElementById('stop-btn');
    if (stopBtn) {
        stopBtn.disabled = true;
        stopBtn.textContent = 'Stopping...';
    }
    console.log('Stop requested');
}

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    // Update top header bar
    updateTopHeader(data);
    
    // Update stats overview
    updateStatsOverview(data);
    
    // Update objective
    if (data.objective) {
        onObjectiveUpdate(data.objective);
    }
    
    // Update status
    if (data.status) {
        onStatusUpdate(data.status);
    }
    
    // Update progress
    if (data.progress && data.progress.length > 0) {
        renderProgress(data.progress);
    }
    
    // Update HeadMaster activity
    if (data.headmaster) {
        updateHeadmasterActivity(data.headmaster);
    }
    
    // Update runners
    if (data.runners || data.active_jobs) {
        updateRunnersList(data.runners || {}, data.active_jobs || []);
    }
    
    // Update tickets
    if (data.tickets) {
        onTicketsUpdate(data.tickets);
    }
    
    // Start elapsed timer if we have start time
    if (data.start_time) {
        startElapsedTimer(data.start_time);
    }
    
    // Handle final summary
    if (data.headmaster && data.headmaster.final_summary) {
        showFinalSummary(data.headmaster.final_summary, data.status === 'completed');
    }
}

/**
 * Update top header bar with current task info
 */
function updateTopHeader(data) {
    const taskTitle = document.getElementById('current-task-title');
    const headmasterAction = document.getElementById('headmaster-action');
    const statusDot = document.getElementById('task-status-dot');
    const stopBtn = document.getElementById('stop-btn');
    
    // Update task title
    if (taskTitle) {
        if (data.objective && data.objective.description) {
            taskTitle.textContent = data.objective.description;
        } else {
            taskTitle.textContent = 'Waiting for objective...';
        }
    }
    
    // Update HeadMaster action text
    if (headmasterAction) {
        const status = data.status || 'idle';
        const actionTexts = {
            'idle': 'HeadMaster is idle',
            'analyzing': '🔍 HeadMaster is analyzing the objective...',
            'executing': '⚡ Runners are executing tickets...',
            'reviewing': '🔎 Reviewing execution results...',
            'integrating': '🔧 Integrating changes...',
            'completed': '✅ Execution completed',
            'failed': '❌ Execution failed'
        };
        headmasterAction.textContent = actionTexts[status] || `Status: ${status}`;
    }
    
    // Update status dot
    if (statusDot) {
        statusDot.className = 'status-dot ' + (data.status || 'idle');
    }
    
    // Show/hide stop button
    if (stopBtn) {
        const isRunning = ['analyzing', 'executing', 'reviewing', 'integrating'].includes(data.status);
        stopBtn.style.display = isRunning ? 'inline-flex' : 'none';
    }
}

/**
 * Update stats overview boxes
 */
function updateStatsOverview(data) {
    const statStatus = document.getElementById('stat-status');
    const statRunners = document.getElementById('stat-runners');
    const statTickets = document.getElementById('stat-tickets');
    const statElapsed = document.getElementById('stat-elapsed');
    
    // Update status
    if (statStatus) {
        const status = data.status || 'Idle';
        statStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    // Update active runners count
    if (statRunners) {
        const activeCount = data.active_jobs ? data.active_jobs.length : 0;
        statRunners.textContent = activeCount.toString();
    }
    
    // Update tickets progress
    if (statTickets && data.tickets) {
        const completed = data.tickets.filter(t => 
            t.status === 'completed' || t.status === 'COMPLETED'
        ).length;
        const total = data.tickets.length;
        statTickets.textContent = `${completed} / ${total}`;
    }
    
    // Elapsed time is updated by startElapsedTimer
}

/**
 * Update HeadMaster activity panel
 */
function updateHeadmasterActivity(headmaster) {
    const container = document.getElementById('headmaster-reasoning');
    const statusBadge = document.getElementById('headmaster-status');
    
    if (statusBadge) {
        const status = headmaster.integration_status || 'pending';
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusBadge.className = 'status-badge ' + formatStatusClass(status);
    }
    
    if (container && headmaster.reasoning_log && headmaster.reasoning_log.length > 0) {
        container.innerHTML = headmaster.reasoning_log.slice(-10).reverse().map(entry => `
            <div class="reasoning-entry">
                <span class="reasoning-time">${formatTimestamp(entry.timestamp)}</span>
                <span class="reasoning-message">${escapeHtml(entry.message)}</span>
            </div>
        `).join('');
    }
}

/**
 * Handle HeadMaster reasoning update
 */
function onHeadmasterReasoning(entry) {
    const container = document.getElementById('headmaster-reasoning');
    if (!container) return;
    
    // Remove empty state if present
    const emptyState = container.querySelector('.reasoning-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Add new entry at the top
    const entryEl = document.createElement('div');
    entryEl.className = 'reasoning-entry';
    entryEl.innerHTML = `
        <span class="reasoning-time">${formatTimestamp(entry.timestamp)}</span>
        <span class="reasoning-message">${escapeHtml(entry.message)}</span>
    `;
    container.insertBefore(entryEl, container.firstChild);
    
    // Keep only last 10 entries
    const entries = container.querySelectorAll('.reasoning-entry');
    if (entries.length > 10) {
        entries[entries.length - 1].remove();
    }
}

/**
 * Update runners list
 */
function updateRunnersList(runners, activeJobs) {
    const container = document.getElementById('runners-list');
    const countBadge = document.getElementById('runners-count');
    
    if (!container) return;
    
    const runnerEntries = Object.entries(runners);
    const activeCount = activeJobs.length;
    
    // Update count badge
    if (countBadge) {
        countBadge.textContent = `${activeCount} active`;
    }
    
    if (runnerEntries.length === 0) {
        container.innerHTML = '<div class="runners-empty">No runners active</div>';
        return;
    }
    
    container.innerHTML = runnerEntries.map(([id, runner]) => {
        const statusClass = runner.status === 'completed' ? 'completed' : 
                           runner.status === 'failed' ? 'failed' : '';
        return `
            <div class="runner-item ${statusClass}">
                <div class="runner-info">
                    <span class="runner-id">🏃 ${escapeHtml(id)}</span>
                    <span class="runner-ticket">${escapeHtml(runner.ticket_id || 'Unknown ticket')}</span>
                </div>
                <span class="status-badge ${formatStatusClass(runner.status)}">${runner.status || 'running'}</span>
            </div>
        `;
    }).join('');
}

/**
 * Handle runner update
 */
function onRunnerUpdate(runner) {
    updateStatsOverview(state);
}

/**
 * Handle active jobs update
 */
function onActiveJobsUpdate(jobs) {
    const statRunners = document.getElementById('stat-runners');
    if (statRunners) {
        statRunners.textContent = jobs.length.toString();
    }
}

/**
 * Handle objective update
 */
function onObjectiveUpdate(objective) {
    const descEl = document.getElementById('objective-description');
    const reqEl = document.getElementById('objective-requirements');
    const constEl = document.getElementById('objective-constraints');
    const taskTitle = document.getElementById('current-task-title');
    const objectiveCta = document.getElementById('objective-cta');
    
    if (descEl) {
        descEl.textContent = objective.description || 'No objective set';
    }
    
    if (taskTitle && objective.description) {
        taskTitle.textContent = objective.description;
    }
    
    if (reqEl) {
        const count = objective.requirements ? objective.requirements.length : 0;
        reqEl.textContent = `📋 ${count} requirement${count !== 1 ? 's' : ''}`;
    }
    
    if (constEl) {
        const count = objective.constraints ? objective.constraints.length : 0;
        constEl.textContent = `⚠️ ${count} constraint${count !== 1 ? 's' : ''}`;
    }
    
    // Hide CTA when objective is set
    if (objectiveCta) {
        objectiveCta.style.display = objective.description ? 'none' : 'block';
    }
}

/**
 * Handle status update
 */
function onStatusUpdate(status) {
    const statusDot = document.getElementById('task-status-dot');
    const statStatus = document.getElementById('stat-status');
    const headmasterAction = document.getElementById('headmaster-action');
    const stopBtn = document.getElementById('stop-btn');
    
    // Update status dot
    if (statusDot) {
        statusDot.className = 'status-dot ' + status;
    }
    
    // Update stat box
    if (statStatus) {
        statStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    // Update action text
    if (headmasterAction) {
        const actionTexts = {
            'idle': 'HeadMaster is idle',
            'analyzing': '🔍 HeadMaster is analyzing the objective...',
            'executing': '⚡ Runners are executing tickets...',
            'reviewing': '🔎 Reviewing execution results...',
            'integrating': '🔧 Integrating changes...',
            'completed': '✅ Execution completed',
            'failed': '❌ Execution failed'
        };
        headmasterAction.textContent = actionTexts[status] || `Status: ${status}`;
    }
    
    // Update stop button visibility
    if (stopBtn) {
        const isRunning = ['analyzing', 'executing', 'reviewing', 'integrating'].includes(status);
        stopBtn.style.display = isRunning ? 'inline-flex' : 'none';
    }
}

/**
 * Show final summary
 */
function showFinalSummary(summary, success) {
    const section = document.getElementById('final-summary-section');
    const content = document.getElementById('final-summary-content');
    const card = section ? section.querySelector('.final-summary-card') : null;
    
    if (section && content) {
        content.textContent = summary;
        section.style.display = 'block';
        
        if (card) {
            card.classList.toggle('failed', !success);
        }
    }
}

/**
 * Handle HeadMaster update (for final summary)
 */
function onHeadmasterUpdate(data) {
    if (data.final_summary) {
        showFinalSummary(data.final_summary, true);
    }
    
    // Update integration status badge
    const statusBadge = document.getElementById('headmaster-status');
    if (statusBadge && data.integration_status) {
        statusBadge.textContent = data.integration_status.charAt(0).toUpperCase() + 
                                  data.integration_status.slice(1);
        statusBadge.className = 'status-badge ' + formatStatusClass(data.integration_status);
    }
}

/**
 * Start elapsed time timer
 */
function startElapsedTimer(startTime) {
    const statElapsed = document.getElementById('stat-elapsed');
    
    if (elapsedInterval) {
        clearInterval(elapsedInterval);
    }
    
    function updateElapsed() {
        if (statElapsed) {
            statElapsed.textContent = formatDuration(startTime);
        }
    }
    
    updateElapsed();
    elapsedInterval = setInterval(updateElapsed, 1000);
}

/**
 * Handle progress update
 */
function onProgressUpdate(entry) {
    const container = document.getElementById('progress-timeline');
    const countEl = document.getElementById('progress-count');
    
    if (!container) return;
    
    // Remove empty state if present
    const emptyState = container.querySelector('.timeline-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Add new entry at the top
    const entryEl = document.createElement('div');
    entryEl.className = 'timeline-entry';
    entryEl.innerHTML = `
        <span class="timeline-time">${formatTimestamp(entry.timestamp)}</span>
        <span class="timeline-message">${escapeHtml(entry.message)}</span>
    `;
    container.insertBefore(entryEl, container.firstChild);
    
    // Update count
    if (countEl) {
        const count = container.querySelectorAll('.timeline-entry').length;
        countEl.textContent = `${count} event${count !== 1 ? 's' : ''}`;
    }
}

/**
 * Render all progress entries
 */
function renderProgress(progress) {
    const container = document.getElementById('progress-timeline');
    const countEl = document.getElementById('progress-count');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    // Add entries in reverse order (newest first)
    const reversed = [...progress].reverse();
    reversed.forEach(entry => {
        const entryEl = document.createElement('div');
        entryEl.className = 'timeline-entry';
        entryEl.innerHTML = `
            <span class="timeline-time">${formatTimestamp(entry.timestamp)}</span>
            <span class="timeline-message">${escapeHtml(entry.message)}</span>
        `;
        container.appendChild(entryEl);
    });
    
    // Update count
    if (countEl) {
        countEl.textContent = `${progress.length} event${progress.length !== 1 ? 's' : ''}`;
    }
}

/**
 * Handle tickets update
 */
function onTicketsUpdate(tickets) {
    renderTickets(tickets);
    updateTicketStats(tickets);
    
    // Update stats overview
    const statTickets = document.getElementById('stat-tickets');
    if (statTickets) {
        const completed = tickets.filter(t => 
            t.status === 'completed' || t.status === 'COMPLETED'
        ).length;
        statTickets.textContent = `${completed} / ${tickets.length}`;
    }
}

/**
 * Handle single ticket update
 */
function onTicketUpdate(data) {
    const card = document.querySelector(`[data-ticket-id="${data.id}"]`);
    if (card) {
        card.className = `ticket-card ${formatStatusClass(data.updates.status || 'pending')}`;
        
        const statusBadge = card.querySelector('.status-badge');
        if (statusBadge && data.updates.status) {
            statusBadge.textContent = data.updates.status;
            statusBadge.className = `status-badge ${formatStatusClass(data.updates.status)}`;
        }
    }
}

/**
 * Render tickets grid
 */
function renderTickets(tickets) {
    const container = document.getElementById('tickets-grid');
    
    if (!container) return;
    
    if (tickets.length === 0) {
        container.innerHTML = '<div class="tickets-empty">No tickets created yet</div>';
        return;
    }
    
    container.innerHTML = tickets.map(ticket => `
        <div class="ticket-card ${formatStatusClass(ticket.status)}" data-ticket-id="${ticket.id}">
            <div class="ticket-id">${escapeHtml(ticket.id)}</div>
            <div class="ticket-title">${escapeHtml(ticket.title)}</div>
            <div class="ticket-status">
                <span class="status-badge ${formatStatusClass(ticket.status)}">${ticket.status || 'pending'}</span>
                <span class="ticket-priority badge">${ticket.priority || 'medium'}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Update ticket statistics
 */
function updateTicketStats(tickets) {
    const completedEl = document.getElementById('tickets-completed');
    const inProgressEl = document.getElementById('tickets-in-progress');
    const pendingEl = document.getElementById('tickets-pending');
    const failedEl = document.getElementById('tickets-failed');
    
    const completed = tickets.filter(t => t.status === 'completed' || t.status === 'COMPLETED').length;
    const inProgress = tickets.filter(t => t.status === 'in_progress' || t.status === 'IN_PROGRESS').length;
    const failed = tickets.filter(t => t.status === 'failed' || t.status === 'FAILED').length;
    const pending = tickets.filter(t => !t.status || t.status === 'pending' || t.status === 'PENDING').length;
    
    if (completedEl) completedEl.textContent = `${completed} completed`;
    if (inProgressEl) inProgressEl.textContent = `${inProgress} in progress`;
    if (pendingEl) pendingEl.textContent = `${pending} pending`;
    if (failedEl) failedEl.textContent = `${failed} failed`;
}
