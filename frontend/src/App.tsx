import { Route, Routes } from "react-router-dom";
import ComparePage from "./pages/ComparePage";
import MapPage from "./pages/MapPage";
import MatchPage from "./pages/MatchPage";
import UnitPage from "./pages/UnitPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/units/:unitId" element={<UnitPage />} />
      <Route path="/compare" element={<ComparePage />} />
      <Route path="/match" element={<MatchPage />} />
    </Routes>
  );
}

export default App;
