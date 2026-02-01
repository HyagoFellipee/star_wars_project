import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage } from '../components';

export default function StarshipDetail() {
  const { id } = useParams<{ id: string }>();
  const starshipId = Number(id);

  const {
    data: starship,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['starship', starshipId],
    queryFn: () => api.getStarship(starshipId),
    enabled: !isNaN(starshipId),
  });

  const { data: pilots } = useQuery({
    queryKey: ['starship-pilots', starshipId],
    queryFn: () => api.getStarshipPilots(starshipId),
    enabled: !isNaN(starshipId),
  });

  const { data: films } = useQuery({
    queryKey: ['starship-films', starshipId],
    queryFn: () => api.getStarshipFilms(starshipId),
    enabled: !isNaN(starshipId),
  });

  if (isLoading) {
    return <Loading message="Loading starship data..." />;
  }

  if (error || !starship) {
    return (
      <ErrorMessage
        title="Starship not found"
        message={error instanceof Error ? error.message : 'Could not find this starship'}
      />
    );
  }

  const formatCredits = (credits: string) => {
    if (credits === 'unknown') return 'Unknown';
    const num = parseInt(credits, 10);
    if (isNaN(num)) return credits;
    return `${num.toLocaleString()} credits`;
  };

  return (
    <div className="space-y-8">
      <Link
        to="/starships"
        className="inline-flex items-center text-gray-400 hover:text-sw-yellow transition-colors"
      >
        ← Back to Starships
      </Link>

      {/* Starship header */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h1 className="text-3xl font-bold text-white mb-2">{starship.name}</h1>
        <p className="text-sw-yellow">{starship.model}</p>
        <p className="text-gray-400 text-sm mt-1">{starship.starship_class}</p>
      </div>

      {/* Starship details grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Specifications */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Specifications</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Manufacturer</dt>
              <dd className="text-white text-right max-w-[60%]">{starship.manufacturer}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Cost</dt>
              <dd className="text-white">{formatCredits(starship.cost_in_credits)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Length</dt>
              <dd className="text-white">
                {starship.length !== 'unknown' ? `${starship.length}m` : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Max Speed</dt>
              <dd className="text-white">
                {starship.max_atmosphering_speed !== 'n/a'
                  ? starship.max_atmosphering_speed
                  : 'N/A'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Hyperdrive Rating</dt>
              <dd className="text-white">{starship.hyperdrive_rating}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">MGLT</dt>
              <dd className="text-white">{starship.MGLT}</dd>
            </div>
          </dl>
        </div>

        {/* Capacity */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Capacity</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Crew</dt>
              <dd className="text-white">{starship.crew}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Passengers</dt>
              <dd className="text-white">{starship.passengers}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Cargo Capacity</dt>
              <dd className="text-white">
                {starship.cargo_capacity !== 'unknown'
                  ? `${parseInt(starship.cargo_capacity).toLocaleString()} kg`
                  : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Consumables</dt>
              <dd className="text-white">{starship.consumables}</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Pilots */}
      {pilots && pilots.length > 0 && (
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Pilots ({pilots.length})
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {pilots.map((pilot) => (
              <Link
                key={pilot.id}
                to={`/characters/${pilot.id}`}
                className="p-4 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-semibold text-white">{pilot.name}</h3>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Films */}
      {films && films.length > 0 && (
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Appears in {films.length} {films.length === 1 ? 'film' : 'films'}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {films.map((film) => (
              <Link
                key={film.id}
                to={`/films/${film.id}`}
                className="p-4 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-semibold text-white">{film.title}</h3>
                <p className="text-gray-400 text-sm">Episode {film.episode_id}</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
