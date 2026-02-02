import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SectionLoader } from '../components';
import { useCharacterImages } from '../hooks';

export default function CharacterDetail() {
  const { id } = useParams<{ id: string }>();
  const characterId = Number(id);
  const getCharacterImage = useCharacterImages();

  const {
    data: character,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['character', characterId],
    queryFn: () => api.getCharacter(characterId, true),
    enabled: !isNaN(characterId),
  });

  const { data: films, isLoading: filmsLoading } = useQuery({
    queryKey: ['character-films', characterId],
    queryFn: () => api.getCharacterFilms(characterId),
    enabled: !isNaN(characterId),
  });

  if (isLoading) {
    return <Loading message="Loading character data..." />;
  }

  if (error || !character) {
    return (
      <ErrorMessage
        title="Character not found"
        message={error instanceof Error ? error.message : 'Could not find this character'}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Back link */}
      <Link
        to="/characters"
        className="inline-flex items-center text-gray-400 hover:text-sw-yellow transition-colors"
      >
        ← Back to Characters
      </Link>

      {/* Character header */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6 flex gap-6">
        {getCharacterImage(characterId) && (
          <div className="w-32 h-40 flex-shrink-0 overflow-hidden rounded-lg bg-sw-darker flex items-center justify-center">
            <img
              src={getCharacterImage(characterId)}
              alt={character.name}
              className="max-w-full max-h-full object-contain"
            />
          </div>
        )}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{character.name}</h1>
          <p className="text-sw-yellow">{character.birth_year}</p>
        </div>
      </div>

      {/* Character details grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Physical attributes */}
        <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Physical Attributes</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-400">Height</dt>
              <dd className="text-white">
                {character.height !== 'unknown' ? `${character.height} cm` : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Mass</dt>
              <dd className="text-white">
                {character.mass !== 'unknown' ? `${character.mass} kg` : 'Unknown'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Gender</dt>
              <dd className="text-white capitalize">{character.gender}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Hair Color</dt>
              <dd className="text-white capitalize">{character.hair_color}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Eye Color</dt>
              <dd className="text-white capitalize">{character.eye_color}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-400">Skin Color</dt>
              <dd className="text-white capitalize">{character.skin_color}</dd>
            </div>
          </dl>
        </div>

        {/* Homeworld */}
        {character.homeworld && (
          <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Homeworld</h2>
            <Link
              to={`/planets/${character.homeworld.id}`}
              className="block p-4 bg-sw-darker rounded-lg hover:border-sw-yellow border border-transparent transition-colors"
            >
              <h3 className="text-xl font-semibold text-sw-yellow">
                {character.homeworld.name}
              </h3>
              <p className="text-gray-400 text-sm mt-1">
                {character.homeworld.climate} · {character.homeworld.terrain}
              </p>
            </Link>
          </div>
        )}
      </div>

      {/* Films */}
      <div className="bg-sw-dark border border-sw-gray rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          {filmsLoading ? 'Films' : `Appears in ${films?.length ?? 0} ${films?.length === 1 ? 'film' : 'films'}`}
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
                <p className="text-gray-400 text-sm">
                  Episode {film.episode_id} · {film.release_date}
                </p>
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
