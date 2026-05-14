import HourlySalesChart from './HourlySalesChart'
import TopItemsList from './TopItemsList'
import AlertsPanel from './AlertsPanel'

export default function VenueContainer({ detail, loading, onClose }) {
  if (!detail && !loading) return null

  return (
    <div
      className="fixed inset-0 bg-black/55 z-100 flex justify-end"
      onClick={onClose}
    >
      <div
        className="bg-zinc-900 border-l border-zinc-700 w-140 max-w-full h-screen overflow-y-auto p-6 relative flex flex-col gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-4 right-4 bg-transparent border-0 text-zinc-400 text-lg leading-none p-1 cursor-pointer hover:text-white transition-colors"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>

        {loading ? (
          <div className="text-zinc-400 py-10 text-center">Loading venue data...</div>
        ) : (
          <>
            <div>
              <h2 className="text-xl font-semibold text-white mb-1.5">{detail.venue.name}</h2>
              <span className="inline-block text-[11px] px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 capitalize mr-2">
                {String(detail.venue.type).replace('_', ' ')}
              </span>
              <span className="text-sm text-zinc-400">{detail.venue.location}</span>
            </div>

            <section>
              <h3 className="text-xs text-zinc-400 uppercase tracking-widest mb-2.5">
                Hourly Sales (last 24h)
              </h3>
              <HourlySalesChart data={detail.hourly_metrics} />
            </section>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <section>
                <TopItemsList items={detail.top_items} title="Top Items Today" />
              </section>
              {detail.active_alerts.length > 0 && (
                <section>
                  <AlertsPanel alerts={detail.active_alerts} />
                </section>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
