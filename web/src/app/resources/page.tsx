import {
  ExternalLink,
  BookOpen,
  Code,
  Wrench,
  GraduationCap,
  FileText,
} from "lucide-react";
import DocLayout from "../../components/DocLayout";
import AnchorHeading from "../../components/AnchorHeading";
import SecondaryButton from "../../components/SecondaryButton";
import resourcesData from "../../data/resources.json";

const categoryIcons = {
  specifications: FileText,
  implementations: Code,
  tools: Wrench,
  research: BookOpen,
  tutorials: GraduationCap,
};

export default function ResourcesPage() {
  return (
    <DocLayout
      title="Resources"
      subtitle="Curated collection of BAL specifications, implementations, tools, and learning materials"
    >
      <div className="space-y-12">
        {resourcesData.categories.map((category) => {
          const IconComponent =
            categoryIcons[category.id as keyof typeof categoryIcons] ||
            FileText;

          return (
            <section id={category.id} key={category.id} className="not-prose">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-lime-100 dark:bg-lime-900/30 rounded-lg">
                  <IconComponent className="w-5 h-5 text-lime-600 dark:text-lime-400" />
                </div>
                <AnchorHeading
                  id={category.id}
                  level={2}
                  className="text-2xl font-bold text-gray-900 dark:text-gray-100"
                >
                  {category.title}
                </AnchorHeading>
              </div>

              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {category.description}
              </p>

              <div className="grid gap-4 lg:grid-cols-2">
                {category.resources.map((resource, index) => (
                  <div
                    key={index}
                    className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6 hover:border-lime-400 dark:hover:border-lime-500 transition-colors group"
                  >
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 group-hover:text-lime-600 dark:group-hover:text-lime-400 transition-colors">
                        {resource.title}
                      </h3>
                      <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-lime-500 transition-colors flex-shrink-0" />
                    </div>

                    <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm leading-relaxed">
                      {resource.description}
                    </p>

                    <div className="flex justify-end">
                      <SecondaryButton href={resource.url} external>
                        Visit
                      </SecondaryButton>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </DocLayout>
  );
}
