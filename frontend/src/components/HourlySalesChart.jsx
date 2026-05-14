import { BarChart, Bar } from 'recharts'

export default function HourlySalesChart({ data = [] }) {
  if (data.length === 0) {
    return <p className="text-zinc-400 text-sm py-2">No hourly data yet</p>
  }

  const chartData = data.map((d) => ({
    hour: d.hour,
    sales: parseFloat(d.total_sales),
  }))

  return (
    <BarChart
      style={{ width: '100%', aspectRatio: 2.5, border: '2px solid #002e5e'}}
      responsive
      data={chartData}
    >
      <Bar dataKey="sales" fill="#ff6a17" radius={[2, 2, 0, 0]} />
    </BarChart>
  )
}
