import type { Goal, SuccessionRecord } from '../types'
import './GoalPanel.css'

interface Props { goals: Goal[]; succession: SuccessionRecord[] }

export function GoalPanel({ goals, succession }: Props) {
  return (
    <div className="goal-panel">
      <div className="panel-title">Goals</div>
      {goals.map(goal => (
        <div key={goal.id} className={`goal-card goal-card--${goal.status}`}>
          <div className="goal-header">
            <span className="goal-name">#{goal.id}</span>
            <span className={`goal-status goal-status--${goal.status}`}>{goal.status.toUpperCase()}</span>
          </div>
          <div className="goal-desc">{goal.description}</div>
        </div>
      ))}
      {goals.length === 0 && <div className="goal-empty">No goals yet</div>}
      <div className="panel-title" style={{ marginTop: 20 }}>Succession</div>
      {succession.map(s => (
        <div key={s.id} className="succession-entry">
          <span className="succession-retired">{s.retired_id}</span>
          <span className="succession-arrow">&rarr;</span>
          <span className="succession-promoted">{s.promoted_id}</span>
        </div>
      ))}
    </div>
  )
}
