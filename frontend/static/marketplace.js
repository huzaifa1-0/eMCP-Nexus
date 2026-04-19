const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', function() {
    fetchTools();
    
    // Search functionality
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    
    if (searchBtn) searchBtn.addEventListener('click', performSearch);
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    }
    
    // Handle payment redirect
    handlePaymentRedirect();
});

let allTools = [];

// 1. Fetch Tools from Backend
async function fetchTools() {
    const grid = document.getElementById('mcpGrid');
    const statusBadge = document.getElementById('statusBadge');
    const resultsCount = document.getElementById('resultsCount');

    if (!grid) return;

    try {
        const response = await fetch(`${API_BASE_URL}/tools/`);
        if (!response.ok) throw new Error("Failed to fetch tools");
        
        allTools = await response.json();
        const count = allTools.length;
        const label = count === 1 ? 'eMCP tool available' : 'eMCP tools available';
        
        if (statusBadge) {
            statusBadge.innerHTML = `<i class="fas fa-check-circle"></i> ${count} ${label}`;
        }
        if (resultsCount) {
            resultsCount.innerText = `${count} ${label}`;
        }
        
        // Check user subscriptions and render
        await renderToolsWithSubscriptions(allTools);
        
    } catch (error) {
        console.error(error);
        if (statusBadge) statusBadge.innerHTML = `<i class="fas fa-times-circle"></i> System Offline`;
        if (grid) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                <h3>Failed to load marketplace</h3>
                <p>Could not connect to the backend.</p>
            </div>`;
        }
    }
}

// Get user subscriptions
async function getUserSubscriptions() {
    const token = localStorage.getItem('accessToken');
    if (!token) return [];
    
    try {
        const response = await fetch(`${API_BASE_URL}/tools/my-subscriptions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Error fetching subscriptions:', error);
    }
    return [];
}

