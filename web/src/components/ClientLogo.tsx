interface ClientLogoProps {
  logo?: string;
  name: string;
  size?: 'small' | 'medium' | 'large';
}

export default function ClientLogo({ logo, name, size = 'medium' }: ClientLogoProps) {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12', 
    large: 'w-16 h-16'
  };

  if (!logo) {
    return (
      <div className={`${sizeClasses[size]} bg-gradient-to-br from-lime-400 to-lime-600 rounded-lg flex items-center justify-center`}>
        <span className="text-white font-bold text-xs">
          {name.charAt(0)}
        </span>
      </div>
    );
  }

  return (
    <div className={`${sizeClasses[size]} relative`}>
      <img 
        src={logo}
        alt={`${name} logo`}
        className={`${sizeClasses[size]} object-contain`}
      />
      <div className={`${sizeClasses[size]} absolute inset-0 bg-gradient-to-br from-lime-400 to-lime-600 rounded-lg flex items-center justify-center opacity-0 group-[.error]:opacity-100`}>
        <span className="text-white font-bold text-xs">
          {name.charAt(0)}
        </span>
      </div>
    </div>
  );
}