import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/sidebar";
import CompanyLogo from "../components/companyLogo";
import { useState } from "react";

type accountInfo = {
  firstName: string;
  lastName: string;
  email: string;
  phonePreference: boolean;
  emailPreference: boolean;
};

function getAccountInfo(accountID: string) {
  return dummyAccountInfo;
}

function togglePhone(
  setPhone: React.Dispatch<React.SetStateAction<boolean>>,
  info: accountInfo,
  setInfo: React.Dispatch<React.SetStateAction<accountInfo>>,
) {
  info.phonePreference = !info.phonePreference;
  setInfo(info);
  setPhone((prev) => !prev);
}

function toggleEmail(
  setEmail: React.Dispatch<React.SetStateAction<boolean>>,
  info: accountInfo,
  setInfo: React.Dispatch<React.SetStateAction<accountInfo>>,
) {
  info.emailPreference = !info.emailPreference;
  setInfo(info);
  setEmail((prev) => !prev);
}

const dummyAccountInfo: accountInfo = {
  firstName: "John",
  lastName: "Doe",
  email: "JohnDoe@gmail.com",
  phonePreference: true,
  emailPreference: true,
};

export default function Profile(accountID: string) {
  const [info, setInfo] = useState<accountInfo>(getAccountInfo("dummyString"));
  const [phone, setPhone] = useState<boolean>(
    getAccountInfo("dummyString").phonePreference,
  );
  const [email, setEmail] = useState<boolean>(
    getAccountInfo("dummyString").emailPreference,
  );

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
          <Sidebar navigations={["Home", "Watchlist", "Insight", "Settings"]} />
        </div>
        <div className="flex flex-col grow-10 gap-7 items-center pt-5">
          <div className="flex flex-row items-center mb-10 gap-2">
            <div className="flex border rounded-full h-[5rem] w-[5rem] justify-center items-center">
              Profile
            </div>
            <div className="flex flex-col text-[2rem]">
              <div className="font-bold">
                {info?.firstName} {info?.lastName}
              </div>
              <div>{info?.email}</div>
            </div>
          </div>
          <div className="border rounded-md w-[80%] p-[1rem]">
            <div className="font-bold text-[2rem] items-start mb-5">
              Investment Notification
            </div>
            <div className="flex flex-col gap-5">
              <div className="flex flex-row justify-between">
                <div className="text-[2rem]">Phone {phone}</div>
                <button
                  type="button"
                  onClick={() => togglePhone(setPhone, info, setInfo)}
                  className={`relative w-14 h-8 rounded-full transition-colors duration-200 ${
                    phone ? "bg-sky-600" : "bg-gray-500"
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 ${
                      phone ? "translate-x-6" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
              <div className="flex flex-row justify-between">
                <div className="text-[2rem]">Email</div>
                <button
                  type="button"
                  onClick={() => toggleEmail(setEmail, info, setInfo)}
                  className={`relative w-14 h-8 rounded-full transition-colors duration-200 ${
                    email ? "bg-sky-600" : "bg-gray-500"
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 ${
                      email ? "translate-x-6" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
