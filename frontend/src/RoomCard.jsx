import { api } from './api'

const SEVERITY_RANK = { yellow: 1, red: 2 }

export default function RoomCard({ room, readings, alarms, onAction }) {
  const latest = readings[readings.length - 1]
  const worst = alarms.reduce(
    (top, a) => (!top || SEVERITY_RANK[a.severity] > SEVERITY_RANK[top.severity] ? a : top),
    null,
  )
  const state = worst ? worst.severity : 'normal'
  const unacked = worst && !worst.acknowledged_at

  return (
    <article className={`room-card state-${state}`}>
      <div className="room-header">
        <h2>{room.name}</h2>
        {worst && (
          <span className={`badge badge-${worst.severity}${unacked ? ' unacked' : ''}`}>
            {worst.priority.toUpperCase()}
          </span>
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
      <div className="actions">
        <button onClick={() => onAction(() => api.setHeater(room.id, !room.heater_on))}>
          {room.heater_on ? 'Heater OFF' : 'Heater ON'}
        </button>
      </div>
      <details className="demo">
        <summary>Demo controls</summary>
        <label>
          <input
            type="checkbox"
            checked={room.cold_fault}
            onChange={(e) => onAction(() => api.simulate(room.id, { cold_fault: e.target.checked }))}
          />
          Simulate fault (cold draught)
        </label>
        <label>
          <input
            type="checkbox"
            checked={room.heater_failed}
            onChange={(e) => onAction(() => api.simulate(room.id, { heater_failed: e.target.checked }))}
          />
          Simulate heater failure
        </label>
      </details>
    </article>
  )
}