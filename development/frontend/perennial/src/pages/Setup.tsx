import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

type TopicProps = {
  topics: Array<string>;
};

function AddInterest(
  topic: string,
  interests: Array<string>,
  setInterests: React.Dispatch<React.SetStateAction<string[]>>,
) {
  interests.push(topic);
  setInterests(interests);
}

export default function Setup({ topics }: TopicProps) {
  const [interests, setInterests] = useState<string[]>([]);
  return (
    <div className="flex-col w-[1126px] mx-auto">
      <h1 className="text-[56px] tracking-[-1.68px] mb-5">
        What Interests You
      </h1>
      <div className="grid grid-cols-5 gap-2">
        {topics.map((t) => (
          <button
            className="border rounded-md h-15 cursor-pointer hover:bg-sky-700"
            key={t}
            value={t}
            onClick={(e) => {
              AddInterest(e.currentTarget.value, interests, setInterests);
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <h1 className="text-[56px] tracking-[-1.68px] my-5">Risk Comfort</h1>
      <div className="flex flex-row text-xl justify-around mb-5">
        <label className="flex items-center gap-3">
          <input type="radio" value="low" className="h-4 w-4" />
          Low
        </label>

        <label className="flex items-center gap-2">
          <input type="radio" value="medium" className="h-4 w-4" />
          Medium
        </label>

        <label className="flex items-center gap-2">
          <input type="radio" value="high" className="h-4 w-4" />
          High
        </label>
      </div>
      <div className="flex justify-end">
        <button
          className="flex h-12 w-12 items-center justify-center rounded-full
             border border-white text-2xl
             hover:bg-white/20 cursor-pointer"
        >
          →
        </button>
      </div>
    </div>
  );
}
