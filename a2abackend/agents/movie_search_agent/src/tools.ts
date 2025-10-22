import { ai } from "./genkit.js";
import { z } from "genkit";

// Hardcoded movie data for demo purposes
const HARDCODED_MOVIES = [
  {
    id: 1,
    title: "The Matrix",
    overview: "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
    release_date: "1999-03-30",
    vote_average: 8.2,
    poster_path: "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
    backdrop_path: "https://image.tmdb.org/t/p/w500/2u7zbn8EudG6kLlBzUYqP8RyFU4.jpg",
    genre_ids: [28, 878],
    adult: false,
    original_language: "en",
    original_title: "The Matrix",
    popularity: 85.5,
    video: false,
    vote_count: 23456
  },
  {
    id: 2,
    title: "Inception",
    overview: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
    release_date: "2010-07-16",
    vote_average: 8.4,
    poster_path: "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
    backdrop_path: "https://image.tmdb.org/t/p/w500/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
    genre_ids: [28, 878, 53],
    adult: false,
    original_language: "en",
    original_title: "Inception",
    popularity: 78.2,
    video: false,
    vote_count: 18923
  },
  {
    id: 3,
    title: "Interstellar",
    overview: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
    release_date: "2014-11-05",
    vote_average: 8.6,
    poster_path: "https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
    backdrop_path: "https://image.tmdb.org/t/p/w500/xu9zaAevzQ5nnrsXN6JcahLnG4i.jpg",
    genre_ids: [18, 878],
    adult: false,
    original_language: "en",
    original_title: "Interstellar",
    popularity: 72.8,
    video: false,
    vote_count: 15678
  },
  {
    id: 4,
    title: "The Dark Knight",
    overview: "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
    release_date: "2008-07-18",
    vote_average: 9.0,
    poster_path: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    backdrop_path: "https://image.tmdb.org/t/p/w500/hqkIcbrOHL86UncnHIsHVcVmzue.jpg",
    genre_ids: [28, 80, 18],
    adult: false,
    original_language: "en",
    original_title: "The Dark Knight",
    popularity: 91.3,
    video: false,
    vote_count: 28765
  },
  {
    id: 5,
    title: "Pulp Fiction",
    overview: "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
    release_date: "1994-10-14",
    vote_average: 8.9,
    poster_path: "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
    backdrop_path: "https://image.tmdb.org/t/p/w500/4cDFJr4HnXN5AdPw4AKrmLlMWdO.jpg",
    genre_ids: [80, 18],
    adult: false,
    original_language: "en",
    original_title: "Pulp Fiction",
    popularity: 67.4,
    video: false,
    vote_count: 19876
  }
];

const HARDCODED_PEOPLE = [
  {
    id: 1,
    name: "Leonardo DiCaprio",
    known_for_department: "Acting",
    profile_path: "https://image.tmdb.org/t/p/w500/5Brc5dLifH3UInk3wUaCuGxweCv.jpg",
    adult: false,
    gender: 2,
    known_for: [
      {
        id: 2,
        title: "Inception",
        overview: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        poster_path: "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        backdrop_path: "https://image.tmdb.org/t/p/w500/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
        media_type: "movie",
        adult: false,
        original_language: "en",
        original_title: "Inception",
        genre_ids: [28, 878, 53],
        popularity: 78.2,
        release_date: "2010-07-16",
        video: false,
        vote_average: 8.4,
        vote_count: 18923
      }
    ],
    popularity: 85.2
  },
  {
    id: 2,
    name: "Christopher Nolan",
    known_for_department: "Directing",
    profile_path: "https://image.tmdb.org/t/p/w500/5Brc5dLifH3UInk3wUaCuGxweCv.jpg",
    adult: false,
    gender: 2,
    known_for: [
      {
        id: 2,
        title: "Inception",
        overview: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        poster_path: "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        backdrop_path: "https://image.tmdb.org/t/p/w500/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
        media_type: "movie",
        adult: false,
        original_language: "en",
        original_title: "Inception",
        genre_ids: [28, 878, 53],
        popularity: 78.2,
        release_date: "2010-07-16",
        video: false,
        vote_average: 8.4,
        vote_count: 18923
      }
    ],
    popularity: 78.5
  }
];

// Helper function to simulate API delay
async function simulateApiDelay() {
  return new Promise(resolve => setTimeout(resolve, 100));
}

// Search for movies
export const searchMovies = ai.defineTool(
  {
    name: "searchMovies",
    description: "Search for movies by title, genre, or other criteria",
    inputSchema: z.object({
      query: z.string().describe("Search query for movies (title, genre, etc.)"),
    }),
  },
  async ({ query }: { query: string }) => {
    console.log("[movie_search:searchMovies]", JSON.stringify(query));
    try {
      // Simulate API delay
      await simulateApiDelay();

      // Filter hardcoded movies based on query
      const filteredMovies = HARDCODED_MOVIES.filter(movie => 
        movie.title.toLowerCase().includes(query.toLowerCase()) ||
        movie.overview.toLowerCase().includes(query.toLowerCase())
      );

      // If no matches, return all movies for demo purposes
      const results = filteredMovies.length > 0 ? filteredMovies : HARDCODED_MOVIES;

      return {
        page: 1,
        results: results,
        total_pages: 1,
        total_results: results.length
      };
    } catch (error) {
      console.error("Error searching movies:", error);
      throw error;
    }
  }
);

