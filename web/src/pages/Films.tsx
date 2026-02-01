import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SearchBar, Card } from '../components';
import type { SearchParams } from '../types';

export default function Films() {
  const [params, setParams] = useState<SearchParams>({
    page: 1,
    search: '',
    sort_by: 'episode_id',
    order: 'asc',
  });

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['films', params],
    queryFn: () => api.getFilms(params),
  });

  const handleSearch = useCallback((query: string) => {
    setParams((prev) => ({ ...prev, search: query, page: 1 }));
  }, []);

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load films"
        message={error instanceof Error ? error.message : 'Unknown error'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Films</h1>
          <p className="text-gray-400 text-sm">
            The complete Star Wars saga
          </p>
        </div>
        <div className="w-full sm:w-64">
          <SearchBar
            onSearch={handleSearch}
            placeholder="Search films..."
            initialValue={params.search}
          />
        </div>
      </div>

      {isLoading ? (
        <Loading message="Loading the saga..." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.results.map((film) => (
            <Card
              key={film.id}
              to={`/films/${film.id}`}
              title={film.title}
              subtitle={film.release_date}
              badge={`Episode ${film.episode_id}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
