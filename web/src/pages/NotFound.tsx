import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="text-6xl mb-6">🌑</div>
      <h1 className="text-4xl font-bold text-white mb-4">
        404
      </h1>
      <p className="text-xl text-gray-400 mb-2">
        This is not the page you're looking for
      </p>
      <p className="text-gray-500 mb-8">
        The page you requested could not be found in this galaxy.
      </p>
      <Link
        to="/"
        className="px-6 py-3 bg-sw-yellow text-sw-black font-semibold rounded-lg
                   hover:bg-yellow-400 transition-colors"
      >
        Return to Home
      </Link>
    </div>
  );
}
