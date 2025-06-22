import Link from "next/link";
import { ExternalLink } from "lucide-react";

interface PrimaryButtonProps {
  href: string;
  children: React.ReactNode;
  external?: boolean;
}

export default function PrimaryButton({
  href,
  children,
  external = false,
}: PrimaryButtonProps) {
  const isExternal = external || href.startsWith("http");

  const buttonContent = (
    <>
      <span>{children}</span>
      {isExternal ? (
        <ExternalLink className="w-4 h-4 text-black group-hover:text-gray-800" />
      ) : (
        <div className="w-2 h-2 bg-black rounded-full group-hover:animate-bounce"></div>
      )}
    </>
  );

  const baseClasses =
    "group flex items-center space-x-2 px-4 py-2 bg-lime-500 text-black font-bold rounded-lg hover:bg-lime-400 transition-all duration-200 shadow-lg hover:shadow-xl";

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
