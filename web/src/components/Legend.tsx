import StatusIcon from "./StatusIcon";

interface LegendItemProps {
  status: "pass" | "fail" | "pending";
  label: string;
  hoverColor: string;
}

function LegendItem({ status, label, hoverColor }: LegendItemProps) {
  return (
    <div className="flex items-center space-x-2 group cursor-pointer bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-full px-3 py-1 border border-white/20 dark:border-gray-600/30 shadow-lg hover:bg-white/15 dark:hover:bg-gray-800/15 transition-all duration-300">
      <div className="transform transition-all duration-300 group-hover:scale-110">
        <StatusIcon status={status} size="small" />
      </div>
      <span
        className={`text-xs font-medium text-gray-800 dark:text-gray-200 ${hoverColor} transition-colors`}
      >
        {label}
      </span>
    </div>
  );
}

export default function Legend() {
  return (
    <div className="mb-4 space-y-4">
      <div className="flex flex-wrap justify-center items-center gap-4 sm:gap-8">
        <LegendItem
          status="pass"
          label="Passing"
          hoverColor="group-hover:text-green-600 dark:group-hover:text-green-400"
        />
        <LegendItem
          status="fail"
          label="Failing"
          hoverColor="group-hover:text-red-600 dark:group-hover:text-red-400"
        />
        <LegendItem
          status="pending"
          label="Pending"
          hoverColor="group-hover:text-gray-600 dark:group-hover:text-gray-400"
        />
      </div>
    </div>
  );
}
