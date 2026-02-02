import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage } from '../components';

// TMDB poster paths for Star Wars films
const FILM_POSTERS: Record<number, string> = {
  1: '/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg', // A New Hope
  2: '/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg', // Empire Strikes Back
  3: '/jQYlydvHm3kUix1f8prMucrplhm.jpg', // Return of the Jedi
  4: '/6wkfovpn7Eq8dYNKaG5PY3q2oq6.jpg', // Phantom Menace
  5: '/oZNPzxqM2s5DyVWab09NTQScDQt.jpg', // Attack of the Clones
  6: '/xfSAoBEm9MNBjmlNcDYLvLSMlnq.jpg', // Revenge of the Sith
};

const getFilmPoster = (filmId: number): string | undefined => {
  const posterPath = FILM_POSTERS[filmId];
  return posterPath ? `https://image.tmdb.org/t/p/w500${posterPath}` : undefined;
};

export default function FilmDetail() {
  const { id } = useParams<{ id: string }>();
  const filmId = Number(id);

  const {
    data: film,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['film', filmId],
    queryFn: () => api.getFilm(filmId),
    enabled: !isNaN(filmId),
  });

  const { data: characters } = useQuery({
    queryKey: ['film-characters', filmId],
    queryFn: () => api.getFilmCharacters(filmId),
    enabled: !isNaN(filmId),
  });

  const { data: planets } = useQuery({
    queryKey: ['film-planets', filmId],
    queryFn: () => api.getFilmPlanets(filmId),
    enabled: !isNaN(filmId),
  });

  const { data: starships } = useQuery({
    queryKey: ['film-starships', filmId],
    queryFn: () => api.getFilmStarships(filmId),
    enabled: !isNaN(filmId),
  });

  if (isLoading) {
    return <Loading message="Loading film data..." />;
  }

  if (error || !film) {
    return (
      <ErrorMessage
        title="Film not found"
        message={error instanceof Error ? error.message : 'Could not find this film'}
      />
    );
  }

  return (
    <div className="space-y-8">
      <Link
        to="/films"
        className="inline-flex items-center text-gray-400 hover:text-sw-yellow transition-colors"
      >
        ← Back to Films
      </Link>

      {/* Film header */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6 flex gap-6">
        {getFilmPoster(filmId) && (
          <div className="w-32 flex-shrink-0 overflow-hidden rounded-lg bg-sw-darker">
            <img
              src={getFilmPoster(filmId)}
              alt={film.title}
              className="w-full object-contain"
            />
          </div>
        )}
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{film.title}</h1>
              <p className="text-sw-yellow">Episode {film.episode_id}</p>
            </div>
            <span className="text-gray-400">{film.release_date}</span>
          </div>
        </div>
      </div>

      {/* Opening crawl */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Opening Crawl</h2>
        <p className="text-gray-300 whitespace-pre-line leading-relaxed font-mono text-sm">
          {film.opening_crawl}
        </p>
      </div>

      {/* Film details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Details</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Director</dt>
              <dd className="text-white">{film.director}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Producer</dt>
              <dd className="text-white text-right max-w-[60%]">{film.producer}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Release Date</dt>
              <dd className="text-white">{film.release_date}</dd>
            </div>
          </dl>
        </div>

        {/* Stats */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Featured</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Characters</dt>
              <dd className="text-sw-yellow">{characters?.length ?? 0}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Planets</dt>
              <dd className="text-sw-yellow">{planets?.length ?? 0}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Starships</dt>
              <dd className="text-sw-yellow">{starships?.length ?? 0}</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Characters */}
      {characters && characters.length > 0 && (
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Characters ({characters.length})
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {characters.map((character) => (
              <Link
                key={character.id}
                to={`/characters/${character.id}`}
                className="p-3 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-medium text-white text-sm truncate">
                  {character.name}
                </h3>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Planets */}
      {planets && planets.length > 0 && (
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Planets ({planets.length})
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {planets.map((planet) => (
              <Link
                key={planet.id}
                to={`/planets/${planet.id}`}
                className="p-3 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-medium text-white text-sm">{planet.name}</h3>
                <p className="text-gray-500 text-xs mt-1">{planet.climate}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Starships */}
      {starships && starships.length > 0 && (
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Starships ({starships.length})
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {starships.map((starship) => (
              <Link
                key={starship.id}
                to={`/starships/${starship.id}`}
                className="p-3 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
              >
                <h3 className="font-medium text-white text-sm truncate">
                  {starship.name}
                </h3>
                <p className="text-gray-500 text-xs mt-1 truncate">
                  {starship.starship_class}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
