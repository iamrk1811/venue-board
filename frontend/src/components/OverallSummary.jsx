export default function Overallsummary({ summary }) {
  if (!summary) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 opacity-50">
        Loading summary...
      </div>
    )
  }

  const sales = parseFloat(summary.total_sales_today || 0)

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
        <div className="text-xs text-zinc-400 uppercase tracking-widest">Total Sales Today</div>
        <div className="text-2xl font-bold text-white mt-1">
          ${sales}
        </div>
      </div>
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
        <div className="text-xs text-zinc-400 uppercase tracking-widest">Total Transactions</div>
        <div className="text-2xl font-bold text-white mt-1">
          {summary.total_transactions_today}
        </div>
      </div>
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
        <div className="text-xs text-zinc-400 uppercase tracking-widest">Active Alerts</div>
        <div className={`text-2xl font-bold mt-1 ${summary.active_alert_count > 0 ? 'text-red-400' : 'text-white'}`}>
          {summary.active_alert_count}
        </div>
      </div>
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
        <div className="text-xs text-zinc-400 uppercase tracking-widest">Venues Reporting</div>
        <div className="text-2xl font-bold text-white mt-1">
          {summary.venue_rankings?.length}
        </div>
      </div>
    </div>
  )
}
