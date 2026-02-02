import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SectionLoader } from '../components';

export default function PlanetDetail() {
  const { id } = useParams<{ id: string }>();
  const planetId = Number(id);

  const {
    data: planet,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['planet', planetId],
    queryFn: () => api.getPlanet(planetId),
    enabled: !isNaN(planetId),
  });

  const { data: residents, isLoading: residentsLoading } = useQuery({
    queryKey: ['planet-residents', planetId],
    queryFn: () => api.getPlanetResidents(planetId),
    enabled: !isNaN(planetId),
  });

  const { data: films, isLoading: filmsLoading } = useQuery({
    queryKey: ['planet-films', planetId],
    queryFn: () => api.getPlanetFilms(planetId),
    enabled: !isNaN(planetId),
  });

  if (isLoading) {
    return <Loading message="Loading planet data..." />;
  }

  if (error || !planet) {
    return (
      <ErrorMessage
        title="Planet not found"
        message={error instanceof Error ? error.message : 'Could not find this planet'}
      />
    );
  }

  const formatPopulation = (pop: string) => {
    if (pop === 'unknown') return 'Unknown';
    const num = parseInt(pop, 10);
    if (isNaN(num)) return pop;
    return num.toLocaleString();
  };

  return (
    <div className="space-y-8">
      <Link
        to="/planets"
        className="inline-flex items-center text-gray-400 hover:text-sw-yellow transition-colors"
      >
        ← Back to Planets
      </Link>

      {/* Planet header */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h1 className="text-3xl font-bold text-white mb-2">{planet.name}</h1>
        <p className="text-sw-yellow">{planet.climate}</p>
      </div>

      {/* Planet details grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Physical characteristics */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Characteristics</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Terrain</dt>
              <dd className="text-white capitalize">{planet.terrain}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Climate</dt>
              <dd className="text-white capitalize">{planet.climate}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Population</dt>
              <dd className="text-white">{formatPopulation(planet.population)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Diameter</dt>
              <dd className="text-white">
                {planet.diameter !== 'unknown' ? `${parseInt(planet.diameter).toLocaleString()} km` : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Gravity</dt>
              <dd className="text-white">{planet.gravity}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Surface Water</dt>
              <dd className="text-white">
                {planet.surface_water !== 'unknown' ? `${planet.surface_water}%` : 'Unknown'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Orbital info */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Orbital Info</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Rotation Period</dt>
              <dd className="text-white">
                {planet.rotation_period !== 'unknown' ? `${planet.rotation_period} hours` : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Orbital Period</dt>
              <dd className="text-white">
                {planet.orbital_period !== 'unknown' ? `${planet.orbital_period} days` : 'Unknown'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Residents */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Notable Residents {!residentsLoading && residents && `(${residents.length})`}
        </h2>
        {residentsLoading ? (
          <SectionLoader itemCount={3} columns="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" />
        ) : residents && residents.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {residents.map((resident) => (
              <Link
                key={resident.id}
                to={`/characters/${resident.id}`}
                className="p-4 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-semibold text-white">{resident.name}</h3>
                <p className="text-gray-400 text-sm">{resident.birth_year}</p>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No residents found</p>
        )}
      </div>

      {/* Films */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          {filmsLoading ? 'Films' : `Featured in ${films?.length ?? 0} ${films?.length === 1 ? 'film' : 'films'}`}
        </h2>
        {filmsLoading ? (
          <SectionLoader itemCount={3} columns="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" />
        ) : films && films.length > 0 ? (
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
        ) : (
          <p className="text-gray-500 text-sm">No films found</p>
        )}
      </div>
    </div>
  );
}
