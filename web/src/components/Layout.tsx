import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { path: '/characters', label: 'Characters', icon: '👤' },
  { path: '/planets', label: 'Planets', icon: '🪐' },
  { path: '/starships', label: 'Starships', icon: '🚀' },
  { path: '/films', label: 'Films', icon: '🎬' },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-sw-dark border-b border-sw-gray">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <span className="text-sw-yellow font-display text-xl font-bold sw-glow">
                SWAPI
              </span>
              <span className="text-gray-400 text-sm hidden sm:inline">
                Explorer
              </span>
            </Link>

            <nav className="flex space-x-1 sm:space-x-4">
              {navItems.map((item) => {
                const isActive = location.pathname.startsWith(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors
                      ${
                        isActive
                          ? 'bg-sw-gray text-sw-yellow'
                          : 'text-gray-300 hover:text-white hover:bg-sw-gray/50'
                      }`}
                  >
                    <span className="mr-1 sm:mr-2">{item.icon}</span>
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-sw-dark border-t border-sw-gray py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            Case Técnico - PowerOfData | Data from{' '}
            <a
              href="https://swapi.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sw-yellow hover:underline"
            >
              SWAPI
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
