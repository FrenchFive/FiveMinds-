/**
 * Five Minds UI - HeadMaster Page JavaScript
 */

// Graph rendering constants
const GRAPH_HEIGHT = 300;
const GRAPH_PADDING = 40;
const NODE_RADIUS = 25;
const DEFAULT_GRAPH_WIDTH = 600;

// Decision entry types for cleaner output
const DECISION_TYPES = {
    parsing: { icon: '📋', class: 'decision-parsing' },
    planning: { icon: '🧭', class: 'decision-planning' },
    dispatching: { icon: '🚀', class: 'decision-dispatching' },
    executing: { icon: '⚡', class: 'decision-executing' },
    completed: { icon: '✅', class: 'decision-completed' }
};

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    if (data.headmaster) {
        renderReasoningLog(data.headmaster.reasoning_log);
        renderDependencies(data.headmaster.dependencies);
        updateIntegrationStatus(data.headmaster.integration_status);
    }
    
    if (data.tickets) {
        renderTicketGraph(data.tickets);
        renderWaves(data.tickets);
    }
}

/**
 * Handle headmaster update
 */
function onHeadmasterUpdate(data) {
    if (data.integration_status) {
        updateIntegrationStatus(data.integration_status);
    }
    if (data.reasoning_log) {
        renderReasoningLog(data.reasoning_log);
    }
    if (data.dependencies) {
        renderDependencies(data.dependencies);
    }
}

/**
 * Handle headmaster reasoning
 */
function onHeadmasterReasoning(entry) {
    addReasoningEntry(entry);
}

/**
 * Handle dependencies update
 */
function onDependenciesUpdate(dependencies) {
    renderDependencies(dependencies);
}

/**
 * Handle tickets update
 */
function onTicketsUpdate(tickets) {
    renderTicketGraph(tickets);
    renderWaves(tickets);
}

/**
 * Determine decision type from message
 */
function getDecisionType(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('pars') || lowerMessage.includes('analyz')) {
        return DECISION_TYPES.parsing;
    }
    if (lowerMessage.includes('plan') || lowerMessage.includes('decompos') || lowerMessage.includes('ticket') || lowerMessage.includes('task')) {
        return DECISION_TYPES.planning;
    }
    if (lowerMessage.includes('dispatch') || lowerMessage.includes('assign') || lowerMessage.includes('runner')) {
        return DECISION_TYPES.dispatching;
    }
    if (lowerMessage.includes('execut') || lowerMessage.includes('running') || lowerMessage.includes('implement')) {
        return DECISION_TYPES.executing;
    }
    if (lowerMessage.includes('complete') || lowerMessage.includes('done') || lowerMessage.includes('success') || lowerMessage.includes('finish')) {
        return DECISION_TYPES.completed;
    }
    
    return { icon: '•', class: '' };
}

/**
 * Format decision entry for cleaner display
 */
function formatDecisionEntry(entry) {
    const decisionType = getDecisionType(entry.message);
    return {
        icon: decisionType.icon,
        className: decisionType.class,
        message: entry.message,
        timestamp: entry.timestamp
    };
}

/**
 * Render reasoning log
 */
function renderReasoningLog(logs) {
    const container = document.getElementById('reasoning-container');
    const countEl = document.getElementById('reasoning-count');
    
    if (!container) return;
    
    if (!logs || logs.length === 0) {
        container.innerHTML = `
            <div class="reasoning-empty">
                <p>No decisions yet</p>
                <span class="empty-hint">Entries will appear as HeadMaster processes objectives.</span>
            </div>
        `;
    } else {
        container.innerHTML = logs.map(entry => {
            const formatted = formatDecisionEntry(entry);
            return `
                <div class="reasoning-entry ${formatted.className}">
                    <span class="reasoning-time">${formatTimestamp(entry.timestamp)}</span>
                    <span class="reasoning-message"><span class="decision-icon">${formatted.icon}</span>${escapeHtml(entry.message)}</span>
                </div>
            `;
        }).join('');
    }
    
    if (countEl) {
        const count = logs ? logs.length : 0;
        countEl.textContent = `${count} entr${count !== 1 ? 'ies' : 'y'}`;
    }
}

/**
 * Add reasoning entry
 */
function addReasoningEntry(entry) {
    const container = document.getElementById('reasoning-container');
    const countEl = document.getElementById('reasoning-count');
    
    if (!container) return;
    
    // Remove empty state
    const emptyState = container.querySelector('.reasoning-empty');
    if (emptyState) {
        emptyState.remove();
    }
    
    const formatted = formatDecisionEntry(entry);
    const entryEl = document.createElement('div');
    entryEl.className = `reasoning-entry ${formatted.className}`;
    entryEl.innerHTML = `
        <span class="reasoning-time">${formatTimestamp(entry.timestamp)}</span>
        <span class="reasoning-message"><span class="decision-icon">${formatted.icon}</span>${escapeHtml(entry.message)}</span>
    `;
    container.appendChild(entryEl);
    
    // Auto-scroll to show new entry
    container.scrollTop = container.scrollHeight;
    
    if (countEl) {
        const count = container.querySelectorAll('.reasoning-entry').length;
        countEl.textContent = `${count} entr${count !== 1 ? 'ies' : 'y'}`;
    }
}

/**
 * Render ticket graph as SVG
 */
