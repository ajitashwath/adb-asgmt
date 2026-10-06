import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import * as api from './api';

jest.mock('./api');

test('lists todos from the API', async () => {
  api.fetchTodos.mockResolvedValue([{ id: '1', description: 'Learn React' }]);
  render(<App />);
  expect(await screen.findByText('Learn React')).toBeInTheDocument();
});

test('creates a todo and refreshes the list', async () => {
  api.fetchTodos
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([{ id: '2', description: 'Write tests' }]);
  api.createTodo.mockResolvedValue({ id: '2', description: 'Write tests' });

  render(<App />);
  userEvent.type(await screen.findByLabelText(/todo:/i), 'Write tests');
  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByText('Write tests')).toBeInTheDocument();
  expect(api.createTodo).toHaveBeenCalledWith('Write tests');
  await waitFor(() => expect(screen.getByLabelText(/todo:/i)).toHaveValue(''));
});

test('shows an error when loading fails', async () => {
  api.fetchTodos.mockRejectedValue(new Error('Database unavailable.'));
  render(<App />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Database unavailable.');
});
