const SEVERITY_RANK = { yellow: 1, red: 2 }

export default function RoomCard({ room, readings, alarms }) {
  const latest = readings[readings.length - 1]
  const worst = alarms.reduce(
    (top, a) => (!top || SEVERITY_RANK[a.severity] > SEVERITY_RANK[top.severity] ? a : top),
    null,
  )
  const state = worst ? worst.severity : 'normal'

  return (
    <article className={`room-card state-${state}`}>
      <div className="room-header">
        <h2>{room.name}</h2>
        {worst && (
          <span className={`badge badge-${worst.severity}`}>{worst.priority.toUpperCase()}</span>
        )}
      </div>
      <div className="temp">{latest ? `${latest.temperature.toFixed(1)}°C` : '--'}</div>
      <dl className="meta">
        <div>
          <dt>Occupancy</dt>
          <dd>{latest ? (latest.occupied ? 'Occupied' : 'Empty') : '--'}</dd>
        </div>
        <div>
          <dt>Heater</dt>
          <dd>{room.heater_on ? 'ON' : 'Off'}</dd>
        </div>
      </dl>
    </article>
  )
}