import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function formatHour(isoHour) {
  return new Date(isoHour).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

function formatCurrency(value) {
  return `$${parseFloat(value).toLocaleString('en-GB', { minimumFractionDigits: 0 })}`
}

export default function HourlySalesChart({ data = [] }) {
  if (data.length === 0) {
    return <p className="text-zinc-400 text-sm py-2">No hourly data yet</p>
  }

  const chartData = data.map((d) => ({
    hour: formatHour(d.hour),
    sales: parseFloat(d.total_sales),
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" vertical={false} />
        <XAxis
          dataKey="hour"
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          tickLine={false}
          axisLine={{ stroke: '#3f3f46' }}
          interval="preserveStartEnd"
          label={{ value: 'Hour', position: 'insideBottom', offset: -2, fontSize: 11, fill: '#71717a' }}
        />
        <YAxis
          tickFormatter={formatCurrency}
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          tickLine={false}
          axisLine={false}
          width={72}
          label={{ value: 'Sales ($)', angle: -90, position: 'insideLeft', offset: 8, fontSize: 11, fill: '#71717a' }}
        />
        <Tooltip
          formatter={(val) => [formatCurrency(val), 'Sales']}
          contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 6 }}
          labelStyle={{ color: '#d4d4d8', marginBottom: 4 }}
          itemStyle={{ color: '#ff6a17' }}
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
        />
        <Bar dataKey="sales" fill="#ff6a17" radius={[3, 3, 0, 0]} maxBarSize={40} />
      </BarChart>
    </ResponsiveContainer>
  )
}
