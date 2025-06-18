interface MenuButtonProps {
  children: React.ReactNode;
  isActive?: boolean;
  onClick?: () => void;
}

export default function MenuButton({ children, isActive = false, onClick }: MenuButtonProps) {
  if (isActive) {
    return (
      <button 
        onClick={onClick}
        className="w-full text-left p-2 text-xs bg-lime-300 dark:bg-lime-700 rounded text-gray-800 dark:text-gray-200 font-bold relative group cursor-pointer"
      >
        <div className="flex items-center justify-between">
          <span>{children}</span>
          <div className="flex items-center space-x-1">
            {/* Active indicator - pixelated cursor */}
            <div className="w-1 h-1 bg-gray-800 dark:bg-gray-200"></div>
            <div className="w-1 h-1 bg-gray-800 dark:bg-gray-200"></div>
            <div className="w-1 h-1 bg-gray-800 dark:bg-gray-200"></div>
          </div>
        </div>
        {/* Animated selection border */}
        <div className="absolute inset-0 border-2 border-gray-800 dark:border-gray-200 rounded animate-pulse opacity-50"></div>
      </button>
    );
  }

  return (
    <button 
      onClick={onClick}
      className="w-full text-left p-2 text-xs bg-gray-300 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-400 relative hover:bg-gray-400 dark:hover:bg-gray-600 transition-colors group cursor-pointer"
    >
      <div className="flex items-center justify-between">
        <span>{children}</span>
        {/* Inactive indicator - dimmed pixels */}
        <div className="flex items-center space-x-1 opacity-30">
          <div className="w-1 h-1 bg-gray-600 dark:bg-gray-400"></div>
          <div className="w-1 h-1 bg-gray-600 dark:bg-gray-400"></div>
          <div className="w-1 h-1 bg-gray-600 dark:bg-gray-400"></div>
        </div>
      </div>
      {/* Hover selection preview */}
      <div className="absolute inset-0 border border-gray-500 dark:border-gray-500 rounded opacity-0 group-hover:opacity-50 transition-opacity"></div>
    </button>
  );
}