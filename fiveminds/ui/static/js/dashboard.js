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
    // Note: The actual stop functionality would need to be implemented via WebSocket
    // For now, this is a placeholder that shows the UI response
    console.log('Stop requested');
}

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    // Handle welcome section visibility
    handleWelcomeSection(data);
    
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
    
    // Update cost
    if (data.cost_usage) {
        onCostUpdate(data.cost_usage);
    }
    
    // Update active jobs
    if (data.active_jobs) {
        onActiveJobsUpdate(data.active_jobs);
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
 * Handle welcome section visibility
 */
function handleWelcomeSection(data) {
    const welcomeSection = document.getElementById('welcome-section');
    if (!welcomeSection) return;
    
    // Hide welcome section when there's an objective or execution has started
    if (data.objective || data.status !== 'idle') {
        welcomeSection.style.display = 'none';
    } else {
        welcomeSection.style.display = 'block';
    }
}

/**
 * Handle objective update
 */
function onObjectiveUpdate(objective) {
    const descEl = document.getElementById('objective-description');
    const reqEl = document.getElementById('objective-requirements');
    const constEl = document.getElementById('objective-constraints');
    const welcomeSection = document.getElementById('welcome-section');
    const stopBtn = document.getElementById('stop-btn');
    
    if (descEl) {
        descEl.textContent = objective.description || 'No objective set';
    }
    
    if (reqEl) {
        const count = objective.requirements ? objective.requirements.length : 0;
        reqEl.textContent = `${count} requirement${count !== 1 ? 's' : ''}`;
    }
    
    if (constEl) {
        const count = objective.constraints ? objective.constraints.length : 0;
        constEl.textContent = `${count} constraint${count !== 1 ? 's' : ''}`;
    }
    
    // Hide welcome section when objective is set
    if (welcomeSection && objective.description) {
        welcomeSection.style.display = 'none';
    }
    
    // Show stop button when objective is set
    if (stopBtn) {
        stopBtn.style.display = objective.description ? 'inline-flex' : 'none';
    }
}

/**
 * Handle status update
 */
function onStatusUpdate(status) {
    const badge = document.getElementById('system-status-badge');
    const stopBtn = document.getElementById('stop-btn');
    
    if (badge) {
        badge.textContent = status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ');
        badge.className = 'status-badge ' + formatStatusClass(status);
    }
    
    // Update stop button visibility based on status
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
}

/**
 * Start elapsed time timer
 */
function startElapsedTimer(startTime) {
    const startEl = document.getElementById('start-time');
    const elapsedEl = document.getElementById('elapsed-time');
    
    if (startEl) {
        startEl.textContent = formatTimestamp(startTime);
    }
    
    if (elapsedInterval) {
        clearInterval(elapsedInterval);
    }
    
    function updateElapsed() {
        if (elapsedEl) {
            elapsedEl.textContent = formatDuration(startTime);
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
 * Handle cost update
 */
function onCostUpdate(cost) {
    const tokensEl = document.getElementById('tokens-used');
    const callsEl = document.getElementById('api-calls');
    const costEl = document.getElementById('estimated-cost');
    
    if (tokensEl) {
        tokensEl.textContent = cost.tokens.toLocaleString();
    }
    
    if (callsEl) {
        callsEl.textContent = cost.api_calls.toLocaleString();
    }
    
    if (costEl) {
        costEl.textContent = `$${cost.estimated_cost.toFixed(2)}`;
    }
}

/**
 * Handle active jobs update
 */
function onActiveJobsUpdate(jobs) {
    const container = document.getElementById('active-jobs-list');
    
    if (!container) return;
    
    if (jobs.length === 0) {
        container.innerHTML = '<div class="jobs-empty">No active jobs</div>';
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-item">
            <div class="job-info">
                <span class="job-runner">🏃 ${escapeHtml(job.runner_id)}</span>
                <span class="job-ticket">${escapeHtml(job.ticket_id)}</span>
            </div>
            <span class="status-badge ${formatStatusClass(job.status)}">${job.status}</span>
        </div>
    `).join('');
}

/**
 * Handle tickets update
 */
function onTicketsUpdate(tickets) {
    renderTickets(tickets);
    updateTicketStats(tickets);
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
    const pendingEl = document.getElementById('tickets-pending');
    const failedEl = document.getElementById('tickets-failed');
    
    const completed = tickets.filter(t => t.status === 'completed' || t.status === 'COMPLETED').length;
    const failed = tickets.filter(t => t.status === 'failed' || t.status === 'FAILED').length;
    const pending = tickets.filter(t => !t.status || t.status === 'pending' || t.status === 'PENDING').length;
    
    if (completedEl) completedEl.textContent = `${completed} completed`;
    if (pendingEl) pendingEl.textContent = `${pending} pending`;
    if (failedEl) failedEl.textContent = `${failed} failed`;
}