function renderTicketGraph(tickets) {
    const svg = document.getElementById('ticket-graph');
    if (!svg || !tickets || tickets.length === 0) return;
    
    // Calculate positions using constants
    const width = svg.clientWidth || DEFAULT_GRAPH_WIDTH;
    const height = GRAPH_HEIGHT;
    const padding = GRAPH_PADDING;
    const nodeRadius = NODE_RADIUS;
    
    // Group tickets by wave (based on dependencies)
    const waves = groupTicketsByWave(tickets);
    const waveCount = Object.keys(waves).length;
    const waveWidth = (width - padding * 2) / Math.max(waveCount, 1);
    
    let svgContent = '';
    
    // Draw edges (dependencies)
    tickets.forEach(ticket => {
        if (ticket.dependencies) {
            ticket.dependencies.forEach(depId => {
                const depTicket = tickets.find(t => t.id === depId);
                if (depTicket) {
                    const fromPos = getTicketPosition(depTicket, waves, waveWidth, height, padding, nodeRadius);
                    const toPos = getTicketPosition(ticket, waves, waveWidth, height, padding, nodeRadius);
                    svgContent += `
                        <line x1="${fromPos.x}" y1="${fromPos.y}" x2="${toPos.x}" y2="${toPos.y}"
                            stroke="#64748b" stroke-width="2" marker-end="url(#arrowhead)"/>
                    `;
                }
            });
        }
    });
    
    // Draw nodes
    tickets.forEach(ticket => {
        const pos = getTicketPosition(ticket, waves, waveWidth, height, padding, nodeRadius);
        const color = getStatusColor(ticket.status);
        
        svgContent += `
            <circle cx="${pos.x}" cy="${pos.y}" r="${nodeRadius}" fill="${color}" stroke="#1e293b" stroke-width="2"/>
            <text x="${pos.x}" y="${pos.y + 4}" text-anchor="middle" fill="white" font-size="10" font-weight="600">
                ${ticket.id.replace('TKT-', '')}
            </text>
        `;
    });
    
    // Add arrowhead marker definition
    svg.innerHTML = `
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
            </marker>
        </defs>
        ${svgContent}
    `;
}

/**
 * Group tickets by wave based on dependencies
 */
function groupTicketsByWave(tickets) {
    const waves = {};
    const processed = new Set();
    let waveNum = 0;
    
    while (processed.size < tickets.length) {
        const currentWave = [];
        
        tickets.forEach(ticket => {
            if (processed.has(ticket.id)) return;
            
            const deps = ticket.dependencies || [];
            const allDepsProcessed = deps.every(d => processed.has(d));
            
            if (allDepsProcessed) {
                currentWave.push(ticket);
            }
        });
        
        if (currentWave.length === 0) break;
        
        waves[waveNum] = currentWave;
        currentWave.forEach(t => processed.add(t.id));
        waveNum++;
    }
    
    return waves;
}

/**
 * Get ticket position in graph
 */
function getTicketPosition(ticket, waves, waveWidth, height, padding, nodeRadius) {
    let waveIndex = 0;
    let ticketIndex = 0;
    
    for (const [wave, waveTickets] of Object.entries(waves)) {
        const idx = waveTickets.findIndex(t => t.id === ticket.id);
        if (idx >= 0) {
            waveIndex = parseInt(wave);
            ticketIndex = idx;
            break;
        }
    }
    
    const waveTickets = waves[waveIndex] || [];
    const ticketHeight = (height - padding * 2) / Math.max(waveTickets.length, 1);
    
    return {
        x: padding + waveWidth * waveIndex + waveWidth / 2,
        y: padding + ticketHeight * ticketIndex + ticketHeight / 2
    };
}

/**
 * Get status color
 */
function getStatusColor(status) {
    switch ((status || '').toLowerCase()) {
        case 'completed': return '#22c55e';
        case 'in_progress': case 'in-progress': return '#f59e0b';
        case 'failed': return '#ef4444';
        default: return '#3b82f6';
    }
}

/**
 * Render dependencies
 */
function renderDependencies(dependencies) {
    const container = document.getElementById('dependency-container');
    if (!container) return;
    
    if (!dependencies || dependencies.length === 0) {
        container.innerHTML = `
            <div class="dependency-empty">
                <span class="empty-icon">🔗</span>
                <p>No dependencies defined</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = dependencies.map(dep => `
        <div class="dependency-item">
            <span class="dep-from">${escapeHtml(dep.from)}</span>
            <span class="dep-arrow">→</span>
            <span class="dep-to">${escapeHtml(dep.to)}</span>
        </div>
    `).join('');
}

/**
 * Update integration status
 */
function updateIntegrationStatus(status) {
    const badge = document.getElementById('integration-status-badge');
    if (badge) {
        badge.textContent = status;
        badge.className = `status-badge ${formatStatusClass(status)}`;
    }
}

/**
 * Render execution waves
 */
function renderWaves(tickets) {
    const container = document.getElementById('waves-container');
    if (!container) return;
    
    const waves = groupTicketsByWave(tickets);
    const waveEntries = Object.entries(waves);
    
    if (waveEntries.length === 0) {
        container.innerHTML = `
            <div class="waves-empty">
                <span class="empty-icon">🌊</span>
                <p>No execution waves created</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = waveEntries.map(([wave, waveTickets]) => `
        <div class="wave-item">
            <div class="wave-header">
                <span class="wave-name">Wave ${parseInt(wave) + 1}</span>
                <span class="badge">${waveTickets.length} ticket${waveTickets.length !== 1 ? 's' : ''}</span>
            </div>
            <div class="wave-tickets">
                ${waveTickets.map(t => `
                    <span class="wave-ticket ${formatStatusClass(t.status)}">${escapeHtml(t.id)}</span>
                `).join('')}
            </div>
        </div>
    `).join('');
}
