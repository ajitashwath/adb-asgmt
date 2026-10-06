import { useCallback, useEffect, useState } from 'react';
import './App.css';
import { createTodo, fetchTodos } from './api';

export function App() {
  const [todos, setTodos] = useState([]);
  const [description, setDescription] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadTodos = useCallback(async () => {
    try {
      setTodos(await fetchTodos());
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!description.trim()) return;

    setSubmitting(true);
    try {
      await createTodo(description);
      setDescription('');
      await loadTodos();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="App">
      <div>
        <h1>List of TODOs</h1>
        {todos.length === 0 && <p>No TODOs yet.</p>}
        <ul>
          {todos.map((todo) => (
            <li key={todo.id}>{todo.description}</li>
          ))}
        </ul>
      </div>
      <div>
        <h1>Create a ToDo</h1>
        {error && <p role="alert" style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="todo">ToDo: </label>
            <input
              id="todo"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={200}
            />
          </div>
          <div style={{ marginTop: '5px' }}>
            <button disabled={submitting || !description.trim()}>Add ToDo!</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
