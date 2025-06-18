interface PrimaryButtonProps {
  href: string;
  children: React.ReactNode;
}

export default function PrimaryButton({ href, children }: PrimaryButtonProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex items-center space-x-2 px-4 py-2 bg-lime-500 text-black font-bold rounded-lg hover:bg-lime-400 transition-all duration-200 shadow-lg hover:shadow-xl"
    >
      <span>{children}</span>
      <div className="w-2 h-2 bg-black rounded-full group-hover:animate-bounce"></div>
    </a>
  );
}