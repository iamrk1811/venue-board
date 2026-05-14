import { useDashboard } from "../hooks/useDashboard";
import Navbar from "../components/Navbar";
import VenueRankingTable from "../components/VenueRankingTable";
import AlertsPanel from "../components/AlertsPanel";
import TopItemsList from "../components/TopItemsList";
import VenueContainer from "../components/VenueContainer";
import Overallsummary from "../components/OverallSummary";

export default function Dashboard() {
  const {
    summary,
    alerts,
    wsStatus,
    venueDetail,
    venueDetailLoading,
    openVenue,
    closeVenue,
  } = useDashboard();

  const topItems = summary?.top_items ?? [];

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar wsStatus={wsStatus} />

      <div className="p-6 flex-1">
        <Overallsummary summary={summary} />
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-4 mt-4">
          <div className="flex flex-col gap-4">
            <VenueRankingTable
              rankings={summary?.venue_rankings ?? []}
              onVenueClick={openVenue}
            />
          </div>
          <div className="flex flex-col gap-4">
            <AlertsPanel alerts={alerts} />
            <TopItemsList items={topItems} title="Global Top Items Today" />
          </div>
        </div>
      </div>

      <VenueContainer
        detail={venueDetail}
        loading={venueDetailLoading}
        onClose={closeVenue}
      />
    </div>
  );
}
