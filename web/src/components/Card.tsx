import { ReactNode, useState } from 'react';
import { Link } from 'react-router-dom';

interface CardProps {
  to: string;
  title: string;
  subtitle?: string;
  children?: ReactNode;
  badge?: string;
  image?: string;
}

export default function Card({ to, title, subtitle, children, badge, image }: CardProps) {
  const [imgError, setImgError] = useState(false);

  return (
    <Link
      to={to}
      className="block bg-sw-dark border border-sw-gray rounded-lg overflow-hidden
                 card-hover hover:border-sw-yellow/50"
    >
      {image && !imgError && (
        <div className="h-40 overflow-hidden bg-sw-gray">
          <img
            src={image}
            alt={title}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-white truncate pr-2">
            {title}
          </h3>
          {badge && (
            <span className="text-xs px-2 py-1 bg-sw-gray rounded text-sw-yellow">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-gray-400 text-sm mb-2">{subtitle}</p>
        )}
        {children && (
          <div className="text-gray-500 text-sm">{children}</div>
        )}
      </div>
    </Link>
  );
}
