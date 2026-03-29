SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    source TEXT NOT NULL DEFAULT 'human',
    created_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    closed_by TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    layer TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idle',
    config JSON DEFAULT '{}',
    created_at TIMESTAMP NOT NULL,
    retired_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY,
    miles_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    goal_id TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (miles_id) REFERENCES agents(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    goal_id TEXT,
    assigned_to TEXT,
    validator TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    summary TEXT,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id),
    FOREIGN KEY (assigned_to) REFERENCES agents(id),
    FOREIGN KEY (validator) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    author TEXT NOT NULL,
    type TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    external_validator_summary TEXT,
    miles_response TEXT,
    goal_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS audits (
    id TEXT PRIMARY KEY,
    auditor_id TEXT NOT NULL,
    miles_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    findings TEXT,
    miles_response TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (auditor_id) REFERENCES agents(id),
    FOREIGN KEY (miles_id) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS scouting (
    id TEXT PRIMARY KEY,
    hunter_id TEXT NOT NULL,
    source TEXT NOT NULL,
    topic TEXT NOT NULL,
    raw_findings TEXT,
    summary TEXT,
    validator TEXT,
    goal_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (hunter_id) REFERENCES agents(id),
    FOREIGN KEY (validator) REFERENCES agents(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    agent_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS succession (
    id INTEGER PRIMARY KEY,
    retired_id TEXT NOT NULL,
    promoted_id TEXT NOT NULL,
    new_shadow_id TEXT NOT NULL,
    compaction TEXT,
    journal_start INTEGER,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (retired_id) REFERENCES agents(id),
    FOREIGN KEY (promoted_id) REFERENCES agents(id),
    FOREIGN KEY (new_shadow_id) REFERENCES agents(id)
);
"""
