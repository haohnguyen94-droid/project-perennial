import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/sidebar";

export default function Dashboard() {
  let navigate = useNavigate();
  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-row grow-1">
        <div className="flex grow-1 justify-center items-center">logo</div>
        <div className="flex grow-1 justify-center items-center">Perennial</div>
        <div className="flex grow-10 justify-center items-center">
          searchbar
        </div>
      </div>
      <div className="flex flex-row w-screen grow-20">
        <div className="flex flex-col grow-2 justify-between">
          <Sidebar
            navigations={["Home", "Watchlist", "Insight", "Settings"]}
          ></Sidebar>
          <button
            className="mb-10"
            onClick={() => {
              navigate("/profile");
            }}
          >
            Profile
          </button>
        </div>
        <div className="flex flex-col grow-10">
          <div className="flex flex-row justify-arouond">
            <button>Affordable and Growing</button>
            <button>Popular and Stable</button>
          </div>
          <div>content</div>
        </div>
      </div>
    </div>
  );
}