// Render tools with subscription status
async function renderToolsWithSubscriptions(tools) {
    const grid = document.getElementById('mcpGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (tools.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: #ccc;">
            <i class="fas fa-box-open" style="font-size: 48px; margin-bottom: 20px; color: #4cc9f0;"></i>
            <h3 style="font-size: 24px; margin-bottom: 10px;">No tools yet</h3>
            <p style="margin-bottom: 20px;">The marketplace is empty. Be the first to publish a tool!</p>
            <a href="seller_dashboard.html" class="btn btn-primary" style="text-decoration: none; display: inline-block;">
                <i class="fas fa-plus"></i> Go to Dashboard
            </a>
        </div>`;
        return;
    }
    
    // Get user's subscriptions
    const subscriptions = await getUserSubscriptions();
    const subscribedToolIds = new Set(subscriptions.map(s => s.tool_id));
    
    tools.forEach(tool => {
        const hasAccess = subscribedToolIds.has(tool.id);
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
                            <span style="font-size: 13px; color: #eee; font-weight: 500;">${typeof t === 'string' ? t : (t.name || 'Tool')}</span>
                            <span style="font-size: 11px; background: rgba(76, 201, 240, 0.2); color: #4cc9f0; padding: 2px 6px; border-radius: 4px;">
                                ${tool.cost > 0 ? '$' + tool.cost : 'Free'}
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>`;
        }
        
        // Determine action buttons
        let actionButtonsHtml = '';
        
        if (hasAccess) {
            actionButtonsHtml = `
                <div class="action-buttons">
                    <button class="btn btn-primary" style="width: 100%; justify-content: center;" 
                        onclick="usePaidTool(${tool.id}, '${tool.name.replace(/'/g, "\\'")}', '${tool.url || ''}')">
                        <i class="fas fa-play"></i> Use Tool
                    </button>
                </div>
            `;
        } else if (tool.cost > 0) {
            const weeklyPrice = (tool.cost / 4).toFixed(2);
            const yearlyPrice = (tool.cost * 10).toFixed(2);
            
            actionButtonsHtml = `
                <div style="margin-top: 15px;">
                    <div style="font-size: 12px; color: #888; margin-bottom: 8px; font-weight: 600;">
                        <i class="fas fa-credit-card"></i> SUBSCRIBE TO USE
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button onclick="subscribeToTool(${tool.id}, 'weekly', '${tool.name.replace(/'/g, "\\'")}')" 
                            style="flex: 1; padding: 8px 4px; background: rgba(108, 117, 125, 0.2); border: 1px solid rgba(108, 117, 125, 0.5); border-radius: 6px; color: #adb5bd; font-size: 11px; font-weight: 600; cursor: pointer;">
                            Weekly ($${weeklyPrice})
                        </button>
                        <button onclick="subscribeToTool(${tool.id}, 'monthly', '${tool.name.replace(/'/g, "\\'")}')" 
                            style="flex: 1; padding: 8px 4px; background: rgba(76, 201, 240, 0.15); border: 1px solid rgba(76, 201, 240, 0.4); border-radius: 6px; color: #4cc9f0; font-size: 11px; font-weight: 600; cursor: pointer;">
                            Monthly ($${tool.cost})
                        </button>
                        <button onclick="subscribeToTool(${tool.id}, 'yearly', '${tool.name.replace(/'/g, "\\'")}')" 
                            style="flex: 1; padding: 8px 4px; background: rgba(40, 167, 69, 0.15); border: 1px solid rgba(40, 167, 69, 0.4); border-radius: 6px; color: #28a745; font-size: 11px; font-weight: 600; cursor: pointer;">
                            Yearly ($${yearlyPrice})
                        </button>
                    </div>
                </div>
            `;
        } else {
            actionButtonsHtml = `
                <div class="action-buttons">
                    <button class="btn btn-primary" style="width: 100%; justify-content: center;" 
                        onclick="useTool(${tool.id}, '${tool.name.replace(/'/g, "\\'")}')">
                        <i class="fas fa-play"></i> Use Tool
                    </button>
                </div>
            `;
        }
        
        const configBtnHtml = `
            <div class="action-buttons" style="margin-top: 10px;">
                <button class="btn btn-secondary" style="width: 100%; justify-content: center;" 
                    onclick="openConfigModal('${tool.name.replace(/'/g, "\\'")}', '${tool.url || ''}', ${tool.id})">
                    <i class="fas fa-copy"></i> Copy Config
                </button>
            </div>
        `;
        
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
                    ${tool.description || 'No description available'}
                </div>
                ${tool.cost > 0 ? `<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <span style="color: #4cc9f0; font-weight: 600;">💰 Price: $${tool.cost}/month</span>
                </div>` : '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);"><span style="color: #28a745;">✨ Free Tool</span></div>'}
            </div>

            ${toolsListHtml}
            
            ${actionButtonsHtml}
            ${configBtnHtml}
            
            <div class="mcp-date" style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                <span><i class="far fa-clock"></i> ${new Date(tool.created_at).toLocaleDateString() || 'Recent'}</span>
                <span style="font-weight: bold; color: ${hasAccess ? '#28a745' : (tool.cost > 0 ? '#4cc9f0' : '#fff')};">
                    ${hasAccess ? '✓ Subscribed' : (tool.cost > 0 ? `$${tool.cost}/month` : 'Free')}
                </span>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Subscribe to a tool
async function subscribeToTool(toolId, plan, toolName) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Please login first!");
        window.location.href = '/';
        return;
    }

    alert(`Starting subscription for ${toolName} (${plan})...`);
    
    try {
        const response = await fetch(`${API_BASE_URL}/stripe/create-checkout-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ tool_id: toolId, plan: plan })
        });
        
        const data = await response.json();
        
        if (response.ok && data.checkout_url) {
            localStorage.setItem('pending_subscription_tool', toolId);
            window.location.href = data.checkout_url;
        } else {
            alert(data.detail || "Failed to create checkout session");
        }
    } catch (error) {
        console.error('Subscription error:', error);
        alert("Error starting subscription");
    }
}

// Use a paid tool
function usePaidTool(toolId, toolName, toolUrl) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Please login first!");
        window.location.href = '/';
        return;
    }
    
    if (toolUrl) {
        window.location.href = toolUrl;
    } else {
        window.location.href = `/tool/${toolName.toLowerCase().replace(/\s+/g, '-')}`;
    }
}

// Handle payment redirect
async function handlePaymentRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('payment') === 'success') {
        localStorage.removeItem('pending_subscription_tool');
        alert("✅ Payment successful! Your subscription is now active.");
        setTimeout(() => {
            window.location.href = '/marketplace';
        }, 2000);
    } else if (urlParams.get('payment') === 'cancelled') {
        localStorage.removeItem('pending_subscription_tool');
        alert("Payment was cancelled. You can try again anytime.");
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// Search functionality
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    const grid = document.getElementById('mcpGrid');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!query) {
        fetchTools();
        return;
    }
    
    if (grid) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ccc;">
            <i class="fas fa-spinner fa-spin" style="font-size: 32px; margin-bottom: 15px; color: #4cc9f0;"></i>
            <p>AI is analyzing your request...</p>
        </div>`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/search/?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Search failed");
        
        const data = await response.json();
        const results = data.results || [];
        
        if (resultsCount) {
            const label = results.length === 1 ? 'match found' : 'matches found';
            resultsCount.innerText = `${results.length} AI ${label}`;
        }
        
        await renderToolsWithSubscriptions(results);
    } catch (error) {
        console.error("Search Error:", error);
        if (grid) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff6b6b;">
                <i class="fas fa-exclamation-triangle" style="font-size: 32px; margin-bottom: 15px;"></i>
                <p>Search failed. Please try again.</p>
            </div>`;
        }
    }
}

// Open config modal (existing function)
function openConfigModal(name, url, toolId) {
    if (!url) {
        alert("No deployment URL available for this tool.");
        return;
    }

    const proxyUrl = `${window.location.origin}/api/proxy/${toolId}/sse`;
    const config = {
        "mcpServers": {
            [name.toLowerCase().replace(/\s+/g, '-')]: {
                "url": proxyUrl,
                "transport": "sse"
            }
        }
    };

    window.currentConfigText = JSON.stringify(config, null, 2);
    const codeBlock = document.getElementById('configCodeBlock');
    if(codeBlock) codeBlock.textContent = window.currentConfigText;

    const modal = document.getElementById('configModal');
    if(modal) modal.style.display = 'flex';
}

function closeConfigModal() {
    const modal = document.getElementById('configModal');
    if(modal) modal.style.display = 'none';
}

async function copyFromModal() {
    try {
        await navigator.clipboard.writeText(window.currentConfigText);
        alert("Configuration copied!");
        closeConfigModal();
    } catch (err) {
        console.error('Failed to copy:', err);
        alert("Failed to copy");
    }
}

// Use free tool
async function useTool(toolId, toolName) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Please login first!");
        return;
    }

    alert(`Running ${toolName}...`);
    
    try {
        const response = await fetch(`${API_BASE_URL}/tools/use/${toolId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`✅ Execution Result:\n\nStatus: ${data.status}\nMessage: ${data.message}\nTime: ${data.processing_time}s`);
        } else {
            throw new Error(data.detail || "Execution failed");
        }
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

// Close modal if clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('configModal');
    if (event.target === modal) {
        closeConfigModal();
    }
}