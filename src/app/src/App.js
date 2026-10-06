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
      <div className="card">
        <h1 className="title">My TODOs</h1>
        {error && <p role="alert" className="error">{error}</p>}
        <form className="todo-form" onSubmit={handleSubmit}>
          <input
            id="todo"
            type="text"
            aria-label="New ToDo"
            placeholder="What needs to be done?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={200}
          />
          <button disabled={submitting || !description.trim()}>Add ToDo!</button>
        </form>

        <h2 className="section-title">List of TODOs</h2>
        {todos.length === 0 ? (
          <p className="empty">No TODOs yet. Add one above!</p>
        ) : (
          <ul className="todo-list">
            {todos.map((todo) => (
              <li key={todo.id} className="todo-item">{todo.description}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
