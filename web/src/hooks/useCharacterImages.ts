import { useQuery } from '@tanstack/react-query';

interface AkababCharacter {
  id: number;
  name: string;
  image: string;
}

const AKABAB_API_URL = 'https://rawcdn.githack.com/akabab/starwars-api/0.2.1/api/all.json';

export function useCharacterImages() {
  const { data: imageMap } = useQuery({
    queryKey: ['character-images'],
    queryFn: async () => {
      const response = await fetch(AKABAB_API_URL);
      const characters: AkababCharacter[] = await response.json();
      return new Map(characters.map(c => [c.id, c.image]));
    },
    staleTime: Infinity,
  });

  return (id: number): string | undefined => imageMap?.get(id);
}
