import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SearchBar, Pagination, Card, FilterSelect } from '../components';
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

export default function Planets() {
  const [params, setParams] = useState<SearchParams>({
    page: 1,
    search: '',
    sort_by: 'name',
    order: 'asc',
    climate: '',
    terrain: '',
    film_id: undefined,
  });

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['planets', params],
    queryFn: () => api.getPlanets(params),
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
        title="Failed to load planets"
        message={error instanceof Error ? error.message : 'Unknown error'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Planets</h1>
          <p className="text-gray-400 text-sm">
            {data?.count ?? 0} planets across the galaxy
          </p>
        </div>
        <div className="w-full sm:w-64">
          <SearchBar
            onSearch={handleSearch}
            placeholder="Search planets..."
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
          label="Climate"
          value={params.climate || ''}
          onChange={(v) => handleFilterChange('climate', v)}
          options={['arid', 'temperate', 'tropical', 'frozen', 'murky', 'hot', 'artificial temperate']}
        />
        <FilterSelect
          label="Terrain"
          value={params.terrain || ''}
          onChange={(v) => handleFilterChange('terrain', v)}
          options={['desert', 'grasslands', 'mountains', 'jungle', 'rainforests', 'tundra', 'ice caves', 'swamp', 'forests', 'lakes', 'ocean', 'cityscape']}
        />
      </div>

      {isLoading ? (
        <Loading message="Scanning the galaxy for planets..." />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.results.map((planet) => (
              <Card
                key={planet.id}
                to={`/planets/${planet.id}`}
                title={planet.name}
                subtitle={planet.climate}
                category="planet"
              >
                <span className="text-gray-500">{planet.terrain}</span>
              </Card>
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