// Search for people (actors, directors, etc.)
export const searchPeople = ai.defineTool(
  {
    name: "searchPeople",
    description: "Search for actors, directors, and other people in the movie industry",
    inputSchema: z.object({
      query: z.string().describe("Search query for people (actor name, director, etc.)"),
    }),
  },
  async ({ query }: { query: string }) => {
    console.log("[movie_search:searchPeople]", JSON.stringify(query));
    try {
      // Simulate API delay
      await simulateApiDelay();

      // Filter hardcoded people based on query
      const filteredPeople = HARDCODED_PEOPLE.filter(person => 
        person.name.toLowerCase().includes(query.toLowerCase()) ||
        person.known_for_department.toLowerCase().includes(query.toLowerCase())
      );

      // If no matches, return all people for demo purposes
      const results = filteredPeople.length > 0 ? filteredPeople : HARDCODED_PEOPLE;

      return {
        page: 1,
        results: results,
        total_pages: 1,
        total_results: results.length
      };
    } catch (error) {
      console.error("Error searching people:", error);
      throw error;
    }
  }
);

// Get detailed information about a specific movie
export const getMovieDetails = ai.defineTool(
  {
    name: "getMovieDetails",
    description: "Get detailed information about a specific movie by its ID",
    inputSchema: z.object({
      movieId: z.number().describe("The movie ID"),
    }),
  },
  async ({ movieId }: { movieId: number }) => {
    console.log("[movie_search:getMovieDetails]", JSON.stringify({ movieId }));
    try {
      // Simulate API delay
      await simulateApiDelay();

      // Find movie by ID in hardcoded data
      const movie = HARDCODED_MOVIES.find(m => m.id === movieId);
      
      if (!movie) {
        throw new Error(`Movie with ID ${movieId} not found`);
      }

      // Return enhanced movie details
      return {
        ...movie,
        genres: [
          { id: 28, name: "Action" },
          { id: 878, name: "Science Fiction" },
          { id: 80, name: "Crime" },
          { id: 18, name: "Drama" }
        ].filter(genre => movie.genre_ids.includes(genre.id)),
        production_companies: [
          { id: 1, name: "Warner Bros.", logo_path: null, origin_country: "US" },
          { id: 2, name: "Legendary Pictures", logo_path: null, origin_country: "US" }
        ],
        production_countries: [
          { iso_3166_1: "US", name: "United States of America" }
        ],
        spoken_languages: [
          { iso_639_1: "en", name: "English" }
        ],
        credits: {
          cast: [
            { id: 1, name: "Leonardo DiCaprio", character: "Cobb", profile_path: "https://image.tmdb.org/t/p/w500/5Brc5dLifH3UInk3wUaCuGxweCv.jpg" },
            { id: 2, name: "Marion Cotillard", character: "Mal", profile_path: "https://image.tmdb.org/t/p/w500/5Brc5dLifH3UInk3wUaCuGxweCv.jpg" }
          ],
          crew: [
            { id: 1, name: "Christopher Nolan", job: "Director", department: "Directing", profile_path: "https://image.tmdb.org/t/p/w500/5Brc5dLifH3UInk3wUaCuGxweCv.jpg" }
          ]
        }
      };
    } catch (error) {
      console.error("Error getting movie details:", error);
      throw error;
    }
  }
);

// Get detailed information about a specific person
export const getPersonDetails = ai.defineTool(
  {
    name: "getPersonDetails",
    description: "Get detailed information about a specific person by their ID",
    inputSchema: z.object({
      personId: z.number().describe("The person ID"),
    }),
  },
  async ({ personId }: { personId: number }) => {
    console.log("[movie_search:getPersonDetails]", JSON.stringify({ personId }));
    try {
      // Simulate API delay
      await simulateApiDelay();

      // Find person by ID in hardcoded data
      const person = HARDCODED_PEOPLE.find(p => p.id === personId);
      
      if (!person) {
        throw new Error(`Person with ID ${personId} not found`);
      }

      // Return enhanced person details
      return {
        ...person,
        biography: person.name === "Leonardo DiCaprio" 
          ? "Leonardo Wilhelm DiCaprio is an American actor and film producer. Known for his work in biopics and period films, DiCaprio is the recipient of numerous accolades, including an Academy Award, a British Academy Film Award, and three Golden Globe Awards."
          : "Christopher Edward Nolan is a British-American filmmaker. Known for his cerebral, often nonlinear storytelling, acclaimed films include Memento, The Dark Knight trilogy, Inception, Interstellar, and Dunkirk.",
        birthday: person.name === "Leonardo DiCaprio" ? "1974-11-11" : "1970-07-30",
        place_of_birth: person.name === "Leonardo DiCaprio" ? "Los Angeles, California, USA" : "London, England, UK",
        movie_credits: {
          cast: [
            { id: 1, title: "Inception", character: "Cobb", release_date: "2010-07-16", vote_average: 8.4 },
            { id: 2, title: "The Revenant", character: "Hugh Glass", release_date: "2015-12-25", vote_average: 7.8 }
          ],
          crew: []
        },
        tv_credits: {
          cast: [],
          crew: []
        },
        images: {
          profiles: [
            { file_path: person.profile_path, width: 1000, height: 1500 }
          ]
        }
      };
    } catch (error) {
      console.error("Error getting person details:", error);
      throw error;
    }
  }
);
