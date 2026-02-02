import { ReactNode, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PlaceholderImage from './PlaceholderImage';

type Category = 'character' | 'film' | 'starship' | 'planet';

interface CardProps {
  to: string;
  title: string;
  subtitle?: string;
  children?: ReactNode;
  badge?: string;
  image?: string;
  aspectRatio?: string;
  category?: Category;
}

export default function Card({ to, title, subtitle, children, badge, image, aspectRatio, category }: CardProps) {
  const [imgStatus, setImgStatus] = useState<'loading' | 'valid' | 'error'>(image ? 'loading' : 'error');

  // Validate image URL with fetch to check HTTP status (404 = error)
  useEffect(() => {
    if (!image) {
      setImgStatus('error');
      return;
    }

    setImgStatus('loading');

    // Try to fetch with cors to get the real HTTP status
    fetch(image, { method: 'HEAD' })
      .then((response) => {
        if (response.ok) {
          setImgStatus('valid');
        } else {
          // 404 or other error status
          setImgStatus('error');
        }
      })
      .catch(() => {
        // CORS error - fallback to loading image directly
        const img = new Image();
        img.onload = () => setImgStatus('valid');
        img.onerror = () => setImgStatus('error');
        img.src = image;
      });
  }, [image]);

  const showImage = imgStatus === 'valid';
  const showPlaceholder = category && imgStatus !== 'valid';

  return (
    <Link
      to={to}
      className="block bg-sw-dark border border-sw-gray rounded-lg overflow-hidden
                 card-hover hover:border-sw-yellow/50"
    >
      {showImage && (
        <div
          className="overflow-hidden bg-sw-darker flex items-center justify-center"
          style={aspectRatio ? { aspectRatio } : { height: '12rem' }}
        >
          <img
            src={image}
            alt={title}
            className={aspectRatio ? "w-full h-full object-cover" : "max-w-full max-h-full object-contain"}
          />
        </div>
      )}
      {showPlaceholder && (
        <PlaceholderImage category={category} aspectRatio={aspectRatio} />
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
