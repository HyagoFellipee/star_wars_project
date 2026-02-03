import { Link } from 'react-router-dom';

const resources = [
  {
    path: '/characters',
    title: 'Characters',
    description: 'Explore heroes, villains, and everyone in between',
    icon: '👤',
    count: '82+',
  },
  {
    path: '/planets',
    title: 'Planets',
    description: 'From desert worlds to frozen wastelands',
    icon: '🪐',
    count: '60+',
  },
  {
    path: '/starships',
    title: 'Starships',
    description: 'The fastest ships in the galaxy',
    icon: '🚀',
    count: '36+',
  },
  {
    path: '/films',
    title: 'Films',
    description: 'The complete saga',
    icon: '🎬',
    count: '6',
  },
];

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero section */}
      <div className="text-center py-12">
        <h1 className="text-4xl sm:text-5xl font-display font-bold text-sw-yellow sw-glow mb-4">
          STAR WARS
        </h1>
        <h2 className="text-xl sm:text-2xl text-gray-300 mb-2">
          API Explorer
        </h2>
        <p className="text-gray-500 max-w-2xl mx-auto">
          Explore the Star Wars universe through data. Search characters,
          discover planets, examine starships, and dive into the films.
        </p>
      </div>

      {/* Resource cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {resources.map((resource) => (
          <Link
            key={resource.path}
            to={resource.path}
            className="group bg-sw-dark border border-sw-gray rounded-xl p-6
                       card-hover hover:border-sw-yellow/50"
          >
            <div className="text-4xl mb-4">{resource.icon}</div>
            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-sw-yellow transition-colors">
              {resource.title}
            </h3>
            <p className="text-gray-400 text-sm mb-4">{resource.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-sw-yellow font-mono">{resource.count}</span>
              <span className="text-gray-500 group-hover:text-sw-yellow transition-colors">
                Explore →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {/* About section */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6 sm:p-8">
        <h2 className="text-xl font-bold text-white mb-4">About this project</h2>
        <p className="text-gray-400 mb-4">
          This API explorer consumes the{' '}
          <a
            href="https://swapi.dev"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sw-yellow hover:underline"
          >
            Star Wars API (SWAPI)
          </a>{' '}
          and provides a clean interface for exploring the data.
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1 bg-sw-gray rounded-full text-sm text-gray-300">
            React
          </span>
          <span className="px-3 py-1 bg-sw-gray rounded-full text-sm text-gray-300">
            TypeScript
          </span>
          <span className="px-3 py-1 bg-sw-gray rounded-full text-sm text-gray-300">
            FastAPI
          </span>
          <span className="px-3 py-1 bg-sw-gray rounded-full text-sm text-gray-300">
            Tailwind CSS
          </span>
        </div>
      </div>
    </div>
  );
}
