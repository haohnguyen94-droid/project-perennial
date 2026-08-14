import { use } from "react";
import { Link, useNavigate } from "react-router-dom";

function Update() {}

export default function Confirmation() {
  let navigate = useNavigate();
  return (
    <div className="flex flex-col w-[1126px] mx-auto">
      <h1 className="text-[56px] tracking-[-1.68px] my-5">Confirmation</h1>
      <div className="text-3xl">
        Lorem ipsum, dolor sit amet consectetur adipisicing elit. Error
        praesentium architecto, porro eius reiciendis voluptatum autem rem nulla
        natus corporis qui quibusdam consectetur provident hic. Rerum
        perspiciatis itaque quia praesentium?
      </div>
      <div className="flex flex-row text-lg h-10 mt-10 justify-between">
        <button
          className="border w-30 rounded-lg cursor-pointer hover:bg-sky-700"
          onClick={Update}
        >
          Update
        </button>
        <button
          className="border w-30 rounded-lg cursor-pointer hover:bg-sky-700"
          onClick={() => {
            navigate("/");
          }}
        >
          Dashboard
        </button>
      </div>
    </div>
  );
}
