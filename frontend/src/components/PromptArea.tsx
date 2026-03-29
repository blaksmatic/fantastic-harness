import { useState } from 'react'
import './PromptArea.css'

interface Props { onSend: (content: string) => Promise<void> }

export function PromptArea({ onSend }: Props) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || sending) return
    setSending(true)
    await onSend(input.trim())
    setInput('')
    setSending(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="prompt-area">
      <input className="prompt-input" type="text" value={input} onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown} placeholder="Talk to Miles... (override decisions, set goals, trigger adversaries)" disabled={sending} />
      <button className="prompt-send" onClick={handleSend} disabled={sending}>{sending ? '...' : 'Send'}</button>
    </div>
  )
}
