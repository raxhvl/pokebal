import Link from "next/link";
import { ExternalLink, FileText } from "lucide-react";

interface SecondaryButtonProps {
  href: string;
  children: React.ReactNode;
  external?: boolean;
}

export default function SecondaryButton({
  href,
  children,
  external = false,
}: SecondaryButtonProps) {
  const isExternal = external || href.startsWith("http");

  const buttonContent = (
    <div className="flex items-center space-x-2">
      {!isExternal && (
        <FileText className="w-4 h-4 text-orange-500 group-hover:text-orange-400" />
      )}
      <span className="font-mono text-xs text-gray-600 dark:text-gray-400 group-hover:text-gray-800 dark:group-hover:text-gray-200">
        {children}
      </span>
      {isExternal && (
        <ExternalLink className="w-4 h-4 text-orange-500 group-hover:text-orange-400" />
      )}
    </div>
  );

  const baseClasses =
    "group inline-block px-3 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:border-orange-400 dark:hover:border-orange-500 transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg";

  if (isExternal) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className={baseClasses}
      >
        {buttonContent}
      </a>
    );
  }

  return (
    <Link href={href} className={baseClasses}>
      {buttonContent}
    </Link>
  );
}
