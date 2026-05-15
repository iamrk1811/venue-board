import HourlySalesChart from './HourlySalesChart'
import TopItemsList from './TopItemsList'
import AlertsPanel from './AlertsPanel'

export default function VenueContainer({ detail, loading, onClose }) {
  if (!detail && !loading) return null

  return (
    <div className="fixed inset-0 bg-black/55 z-100 flex justify-end" onClick={onClose}>
      <div
        className="bg-zinc-900 border-l border-zinc-700 w-140 max-w-full h-screen overflow-y-auto p-6 relative flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-4 right-4 text-zinc-400 hover:text-white"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>

        {loading ? (
          <p className="text-zinc-400 py-10 text-center">Loading venue data...</p>
        ) : (
          <>
            <div>
              <h2 className="text-xl font-semibold text-white mb-1.5">{detail.venue.name}</h2>
              <span className="text-[11px] px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 capitalize mr-2">
                {String(detail.venue.type).replace('_', ' ')}
              </span>
              <span className="text-sm text-zinc-400">{detail.venue.location}</span>
            </div>

            <section>
              <h3 className="text-xs text-zinc-400 uppercase mb-2">Hourly Sales (last 24h)</h3>
              <HourlySalesChart data={detail.hourly_metrics} />
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <TopItemsList items={detail.top_items} title="Top Items Today" />
              {detail.active_alerts.length > 0 && (
                <AlertsPanel alerts={detail.active_alerts} />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
