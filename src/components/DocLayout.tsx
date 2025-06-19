import { ReactNode } from "react";
import { Github } from "lucide-react";
import clientsData from "../../data/clients.json";
import Sidebar from "./Sidebar";
import GitHubLink from "./GitHubLink";
import SecondaryButton from "./SecondaryButton";

interface DocLayoutProps {
  title: string;
  subtitle?: string;
  titleHighlight?: string; // part of title to highlight in lime-500
  backLink?: {
    href: string;
    label: string;
  };
  actions?: ReactNode;
  children: ReactNode;
}

export default function DocLayout({
  title,
  subtitle,
  titleHighlight,
  backLink = { href: "/", label: "← Back to Home" },
  actions,
  children,
}: DocLayoutProps) {
  // Split title for highlighting
  const renderTitle = () => {
    if (!titleHighlight) {
      return title;
    }

    const parts = title.split(titleHighlight);
    return (
      <>
        {parts[0]}
        <span className="text-lime-500">{titleHighlight}</span>
        {parts[1]}
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 font-mono">
      <Sidebar clientsData={clientsData} />

      {/* Main content */}
      <div className="ml-48 min-h-screen relative bg-gray-100 dark:bg-gray-900 border-l-2 border-gray-300 dark:border-gray-700">
        {/* Documentation content area */}
        <div className="bg-gradient-to-br from-gray-50 via-gray-100 to-lime-50 dark:from-gray-950 dark:via-gray-900 dark:to-lime-950 min-h-screen relative">
          <GitHubLink />

          {/* Documentation container - Docusaurus inspired */}
          <div className="max-w-5xl mx-auto">
            {/* Documentation header */}
            <header className="px-8 lg:px-16 pt-8 lg:pt-16 pb-8 border-b border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
              <div className="max-w-4xl">

                {/* Page title */}
                <h1 className="text-3xl lg:text-5xl font-black text-gray-900 dark:text-gray-100 leading-tight mb-4 tracking-tight">
                  {renderTitle()}
                </h1>

                {/* Subtitle */}
                {subtitle && (
                  <p className="text-lg lg:text-xl text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                    {subtitle}
                  </p>
                )}

                {/* Action buttons */}
                {actions && (
                  <div className="flex items-center space-x-4 text-sm">
                    {actions}
                  </div>
                )}
              </div>
            </header>

            {/* Documentation content */}
            <main className="px-8 lg:px-16 py-8 lg:py-12">
              <div className="max-w-4xl prose prose-gray dark:prose-invert prose-lg">
                {children}
              </div>
            </main>

            {/* Documentation footer */}
            <footer className="px-8 lg:px-16 py-8 border-t border-gray-200 dark:border-gray-800 bg-white/30 dark:bg-gray-900/30 backdrop-blur-sm">
              <div className="max-w-4xl">
                <div className="flex items-center justify-between">
                  {/* Contribute button */}
                  <SecondaryButton 
                    href="https://github.com/raxhvl/pokebal/blob/main/CONTRIBUTING.md"
                    icon={<Github className="w-4 h-4" />}
                  >
                    Contribute
                  </SecondaryButton>

                  {/* Made with love by EF */}
                  <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                    <span>Made with</span>
                    <span className="text-red-500">♥</span>
                    <span>by</span>
                    <a
                      href="https://ethereum.foundation/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 hover:opacity-80 transition-opacity duration-200"
                    >
                      <img
                        src="/img/ethereum-foundation.png"
                        alt="Ethereum Foundation"
                        className="w-4 h-4"
                      />
                      <span className="font-medium">EF</span>
                    </a>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
