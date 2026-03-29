import type { Agent, Goal, HarnessEvent, JournalEntry, SuccessionRecord } from './types';

const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getGoals: () => fetchJSON<Goal[]>('/goals'),
  createGoal: (id: string, description: string) =>
    fetchJSON<Goal>('/goals', { method: 'POST', body: JSON.stringify({ id, description, source: 'human' }) }),
  closeGoal: (id: string) =>
    fetchJSON<Goal>(`/goals/${id}`, { method: 'PATCH', body: JSON.stringify({ status: 'completed' }) }),
  getAgents: () => fetchJSON<Agent[]>('/agents'),
  getEvents: (limit = 50) => fetchJSON<HarnessEvent[]>(`/events?limit=${limit}`),
  sendInput: (content: string) =>
    fetchJSON<{ event_id: number }>('/input', { method: 'POST', body: JSON.stringify({ content }) }),
  triggerAdversary: (name: string) =>
    fetchJSON<{ status: string }>('/adversaries/trigger', { method: 'POST', body: JSON.stringify({ name }) }),
  getJournal: () => fetchJSON<JournalEntry[]>('/journal'),
  getSuccession: () => fetchJSON<SuccessionRecord[]>('/succession'),
};
