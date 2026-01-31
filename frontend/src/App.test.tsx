import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('react-select/async');

test('renders search functionality', () => {
  render(<App />);
  expect(screen.getByText(/Start \(person or movie\):/i)).toBeInTheDocument();
  expect(screen.getByText(/End \(person or movie\):/i)).toBeInTheDocument();
  expect(screen.getByText(/Find Connection/i)).toBeInTheDocument();
});
