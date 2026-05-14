import { useState } from "react";
import { useDispatch } from "react-redux";
import { login } from "../api/dashboard";
import { loginSuccess } from "../store/slices/authSlice";

export default function Login() {
  const dispatch = useDispatch();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await login(username, password);
      dispatch(loginSuccess(data));
    } catch {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-10 w-90 text-center">
        <h1 className="text-3xl font-bold mb-1.5 text-white">Venue Board</h1>
        <p className="text-zinc-400 text-sm mb-7">
          Hospitality Operations Dashboard
        </p>
        <form onSubmit={handleSubmit} className="text-left">
          <div className="mb-4">
            <label htmlFor="username" className="block text-xs text-zinc-400 mb-1.5">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white text-sm outline-none focus:border-blue-400 transition-colors"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-xs text-zinc-400 mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white text-sm outline-none focus:border-blue-400 transition-colors"
            />
          </div>
          {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-[#ff6a17] text-zinc-950 border-0 rounded-md text-sm font-semibold cursor-pointer hover:opacity-90 disabled:opacity-60 disabled:cursor-not-allowed transition-opacity"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
