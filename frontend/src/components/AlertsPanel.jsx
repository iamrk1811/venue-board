const SEVERITY_LABELS = { warning: '⚠', critical: '🔴' }
const TYPE_LABELS = {
  sales_drop: 'Sales Drop',
  void_spike: 'Void Spike',
  refund_spike: 'Refund Spike',
}

export default function AlertsPanel({ alerts = [] }) {
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4 max-h-105 overflow-y-auto">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3 flex items-center">
        Active Alerts
        {alerts.length > 0 && (
          <span className="inline-flex items-center justify-center bg-red-500 text-white text-[11px] font-bold rounded-full px-1.5 min-w-4.5 h-4.5 ml-2">
            {alerts.length}
          </span>
        )}
      </h2>
      {alerts.length === 0 ? (
        <p className="text-zinc-400 text-sm py-2">No active alerts</p>
      ) : (
        <ul className="flex flex-col gap-2 list-none p-0 m-0">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className={`flex gap-2.5 p-2.5 rounded-md bg-zinc-800 border-l-[3px] ${
                alert.severity === 'critical' ? 'border-l-red-500' : 'border-l-yellow-400'
              }`}
            >
              <span className="text-base shrink-0">{SEVERITY_LABELS[alert.severity] ?? '!'}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="font-semibold text-xs text-white">
                    {TYPE_LABELS[alert.type] ?? alert.type}
                  </span>
                  {alert.venue_name && (
                    <span className="text-xs text-blue-400">{alert.venue_name}</span>
                  )}
                  <span className="text-[11px] text-zinc-400 ml-auto">
                    {alert.created_at}
                  </span>
                </div>
                <p className="text-xs text-zinc-200 leading-snug">{alert.message}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
