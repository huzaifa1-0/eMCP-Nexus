 function addEnvVar() {
            const envVarsContainer = document.getElementById('envVarsContainer');
            const newEnvVar = document.createElement('div');
            newEnvVar.className = 'env-var-item';
            newEnvVar.innerHTML = `
                <input type="text" class="form-control env-var-input" placeholder="KEY">
                <input type="text" class="form-control env-var-input" placeholder="VALUE">
                <button type="button" class="btn btn-danger" onclick="removeEnvVar(this)">
                    <i class="fas fa-times"></i>
                </button>
            `;
            envVarsContainer.appendChild(newEnvVar);
        }
        
        // Function to remove environment variable field
        function removeEnvVar(button) {
            const envVarItem = button.parentElement;
            // Only remove if there's more than one field
            if (document.querySelectorAll('.env-var-item').length > 1) {
                envVarItem.remove();
            } else {
                showAlert('You need at least one environment variable field.', 'error');
            }
        }
        
        // Function to show alert message
        function showAlert(message, type) {
            const alertBox = document.getElementById('alertBox');
            alertBox.className = `alert ${type === 'error' ? 'alert-error' : ''}`;
            alertBox.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle"></i>
                ${message}
            `;
            alertBox.style.display = 'flex';
            
            // Hide alert after 5 seconds
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 5000);
        }
        
        // Handle form submission
        document.getElementById('emcpForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const serviceName = document.getElementById('serviceName').value;
            const serviceDescription = document.getElementById('serviceDescription').value;
            const repoUrl = document.getElementById('repoUrl').value;
            const branch = document.getElementById('branch').value;
            const buildCommand = document.getElementById('buildCommand').value;
            const startCommand = document.getElementById('startCommand').value;
            const rootDir = document.getElementById('rootDir').value;

            const authToken = localStorage.getItem('accessToken'); 
            
            
            if (!serviceName || !repoUrl) {
                showAlert('Please fill in all required fields.', 'error');
                return;
            }

            // --- NEW: Collect Environment Variables ---
            const envVars = {};
            document.querySelectorAll('.env-var-item').forEach(item => {
                const inputs = item.querySelectorAll('input');
                const key = inputs[0].value.trim();
                const value = inputs[1].value.trim();
                
                if (key && value) {
                    envVars[key] = value;
                }
            });
            
            try {
            const response = await fetch('/api/tools/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: serviceName,
                    description: serviceDescription,
                    cost: 0.0, // You can add a cost field
                    repo_url: repoUrl,
                    branch: branch,
                    build_command: buildCommand,
                    start_command: startCommand,
                    root_dir: rootDir,
                    env_vars: envVars
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create eMCP service.');
            }

            showAlert('eMCP service deployed successfully!', 'success');
            // Optionally, redirect to the marketplace page
            // window.location.href = '/marketplace.html';

        } catch (error) {
            showAlert(error.message, 'error');
        }
            // Reset form after successful submission simulation
            setTimeout(() => {
                this.reset();
                // Clear all but one environment variable field
                const envVars = document.querySelectorAll('.env-var-item');
                for (let i = 1; i < envVars.length; i++) {
                    envVars[i].remove();
                }
            }, 3000);
        });
        
        // Add event listener to cancel button
        document.querySelector('.btn-secondary').addEventListener('click', function() {
            if (confirm('Are you sure you want to cancel? All changes will be lost.')) {
                document.getElementById('emcpForm').reset();
                // Clear all but one environment variable field
                const envVars = document.querySelectorAll('.env-var-item');
                for (let i = 1; i < envVars.length; i++) {
                    envVars[i].remove();
                }
                showAlert('Form has been reset.', 'success');
            }
        });