import ClientLogo from "./ClientLogo";
import { Test, Client } from "../types";
import { getClientOverallProgress } from "../lib/utils";

interface ClientLogoWithProgressProps {
  client: Client;
  tests: Test[];
  showProgress?: boolean;
}

export default function ClientLogoWithProgress({
  client,
  tests,
  showProgress = true,
}: ClientLogoWithProgressProps) {
  const progress = getClientOverallProgress(tests, client.id);
  const progressPercentage = progress.total > 0 ? (progress.passed / progress.total) * 100 : 0;

  const content = (
    <div className="relative bg-white/25 dark:bg-gray-800/35 backdrop-blur-md px-3 py-1 rounded-lg border border-white/40 dark:border-gray-500/50 shadow-lg overflow-hidden">
      {showProgress && (
        <>
          {/* Health Bar Background */}
          <div className="absolute inset-0 bg-gray-300/20 dark:bg-gray-600/20 rounded-lg"></div>
          {/* Health Bar Progress */}
          <div
            className="absolute inset-0 rounded-lg transition-all duration-1000 ease-out"
            style={{
              width: `${progressPercentage}%`,
              background: progressPercentage === 0 ? 'rgba(156, 163, 175, 0.4)' : // gray-400
                         progressPercentage <= 25 ? 'rgba(239, 68, 68, 0.4)' :  // red-500
                         progressPercentage <= 50 ? 'rgba(249, 115, 22, 0.4)' : // orange-500
                         'rgba(34, 197, 94, 0.4)' // green-500
            }}
          ></div>
        </>
      )}
      <div className="relative flex flex-col items-center space-y-1">
        <div className="flex items-center space-x-2">
          <ClientLogo
            logo={client.logo}
            name={client.name}
            size="small"
          />
          <span className="font-bold text-gray-800 dark:text-gray-100">
            {client.name}
          </span>
        </div>
        <div
          className="text-xs text-gray-600 dark:text-gray-400 font-mono truncate w-full px-1"
          title={client.version}
        >
          {client.version}
        </div>
        {showProgress && (
          <div className="text-xs font-bold text-gray-700 dark:text-gray-300">
            {progress.passed}/{progress.total} ({Math.round(progressPercentage)}%)
          </div>
        )}
      </div>
    </div>
  );

  // If client has a GitHub repo, wrap content in a link
  if (client.githubRepo) {
    return (
      <a
        href={client.githubRepo}
        target="_blank"
        rel="noopener noreferrer"
        className="block hover:opacity-80 transition-opacity"
        onClick={(e) => e.stopPropagation()}
      >
        {content}
      </a>
    );
  }

  return content;
}