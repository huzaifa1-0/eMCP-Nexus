const API_BASE_URL = '/api';
        
        document.addEventListener('DOMContentLoaded', function() {
            fetchTools();
            
            // Search functionality
            document.getElementById('searchBtn').addEventListener('click', performSearch);
            document.getElementById('searchInput').addEventListener('keyup', function(e) {
                if (e.key === 'Enter') performSearch();
            });
        });

        let allTools = [];

        // 1. Fetch Tools from Backend
        async function fetchTools() {
            const grid = document.getElementById('mcpGrid');
            const statusBadge = document.getElementById('statusBadge');
            const resultsCount = document.getElementById('resultsCount');

            try {
                const response = await fetch(`${API_BASE_URL}/tools/`);
                if (!response.ok) throw new Error("Failed to fetch tools");
                
                allTools = await response.json();
                const count = allTools.length;

                const label = count === 1 ? 'eMCP tool available' : 'eMCP tools available';
                
                // Update counts
                if (statusBadge) {
                    statusBadge.innerHTML = `<i class="fas fa-check-circle"></i> ${count} ${label}`;
                }
        
                if (resultsCount) {
                    resultsCount.innerText = `${count} ${label}`;
                }

                // Render
                renderTools(allTools);
                
            } catch (error) {
                console.error(error);
                if (statusBadge) statusBadge.innerHTML = `<i class="fas fa-times-circle"></i> System Offline`;
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                        <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                        <h3>Failed to load marketplace</h3>
                        <p>Could not connect to the backend.</p>
                    </div>`;
                if (statusBadge) statusBadge.innerHTML = `<i class="fas fa-times-circle"></i> Offline`;
            }
        }

        // --- NEW MODAL LOGIC ---
        let currentConfigText = "";

        function openConfigModal(name, url) {
            if (!url) {
                showAlert("No deployment URL available for this tool.", "error");
                return;
            }

            // 1. Generate the JSON Config
            const config = {
                "mcpServers": {
                    [name.toLowerCase().replace(/\s+/g, '-')]: {
                        "url": url,
                        "type": "sse"
                    }
                }
            };

            // 2. Format it prettily
            currentConfigText = JSON.stringify(config, null, 2);

            // 3. Inject into the modal
            const codeBlock = document.getElementById('configCodeBlock');
            if(codeBlock) codeBlock.textContent = currentConfigText;

            // 4. Show the modal
            const modal = document.getElementById('configModal');
            if(modal) modal.style.display = 'flex';
        }

        function closeConfigModal() {
            const modal = document.getElementById('configModal');
            if(modal) modal.style.display = 'none';
        }

        async function copyFromModal() {
            try {
                await navigator.clipboard.writeText(currentConfigText);
                showAlert("Configuration copied!", "success");
                closeConfigModal();
            } catch (err) {
                console.error('Failed to copy:', err);
                showAlert("Failed to copy", "error");
            }
        }

        // Close modal if clicking outside the content box
        window.onclick = function(event) {
            const modal = document.getElementById('configModal');
            if (event.target === modal) {
                closeConfigModal();
            }
        }

        // 2. Render Tools (Handles Empty State)
        function renderTools(tools) {
            const grid = document.getElementById('mcpGrid');
            grid.innerHTML = ''; 

            // ✅ SHOW THIS IF NO TOOLS EXIST
            if (tools.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: #ccc;">
                <i class="fas fa-box-open" style="font-size: 48px; margin-bottom: 20px; color: #4cc9f0;"></i>
                <h3 style="font-size: 24px; margin-bottom: 10px;">No tools yet</h3>
                <p style="margin-bottom: 20px;">The marketplace is empty. Be the first to publish a tool!</p>
                <a href="seller_dashboard.html" class="btn btn-primary" style="text-decoration: none; display: inline-block;">
                    <i class="fas fa-plus"></i> Go to Dashboard
                </a>
                </div>`;
            return;
            }

            // ✅ RENDER CARDS IF TOOLS EXIST
            tools.forEach(tool => {
            // 1. Process Tool Definitions
            const subTools = tool.tool_definitions || [];
        
            let toolsListHtml = '';
            if (subTools.length > 0) {
                toolsListHtml = `<div class="tools-section" style="margin: 15px 0;">
                <div style="font-size: 12px; font-weight: 600; color: #888; margin-bottom: 8px;">
                    <i class="fas fa-wrench"></i> INCLUDED TOOLS (${subTools.length})
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    ${subTools.slice(0, 3).map(t => `
                        <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px; color: #eee; font-weight: 500;">${t.name}</span>
                            <span style="font-size: 11px; background: rgba(76, 201, 240, 0.2); color: #4cc9f0; padding: 2px 6px; border-radius: 4px;">
                                ${tool.cost > 0 ? '$' + tool.cost : 'Free'}
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>`;
            } else {
             toolsListHtml = `<div style="margin: 15px 0; font-size: 13px; color: #666; font-style: italic;">
                No specific tools discovered yet.
             </div>`;
            }

            // 2. Determine Config Button State
            const hasUrl = !!tool.url;
            const configBtnClass = hasUrl ? 'btn-secondary' : 'btn-secondary disabled';
            const configBtnStyle = hasUrl ? 'width: 100%; justify-content: center;' : 'width: 100%; justify-content: center; opacity: 0.5; cursor: not-allowed;';

            const card = document.createElement('div');
            card.className = 'mcp-card';
            card.innerHTML = `
            <div class="mcp-header">
                <div class="mcp-title">${tool.name}</div>
                ${tool.url 
                    ? `<div class="mcp-badge" style="background: rgba(76, 201, 240, 0.2); color: #4cc9f0;">Live</div>`
                    : `<div class="mcp-badge" style="background: rgba(255, 193, 7, 0.2); color: #ffc107;">Deploying</div>`
                }
            </div>
            
            <div class="mcp-config" style="text-align: left; font-size: 13px; padding: 15px;">
                <div style="margin-bottom: 5px;"><strong>Description:</strong></div>
                <div class="line-clamp-3" style="color: #ccc; margin-bottom: 10px; line-height: 1.4;">
                ${tool.description}
                </div>
            </div>

            ${toolsListHtml}
            
            <div class="action-buttons">
                <button class="btn ${configBtnClass}" style="${configBtnStyle}" 
                    onclick="openConfigModal('${tool.name}', '${tool.url || ''}')">
                    <i class="fas fa-copy"></i> Copy Config
                </button>
            </div>
            
            <div class="mcp-date" style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                <span><i class="far fa-clock"></i> Recent</span>
                <span style="font-weight: bold; color: #fff;">${tool.cost > 0 ? tool.cost + ' USDC' : 'Free'}</span>
            </div>
            `;
            grid.appendChild(card);
            });
        }

        // 3. Search/Filter Logic
        async function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            const grid = document.getElementById('mcpGrid');
            const resultsCount = document.getElementById('resultsCount');
            
            if (!query) {
                fetchTools(); // Reloads the full list
                return;
            }
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ccc;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 32px; margin-bottom: 15px; color: #4cc9f0;"></i>
                    <p>AI is analyzing your request...</p>
                </div>`;
            
            try {
                // Call the AI Search Endpoint
                const response = await fetch(`${API_BASE_URL}/search/?query=${encodeURIComponent(query)}`);
                
                if (!response.ok) throw new Error("Search failed");
                
                const data = await response.json();
                const results = data.results;

                if (resultsCount) {
                    const label = results.length === 1 ? 'match found' : 'matches found';
                    resultsCount.innerText = `${results.length} AI ${label}`;
                }

                renderTools(results);
            } catch (error) {
                console.error("Search Error:", error);
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 32px; margin-bottom: 15px;"></i>
                        <p>Search failed. Please try again.</p>
                    </div>`;
            }
        }

        // 4. Functionality: Use/Run the Tool
       // 4. Functionality: Use/Run the Tool (Now with Crypto Payment Support)
async function useTool(toolId, toolName) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        showAlert("Please log in first!", "error");
        return;
    }

    showAlert(`Running ${toolName}...`, "info");
    
    try {
        // ATTEMPT 1: Try to use the tool normally
        let response = await fetch(`${API_BASE_URL}/tools/use/${toolId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        // 🛑 CHECK: Did we get a 402 Payment Required?
        if (response.status === 402) {
            const errorData = await response.json();
            const paymentDetails = errorData.detail; // { amount, receiver, currency }

            // Close the "Running..." alert
            const existingAlert = document.querySelector('.alert-popup');
            if (existingAlert) existingAlert.remove();

            // Ask user to pay
            const confirmPay = confirm(`💰 Payment Required\n\nThis tool costs ${paymentDetails.amount} ETH.\n\nClick OK to pay with MetaMask.`);
            
            if (!confirmPay) {
                showAlert("Payment cancelled.", "error");
                return;
            }

            showAlert("Opening MetaMask...", "info");

            // 1. Trigger Crypto Payment
            const txHash = await handleCryptoPayment(paymentDetails.amount, paymentDetails.receiver);
            
            if (txHash) {
                showAlert("Payment sent! Verifying...", "success");
                
                // ATTEMPT 2: Retry request with Proof of Payment
                response = await fetch(`${API_BASE_URL}/tools/use/${toolId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'X-Transaction-Hash': txHash // <--- The Proof
                    }
                });
            } else {
                return; // Payment failed or cancelled
            }
        }

        // Handle final success/failure
        const data = await response.json();
        
        if (response.ok) {
            const statusMsg = data.status === 'success' ? 'Success' : 'Failed';
            alert(`✅ Execution Result:\n\nStatus: ${statusMsg}\nMessage: ${data.message}\nTime: ${data.processing_time}s`);
        } else {
            throw new Error(data.detail || "Execution failed");
        }

    } catch (error) {
        console.error(error);
        showAlert(error.message, "error");
    }
}

// --- Helper: Handle MetaMask Payment ---
async function handleCryptoPayment(amountEth, receiverAddress) {
    // Check if MetaMask is installed
    if (typeof window.ethereum === 'undefined') {
        alert("MetaMask is not installed! You need a crypto wallet to pay for this tool.");
        return null;
    }

    try {
        // Request account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const sender = accounts[0];

        // Convert ETH to Wei (Hex format). 1 ETH = 10^18 Wei.
        // using BigInt ensures precision for crypto math
        const weiValue = BigInt(Math.floor(amountEth * 1e18)).toString(16);

        // Send Transaction
        const txHash = await window.ethereum.request({
            method: 'eth_sendTransaction',
            params: [
                {
                    from: sender,
                    to: receiverAddress,
                    value: "0x" + weiValue, // Hex value
                },
            ],
        });

        console.log("Tx Hash:", txHash);
        return txHash;

    } catch (error) {
        console.error("Payment Error:", error);
        showAlert("Payment failed: " + error.message, "error");
        return null;
    }
}

        function showDetails(name, desc, cost) {
            alert(`Details for ${name}:\n\n${desc}\n\nCost per run: $${cost}\n\nThis tool is hosted on eMCP Nexus.`);
        }

        // Helper to show floating alerts
        function showAlert(message, type) {
            const existing = document.querySelector('.alert-popup');
            if (existing) existing.remove();

            const alert = document.createElement('div');
            alert.className = 'alert alert-popup';
            alert.style.background = 'rgba(18, 18, 18, 0.95)';
            alert.style.border = '1px solid rgba(255, 255, 255, 0.2)';
            alert.style.borderLeft = `4px solid ${type === 'error' ? '#ff4d4d' : '#4cc9f0'}`;
            alert.style.padding = '15px 20px';
            alert.style.borderRadius = '8px';
            alert.style.color = '#fff';
            alert.style.position = 'fixed';
            alert.style.top = '20px';
            alert.style.right = '20px';
            alert.style.zIndex = '9999';
            alert.style.display = 'flex';
            alert.style.alignItems = 'center';
            alert.style.gap = '10px';
            alert.style.boxShadow = '0 5px 15px rgba(0,0,0,0.5)';
            alert.style.minWidth = '300px';
            
            alert.innerHTML = `
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}" style="color: ${type === 'error' ? '#ff4d4d' : '#4cc9f0'}"></i>
                <span>${message}</span>
            `;
            document.body.appendChild(alert);

            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s ease';
                setTimeout(() => alert.remove(), 500);
            }, 4000);
        }
        // --- Voice Search Feature ---
    const voiceBtn = document.getElementById('voiceBtn');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    // Check browser support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = false; // Stop listening after one sentence
        recognition.lang = 'en-US';     // Default language
        recognition.interimResults = false;

        voiceBtn.addEventListener('click', () => {
            if (voiceBtn.classList.contains('listening')) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                    // Visual feedback: Add 'listening' class
                    voiceBtn.classList.add('listening');
                    searchInput.placeholder = "Listening...";
                } catch (error) {
                    console.error("Speech recognition start error:", error);
                }
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            
            // Automatically trigger the search
            performSearch();
        };

        recognition.onend = () => {
            // Reset UI when finished
            voiceBtn.classList.remove('listening');
            searchInput.placeholder = "Search eMCPs, tools, or descriptions...";
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            voiceBtn.classList.remove('listening');
            searchInput.placeholder = "Error. Try again.";
        };
    } else {
        // Hide microphone if browser doesn't support API
        voiceBtn.style.display = 'none';
        console.log("Web Speech API not supported in this browser.");
    }

    // --- NEXUS CHAT LOGIC ---
    document.addEventListener('DOMContentLoaded', () => {
        // Ensure API_BASE_URL is defined
        const API_BASE_URL = '/api'; 

        const widget = document.getElementById('nexus-chat-widget');
        const toggleBtn = document.getElementById('chat-toggle');
        const windowEl = document.getElementById('chat-window');
        const closeBtn = document.getElementById('close-chat');
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const messages = document.getElementById('chat-messages');

        // Check if elements exist to prevent errors
        if (!toggleBtn || !windowEl || !input || !sendBtn) return;

        // 1. Toggle Chat Window
        const toggleChat = () => {
            const isVisible = windowEl.style.display === 'flex';
            windowEl.style.display = isVisible ? 'none' : 'flex';
            if (!isVisible) setTimeout(() => input.focus(), 100);
        };

        toggleBtn.addEventListener('click', toggleChat);
        closeBtn.addEventListener('click', toggleChat);

        // 2. Send Message Logic
        const sendMessage = async () => {
            const text = input.value.trim();
            if (!text) return;

            // Add User Message
            appendMessage(text, 'user');
            input.value = '';

            // Add "Thinking..." bubble
            const loadingId = 'loading-' + Date.now();
            appendMessage('Thinking...', 'bot', loadingId);

            try {
                // Call Backend API
                const res = await fetch(`${API_BASE_URL}/chat/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                
                const data = await res.json();
                
                // Remove loading and show response
                const loader = document.getElementById(loadingId);
                if (loader) loader.remove();
                
                // Handle different response formats
                const replyText = data.response || data.reply || "I didn't get a response.";
                appendMessage(replyText, 'bot');

            } catch (error) {
                console.error(error);
                const loader = document.getElementById(loadingId);
                if(loader) loader.innerText = "Error connecting to NexusAI.";
            }
        };

        // 3. Helper to append messages
        function appendMessage(text, sender, id = null) {
            const div = document.createElement('div');
            if (id) div.id = id;
            div.style.padding = '10px 15px';
            div.style.borderRadius = '15px';
            div.style.maxWidth = '80%';
            div.style.lineHeight = '1.4';
            div.style.fontSize = '14px';
            div.style.marginBottom = '10px';
            
            if (sender === 'user') {
                div.style.alignSelf = 'flex-end';
                div.style.background = '#4cc9f0';
                div.style.color = '#fff';
                div.style.borderRadius = '15px 15px 0 15px';
            } else {
                div.style.alignSelf = 'flex-start';
                div.style.background = '#2a2a2a';
                div.style.color = '#ddd';
                div.style.borderRadius = '15px 15px 15px 0';
            }
            
            div.innerHTML = text.replace(/\n/g, '<br>');
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        // Listeners
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    });