import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface CardProps {
  to: string;
  title: string;
  subtitle?: string;
  children?: ReactNode;
  badge?: string;
}

export default function Card({ to, title, subtitle, children, badge }: CardProps) {
  return (
    <Link
      to={to}
      className="block bg-sw-dark border border-sw-gray rounded-lg p-4
                 card-hover hover:border-sw-yellow/50"
    >
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
    </Link>
  );
}
