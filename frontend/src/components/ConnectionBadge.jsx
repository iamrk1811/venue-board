const STATUS_CONFIG = {
  connected: {
    label: "Live",
    dot: "bg-green-400",
  },
  reconnecting: {
    label: "Reconnecting...",
    dot: "bg-yellow-400",
  },
  connecting: {
    label: "Connecting...",
    dot: "bg-orange-400",
  },
};

export default function ConnectionBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.connecting;
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 border ${config.badge}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
}
