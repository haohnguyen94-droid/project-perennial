import { useNavigate } from "react-router-dom";

type SidebarProps = {
  navigations: Array<string>;
};

export default function Sidebar({ navigations }: SidebarProps) {
  let navigate = useNavigate();
  return (
    <div className="flex flex-col">
      {navigations.map((n) => (
        <button
          className="border rounded-md h-15 cursor-pointer hover:bg-sky-700"
          key={n}
          value={n}
          onClick={(e) => {
            navigate(`/${e.currentTarget.value}`);
          }}
        >
          {n}
        </button>
      ))}
    </div>
  );
}
