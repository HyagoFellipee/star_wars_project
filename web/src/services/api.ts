import type {
  Character,
  CharacterSummary,
  Film,
  FilmSummary,
  PaginatedResponse,
  Planet,
  PlanetSummary,
  SearchParams,
  Starship,
  StarshipSummary,
  ApiErrorResponse,
} from '../types';
import { ApiError } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-key-change-me';

class SwapiApi {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = API_BASE, apiKey: string = API_KEY) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      let errorData: ApiErrorResponse;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error: 'UnknownError',
          message: `Request failed with status ${response.status}`,
        };
      }
      throw new ApiError(response.status, errorData.error, errorData.message);
    }

    return response.json();
  }

  private buildQueryString(params: SearchParams): string {
    const query = new URLSearchParams();

    if (params.page) query.set('page', params.page.toString());
    if (params.search) query.set('search', params.search);
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.order) query.set('order', params.order);

    const queryString = query.toString();
    return queryString ? `?${queryString}` : '';
  }

  // --- Characters ---

  async getCharacters(
    params: SearchParams = {}
  ): Promise<PaginatedResponse<CharacterSummary>> {
    return this.request(`/characters/${this.buildQueryString(params)}`);
  }

  async getCharacter(id: number, includeHomeworld = false): Promise<Character> {
    const query = includeHomeworld ? '?include_homeworld=true' : '';
    return this.request(`/characters/${id}${query}`);
  }

  async getCharacterFilms(id: number): Promise<FilmSummary[]> {
    return this.request(`/characters/${id}/films`);
  }

  // --- Planets ---

  async getPlanets(
    params: SearchParams = {}
  ): Promise<PaginatedResponse<PlanetSummary>> {
    return this.request(`/planets/${this.buildQueryString(params)}`);
  }

  async getPlanet(id: number): Promise<Planet> {
    return this.request(`/planets/${id}`);
  }

  async getPlanetResidents(id: number): Promise<CharacterSummary[]> {
    return this.request(`/planets/${id}/residents`);
  }

  async getPlanetFilms(id: number): Promise<FilmSummary[]> {
    return this.request(`/planets/${id}/films`);
  }

  // --- Starships ---

  async getStarships(
    params: SearchParams = {}
  ): Promise<PaginatedResponse<StarshipSummary>> {
    return this.request(`/starships/${this.buildQueryString(params)}`);
  }

  async getStarship(id: number): Promise<Starship> {
    return this.request(`/starships/${id}`);
  }

  async getStarshipPilots(id: number): Promise<CharacterSummary[]> {
    return this.request(`/starships/${id}/pilots`);
  }

  async getStarshipFilms(id: number): Promise<FilmSummary[]> {
    return this.request(`/starships/${id}/films`);
  }

  // --- Films ---

  async getFilms(
    params: SearchParams = {}
  ): Promise<PaginatedResponse<FilmSummary>> {
    return this.request(`/films/${this.buildQueryString(params)}`);
  }

  async getFilm(id: number): Promise<Film> {
    return this.request(`/films/${id}`);
  }

  async getFilmCharacters(id: number): Promise<CharacterSummary[]> {
    return this.request(`/films/${id}/characters`);
  }

  async getFilmPlanets(id: number): Promise<PlanetSummary[]> {
    return this.request(`/films/${id}/planets`);
  }

  async getFilmStarships(id: number): Promise<StarshipSummary[]> {
    return this.request(`/films/${id}/starships`);
  }
}

// Export singleton instance
export const api = new SwapiApi();

// Also export class for testing
export { SwapiApi };
