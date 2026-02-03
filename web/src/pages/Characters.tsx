import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SearchBar, Pagination, Card, FilterSelect } from '../components';
import { useCharacterImages } from '../hooks';
import type { SearchParams } from '../types';

// Film options for filter (id -> title)
const FILM_OPTIONS = [
  { id: '4', label: 'Episode I - The Phantom Menace' },
  { id: '5', label: 'Episode II - Attack of the Clones' },
  { id: '6', label: 'Episode III - Revenge of the Sith' },
  { id: '1', label: 'Episode IV - A New Hope' },
  { id: '2', label: 'Episode V - The Empire Strikes Back' },
  { id: '3', label: 'Episode VI - Return of the Jedi' },
];

export default function Characters() {
  const [params, setParams] = useState<SearchParams>({
    page: 1,
    search: '',
    sort_by: 'name',
    order: 'asc',
    gender: '',
    eye_color: '',
    hair_color: '',
    skin_color: '',
    film_id: undefined,
  });

  const getCharacterImage = useCharacterImages();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['characters', params],
    queryFn: () => api.getCharacters(params),
  });

  const handleSearch = useCallback((query: string) => {
    setParams((prev) => ({ ...prev, search: query, page: 1 }));
  }, []);

  const handleFilterChange = useCallback((field: string, value: string) => {
    if (field === 'film_id') {
      setParams((prev) => ({ ...prev, film_id: value ? Number(value) : undefined, page: 1 }));
    } else {
      setParams((prev) => ({ ...prev, [field]: value || undefined, page: 1 }));
    }
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setParams((prev) => ({ ...prev, page }));
  }, []);

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load characters"
        message={error instanceof Error ? error.message : 'Unknown error'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Characters</h1>
          <p className="text-gray-400 text-sm">
            {data?.count ?? 0} characters in the Star Wars universe
          </p>
        </div>
        <div className="w-full sm:w-64">
          <SearchBar
            onSearch={handleSearch}
            placeholder="Search characters..."
            initialValue={params.search}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <select
          value={params.film_id?.toString() || ''}
          onChange={(e) => handleFilterChange('film_id', e.target.value)}
          aria-label="Film"
          className="bg-sw-dark border border-sw-gray rounded-lg px-3 py-2 text-sm text-white
                     focus:border-sw-yellow focus:outline-none focus:ring-1 focus:ring-sw-yellow
                     hover:border-sw-gray/70 transition-colors cursor-pointer"
        >
          <option value="">All Films</option>
          {FILM_OPTIONS.map((film) => (
            <option key={film.id} value={film.id}>{film.label}</option>
          ))}
        </select>
        <FilterSelect
          label="Gender"
          value={params.gender || ''}
          onChange={(v) => handleFilterChange('gender', v)}
          options={['male', 'female', 'n/a', 'hermaphrodite']}
        />
        <FilterSelect
          label="Eye Color"
          value={params.eye_color || ''}
          onChange={(v) => handleFilterChange('eye_color', v)}
          options={['blue', 'brown', 'yellow', 'red', 'black', 'orange', 'hazel', 'pink', 'gold', 'green', 'white']}
        />
        <FilterSelect
          label="Hair Color"
          value={params.hair_color || ''}
          onChange={(v) => handleFilterChange('hair_color', v)}
          options={['blond', 'brown', 'black', 'auburn', 'white', 'grey', 'none']}
        />
        <FilterSelect
          label="Skin Color"
          value={params.skin_color || ''}
          onChange={(v) => handleFilterChange('skin_color', v)}
          options={['fair', 'gold', 'white', 'light', 'green', 'pale', 'metal', 'dark', 'brown', 'grey', 'blue', 'red', 'yellow', 'tan', 'orange']}
        />
      </div>

      {isLoading ? (
        <Loading message="Fetching characters from a galaxy far, far away..." />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.results.map((character) => (
              <Card
                key={character.id}
                to={`/characters/${character.id}`}
                title={character.name}
                badge={character.birth_year}
                image={getCharacterImage(character.id)}
                category="character"
              />
            ))}
          </div>

          {data && (
            <Pagination
              currentPage={data.page}
              totalPages={data.total_pages}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </div>
  );
}
