import { useEffect, useState } from 'react'
import { api } from './api'
import type { Agent, Goal, HarnessEvent, SuccessionRecord } from './types'
import { AgentPanel } from './components/AgentPanel'
import { Timeline } from './components/Timeline'
import { GoalPanel } from './components/GoalPanel'
import { PromptArea } from './components/PromptArea'

export default function App() {
  const [events, setEvents] = useState<HarnessEvent[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [goals, setGoals] = useState<Goal[]>([])
  const [succession, setSuccession] = useState<SuccessionRecord[]>([])

  const refresh = async () => {
    const [e, a, g, s] = await Promise.all([
      api.getEvents(), api.getAgents(), api.getGoals(), api.getSuccession(),
    ])
    setEvents(e); setAgents(a); setGoals(g); setSuccession(s)
  }

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSendInput = async (content: string) => {
    await api.sendInput(content)
    await refresh()
  }

  return (
    <div className="harness">
      <header className="harness-header"><h1>Fantastic Harness</h1></header>
      <div className="harness-body">
        <AgentPanel agents={agents} />
        <Timeline events={events} />
        <GoalPanel goals={goals} succession={succession} />
      </div>
      <PromptArea onSend={handleSendInput} />
    </div>
  )
}
