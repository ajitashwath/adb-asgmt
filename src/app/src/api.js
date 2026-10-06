const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  return body;
}

export const fetchTodos = () => request('/todos');

export const createTodo = (description) =>
  request('/todos', { method: 'POST', body: JSON.stringify({ description }) });
