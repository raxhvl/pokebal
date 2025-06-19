import clientsData from "../../data/clients.json";
import Sidebar from "../components/Sidebar";
import PrimaryButton from "../components/PrimaryButton";
import SecondaryButton from "../components/SecondaryButton";
import GitHubLink from "../components/GitHubLink";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 font-mono">
      <Sidebar clientsData={clientsData} />

      {/* Main content */}
      <div className="ml-48 min-h-screen relative bg-gray-100 dark:bg-gray-900 border-l-2 border-gray-300 dark:border-gray-700">
        {/* Main screen content */}
        <div className="p-8 lg:p-16 bg-gradient-to-br from-gray-50 via-gray-100 to-lime-50 dark:from-gray-950 dark:via-gray-900 dark:to-lime-950 min-h-screen relative">
          <GitHubLink />
          <div className="max-w-4xl">
            {/* Pixelated title section */}
            <div className="mb-16">
              <div className="flex items-center space-x-2 mb-6">
                <div className="w-3 h-3 bg-blue-500 rounded-sm"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-sm"></div>
                <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
              </div>

              <h1 className="text-5xl lg:text-7xl font-black text-gray-900 dark:text-gray-100 leading-none mb-4 tracking-tight">
                Poké<span className="text-lime-500 drop-shadow-lg">BAL</span>
              </h1>

              <div className="text-lg text-gray-600 dark:text-gray-400 italic mb-6 font-mono">
                &gt; gotta access 'em all!
              </div>

              <div className="flex space-x-1 mb-2">
                {Array.from({ length: 12 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-2 h-1 bg-lime-500"
                    style={{ opacity: 1 - i * 0.08 }}
                  ></div>
                ))}
              </div>
            </div>

            <div className="mb-16 space-y-8">
              <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6 shadow-inner">
                <p className="text-lg lg:text-xl text-gray-800 dark:text-gray-200 leading-relaxed">
                  A collection of helpful resources for Block Access Lists (BAL)
                  implementors.
                </p>
              </div>

              <div className="flex items-center space-x-6 text-sm">
                <PrimaryButton href="https://eips.ethereum.org/EIPS/eip-7928">
                  READ THE SPECIFICATION
                </PrimaryButton>
                <SecondaryButton href="/schema">
                  Schema Reference
                </SecondaryButton>
                <SecondaryButton
                  href="https://ethresear.ch/t/block-level-access-lists-bals/22331/6"
                  external
                >
                  Follow the discussion on ETH.research
                </SecondaryButton>
              </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
              <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-4 shadow-inner">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 font-bold">
                    TARGET
                  </div>
                </div>
                <div className="text-gray-900 dark:text-gray-100 font-mono text-sm">
                  Ethereum Virtual Machine
                </div>
              </div>

              <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-4 shadow-inner">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 font-bold">
                    TYPE
                  </div>
                </div>
                <div className="text-gray-900 dark:text-gray-100 font-mono text-sm">
                  State Access Optimization
                </div>
              </div>

              <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-4 shadow-inner">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 font-bold">
                    STATUS
                  </div>
                </div>
                <div className="text-gray-900 dark:text-gray-100 font-mono text-sm">
                  Research & Development
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Pixel art inspired decorations */}
        <div className="absolute top-24 right-8 w-48 h-48 opacity-10 dark:opacity-20">
          {/* Ethereum diamond in pixel style */}
          <div className="relative w-full h-full">
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2 space-y-1">
              <div className="flex justify-center">
                <div className="w-2 h-2 bg-blue-500"></div>
              </div>
              <div className="flex justify-center space-x-1">
                <div className="w-2 h-2 bg-blue-500"></div>
                <div className="w-2 h-2 bg-blue-400"></div>
                <div className="w-2 h-2 bg-blue-500"></div>
              </div>
              <div className="flex justify-center space-x-1">
                <div className="w-2 h-2 bg-blue-500"></div>
                <div className="w-2 h-2 bg-blue-400"></div>
                <div className="w-2 h-2 bg-blue-300"></div>
                <div className="w-2 h-2 bg-blue-400"></div>
                <div className="w-2 h-2 bg-blue-500"></div>
              </div>
              <div className="flex justify-center space-x-1">
                <div className="w-2 h-2 bg-blue-500"></div>
                <div className="w-2 h-2 bg-blue-400"></div>
                <div className="w-2 h-2 bg-blue-500"></div>
              </div>
              <div className="flex justify-center">
                <div className="w-2 h-2 bg-blue-500"></div>
              </div>
            </div>

            <div className="absolute bottom-8 left-8">
              <div
                className="w-6 h-6 relative animate-pulse"
                style={{ animationDuration: "3s" }}
              >
                <div className="w-6 h-3 bg-red-500 rounded-t-full"></div>
                <div className="w-6 h-3 bg-gray-300 rounded-b-full"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-2 h-2 bg-gray-700 rounded-full border border-gray-900"></div>
                </div>
              </div>
            </div>

            <div className="absolute top-32 right-8 grid grid-cols-4 gap-1">
              {Array.from({ length: 16 }).map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 ${
                    i % 3 === 0 ? "bg-lime-500 animate-pulse" : "bg-gray-400"
                  } rounded-sm`}
                  style={{
                    animationDelay: `${i * 200}ms`,
                    animationDuration: "4s",
                  }}
                ></div>
              ))}
            </div>

            {/* Floating blockchain nodes */}
            <div
              className="absolute top-1/4 left-1/4 w-1 h-1 bg-blue-400 rounded-full animate-bounce opacity-30"
              style={{ animationDuration: "6s", animationDelay: "0s" }}
            ></div>
            <div
              className="absolute top-1/3 right-1/3 w-1 h-1 bg-purple-400 rounded-full animate-bounce opacity-30"
              style={{ animationDuration: "8s", animationDelay: "2s" }}
            ></div>
            <div
              className="absolute bottom-1/4 left-1/3 w-1 h-1 bg-orange-400 rounded-full animate-bounce opacity-30"
              style={{ animationDuration: "7s", animationDelay: "4s" }}
            ></div>

            {/* Ethereum diamond with sparkle effect */}
            <div
              className="absolute top-16 left-12 w-3 h-3 bg-blue-500 opacity-20 animate-ping"
              style={{ animationDuration: "5s" }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
