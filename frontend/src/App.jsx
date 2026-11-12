import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import AlarmPanel from './AlarmPanel'
import RoomCard from './RoomCard'
import TrendChart from './TrendChart'

const POLL_MS = 2000

export default function App() {
  const [rooms, setRooms] = useState([])
  const [readings, setReadings] = useState([])
  const [alarms, setAlarms] = useState([])
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const [roomData, readingData, alarmData] = await Promise.all([
        api.rooms(),
        api.readings(10),
        api.alarms(false),
      ])
      setRooms(roomData)
      setReadings(readingData)
      setAlarms(alarmData)
      setError(null)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, POLL_MS)
    return () => clearInterval(timer)
  }, [refresh])

  async function runAction(action) {
    try {
      await action()
      await refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  const activeAlarms = alarms.filter((a) => a.cleared_at === null)

  return (
    <div className="app">
      <header className="topbar">
        <h1>Night Care Room Monitor</h1>
        <span className={error ? 'status error' : 'status'}>
          {error
            ? `Connection lost: ${error}`
            : lastUpdated
              ? `Updated ${lastUpdated.toLocaleTimeString('en-GB')}`
              : 'Connecting...'}
        </span>
      </header>
      <main>
        <section className="rooms">
          {rooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              readings={readings.filter((r) => r.room_id === room.id)}
              alarms={activeAlarms.filter((a) => a.room_id === room.id)}
              onAction={runAction}
            />
          ))}
        </section>
        <section className="lower">
          <TrendChart rooms={rooms} readings={readings} />
          <AlarmPanel
            alarms={alarms}
            onAcknowledge={(id) => runAction(() => api.acknowledge(id))}
          />
        </section>
      </main>
    </div>
  )
}