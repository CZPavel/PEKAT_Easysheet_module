import type { DemoState } from './types';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API ${path} selhalo: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const api = {
  getDemoState: () => request<DemoState>('/api/demo/state'),
  tickDemo: () => request<DemoState>('/api/demo/tick', { method: 'POST' }),
  resetDemo: () => request<DemoState>('/api/demo/reset', { method: 'POST' }),
};
