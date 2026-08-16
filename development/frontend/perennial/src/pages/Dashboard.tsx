import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/sidebar";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

function Search(
  term: string,
  setter: React.Dispatch<React.SetStateAction<string>>,
) {
  setter(term);
}

export default function Dashboard() {
  let navigate = useNavigate();
  const [content, setContent] = useState<string>("content");
  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 justify-start items-center pl-5">
          <input
            type="text"
            placeholder="Search..."
            value={content}
            onChange={(e) => Search(e.target.value, setContent)}
            className="border rounded-md w-[40%] px-3 py-2"
          />
        </div>
      </div>
      <div className="flex flex-row w-screen grow-20">
        <div className="flex flex-col grow-2 justify-between items-center border-r">
          <Sidebar navigations={["Watchlist", "Insight", "Settings"]} />
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
        <div className="flex flex-col grow-10 pt-5">
          <div className="flex flex-row justify-around">
            <button className="border rounded-md h-[3rem] w-[15rem] cursor-pointer hover:bg-sky-700">
              Affordable and Growing
            </button>
            <button className="border rounded-md h-[3rem] w-[15rem] cursor-pointer hover:bg-sky-700">
              Popular and Stable
            </button>
          </div>
          <div className="w-[90%] mx-auto py-[2rem]">{content}</div>
        </div>
      </div>
    </div>
  );
}
