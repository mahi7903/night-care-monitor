import { useEffect, useState } from 'react'
import { api } from './api'
import RoomCard from './RoomCard'

const POLL_MS = 2000

export default function App() {
  const [rooms, setRooms] = useState([])
  const [readings, setReadings] = useState([])
  const [alarms, setAlarms] = useState([])
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [roomData, readingData, alarmData] = await Promise.all([
          api.rooms(),
          api.readings(10),
          api.alarms(true),
        ])
        if (cancelled) return
        setRooms(roomData)
        setReadings(readingData)
        setAlarms(alarmData)
        setError(null)
        setLastUpdated(new Date())
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }

    load()
    const timer = setInterval(load, POLL_MS)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

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
              alarms={alarms.filter((a) => a.room_id === room.id)}
            />
          ))}
        </section>
      </main>
    </div>
  )
}