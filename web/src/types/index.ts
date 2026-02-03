// --- API Response Types ---

export interface PaginatedResponse<T> {
  count: number;
  page: number;
  total_pages: number;
  next_page: number | null;
  previous_page: number | null;
  results: T[];
}

// --- Character Types ---

export interface CharacterSummary {
  id: number;
  name: string;
  gender: string;
  birth_year: string;
}

export interface Character extends CharacterSummary {
  height: string;
  mass: string;
  hair_color: string;
  skin_color: string;
  eye_color: string;
  homeworld_url: string;
  homeworld?: Planet;
  film_urls: string[];
  films_data: FilmSummary[];
  species_urls: string[];
  vehicle_urls: string[];
  starship_urls: string[];
}

// --- Planet Types ---

export interface PlanetSummary {
  id: number;
  name: string;
  climate: string;
  terrain: string;
}

export interface Planet extends PlanetSummary {
  rotation_period: string;
  orbital_period: string;
  diameter: string;
  gravity: string;
  surface_water: string;
  population: string;
  resident_urls: string[];
  residents_data: CharacterSummary[];
  film_urls: string[];
  films_data: FilmSummary[];
}

// --- Starship Types ---

export interface StarshipSummary {
  id: number;
  name: string;
  model: string;
  starship_class: string;
}

export interface Starship extends StarshipSummary {
  manufacturer: string;
  cost_in_credits: string;
  length: string;
  max_atmosphering_speed: string;
  crew: string;
  passengers: string;
  cargo_capacity: string;
  consumables: string;
  hyperdrive_rating: string;
  MGLT: string;
  pilot_urls: string[];
  pilots_data: CharacterSummary[];
  film_urls: string[];
  films_data: FilmSummary[];
}

// --- Film Types ---

export interface FilmSummary {
  id: number;
  title: string;
  episode_id: number;
  release_date: string;
}

export interface Film extends FilmSummary {
  opening_crawl: string;
  director: string;
  producer: string;
  character_urls: string[];
  characters_data: CharacterSummary[];
  planet_urls: string[];
  planets_data: PlanetSummary[];
  starship_urls: string[];
  starships_data: StarshipSummary[];
  vehicle_urls: string[];
  species_urls: string[];
}

// --- Search/Filter Types ---

export type SortOrder = 'asc' | 'desc';

export interface SearchParams {
  page?: number;
  search?: string;
  sort_by?: string;
  order?: SortOrder;
  // Character filters
  gender?: string;
  eye_color?: string;
  hair_color?: string;
  skin_color?: string;
  film_id?: number;
  // Planet filters
  climate?: string;
  terrain?: string;
  // Starship filters
  starship_class?: string;
  manufacturer?: string;
  // Film filters
  director?: string;
  producer?: string;
}

// --- API Error Types ---

export interface ApiErrorResponse {
  error: string;
  message: string;
  path?: string;
  request_id?: string;
}

export class ApiError extends Error {
  status: number;
  errorType: string;

  constructor(status: number, errorType: string, message: string) {
    super(message);
    this.status = status;
    this.errorType = errorType;
    this.name = 'ApiError';
  }
}

// --- Resource type union for generic components ---

export type ResourceType = 'characters' | 'planets' | 'starships' | 'films';

export type ResourceSummary = CharacterSummary | PlanetSummary | StarshipSummary | FilmSummary;
export type Resource = Character | Planet | Starship | Film;
