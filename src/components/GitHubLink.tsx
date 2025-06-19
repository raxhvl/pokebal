import { Github } from "lucide-react";

export default function GitHubLink() {
  return (
    <a
      href="https://github.com/raxhvl/pokebal"
      target="_blank"
      rel="noopener noreferrer"
      className="absolute top-8 right-8 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors duration-200"
      title="View on GitHub"
    >
      <Github className="w-5 h-5" />
    </a>
  );
}