import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/sidebar";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

type CompanyOverview = {
  name: string;
  notes: Array<string>;
  sentiment: string;
  score: number;
  currentPrice: number;
};

const dummyOverviews: Array<CompanyOverview> = [
  {
    name: "spaceX",
    notes: ["stable", "new technology"],
    sentiment: "good",
    score: 75.72,
    currentPrice: 323.14,
  },
  {
    name: "palantir",
    notes: ["government", "potential"],
    sentiment: "average",
    score: 60.33,
    currentPrice: 504.28,
  },
  {
    name: "anthropic",
    notes: ["trending", "new model"],
    sentiment: "great",
    score: 84.26,
    currentPrice: 413.96,
  },
];

export default function Dashboard() {
  let navigate = useNavigate();
  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 text-[2rem] justify-center items-center pl-5">
          Your Watch List
        </div>
      </div>
      <div className="flex flex-row w-screen grow-20">
        <div className="flex flex-col grow-2 justify-between items-center border-r">
          <Sidebar navigations={["Home", "Insight", "Settings"]} />
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
              All
            </button>
            <button className="border rounded-md h-[3rem] w-[15rem] cursor-pointer hover:bg-sky-700">
              Sectors
            </button>
          </div>
          <div className="flex flex-col w-[90%] mx-auto py-[2rem]">
            <div className="grid grid-cols-14 gap-3 items-center">
              <div className="col-span-6 underline font-bold">Name</div>
              <div className="col-span-3 underline font-bold">Sentiment</div>
              <div className="col-span-1 underline font-bold">Score</div>
              <div className="col-span-2 underline font-bold">
                Current Price
              </div>
              <div className="col-span-2" />
              {dummyOverviews.map((d) => (
                <div key={d.name} className="contents">
                  <div className="col-span-2">{d.name}</div>
                  <div className="col-span-4 flex flex-row gap-2 items-center">
                    {d.notes.map((m) => (
                      <div className="bg-sky-500 p-1 rounded-md">{m}</div>
                    ))}
                  </div>
                  <div className="col-span-3">{d.sentiment}</div>
                  <div className="col-span-1">{d.score}</div>
                  <div className="col-span-2">{d.currentPrice}</div>
                  <div className="col-span-2 flex flex-col">
                    <button>View</button>
                    <button>Remove</button>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex flex-row justify-center mt-3">
              End of Watchlist
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
