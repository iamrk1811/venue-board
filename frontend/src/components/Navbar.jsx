import { useDispatch } from "react-redux";
import { logout } from "../store/slices/authSlice";
import ConnectionBadge from "./ConnectionBadge";

export default function Navbar({ wsStatus }) {
  const dispatch = useDispatch();

  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-zinc-700 bg-zinc-900 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-bold text-white">Venue Board</h1>
        <ConnectionBadge status={wsStatus} />
      </div>
      <button
        onClick={() => dispatch(logout())}
        className="text-sm px-3 py-1.5 rounded bg-[#ff6a17] font-semibold text-zinc-950 hover:opacity-90"
      >
        Sign out
      </button>
    </div>
  );
}
