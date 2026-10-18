import React, { useState, useEffect } from 'react';
import { dsarApi } from './services/api';
import DsarButton from './components/DsarButton';
import './App.css';

function App() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    requester_name: '',
    requester_email: '',
    request_type: 'access',
    identifier: '',
    identifier_type: 'email',
  });
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await dsarApi.listRequests();
      setRequests(response.data);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await dsarApi.createRequest(formData);
      setMessage({ type: 'success', text: 'DSAR request submitted successfully!' });
      setFormData({
        requester_name: '',
        requester_email: '',
        request_type: 'access',
        identifier: '',
        identifier_type: 'email',
      });
      fetchRequests();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to submit request' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleProcess = async (id) => {
    try {
      setLoading(true);
      await dsarApi.processRequest(id);
      setMessage({ type: 'success', text: 'Request processed successfully!' });
      fetchRequests();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to process request' });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (id, format) => {
    try {
      const response = await dsarApi.downloadExport(id, format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dsar_${id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to download export' });
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: '#fbbf24',
      processing: '#60a5fa',
      completed: '#4ade80',
      rejected: '#f87171',
    };
    return (
      <span
        style={{
          backgroundColor: statusColors[status],
          color: '#1e293b',
          padding: '4px 12px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: '600',
          textTransform: 'capitalize',
        }}
      >
        {status}
      </span>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>DSAR Management System</h1>
        <p>Data Subject Access Request Portal</p>
      </header>

      <div className="container">
        {message && (
          <div className={`message message--${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="content-grid">
          <section className="form-section">
            <h2>Submit DSAR Request</h2>
            <form onSubmit={handleSubmit} className="dsar-form">
              <div className="form-group">
                <label htmlFor="requester_name">Full Name</label>
                <input
                  type="text"
                  id="requester_name"
                  name="requester_name"
                  value={formData.requester_name}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="requester_email">Email Address</label>
                <input
                  type="email"
                  id="requester_email"
                  name="requester_email"
                  value={formData.requester_email}
                  onChange={handleInputChange}
                  required
                  placeholder="your.email@example.com"
                />
              </div>

              <div className="form-group">
                <label htmlFor="request_type">Request Type</label>
                <select
                  id="request_type"
                  name="request_type"
                  value={formData.request_type}
                  onChange={handleInputChange}
                >
                  <option value="access">Access Request</option>
                  <option value="deletion">Deletion Request</option>
                  <option value="rectification">Rectification Request</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="identifier">Identifier</label>
                <input
                  type="text"
                  id="identifier"
                  name="identifier"
                  value={formData.identifier}
                  onChange={handleInputChange}
                  required
                  placeholder="Email, customer ID, or name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="identifier_type">Identifier Type</label>
                <select
                  id="identifier_type"
                  name="identifier_type"
                  value={formData.identifier_type}
                  onChange={handleInputChange}
                >
                  <option value="email">Email</option>
                  <option value="customer_id">Customer ID</option>
                  <option value="name">Name</option>
                </select>
              </div>

              <DsarButton type="submit" variant="primary" size="large" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Request'}
              </DsarButton>
            </form>
          </section>

          <section className="requests-section">
            <h2>DSAR Requests</h2>
            <div className="requests-list">
              {requests.length === 0 ? (
                <p className="no-requests">No requests submitted yet.</p>
              ) : (
                requests.map((req) => (
                  <div key={req.id} className="request-card">
                    <div className="request-header">
                      <h3>{req.requester_name}</h3>
                      {getStatusBadge(req.status)}
                    </div>
                    <div className="request-details">
                      <p><strong>Email:</strong> {req.requester_email}</p>
                      <p><strong>Type:</strong> {req.request_type}</p>
                      <p><strong>Identifier:</strong> {req.identifier} ({req.identifier_type})</p>
                      <p><strong>Submitted:</strong> {new Date(req.created_at).toLocaleString()}</p>
                      {req.processed_at && (
                        <p><strong>Processed:</strong> {new Date(req.processed_at).toLocaleString()}</p>
                      )}
                    </div>
                    <div className="request-actions">
                      {req.status === 'pending' && (
                        <DsarButton
                          variant="success"
                          size="small"
                          onClick={() => handleProcess(req.id)}
                          disabled={loading}
                        >
                          Process
                        </DsarButton>
                      )}
                      {req.status === 'completed' && (
                        <>
                          <DsarButton
                            variant="secondary"
                            size="small"
                            onClick={() => handleDownload(req.id, 'json')}
                          >
                            JSON
                          </DsarButton>
                          <DsarButton
                            variant="secondary"
                            size="small"
                            onClick={() => handleDownload(req.id, 'csv')}
                          >
                            CSV
                          </DsarButton>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
