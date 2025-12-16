/**
 * Five Minds UI - Review Page JavaScript
 */

let allReviews = [];
let allTickets = [];

/**
 * Handle full state update
 */
function onStateUpdate(data) {
    if (data.reviews) {
        allReviews = data.reviews;
        renderReviews(data.reviews);
        updateSummary(data.reviews);
    }
    
    if (data.tickets) {
        allTickets = data.tickets;
        populateParentSelect(data.tickets);
        renderFollowUps(data.tickets);
    }
}

/**
 * Handle review update
 */
function onReviewUpdate(review) {
    allReviews.push(review);
    renderReviews(allReviews);
    updateSummary(allReviews);
}

/**
 * Handle tickets update
 */
function onTicketsUpdate(tickets) {
    allTickets = tickets;
    populateParentSelect(tickets);
    renderFollowUps(tickets);
}

/**
 * Render reviews
 */
function renderReviews(reviews) {
    const container = document.getElementById('reviews-container');
    const filter = document.getElementById('review-filter');
    
    if (!container) return;
    
    let filteredReviews = reviews;
    if (filter) {
        const filterValue = filter.value;
        if (filterValue === 'approved') {
            filteredReviews = reviews.filter(r => r.approved);
        } else if (filterValue === 'rejected') {
            filteredReviews = reviews.filter(r => !r.approved);
        }
    }
    
    if (filteredReviews.length === 0) {
        container.innerHTML = `
            <div class="reviews-empty">
                <span class="empty-icon">🔍</span>
                <h3>No Reviews Yet</h3>
                <p>Reviews will appear here after runner execution completes</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredReviews.map(review => `
        <div class="review-item ${review.approved ? 'approved' : 'rejected'}" onclick="viewReview('${review.ticket_id}')">
            <div class="review-info">
                <span class="review-ticket">${escapeHtml(review.ticket_id)}</span>
                <span class="review-score">Alignment: ${(review.alignment_score * 100).toFixed(0)}%</span>
            </div>
            <span class="status-badge ${review.approved ? 'approved' : 'rejected'}">
                ${review.approved ? 'Approved' : 'Rejected'}
            </span>
        </div>
    `).join('');
}

/**
 * Update summary statistics
 */
function updateSummary(reviews) {
    const approvedEl = document.getElementById('approved-count');
    const rejectedEl = document.getElementById('rejected-count');
    const pendingEl = document.getElementById('pending-count');
    const alignmentEl = document.getElementById('avg-alignment');
    
    const approved = reviews.filter(r => r.approved).length;
    const rejected = reviews.filter(r => !r.approved).length;
    const pending = allTickets.filter(t => !reviews.find(r => r.ticket_id === t.id)).length;
    
    const avgAlignment = reviews.length > 0 
        ? reviews.reduce((sum, r) => sum + r.alignment_score, 0) / reviews.length 
        : 0;
    
    if (approvedEl) approvedEl.textContent = approved;
    if (rejectedEl) rejectedEl.textContent = rejected;
    if (pendingEl) pendingEl.textContent = pending;
    if (alignmentEl) alignmentEl.textContent = `${(avgAlignment * 100).toFixed(0)}%`;
}

/**
 * View review detail
 */
function viewReview(ticketId) {
    window.location.href = `/review/${ticketId}`;
}

/**
 * Populate parent ticket select
 */
function populateParentSelect(tickets) {
    const select = document.getElementById('followup-parent');
    if (!select) return;
    
    select.innerHTML = '<option value="">None</option>';
    tickets.forEach(ticket => {
        select.innerHTML += `<option value="${ticket.id}">${ticket.id} - ${escapeHtml(ticket.title)}</option>`;
    });
}

/**
 * Render follow-up tickets
 */
function renderFollowUps(tickets) {
    const container = document.getElementById('followups-container');
    if (!container) return;
    
    // Find follow-up tickets (those with dependencies)
    const followUps = tickets.filter(t => t.id.includes('-FU-') || (t.dependencies && t.dependencies.length > 0 && t.metadata && t.metadata.is_followup));
    
    if (followUps.length === 0) {
        container.innerHTML = `
            <div class="followups-empty">
                <span class="empty-icon">📝</span>
                <p>No follow-up tickets created</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = followUps.map(ticket => `
        <div class="followup-item">
            <div class="followup-info">
                <span class="followup-title">${escapeHtml(ticket.title)}</span>
                <span class="followup-parent">Parent: ${ticket.dependencies && ticket.dependencies.length > 0 ? ticket.dependencies[0] : 'None'}</span>
            </div>
            <span class="status-badge ${formatStatusClass(ticket.status)}">${ticket.status || 'pending'}</span>
        </div>
    `).join('');
}

/**
 * Open follow-up modal
 */
function openFollowUpModal() {
    const modal = document.getElementById('followup-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Close follow-up modal
 */
function closeFollowUpModal() {
    const modal = document.getElementById('followup-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    
    // Reset form
    const form = document.getElementById('followup-form');
    if (form) {
        form.reset();
    }
}

/**
 * Submit follow-up ticket
 */
async function submitFollowUp() {
    const title = document.getElementById('followup-title').value;
    const description = document.getElementById('followup-description').value;
    const priority = document.getElementById('followup-priority').value;
    const parent = document.getElementById('followup-parent').value;
    
    if (!title || !description) {
        alert('Please fill in all required fields');
        return;
    }
    
    const ticketId = `TKT-FU-${Date.now()}`;
    const ticket = {
        id: ticketId,
        title: title,
        description: description,
        priority: priority,
        status: 'pending',
        dependencies: parent ? [parent] : [],
        acceptance_criteria: [
            { description: 'Complete follow-up work', met: false }
        ],
        metadata: { is_followup: true }
    };
    
    try {
        const result = await apiRequest('/api/follow-up', 'POST', ticket);
        if (result.success) {
            closeFollowUpModal();
            alert('Follow-up ticket created successfully');
        } else {
            alert(`Failed to create ticket: ${result.message}`);
        }
    } catch (error) {
        alert(`Error creating ticket: ${error.message}`);
    }
}

// Add filter event listener
document.addEventListener('DOMContentLoaded', function() {
    const filter = document.getElementById('review-filter');
    if (filter) {
        filter.addEventListener('change', function() {
            renderReviews(allReviews);
        });
    }
});
