import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SearchBar, Pagination, Card } from '../components';
import type { SearchParams } from '../types';

export default function Starships() {
  const [params, setParams] = useState<SearchParams>({
    page: 1,
    search: '',
    sort_by: 'name',
    order: 'asc',
  });

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['starships', params],
    queryFn: () => api.getStarships(params),
  });

  const handleSearch = useCallback((query: string) => {
    setParams((prev) => ({ ...prev, search: query, page: 1 }));
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setParams((prev) => ({ ...prev, page }));
  }, []);

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load starships"
        message={error instanceof Error ? error.message : 'Unknown error'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Starships</h1>
          <p className="text-gray-400 text-sm">
            {data?.count ?? 0} starships in the fleet
          </p>
        </div>
        <div className="w-full sm:w-64">
          <SearchBar
            onSearch={handleSearch}
            placeholder="Search starships..."
            initialValue={params.search}
          />
        </div>
      </div>

      {isLoading ? (
        <Loading message="Scanning for starships..." />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.results.map((starship) => (
              <Card
                key={starship.id}
                to={`/starships/${starship.id}`}
                title={starship.name}
                subtitle={starship.model}
                badge={starship.starship_class}
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
