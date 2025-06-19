import clientsData from "../../../data/clients.json";
import Sidebar from "../../components/Sidebar";
import PrimaryButton from "../../components/PrimaryButton";
import SecondaryButton from "../../components/SecondaryButton";
import SchemaTree from "../../components/SchemaTree";
import GitHubLink from "../../components/GitHubLink";
import { PRIMITIVE_TYPES, SCHEMA_CONSTANTS } from "../../config/schema";

export default function SchemaPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 font-mono">
      <Sidebar clientsData={clientsData} />

      {/* Main content */}
      <div className="ml-48 min-h-screen relative bg-gray-100 dark:bg-gray-900 border-l-2 border-gray-300 dark:border-gray-700">
        {/* Main screen content */}
        <div className="p-8 lg:p-16 bg-gradient-to-br from-gray-50 via-gray-100 to-lime-50 dark:from-gray-950 dark:via-gray-900 dark:to-lime-950 min-h-screen relative">
          <GitHubLink />

          <div className="max-w-6xl">
            {/* Header */}
            <div className="mb-12">
              <h1 className="text-4xl lg:text-6xl font-black text-gray-900 dark:text-gray-100 leading-none mb-4 tracking-tight">
                Schema <span className="text-lime-500">Reference</span>
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
                Complete reference for Block Access List data structures and
                implementation
              </p>

              <div className="flex items-center space-x-4 text-sm">
                <SecondaryButton href="/">← Back to Home</SecondaryButton>
                <PrimaryButton href="https://eips.ethereum.org/EIPS/eip-7928">
                  View EIP-7928
                </PrimaryButton>
              </div>
            </div>

            {/* Schema Tree Section */}
            <section id="schema-tree" className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                Interactive Schema Tree
              </h2>
              <SchemaTree />
            </section>

            {/* Type Reference Section */}
            <section id="types" className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                Type Reference
              </h2>
              <div className="grid lg:grid-cols-2 gap-6">
                <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
                    Primitive Types
                  </h3>
                  <div className="space-y-3 font-mono text-sm">
                    {PRIMITIVE_TYPES.map((type) => (
                      <div
                        key={type.name}
                        className="border-b border-gray-300 dark:border-gray-600 pb-2 last:border-b-0"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-purple-600 dark:text-purple-400 font-bold">
                            {type.name}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400 text-xs">
                            {type.size}
                          </span>
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 text-xs mt-1">
                          {type.description}
                        </div>
                        <div className="text-orange-600 dark:text-orange-400 text-xs">
                          {type.encoding}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
                    Constants
                  </h3>
                  <div className="space-y-3 font-mono text-sm">
                    {SCHEMA_CONSTANTS.map((constant) => (
                      <div
                        key={constant.name}
                        className="border-b border-gray-300 dark:border-gray-600 pb-2 last:border-b-0"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-orange-600 dark:text-orange-400 font-bold">
                            {constant.name}
                          </span>
                          <span className="text-gray-900 dark:text-gray-100">
                            {typeof constant.value === "number"
                              ? constant.value.toLocaleString()
                              : constant.value}
                            {constant.unit && ` ${constant.unit}`}
                          </span>
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 text-xs mt-1">
                          {constant.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
