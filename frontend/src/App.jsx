import { useSelector } from "react-redux";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

function App() {
  const authenticated = useSelector((state) => state.auth.authenticated);

  return authenticated ? <Dashboard /> : <Login />;
}

export default App;
