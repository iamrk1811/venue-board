export default function TopItemsList({ items = [], title = 'Top Items' }) {
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">{title}</h2>
      {items.length === 0 ? (
        <p className="text-zinc-400 text-sm py-2">No item data yet</p>
      ) : (
        <ol className="list-none p-0 m-0">
          {items.map((item, i) => {
            const revenue = parseFloat(item.total_revenue || 0)
            return (
              <li
                key={item.item_id ?? i}
                className="flex justify-between items-center py-1.5 border-b border-zinc-700 gap-2 last:border-0"
              >
                <span className="text-sm text-white flex-1">{item.item_name}</span>
                <span className="flex gap-3 shrink-0">
                  <span className="text-xs text-zinc-400">{item.total_qty} sold</span>
                  <span className="text-sm text-blue-400 font-semibold">
                    £{revenue.toLocaleString('en-GB', { minimumFractionDigits: 2 })}
                  </span>
                </span>
              </li>
            )
          })}
        </ol>
      )}
    </div>
  )
}
