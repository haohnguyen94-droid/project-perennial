import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/sidebar";
import CompanyLogo from "../components/companyLogo";

export default function Settings() {
  let navigate = useNavigate();
  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 text-[2rem] justify-center items-center pl-5">
          Your Settings
        </div>
      </div>
      <div className="flex flex-row w-screen grow-20">
        <div className="flex flex-col grow-2 justify-between items-center border-r">
          <Sidebar navigations={["Home", "Watchlist", "Insight"]} />
          <div className="flex flex-col items-center mb-10 gap-2">
            <button
              className="border rounded-full h-[5rem] w-[5rem] cursor-pointer"
              onClick={() => {
                navigate("/profile");
              }}
            >
              Profile
            </button>
            <div> Profile </div>
          </div>
        </div>
        <div className="flex flex-col grow-10 gap-7 text-[2rem] items-start pl-[5rem] pt-5">
          <button className="cursor-pointer hover:underline">
            Notification
          </button>
          <button className="cursor-pointer hover:underline">
            Your Profile
          </button>
          <button className="cursor-pointer hover:underline">
            Update Preference
          </button>
          <button className="cursor-pointer hover:underline">
            Change Your Password
          </button>
          <button className="cursor-pointer hover:underline">Log Out</button>
        </div>
      </div>
    </div>
  );
}
