import { Link, useNavigate } from "react-router-dom";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

type details = {
  name: string;
  category: string;
  stock: string;
  score: number;
  scoreBreakdown: Array<number>;
  priceBreakdown: Array<number>;
  //more stuff
};

function Back() {
  return;
}

function getCompanyDetails() {
  return;
}

export default function Company() {
  const [insights, setInsights] = useState(getCompanyDetails());
  let navigate = useNavigate();
  return (
    <div className="flex flex-col min-h-screen mb-20">
      <div className="flex flex-row grow-1 border-b">
        <CompanyLogo />
        <div className="flex grow-10 text-[2rem] justify-center items-center pl-5">
          Company Detail
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
        <div className="flex text-[3rem] flex-row gap-7">
          <div className="border rounded-sm p-2">Company Name</div>
          <div className="border rounded-sm p-2">Category</div>
          <div className="border rounded-sm p-2">Stock</div>
        </div>
        <div className="flex flex-col items-center gap-7">
          <div className="flex justify-center items-center text-[7rem] border rounded-full w-[10rem] h-[10rem] bg-grey">
            74
          </div>
          <div className="flex flex-row underline justify-around w-[50%]">
            <div>one</div>
            <div>two</div>
            <div>three</div>
          </div>
          <div className="border-t w-screen" />
          <div className="flex flex-col w-[100%] gap-2">
            <div className="flex text-[3rem] justify-start">
              Score Breakdown
            </div>
            <div className="flex text[2rem] justify-start">
              Tap Anywhere to Learn More
            </div>
            <div className="flex flex-col gap-5">
              <div className="border rounded-md h-[3rem]">Reason 1</div>
              <div className="border rounded-md h-[3rem]">Reason 2</div>
              <div className="border rounded-md h-[3rem]">Reason 3</div>
            </div>
          </div>
          <div className="border-t w-screen" />
          <div className="flex flex-col w-[100%] gap-2">
            <div className="flex text-[3rem] justify-start">
              Price Breakdown
            </div>
            <div className="flex">
              <div className="border rounded-md h-[3rem] w-[100%]">Reasons</div>
            </div>
            <div className="flex text-[3rem] justify-start">Week Range</div>
            <div className="flex">
              <div className="border rounded-md h-[3rem] w-[100%]">Numbers</div>
            </div>
          </div>
          <div className="border-t w-screen" />
          <div className="flex flex-col w-[100%] gap-3">
            <div className="flex text-[3rem] justify-start">
              Sentiment Pulse
            </div>
            <div className="flex flex-row gap-5">
              <div className="border rounded-md p-3">News</div>
              <div className="border rounded-md p-3">Social Media</div>
              <div className="border rounded-md p-3">Analyst</div>
            </div>
            <div className="flex flex-row gap-2">
              <div className="border rounded-md h-[2rem] w-[5rem]">One</div>
              <div className="border rounded-md h-[2rem] w-[5rem]">Two</div>
              <div className="border rounded-md h-[2rem] w-[5rem]">Three</div>
            </div>
            <div className="flex text-[1rem] justify-start">
              What is Driving Sentiment
            </div>
            <div className="flex flex-col border rounded-sm py-5 gap-3 px-3 max-h-[10rem] overflow-y-auto">
              <div className="border rounded-md h-[3rem] w-[100%] shrink-0">
                reason 1
              </div>
              <div className="border rounded-md h-[3rem] w-[100%] shrink-0">
                reason 2
              </div>
              <div className="border rounded-md h-[3rem] w-[100%] shrink-0">
                reason 3
              </div>
              <div className="border rounded-md h-[3rem] w-[100%] shrink-0">
                reason 4
              </div>
              <div className="border rounded-md h-[3rem] w-[100%] shrink-0">
                reason 5
              </div>
            </div>
          </div>
          <div className="border-t w-screen" />
          <div className="flex flex-col border rounded-md items-start p-3 w-[100%] gap-3">
            <button className="cursor-pointer hover:underline">
              Why This Company
            </button>
            <button className="cursor-pointer hover:underline">
              Key Reason
            </button>
            <button className="cursor-pointer hover:underline">
              View More
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
