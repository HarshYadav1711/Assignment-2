-- Production-grade schema for conversational AI session management
-- Designed for high write throughput and chronological event retrieval

-- Sessions table: Core session metadata
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    final_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session events table: Chronological event log
-- Optimized for append-heavy workloads and time-series queries
CREATE TABLE IF NOT EXISTS session_events (
    event_id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    -- event_type values: user_message, ai_token, tool_call, tool_result, system_event
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_timestamp ON session_events(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE session_events ENABLE ROW LEVEL SECURITY;

