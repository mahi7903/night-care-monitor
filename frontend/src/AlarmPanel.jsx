import { useState } from 'react'

const SEVERITY_RANK = { yellow: 1, red: 2 }
const PRIORITY_RANK = { low: 0, normal: 1, urgent: 2 }

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('en-GB')
}

export default function AlarmPanel({ alarms, onAcknowledge }) {
  const [view, setView] = useState('active')

  const active = alarms
    .filter((a) => a.cleared_at === null)
    .sort(
      (a, b) =>
        SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity] ||
        PRIORITY_RANK[b.priority] - PRIORITY_RANK[a.priority] ||
        new Date(b.raised_at) - new Date(a.raised_at),
    )
  const shown = view === 'active' ? active : alarms

  return (
    <section className="panel alarms">
      <div className="panel-header">
        <h2>Alarms</h2>
        <div className="tabs">
          <button
            className={view === 'active' ? 'tab selected' : 'tab'}
            onClick={() => setView('active')}
          >
            Active ({active.length})
          </button>
          <button
            className={view === 'history' ? 'tab selected' : 'tab'}
            onClick={() => setView('history')}
          >
            History
          </button>
        </div>
      </div>
      {shown.length === 0 && (
        <p className="empty">{view === 'active' ? 'No active alarms' : 'No alarms recorded'}</p>
      )}
      <ul className="alarm-list">
        {shown.map((a) => (
          <li key={a.id} className={`alarm alarm-${a.severity}${a.cleared_at ? ' cleared' : ''}`}>
            <div className="alarm-main">
              <span
                className={`badge badge-${a.severity}${!a.acknowledged_at && !a.cleared_at ? ' unacked' : ''}`}
              >
                {a.priority.toUpperCase()}
              </span>
              <span className="alarm-msg">{a.message}</span>
            </div>
            <div className="alarm-meta">
              Raised {formatTime(a.raised_at)}
              {a.acknowledged_at && ` · Acknowledged ${formatTime(a.acknowledged_at)}`}
              {a.cleared_at && ` · Cleared ${formatTime(a.cleared_at)}`}
            </div>
            {!a.acknowledged_at && !a.cleared_at && (
              <button className="ack" onClick={() => onAcknowledge(a.id)}>
                Acknowledge
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}