export default function TopItemsList({ items = [], title = 'Top Items' }) {
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4">
      <h2 className="text-xs font-semibold uppercase text-zinc-400 mb-3">{title}</h2>
      {items.length === 0 ? (
        <p className="text-zinc-400 text-sm">No item data yet</p>
      ) : (
        <ol>
          {items.map((item, i) => (
            <li
              key={item.item_id ?? i}
              className="flex justify-between items-center py-1.5 border-b border-zinc-700 last:border-0"
            >
              <span className="text-sm text-white">{item.item_name}</span>
              <span className="flex gap-3 text-xs">
                <span className="text-zinc-400">{item.total_qty} sold</span>
                <span className="text-blue-400 font-semibold">${parseFloat(item.total_revenue || 0)}</span>
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
