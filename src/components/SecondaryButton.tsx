interface SecondaryButtonProps {
  href: string;
  children: React.ReactNode;
}

export default function SecondaryButton({ href, children }: SecondaryButtonProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group inline-block px-3 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 hover:border-orange-400 dark:hover:border-orange-500 transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg"
    >
      <div className="flex items-center space-x-2">
        <svg className="w-4 h-4 text-orange-500 group-hover:text-orange-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4v3c0 .6.4 1 1 1 .2 0 .5-.1.7-.3L14.6 18H20c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
        </svg>
        <span className="font-mono text-xs text-gray-600 dark:text-gray-400 group-hover:text-gray-800 dark:group-hover:text-gray-200">
          {children}
        </span>
      </div>
    </a>
  );
}