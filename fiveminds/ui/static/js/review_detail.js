/**
 * Five Minds UI - Review Detail Page JavaScript
 */

let reviewData = null;
let ticketData = null;
let resultData = null;

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    // Find review for this ticket
    if (data.reviews) {
        reviewData = data.reviews.find(r => r.ticket_id === TICKET_ID);
        if (reviewData) {
            renderReviewStatus(reviewData);
            renderFeedback(reviewData);
            renderSuggestions(reviewData);
            renderFollowUps(reviewData.follow_up_tickets);
        }
    }
    
    // Find ticket data
    if (data.tickets) {
        ticketData = data.tickets.find(t => t.id === TICKET_ID);
        if (ticketData) {
            renderAcceptanceCriteria(ticketData.acceptance_criteria);
        }
    }
    
    // Find result data
    if (data.results && data.results[TICKET_ID]) {
        resultData = data.results[TICKET_ID];
        renderDiff(resultData.diff);
        analyzeRisks(resultData);
    }
}

/**
 * Handle review update
 */
function onReviewUpdate(review) {
    if (review.ticket_id === TICKET_ID) {
        reviewData = review;
        renderReviewStatus(review);
        renderFeedback(review);
        renderSuggestions(review);
        renderFollowUps(review.follow_up_tickets);
    }
}

/**
 * Render review status
 */
function renderReviewStatus(review) {
    const badge = document.getElementById('review-status-badge');
    const scoreFill = document.getElementById('score-fill');
    const scoreValue = document.getElementById('score-value');
    
    if (badge) {
        badge.textContent = review.approved ? 'Approved' : 'Rejected';
        badge.className = `status-badge ${review.approved ? 'approved' : 'rejected'}`;
    }
    
    const scorePercent = review.alignment_score * 100;
    if (scoreFill) {
        scoreFill.style.width = `${scorePercent}%`;
    }
    
    if (scoreValue) {
        scoreValue.textContent = `${scorePercent.toFixed(0)}%`;
    }
}

/**
 * Render diff
 */
function renderDiff(diff) {
    const container = document.getElementById('diff-content');
    if (!container) return;
    
    container.innerHTML = formatDiff(diff);
}

/**
 * Toggle diff view
 */
function toggleDiffView(mode) {
    // For simplicity, just log - could implement split view
    console.log(`Switching to ${mode} view`);
}

/**
 * Render acceptance criteria
 */
function renderAcceptanceCriteria(criteria) {
    const container = document.getElementById('criteria-list');
    const progressEl = document.getElementById('criteria-progress');
    
    if (!container) return;
    
    if (!criteria || criteria.length === 0) {
        container.innerHTML = '<li class="criteria-empty">No acceptance criteria defined</li>';
        return;
    }
    
    const met = criteria.filter(c => c.met).length;
    
    container.innerHTML = criteria.map(c => `
        <li class="${c.met ? 'met' : 'unmet'}">
            ${escapeHtml(c.description)}
        </li>
    `).join('');
    
    if (progressEl) {
        progressEl.textContent = `${met}/${criteria.length} met`;
    }
}

/**
 * Analyze risks from result
 */
function analyzeRisks(result) {
    const container = document.getElementById('risks-list');
    if (!container) return;
    
    const risks = [];
    
    // Check for common risk indicators
    if (result.diff) {
        if (result.diff.includes('TODO')) {
            risks.push('TODO comments found - incomplete implementation');
        }
        if (result.diff.includes('FIXME')) {
            risks.push('FIXME comments found - known issues');
        }
        if (result.diff.includes('console.log') || result.diff.includes('print(')) {
            risks.push('Debug statements detected');
        }
        if (result.diff.includes('password') || result.diff.includes('secret')) {
            risks.push('Potential sensitive data exposure');
        }
    }
    
    if (result.test_results) {
        if (result.test_results.failed > 0) {
            risks.push(`${result.test_results.failed} test(s) failing`);
        }
        if (result.test_results.skipped > 0) {
            risks.push(`${result.test_results.skipped} test(s) skipped`);
        }
    }
    
    if (!result.success) {
        risks.push('Execution failed');
    }
    
    if (risks.length === 0) {
        container.innerHTML = '<li class="risks-empty">No risks identified</li>';
    } else {
        container.innerHTML = risks.map(risk => `<li>${escapeHtml(risk)}</li>`).join('');
    }
}

/**
 * Render feedback
 */
function renderFeedback(review) {
    const container = document.getElementById('feedback-content');
    if (!container) return;
    
    if (!review.feedback) {
        container.innerHTML = '<p class="feedback-empty">No feedback provided</p>';
        return;
    }
    
    container.innerHTML = `<pre>${escapeHtml(review.feedback)}</pre>`;
}

/**
 * Render suggestions
 */
function renderSuggestions(review) {
    const container = document.getElementById('suggestions-list');
    if (!container) return;
    
    if (!review.suggestions || review.suggestions.length === 0) {
        container.innerHTML = '<li class="suggestions-empty">No suggestions available</li>';
        return;
    }
    
    container.innerHTML = review.suggestions.map(s => `<li>${escapeHtml(s)}</li>`).join('');
}

/**
 * Render follow-up tickets
 */
function renderFollowUps(followUps) {
    const container = document.getElementById('followup-list');
    if (!container) return;
    
    if (!followUps || followUps.length === 0) {
        container.innerHTML = '<li class="followup-empty">No follow-up tickets</li>';
        return;
    }
    
    container.innerHTML = followUps.map(ticket => `
        <li>
            <strong>${escapeHtml(ticket.id)}</strong> - ${escapeHtml(ticket.title)}
        </li>
    `).join('');
}

/**
 * Create follow-up from review
 */
async function createFollowUpFromReview() {
    const title = prompt('Enter follow-up ticket title:');
    if (!title) return;
    
    const description = prompt('Enter description:');
    if (!description) return;
    
    const ticketId = `${TICKET_ID}-FU-${Date.now()}`;
    const ticket = {
        id: ticketId,
        title: title,
        description: description,
        priority: 'medium',
        status: 'pending',
        dependencies: [TICKET_ID],
        acceptance_criteria: [
            { description: 'Complete follow-up work', met: false }
        ],
        metadata: { is_followup: true }
    };
    
    try {
        const result = await apiRequest('/api/follow-up', 'POST', ticket);
        if (result.success) {
            alert('Follow-up ticket created successfully');
        } else {
            alert(`Failed to create ticket: ${result.message}`);
        }
    } catch (error) {
        alert(`Error creating ticket: ${error.message}`);
    }
}

/**
 * Request re-run of ticket
 */
function rerunTicket() {
    alert('Re-run request submitted. This feature would trigger the ticket to be executed again.');
}
