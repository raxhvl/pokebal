"use client";

import { useRouter } from "next/navigation";
import ClientProgressCard from "./ClientProgressCard";
import MenuButton from "./MenuButton";

interface ProgressStage {
  id: string;
  name: string;
  color: string;
  description: string;
}

interface Client {
  id: string;
  name: string;
  language: string;
  website: string;
  progress: string;
}

interface ClientsData {
  spec: string;
  progressStages: ProgressStage[];
  clients: Client[];
}

interface SidebarProps {
  clientsData: ClientsData;
}

export default function Sidebar({ clientsData }: SidebarProps) {
  const router = useRouter();

  const handleHomeClick = () => {
    router.push("/");
  };

  const handleSpecsClick = () => {
    window.open(
      "https://ethresear.ch/t/block-level-access-lists-bals/22331/6",
      "_blank"
    );
  };

  return (
    <div className="fixed left-0 top-0 h-full w-48 bg-gradient-to-b from-lime-100 to-lime-200 dark:from-lime-900 dark:to-lime-950 border-r-4 border-lime-300 dark:border-lime-700 flex flex-col py-8 shadow-2xl">
      {/* Status indicators */}
      <div className="flex-1 space-y-8 px-4">
        {/* EIP Status */}
        <div className="space-y-2">
          <div className="text-xs text-lime-700 dark:text-lime-300 font-bold">
            EIP STATUS
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="text-xs text-gray-700 dark:text-gray-300">
                DRAFT
              </div>
            </div>
            <div className="w-full bg-lime-200 dark:bg-lime-800 rounded-full h-1">
              <div className="bg-lime-500 h-1 rounded-full w-1/4"></div>
            </div>
          </div>
        </div>

        {/* Client Implementation Progress */}
        <div className="space-y-2">
          <div className="text-xs text-lime-700 dark:text-lime-300 font-bold">
            PROGRESS
          </div>
          <div className="space-y-2">
            {clientsData.clients.map((client) => (
              <ClientProgressCard
                key={client.id}
                client={client}
                stages={clientsData.progressStages}
              />
            ))}
          </div>
        </div>

        {/* Mini Navigation */}
        <div className="space-y-2">
          <div className="text-xs text-lime-700 dark:text-lime-300 font-bold">
            MENU
          </div>
          <div className="space-y-1">
            <MenuButton isActive={true} onClick={handleHomeClick}>
              HOME
            </MenuButton>
          </div>
        </div>
      </div>

      {/* Bottom indicator with Ethereum icon */}
      <div className="px-4 pb-4">
        <div className="flex items-center justify-center">
          <div className="relative">
            <svg
              className="w-6 h-6 text-lime-500 animate-pulse"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M11.944 17.97L4.58 13.62 11.943 24l7.37-10.38-7.372 4.35h.003zM12.056 0L4.69 12.223l7.365 4.354 7.365-4.35L12.056 0z" />
            </svg>
            <div className="absolute inset-0 animate-ping opacity-30">
              <svg
                className="w-6 h-6 text-lime-400"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M11.944 17.97L4.58 13.62 11.943 24l7.37-10.38-7.372 4.35h.003zM12.056 0L4.69 12.223l7.365 4.354 7.365-4.35L12.056 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
