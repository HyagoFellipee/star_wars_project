import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Loading, ErrorMessage, SearchBar, Pagination, Card } from '../components';
import { useCharacterImages } from '../hooks';
import type { SearchParams } from '../types';

export default function Characters() {
  const [params, setParams] = useState<SearchParams>({
    page: 1,
    search: '',
    sort_by: 'name',
    order: 'asc',
  });

  const getCharacterImage = useCharacterImages();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['characters', params],
    queryFn: () => api.getCharacters(params),
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
