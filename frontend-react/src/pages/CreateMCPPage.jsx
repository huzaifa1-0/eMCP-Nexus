import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AlertToast, { showToast } from '../components/AlertToast';
import { API_BASE_URL } from '../api/config';
import { useAuth } from '../hooks/useAuth';

export default function CreateMCPPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    serviceName: '',
    serviceDescription: '',
    repoUrl: '',
    branch: 'main',
    rootDir: '',
    buildCommand: 'pip install -r requirements.txt',
    startCommand: 'python main.py',
    dataSource: 'Select a data source',
  });

  const [envVars, setEnvVars] = useState([{ key: '', value: '' }]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const addEnvVar = () => setEnvVars([...envVars, { key: '', value: '' }]);

  const removeEnvVar = (index) => {
    if (envVars.length <= 1) {
      showToast('You need at least one environment variable field.', 'error');
      return;
    }
    setEnvVars(envVars.filter((_, i) => i !== index));
  };

  const updateEnvVar = (index, field, value) => {
    const updated = [...envVars];
    updated[index][field] = value;
    setEnvVars(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.serviceName || !formData.repoUrl) {
      showToast('Please fill in all required fields.', 'error');
      return;
    }

    const envVarsObj = {};
    envVars.forEach(({ key, value }) => {
      if (key.trim() && value.trim()) envVarsObj[key.trim()] = value.trim();
    });

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/tools/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: formData.serviceName,
          description: formData.serviceDescription,
          cost: 0.0,
          repo_url: formData.repoUrl,
          branch: formData.branch,
          build_command: formData.buildCommand,
          start_command: formData.startCommand,
          root_dir: formData.rootDir,
          env_vars: envVarsObj,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create eMCP service.');
      }

      showToast('eMCP service deployed successfully!', 'success');
      setTimeout(() => navigate('/marketplace'), 2000);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (confirm('Are you sure you want to cancel? All changes will be lost.')) {
      navigate('/dashboard');
    }
  };

  return (
    <>
      <Navbar />
      <AlertToast />

      <div className="page-container" style={{ maxWidth: '800px', padding: '20px' }}>
        <header style={{ textAlign: 'center', padding: '30px 0' }}>
          <div className="page-title" style={{ justifyContent: 'center', fontSize: '28px' }}>
            <i className="fas fa-plus-circle"></i> Create New eMCP
          </div>
          <p className="page-subtitle">
            Deploy your Model Context Protocol service with GitHub Integration
          </p>
        </header>

        <div className="divider"></div>

        <form onSubmit={handleSubmit}>
          <div className="card">
            <h2 className="card-title">
              <i className="fas fa-cog"></i> Service Configuration
            </h2>

            <div className="form-group">
              <label htmlFor="serviceName">Service Name</label>
              <input type="text" className="form-control" name="serviceName" value={formData.serviceName}
                onChange={handleChange} required />
              <div className="description">A unique name for your eMCP service</div>
            </div>

            <div className="form-group">
              <label htmlFor="serviceDescription">Description</label>
              <textarea className="form-control" name="serviceDescription" rows="3"
                value={formData.serviceDescription} onChange={handleChange} required
                placeholder="Describe what your tool does (e.g., 'A generic PDF parser...')" />
              <div className="description">Detailed description for the AI search engine and RAG chatbot.</div>
            </div>

            <div className="form-group">
              <label htmlFor="repoUrl">GitHub Repository URL</label>
              <input type="url" className="form-control" name="repoUrl"
                placeholder="https://github.com/username/repo"
                value={formData.repoUrl} onChange={handleChange} required />
              <div className="description">The GitHub repository containing your eMCP service</div>
            </div>

            <div className="form-group">
              <label htmlFor="branch">Branch</label>
              <div className="select-wrapper">
                <select className="form-control" name="branch" value={formData.branch} onChange={handleChange}>
                  <option>main</option>
                  <option>develop</option>
                  <option>staging</option>
                  <option>production</option>
                </select>
              </div>
              <div className="description">The Git branch to deploy from</div>
            </div>

            <div className="form-group">
              <label htmlFor="rootDir">Root Directory (Optional)</label>
              <input type="text" className="form-control" name="rootDir" placeholder="./"
                value={formData.rootDir} onChange={handleChange} />
              <div className="description">Directory where your app is located (leave empty for root)</div>
            </div>

            <div className="form-group">
              <label htmlFor="buildCommand">Build Command</label>
              <input type="text" className="form-control" name="buildCommand"
                value={formData.buildCommand} onChange={handleChange} />
              <div className="description">Command to build your application</div>
            </div>

            <div className="form-group">
              <label htmlFor="startCommand">Start Command</label>
              <input type="text" className="form-control" name="startCommand"
                value={formData.startCommand} onChange={handleChange} />
              <div className="description">Command to start your application</div>
            </div>

            <div className="form-group">
              <label>Environment Variables</label>
              {envVars.map((env, i) => (
                <div className="env-var-item" key={i}>
                  <input type="text" className="form-control" placeholder="KEY"
                    value={env.key} onChange={(e) => updateEnvVar(i, 'key', e.target.value)} />
                  <input type="text" className="form-control" placeholder="VALUE"
                    value={env.value} onChange={(e) => updateEnvVar(i, 'value', e.target.value)} />
                  <button type="button" className="btn btn-danger" onClick={() => removeEnvVar(i)}>
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              ))}
              <button type="button" className="btn btn-secondary" onClick={addEnvVar}>
                <i className="fas fa-plus"></i> Add Variable
              </button>
            </div>

            <div className="form-group">
              <label>Runtime</label>
              <div className="runtime-badge">
                <i className="fas fa-check-circle"></i> Python 3
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">
              <i className="fas fa-database"></i> Data Source
            </h2>
            <div className="form-group">
              <label htmlFor="dataSource">Data Source</label>
              <div className="select-wrapper">
                <select className="form-control" name="dataSource" value={formData.dataSource} onChange={handleChange}>
                  <option>Select a data source</option>
                  <option>YouTube API</option>
                  <option>GitHub API</option>
                  <option>Twitter API</option>
                  <option>Custom API</option>
                </select>
              </div>
            </div>
          </div>

          <div className="actions">
            <button type="button" className="btn btn-secondary" onClick={handleCancel}>
              <i className="fas fa-times"></i> Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              <i className="fas fa-rocket"></i> {loading ? 'Deploying...' : 'Deploy eMCP Service'}
            </button>
          </div>
        </form>
      </div>

      <Footer />
    </>
  );
}
