/**
 * Five Minds UI - Settings JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    loadSettings();
    
    // Setup event listeners
    setupEventListeners();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Toggle visibility buttons
    document.querySelectorAll('.toggle-visibility').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '🙈';
                } else {
                    input.type = 'password';
                    this.textContent = '👁️';
                }
            }
        });
    });
    
    // Temperature slider
    const tempSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temperature-value');
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', function() {
            tempValue.textContent = this.value;
        });
    }
    
    // Save button
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
    
    // Reset button
    const resetBtn = document.getElementById('reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSettings);
    }
}

/**
 * Load settings from server/localStorage
 */
function loadSettings() {
    // Try to load from server first
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            applySettings(settings);
        })
        .catch(() => {
            // Fallback to localStorage
            const saved = localStorage.getItem('fiveminds_settings');
            if (saved) {
                try {
                    const settings = JSON.parse(saved);
                    applySettings(settings);
                } catch (e) {
                    console.error('Failed to parse saved settings:', e);
                }
            }
        });
}

/**
 * Apply settings to form
 */
function applySettings(settings) {
    if (!settings) return;
    
    // API Keys (show masked versions for security)
    if (settings.api_keys) {
        if (settings.api_keys.openai_configured) {
            document.getElementById('openai-key').placeholder = '••••••••••••••••';
        }
        if (settings.api_keys.anthropic_configured) {
            document.getElementById('anthropic-key').placeholder = '••••••••••••••••';
        }
        if (settings.api_keys.google_configured) {
            document.getElementById('google-key').placeholder = '••••••••••••••••';
        }
        if (settings.api_keys.cohere_configured) {
            document.getElementById('cohere-key').placeholder = '••••••••••••••••';
        }
        if (settings.api_keys.custom_endpoint) {
            document.getElementById('custom-endpoint').value = settings.api_keys.custom_endpoint;
        }
    }
    
    // Model Configuration
    if (settings.models) {
        if (settings.models.headmaster) {
            document.getElementById('headmaster-model').value = settings.models.headmaster;
        }
        if (settings.models.runner) {
            document.getElementById('runner-model').value = settings.models.runner;
        }
        if (settings.models.reviewer) {
            document.getElementById('reviewer-model').value = settings.models.reviewer;
        }
        if (settings.models.temperature !== undefined) {
            document.getElementById('temperature').value = settings.models.temperature;
            document.getElementById('temperature-value').textContent = settings.models.temperature;
        }
        if (settings.models.max_tokens) {
            document.getElementById('max-tokens').value = settings.models.max_tokens;
        }
    }
}

/**
 * Save settings to server
 */
function saveSettings() {
    const settings = {
        api_keys: {
            openai_key: document.getElementById('openai-key').value || null,
            anthropic_key: document.getElementById('anthropic-key').value || null,
            google_key: document.getElementById('google-key').value || null,
            cohere_key: document.getElementById('cohere-key').value || null,
            custom_endpoint: document.getElementById('custom-endpoint').value || null
        },
        models: {
            headmaster: document.getElementById('headmaster-model').value,
            runner: document.getElementById('runner-model').value,
            reviewer: document.getElementById('reviewer-model').value,
            temperature: parseFloat(document.getElementById('temperature').value),
            max_tokens: parseInt(document.getElementById('max-tokens').value)
        }
    };
    
    // Show saving status
    showStatus('Saving...', 'info');
    
    // Save to server
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showStatus('Settings saved successfully!', 'success');
            
            // Also save to localStorage as backup
            const localSettings = {
                models: settings.models,
                api_keys: {
                    custom_endpoint: settings.api_keys.custom_endpoint
                }
            };
            localStorage.setItem('fiveminds_settings', JSON.stringify(localSettings));
            
            // Clear the password fields after save (for security)
            document.getElementById('openai-key').value = '';
            document.getElementById('anthropic-key').value = '';
            document.getElementById('google-key').value = '';
            document.getElementById('cohere-key').value = '';
            
            // Update placeholders to indicate keys are configured
            if (settings.api_keys.openai_key) {
                document.getElementById('openai-key').placeholder = '••••••••••••••••';
            }
            if (settings.api_keys.anthropic_key) {
                document.getElementById('anthropic-key').placeholder = '••••••••••••••••';
            }
            if (settings.api_keys.google_key) {
                document.getElementById('google-key').placeholder = '••••••••••••••••';
            }
            if (settings.api_keys.cohere_key) {
                document.getElementById('cohere-key').placeholder = '••••••••••••••••';
            }
        } else {
            showStatus('Failed to save settings: ' + (result.message || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        showStatus('Error saving settings: ' + error.message, 'error');
    });
}

/**
 * Reset settings to defaults
 */
function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This will clear all API keys.')) {
        return;
    }
    
    // Clear form
    document.getElementById('openai-key').value = '';
    document.getElementById('anthropic-key').value = '';
    document.getElementById('google-key').value = '';
    document.getElementById('cohere-key').value = '';
    document.getElementById('custom-endpoint').value = '';
    
    document.getElementById('headmaster-model').value = 'gpt-4';
    document.getElementById('runner-model').value = 'gpt-4';
    document.getElementById('reviewer-model').value = 'gpt-4';
    document.getElementById('temperature').value = '0.7';
    document.getElementById('temperature-value').textContent = '0.7';
    document.getElementById('max-tokens').value = '4096';
    
    // Reset placeholders
    document.getElementById('openai-key').placeholder = 'sk-...';
    document.getElementById('anthropic-key').placeholder = 'sk-ant-...';
    document.getElementById('google-key').placeholder = 'AIza...';
    document.getElementById('cohere-key').placeholder = '...';
    
    // Clear localStorage
    localStorage.removeItem('fiveminds_settings');
    
    // Clear server settings
    fetch('/api/settings/reset', { method: 'POST' })
        .then(response => response.json())
        .then(result => {
            showStatus('Settings reset to defaults', 'success');
        })
        .catch(error => {
            showStatus('Settings reset locally (server unavailable)', 'warning');
        });
}

/**
 * Show status message
 */
function showStatus(message, type) {
    const statusEl = document.getElementById('settings-status');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = 'settings-status ' + type;
        
        // Clear after 3 seconds for success/info
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                statusEl.textContent = '';
                statusEl.className = 'settings-status';
            }, 3000);
        }
    }
}
