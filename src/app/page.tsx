export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-blue-900">
      <div className="container mx-auto px-4 py-16">
        <header className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-800 dark:text-white mb-4">
            PokéBAL
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 italic mb-8">
            Gotta access 'em all!
          </p>
          <p className="text-lg text-gray-700 dark:text-gray-200 max-w-2xl mx-auto">
            A collection of helpful resources for Block Access Lists (BAL)
            implementors.
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-white mb-4">
              About Block Access Lists
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Block Access Lists (BAL) is an upcoming Ethereum specification
              that enhances transaction execution efficiency by providing access
              patterns at the block level.
            </p>
            <a
              href="https://ethresear.ch/t/block-level-access-lists-bals/22331/6"
              className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Learn more about BAL specification →
            </a>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-white mb-4">
              Getting Started
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              This repository provides tools and documentation to help
              developers understand and implement the Block Access List
              specification.
            </p>
            <div className="bg-gray-100 dark:bg-gray-700 rounded-md p-4">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                Coming soon: Implementation guides, tools, and examples
              </p>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
