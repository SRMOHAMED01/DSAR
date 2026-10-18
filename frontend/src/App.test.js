import { render, screen } from '@testing-library/react';
import App from './App';

test('renders DSAR header', () => {
  render(<App />);
  const headerElement = screen.getByText(/DSAR Management System/i);
  expect(headerElement).toBeInTheDocument();
});
