// static/script.js
// THE DEFINITIVE VERSION - Prioritizes both responsiveness and accuracy.

document.addEventListener('DOMContentLoaded', () => {
    const apiButton = document.getElementById('api-button');
    const requestLog = document.getElementById('request-log');
    const tokenCountSpan = document.getElementById('token-count');

    // --- Configuration ---
    const BUCKET_CAPACITY = 100;
    const REFILL_RATE_PER_SECOND = 1; // Visual refill ticks by 1
    const REFILL_COOLDOWN_MS = 3000;   // 3-second delay after last user action

    let requestCounter = 0;
    let refillCooldownTimerId = null; // ID for the 3s delay timer
    let refillIntervalId = null;      // ID for the repeating visual tick-up timer

    // --- Core Timer Control: The heart of the visual logic ---

    /**
     * Stops all active timers. This is called on ANY user interaction
     * to prevent visual bugs and race conditions.
     */
    function stopAllTimers() {
        clearTimeout(refillCooldownTimerId);
        clearInterval(refillIntervalId);
        refillIntervalId = null; // Resetting the ID is crucial
    }

    /**
     * Starts the repeating visual timer that ticks the number up on the screen.
     * This is purely for show and runs every second.
     */
    function startVisualRefill() {
        if (refillIntervalId !== null) return; // Prevent multiple intervals

        refillIntervalId = setInterval(() => {
            let currentTokens = parseInt(tokenCountSpan.textContent);
            if (currentTokens < BUCKET_CAPACITY) {
                updateTokenDisplay(currentTokens + REFILL_RATE_PER_SECOND);
            } else {
                stopAllTimers(); // Stop when visually full
            }
        }, 1000); // Ticks every 1 second
    }
    
    // --- UI Update & Logging Functions ---

    const updateTokenDisplay = (tokens) => {
        const displayTokens = Math.floor(tokens);
        tokenCountSpan.textContent = displayTokens;
        if (displayTokens < 20) { tokenCountSpan.style.color = '#dc3545'; }
        else if (displayTokens < 50) { tokenCountSpan.style.color = '#ffc107'; }
        else { tokenCountSpan.style.color = '#0d6efd'; }
    };

    const addLog = (message, className) => {
        const logEntry = document.createElement('div');
        logEntry.innerHTML = message;
        logEntry.className = `log-entry ${className}`;
        requestLog.prepend(logEntry);
    };

    // --- The Main API Call Handler ---

    const handleApiCall = async () => {
        // 1. Immediately stop any visual timers. This is the KEY to preventing choppiness.
        stopAllTimers();

        requestCounter++;
        apiButton.disabled = true;
        apiButton.textContent = 'Requesting...';

        // 2. Perform an "Optimistic UI Update". We GUESS the count will go down by one
        // to make the interface feel instantaneous.
        let currentTokens = parseInt(tokenCountSpan.textContent);
        if (currentTokens >= 1) {
            updateTokenDisplay(currentTokens - 1);
        }

        try {
            const response = await fetch('/api/resource/');
            
            // 3. Re-synchronize with the Server's Authoritative State.
            // This is the moment of truth. We get the REAL number from the backend.
            const serverTokensLeft = parseInt(response.headers.get('X-RateLimit-Tokens-Left') || '0');
            
            // 4. Update the UI with the REAL number. This corrects our guess and explains
            // the "jump" you see after a pause - it's the UI catching up to reality.
            updateTokenDisplay(serverTokensLeft);
            
            const ts = `<span style="color:#6c757d">[${new Date().toLocaleTimeString()}]</span>`;
            if (response.ok) {
                addLog(`${ts} REQ #${requestCounter}: <b class="success">SUCCESS (${response.status})</b>`, 'success');
            } else {
                addLog(`${ts} REQ #${requestCounter}: <b class="error">RATE LIMITED (${response.status})</b>`, 'error');
            }
        } catch (error) {
            console.error("Error:", error);
            addLog(`${ts} REQ #${requestCounter}: <b class="error">CLIENT ERROR</b>`, 'error');
        } finally {
            apiButton.disabled = false;
            apiButton.textContent = 'Make API Request';
            
            // 5. After the request is totally finished, start the 3-second cooldown.
            // If the user clicks again, this timer will be cancelled by step 1.
            refillCooldownTimerId = setTimeout(startVisualRefill, REFILL_COOLDOWN_MS);
        }
    };
    
    apiButton.addEventListener('click', handleApiCall);
});