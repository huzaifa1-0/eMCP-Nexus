const API_BASE_URL = '/api';

    document.addEventListener('DOMContentLoaded', function() {
        // 1. Set default date range (Visual only for now)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);
        
        document.getElementById('startDate').valueAsDate = startDate;
        document.getElementById('endDate').valueAsDate = endDate;
        
        // 2. Load REAL data immediately when page opens
        fetchDashboardData();

        const headerBtn = document.getElementById('headerCreateBtn');
    if (headerBtn) {
        headerBtn.addEventListener('click', function() {
            window.location.href = 'newmcp.html';
        });
    }

        // 3. Setup Buttons
        document.getElementById('applyFilter').addEventListener('click', function() {
            // For now, just reload current data (Filtering logic comes later)
            fetchDashboardData(); 
            showAlert('Refreshed data from database', 'success');
        });
    });

    // --- NEW FUNCTION: Fetches Real Data from Your Backend ---
    async function fetchDashboardData() {
        const token = localStorage.getItem('accessToken');
        
        // Security Check: Are we logged in?
        if (!token) {
            showAlert("Please log in to view your dashboard", "error");
            setTimeout(() => window.location.href = 'index.html', 2000);
            return;
        }

        // Show "Loading spinners" while we wait for the server
        const metrics = ['totalInstalls', 'totalRuns', 'tokensUsed', 'totalRevenue'];
        metrics.forEach(id => {
            document.getElementById(id).innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        });

        try {
            // The actual API Call to the file you created (routers/dashboard.py)
            const response = await fetch(`${API_BASE_URL}/seller_dashboard/stats`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`, // Send the token so server knows who we are
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error("Failed to load stats");

            const data = await response.json();

            // Update HTML with REAL numbers from database
            document.getElementById('totalInstalls').textContent = data.totalInstalls;
            document.getElementById('totalRuns').textContent = data.totalRuns;
            document.getElementById('tokensUsed').textContent = (data.tokensUsed || 0).toLocaleString();
            document.getElementById('totalRevenue').textContent = '$' + (data.totalRevenue || 0).toFixed(2);

            // Update the Table with REAL tool list
            renderTable(data.performanceData);
            
            // If user has tools, hide the "No Data" message
            if (data.totalInstalls > 0) {
                const noDataMsg = document.querySelector('.no-data');
                if(noDataMsg) noDataMsg.style.display = 'none';
            }

        } catch (error) {
            console.error(error);
            showAlert("Could not load dashboard data. Is the server running?", "error");
            // Reset spinners to 0 on error
            metrics.forEach(id => document.getElementById(id).textContent = "0");
        }
    }

    // Helper to build the table rows
    function renderTable(items) {
        const tbody = document.getElementById('metricsTableBody');
        tbody.innerHTML = ''; // Clear existing rows

        if (!items || items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="no-data">
                            <i class="fas fa-inbox"></i>
                            <div class="no-data-title">No metrics data available</div>
                        </div>
                    </td>
                </tr>`;
            return;
        }

        items.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${item.name}</strong></td>
                <td>${item.installs}</td>
                <td>${item.runs}</td>
                <td>${item.tokens.toLocaleString()}</td>
                <td style="color: #4cc9f0;">$${item.revenue.toFixed(2)}</td>
                <td>${item.date}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Function to show alert message (Kept same as before)
    function showAlert(message, type) {
        const existingAlert = document.querySelector('.alert-popup');
        if (existingAlert) existingAlert.remove();

        const alert = document.createElement('div');
        alert.className = `alert alert-popup ${type === 'error' ? 'alert-error' : 'alert-success'}`;
        alert.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle"></i> ${message}`;
        
        // Add styling for fixed popup if not already in CSS
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        
        document.body.appendChild(alert);
        
        setTimeout(() => alert.remove(), 3000);
    }