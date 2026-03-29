import type { Agent } from '../types'
import './AgentPanel.css'

const STATUS_COLORS: Record<string, string> = { active: '#22c55e', idle: '#94a3b8', retired: '#64748b' }
const STATUS_LABELS: Record<string, string> = { active: 'ACTIVE', idle: 'IDLE', retired: 'RETIRED' }

interface Props { agents: Agent[] }

export function AgentPanel({ agents }: Props) {
  const active = agents.filter(a => a.status !== 'retired')
  return (
    <div className="agent-panel">
      <div className="panel-title">Agents</div>
      {active.map(agent => (
        <div key={agent.id} className={`agent-card agent-card--${agent.layer}`}>
          <div className="agent-card-header">
            <span className="agent-name">{agent.name}</span>
            <span className="agent-status" style={{ background: STATUS_COLORS[agent.status] ?? '#94a3b8' }}>
              {STATUS_LABELS[agent.status] ?? agent.status.toUpperCase()}
            </span>
          </div>
          <div className="agent-meta">{agent.layer} &middot; {agent.model.split('-').slice(0, 2).join(' ')}</div>
        </div>
      ))}
    </div>
  )
}
