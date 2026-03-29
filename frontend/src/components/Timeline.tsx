import type { HarnessEvent } from '../types'
import './Timeline.css'

const TYPE_COLORS: Record<string, string> = {
  decision: '#8b5cf6', feedback: '#f59e0b', task: '#22d3ee', scouting: '#3b82f6',
  audit: '#ec4899', promotion: '#ef4444', retirement: '#ef4444', human_input: '#22c55e',
}

interface Props { events: HarnessEvent[] }

export function Timeline({ events }: Props) {
  return (
    <div className="timeline">
      <div className="panel-title">Timeline</div>
      <div className="timeline-events">
        {events.map(event => (
          <div key={event.id} className="timeline-event">
            <div className="event-dot" style={{ background: TYPE_COLORS[event.type] ?? '#94a3b8' }} />
            <div className="event-body">
              <div className="event-meta">{formatTime(event.created_at)} &middot; {event.agent_id}</div>
              <span className="event-type" style={{
                background: (TYPE_COLORS[event.type] ?? '#94a3b8') + '20',
                color: TYPE_COLORS[event.type] ?? '#94a3b8',
              }}>{event.type.replace('_', ' ').toUpperCase()}</span>
              <div className="event-content">{event.content}</div>
            </div>
          </div>
        ))}
        {events.length === 0 && <div className="timeline-empty">No events yet. Start the harness to begin.</div>}
      </div>
    </div>
  )
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const diffMin = Math.floor((now.getTime() - d.getTime()) / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  return `${Math.floor(diffMin / 60)}h ago`
}
