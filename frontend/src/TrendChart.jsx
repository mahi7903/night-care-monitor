import {
  CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'

const LINE_COLOURS = ['#1f4e79', '#4b6b3c', '#6a4c93']
const WARN_C = 18
const CRITICAL_C = 16

function formatTime(ms) {
  return new Date(ms).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

export default function TrendChart({ rooms, readings }) {
  const series = {}
  for (const r of readings) {
    if (!series[r.room_id]) series[r.room_id] = []
    series[r.room_id].push({ time: new Date(r.created_at).getTime(), temperature: r.temperature })
  }

  return (
    <section className="panel trend">
      <div className="panel-header">
        <h2>Temperature, last 10 minutes</h2>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#c9ced2" strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={formatTime}
          />
          <YAxis domain={[8, 24]} unit="°C" width={55} />
          <Tooltip
            labelFormatter={(ms) => new Date(ms).toLocaleTimeString('en-GB')}
            formatter={(value) => `${Number(value).toFixed(1)}°C`}
          />
          <Legend />
          <ReferenceLine y={WARN_C} stroke="#f2c200" strokeDasharray="6 4" />
          <ReferenceLine y={CRITICAL_C} stroke="#d32f2f" strokeDasharray="6 4" />
          {rooms.map((room, i) => (
            <Line
              key={room.id}
              data={series[room.id] ?? []}
              dataKey="temperature"
              name={room.name}
              stroke={LINE_COLOURS[i % LINE_COLOURS.length]}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}