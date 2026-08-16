import { Link, useNavigate } from "react-router-dom";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

// TODO's
// define insight type
// determine how we get the company that we are displaying insight about

type insight = {};

function Back() {
  return;
}

function GetCompanyInsights(CompanyName: string) {}

export default function Insights(CompanyName: string) {
  GetCompanyInsights(CompanyName);
  const [insights, setInsights] = useState<insight>();
  let navigate = useNavigate();
  return (
    <div className="flex flex-col h-screen">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 text-[2rem] justify-center items-center pl-5">
          Insight
        </div>
      </div>
      <div className="flex flex-col w-screen grow-20">
        <div className="flex justify-start ml-[2rem] mt-[2rem]">
          <button
            className="flex h-12 w-12 items-center justify-center rounded-full
             border border-white text-2xl
             hover:bg-white/20 cursor-pointer"
            onClick={() => Back()}
          >
            ←
          </button>
        </div>
      </div>
    </div>
  );
}
