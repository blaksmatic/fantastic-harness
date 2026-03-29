export interface Goal {
  id: string;
  description: string;
  status: string;
  source: string;
  created_at: string;
  closed_at: string | null;
  closed_by: string | null;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  layer: string;
  model: string;
  status: string;
  config: Record<string, unknown>;
  created_at: string;
  retired_at: string | null;
}

export interface HarnessEvent {
  id: number;
  agent_id: string;
  type: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface JournalEntry {
  id: number;
  miles_id: string;
  type: string;
  content: string;
  context: string | null;
  goal_id: string | null;
  created_at: string;
}

export interface SuccessionRecord {
  id: number;
  retired_id: string;
  promoted_id: string;
  new_shadow_id: string;
  compaction: string | null;
  journal_start: number | null;
  created_at: string;
}
