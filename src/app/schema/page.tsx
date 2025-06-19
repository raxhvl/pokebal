import PrimaryButton from "../../components/PrimaryButton";
import SchemaTree from "../../components/SchemaTree";
import DocLayout from "../../components/DocLayout";
import AnchorHeading from "../../components/AnchorHeading";
import { PRIMITIVE_TYPES, SCHEMA_CONSTANTS } from "../../config/schema";

export default function SchemaPage() {
  return (
    <DocLayout
      title="Schema Reference"
      titleHighlight="Reference"
      subtitle="Complete reference for Block Access List data structures and implementation"
      actions={
        <PrimaryButton href="https://eips.ethereum.org/EIPS/eip-7928">
          View EIP-7928
        </PrimaryButton>
      }
    >
      {/* Schema Tree Section */}
      <section id="schema-tree" className="not-prose mb-12">
        <AnchorHeading 
          id="schema-tree" 
          level={2} 
          className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6"
        >
          Interactive Schema Tree
        </AnchorHeading>
        <SchemaTree />
      </section>

      {/* Type Reference Section */}
      <section id="types" className="not-prose mb-12">
        <AnchorHeading 
          id="types" 
          level={2} 
          className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6"
        >
          Type Reference
        </AnchorHeading>
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6">
            <AnchorHeading 
              id="primitive-types" 
              level={3} 
              className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4"
            >
              Primitive Types
            </AnchorHeading>
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
            <AnchorHeading 
              id="constants" 
              level={3} 
              className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4"
            >
              Constants
            </AnchorHeading>
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
    </DocLayout>
  );
}
