import { Status } from "../types";

interface StatusIconProps {
  status: Status;
  size?: "small" | "large";
}

export default function StatusIcon({ status, size = "large" }: StatusIconProps) {
  const isSmall = size === "small";
  const iconSize = isSmall ? "w-3 h-3" : "w-4 h-4";
  const containerSize = isSmall ? "w-6 h-6" : "w-8 h-8";
  const shadowClass = isSmall ? "shadow-lg" : "shadow-xl";

  const getStatusConfig = () => {
    switch (status) {
      case "pass":
        return {
          containerClass: `${containerSize} bg-gradient-to-br from-green-400/90 to-green-600/90 backdrop-blur-sm rounded-full flex items-center justify-center ${shadowClass} border border-white/30 transform transition-all duration-300 hover:scale-110 hover:rotate-12`,
          icon: (
            <svg className={`${iconSize} text-white`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )
        };
      case "fail":
        return {
          containerClass: `${containerSize} bg-gradient-to-br from-red-400/90 to-red-600/90 backdrop-blur-sm rounded-full flex items-center justify-center ${shadowClass} border border-white/30 transform transition-all duration-300 hover:scale-110 hover:rotate-12`,
          icon: (
            <svg className={`${iconSize} text-white`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          )
        };
      case "pending":
        return {
          containerClass: `${containerSize} bg-gradient-to-br from-gray-300/80 to-gray-500/80 backdrop-blur-sm rounded-full flex items-center justify-center ${shadowClass} border border-white/30 transform transition-all duration-300 hover:scale-110`,
          icon: (
            <svg className={`${iconSize} text-white`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          )
        };
      default:
        return {
          containerClass: `${containerSize} bg-gradient-to-br from-gray-300/80 to-gray-500/80 backdrop-blur-sm rounded-full flex items-center justify-center ${shadowClass} border border-white/30 transform transition-all duration-300 hover:scale-110`,
          icon: (
            <svg className={`${iconSize} text-white`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          )
        };
    }
  };

  const { containerClass, icon } = getStatusConfig();

  return (
    <div className={containerClass}>
      {icon}
    </div>
  );
}