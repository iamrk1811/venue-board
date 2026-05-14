import { memo } from "react";

const tdBase = "px-2.5 py-2 border-b border-zinc-700";

const VenueRow = memo(function VenueRow({ venue, rank, onClick }) {
  const sales = parseFloat(venue.total_sales || 0);
  return (
    <tr
      className="cursor-pointer hover:bg-zinc-800 transition-colors"
      onClick={() => onClick(venue.venue_id)}
    >
      <td className={`${tdBase} text-zinc-400 w-8 font-semibold`}>{rank}</td>
      <td className={`${tdBase} font-medium text-white`}>{venue.name}</td>
      <td className={`${tdBase} text-blue-400 font-semibold`}>${sales}</td>
      <td className={`${tdBase} text-zinc-400`}>{venue.transaction_count}</td>
      <td className={`${tdBase} text-zinc-400`}>{venue.void_count}</td>
    </tr>
  );
});

export default function VenueRankingTable({ rankings = [], onVenueClick }) {
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
        Venue Rankings
      </h2>
      {rankings.length === 0 ? (
        <p className="text-zinc-400 text-sm py-2">
          No sales data yet
        </p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              {["#", "Venue", "Sales", "Transactions", "Voids"].map((h) => (
                <th
                  key={h}
                  className="text-left px-2.5 py-1.5 text-zinc-400 font-medium border-b border-zinc-700"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rankings.map((v, i) => (
              <VenueRow
                key={v.venue_id}
                venue={v}
                rank={i + 1}
                onClick={onVenueClick}
              />
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
