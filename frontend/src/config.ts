// Configuration for API endpoints
const isDevelopment = process.env.NODE_ENV === 'development';
const isVercel = process.env.VERCEL === '1';

// Determine the API base URL
let API_BASE_URL: string;

if (isDevelopment) {
  // Local development
  API_BASE_URL = 'http://127.0.0.1:8006';
} else if (isVercel) {
  // Vercel production deployment
  API_BASE_URL = window.location.origin;
} else {
  // Fallback for other production environments
  API_BASE_URL = window.location.origin;
}

export const config = {
  API_BASE_URL,
  isDevelopment,
  isVercel
};

export default config;
