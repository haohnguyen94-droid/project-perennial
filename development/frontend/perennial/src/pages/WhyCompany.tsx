import { Link, useNavigate } from "react-router-dom";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

function Back() {
  return;
}

function getWhyCompany() {
  return;
}

const dummyReasons = ["reason 1", "reason 2", "reason 2"];

export default function WhyCompany() {
  const [insights, setInsights] = useState(getWhyCompany());
  let navigate = useNavigate();
  return (
    <div className="flex flex-col min-h-screen mb-20">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 text-[2rem] justify-center items-center pl-5">
          Why This Company
        </div>
      </div>
      <div className="flex flex-col w-screen grow-20 px-[2rem]">
        <div className="flex justify-start my-[2rem]">
          <button
            className="flex h-12 w-12 items-center justify-center rounded-full
                 border border-white text-2xl
                 hover:bg-white/20 cursor-pointer"
            onClick={() => Back()}
          >
            ←
          </button>
        </div>
        <div className="flex flex-col items-center gap-7">
          <div className="flex flex-col border rounded-md w-[100%] gap-2">
            <div className="flex text-[3rem] justify-start">Key Reasons</div>
            <ul className="list-disc list-inside text-[3rem] marker:text-5xl">
              {dummyReasons.map((r) => (
                <li>{r}</li>
              ))}
            </ul>
          </div>
          <div className="flex flex-col border rounded-md w-[100%] gap-2">
            <div className="flex text-[3rem] justify-center">Finance</div>
            <div className="text-[10rem]">Stuff</div>
          </div>
        </div>
      </div>
    </div>
  );
}
