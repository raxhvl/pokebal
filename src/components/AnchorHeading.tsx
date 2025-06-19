import { Link } from "lucide-react";
import { ReactNode } from "react";

interface AnchorHeadingProps {
  id: string;
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  className?: string;
  children: ReactNode;
}

export default function AnchorHeading({ 
  id, 
  level = 2, 
  className = "", 
  children 
}: AnchorHeadingProps) {
  const Tag = `h${level}` as keyof JSX.IntrinsicElements;
  
  return (
    <Tag id={id} className={`group relative ${className}`}>
      <a 
        href={`#${id}`} 
        className="hover:text-lime-500 transition-colors flex items-center gap-2"
      >
        {children}
        <Link 
          className="w-4 h-4 opacity-0 group-hover:opacity-50 transition-opacity" 
          aria-hidden="true"
        />
      </a>
    </Tag>
  );
}