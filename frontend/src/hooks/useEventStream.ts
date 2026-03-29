import { useEffect, useRef } from 'react'
import type { HarnessEvent } from '../types'

export function useEventStream(onEvent: (event: HarnessEvent) => void) {
  const callbackRef = useRef(onEvent)
  callbackRef.current = onEvent
  useEffect(() => {
    const source = new EventSource('/api/events/stream')
    source.onmessage = (msg) => { callbackRef.current(JSON.parse(msg.data)) }
    source.onerror = () => { source.close() }
    return () => source.close()
  }, [])
}
