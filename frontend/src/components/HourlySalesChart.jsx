import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'

function formatHour(isoHour) {
  const d = new Date(isoHour)
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

function formatCurrency(value) {
  return `£${parseFloat(value).toLocaleString('en-GB', { minimumFractionDigits: 0 })}`
}

export default function HourlySalesChart({ data = [] }) {
  const chartData = data.map((d) => ({
    hour: formatHour(d.hour),
    sales: parseFloat(d.total_sales),
    transactions: d.transaction_count,
  }))

  if (chartData.length === 0) {
    return <p className="text-zinc-400 text-sm py-2">No hourly data yet</p>
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="hour"
          tick={{ fontSize: 11, fill: '#aaa' }}
          interval="preserveStartEnd"
        />
        <YAxis
          tickFormatter={formatCurrency}
          tick={{ fontSize: 11, fill: '#aaa' }}
          width={64}
        />
        <Tooltip
          formatter={(val) => formatCurrency(val)}
          contentStyle={{ background: '#1e1e1e', border: '1px solid #444', borderRadius: 4 }}
          labelStyle={{ color: '#ccc' }}
          itemStyle={{ color: '#7eb8f7' }}
        />
        <Bar dataKey="sales" fill="#7eb8f7" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
