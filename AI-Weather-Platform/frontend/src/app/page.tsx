"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";
import type { WeatherMapProps } from "./components/WeatherMap";
import "./globals.css";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  City,
  Country,
  State,
} from "country-state-city";

// ============================================================
// BACKEND CONFIG
// ============================================================

const BACKEND_URL = "http://127.0.0.1:8000";
const WEATHER_API = `${BACKEND_URL}/api/weather`;
const AI_API = `${BACKEND_URL}/api/ai/weather`;

// ============================================================
// MAP COMPONENT (client-only, Leaflet needs the browser)
// ============================================================

const WeatherMap = dynamic<WeatherMapProps>(() => import("./components/WeatherMap"), {
  ssr: false,
  loading: () => (
    <div
      className="real-map-wrapper"
      style={{ display: "grid", placeItems: "center" }}
    >
      <span style={{ opacity: 0.6, fontSize: "13px" }}>Loading map...</span>
    </div>
  ),
});

// ============================================================
// TYPES
// ============================================================

type WeatherData = {
  location: {
    name: string;
    country: string;
    country_code: string;
    latitude: number;
    longitude: number;
  };

  weather: {
    current: {
      temperature_2m: number;
      relative_humidity_2m: number;
      apparent_temperature: number;
      weather_code: number;
      wind_speed_10m: number;
      time: string;
    };

    hourly: {
      time: string[];
      temperature_2m: number[];
      relative_humidity_2m: number[];
      precipitation_probability: number[];
      weather_code: number[];
    };

    daily: {
      time: string[];
      weather_code: number[];
      temperature_2m_max: number[];
      temperature_2m_min: number[];
      precipitation_probability_max: number[];
    };
  };
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  // Only set on assistant messages — where the answer actually came from.
  // Can differ from the search-bar location if the question named a city.
  resolvedLocation?: string;
  extractedCity?: string | null;
  timestamp: string;
};

// ============================================================
// WEATHER INFO HELPER
// ============================================================

function getWeatherInfo(code: number) {
  if (code === 0) {
    return { icon: "☀️", text: "Clear sky" };
  }

  if (code === 1 || code === 2) {
    return { icon: "🌤️", text: "Partly cloudy" };
  }

  if (code === 3) {
    return { icon: "☁️", text: "Overcast" };
  }

  if (code === 45 || code === 48) {
    return { icon: "🌫️", text: "Foggy" };
  }

  if (code >= 51 && code <= 57) {
    return { icon: "🌦️", text: "Drizzle" };
  }

  if (code >= 61 && code <= 67) {
    return { icon: "🌧️", text: "Rain" };
  }

  if (code >= 71 && code <= 77) {
    return { icon: "🌨️", text: "Snow" };
  }

  if (code >= 80 && code <= 82) {
    return { icon: "🌧️", text: "Rain showers" };
  }

  if (code >= 95 && code <= 99) {
    return { icon: "⛈️", text: "Thunderstorm" };
  }

  return { icon: "🌤️", text: "Unknown" };
}

// ============================================================
// DATE HELPERS
// ============================================================

function formatHour(dateString: string) {
  const date = new Date(dateString);

  return date.toLocaleTimeString([], {
    hour: "numeric",
    hour12: true,
  });
}

function formatDay(dateString: string, index: number) {
  if (index === 0) {
    return "Today";
  }

  const date = new Date(`${dateString}T12:00:00`);

  return date.toLocaleDateString([], {
    weekday: "long",
  });
}

function formatChatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

// ============================================================
// MAIN COMPONENT
// ============================================================

export default function Home() {
  // ==========================================================
  // THEME — default DARK
  // ==========================================================

  const [isDay, setIsDay] = useState(false);

  // ==========================================================
  // LOCATION — default Islamabad
  // ==========================================================

  const [location, setLocation] = useState("Islamabad, Pakistan");
  const [latitude, setLatitude] = useState(33.72148);
  const [longitude, setLongitude] = useState(73.04329);

  // ==========================================================
  // LOCATION SELECTION MODAL (Country -> State -> City only)
  // ==========================================================

  const [showLocationSearch, setShowLocationSearch] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState("");
  const [selectedState, setSelectedState] = useState("");
  const [selectedCity, setSelectedCity] = useState("");

  // ==========================================================
  // WEATHER
  // ==========================================================

  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ==========================================================
  // HOURLY
  // ==========================================================

  const [showAllHourly, setShowAllHourly] = useState(false);

  // ==========================================================
  // AI CHAT
  // ==========================================================

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [aiQuestion, setAiQuestion] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // ==========================================================
  // COUNTRIES — alphabetical
  // ==========================================================

  const countries = useMemo(() => {
    return Country.getAllCountries().sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: "base" })
    );
  }, []);

  // ==========================================================
  // STATES — alphabetical, depends on country
  // ==========================================================

  const states = useMemo(() => {
    if (!selectedCountry) {
      return [];
    }

    return State.getStatesOfCountry(selectedCountry).sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: "base" })
    );
  }, [selectedCountry]);

  // ==========================================================
  // CITIES — alphabetical, depends on state
  // ==========================================================

  const cities = useMemo(() => {
    if (!selectedCountry || !selectedState) {
      return [];
    }

    return City.getCitiesOfState(selectedCountry, selectedState).sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: "base" })
    );
  }, [selectedCountry, selectedState]);

  // ==========================================================
  // FETCH WEATHER
  // ==========================================================

  const fetchWeather = async (lat: number, lon: number) => {
    try {
      setLoading(true);
      setError("");

      const url = `${WEATHER_API}?latitude=${lat}&longitude=${lon}`;

      const response = await fetch(url, {
        method: "GET",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`Weather backend returned ${response.status}`);
      }

      const responseText = await response.text();

      let data: WeatherData;

      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error("Weather backend returned an invalid response.");
      }

      if (!data || !data.weather || !data.weather.current) {
        throw new Error("Weather backend returned incomplete data.");
      }

      setWeather(data);
    } catch (err) {
      console.error("WEATHER FETCH ERROR:", err);

      setWeather(null);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to weather backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // INITIAL LOAD — default Islamabad
  // ==========================================================

  useEffect(() => {
    fetchWeather(33.72148, 73.04329);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ==========================================================
  // AUTO-SCROLL CHAT TO LATEST MESSAGE
  // ==========================================================

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatMessages, aiLoading]);

  // ==========================================================
  // COUNTRY CHANGE
  // ==========================================================

  const handleCountryChange = (countryCode: string) => {
    setSelectedCountry(countryCode);
    setSelectedState("");
    setSelectedCity("");
  };

  // ==========================================================
  // STATE CHANGE
  // ==========================================================

  const handleStateChange = (stateCode: string) => {
    setSelectedState(stateCode);
    setSelectedCity("");
  };

  // ==========================================================
  // SET LOCATION
  // ==========================================================

  const handleSetLocation = () => {
    if (!selectedCountry || !selectedState || !selectedCity) {
      return;
    }

    const country = countries.find((item) => item.isoCode === selectedCountry);
    const state = states.find((item) => item.isoCode === selectedState);
    const city = cities.find((item) => item.name === selectedCity);

    if (!country || !state || !city) {
      return;
    }

    const lat = Number(city.latitude);
    const lon = Number(city.longitude);

    if (Number.isNaN(lat) || Number.isNaN(lon)) {
      return;
    }

    setLatitude(lat);
    setLongitude(lon);
    setLocation(`${city.name}, ${country.name}`);
    setShowLocationSearch(false);

    fetchWeather(lat, lon);

    // Clear previous AI conversation when location changes
    setChatMessages([]);
    setAiError("");
  };

  // ==========================================================
  // CURRENT WEATHER (safely narrowed)
  // ==========================================================

  const weatherData = weather;

  const current = weatherData ? weatherData.weather.current : null;
  const currentInfo = current ? getWeatherInfo(current.weather_code) : null;

  // ==========================================================
  // HOURLY CHART DATA (narrowed via local const, avoids TS
  // "possibly null" errors inside the callback closures)
  // ==========================================================

  const hourlyChartData = weatherData
    ? weatherData.weather.hourly.time.slice(0, 24).map((time, index) => ({
        time: formatHour(time),
        temperature: weatherData.weather.hourly.temperature_2m[index],
        rain: weatherData.weather.hourly.precipitation_probability[index],
      }))
    : [];

  // ==========================================================
  // HOURLY LIST DATA
  // ==========================================================

  const hourlyData = weatherData
    ? weatherData.weather.hourly.time.map((time, index) => {
        const code = weatherData.weather.hourly.weather_code[index];
        const info = getWeatherInfo(code);

        return {
          time: index === 0 ? "Now" : formatHour(time),
          icon: info.icon,
          temperature: Math.round(
            weatherData.weather.hourly.temperature_2m[index]
          ),
          rain: weatherData.weather.hourly.precipitation_probability[index],
        };
      })
    : [];

  const visibleHourlyData = showAllHourly
    ? hourlyData.slice(0, 24)
    : hourlyData.slice(0, 6);

  // ==========================================================
  // DAILY FORECAST DATA
  // ==========================================================

  const dailyData = weatherData
    ? weatherData.weather.daily.time.map((date, index) => {
        const code = weatherData.weather.daily.weather_code[index];
        const info = getWeatherInfo(code);

        return {
          day: formatDay(date, index),
          icon: info.icon,
          condition: info.text,
          high: Math.round(weatherData.weather.daily.temperature_2m_max[index]),
          low: Math.round(weatherData.weather.daily.temperature_2m_min[index]),
          rain: weatherData.weather.daily.precipitation_probability_max[index],
        };
      })
    : [];

  // ==========================================================
  // BASIC AI INSIGHT (derived from current conditions)
  // ==========================================================

  let aiTitle = "Weather looks stable";
  let aiMessage = "Conditions are currently favorable.";

  if (current) {
    if (current.weather_code >= 95) {
      aiTitle = "Thunderstorm conditions";
      aiMessage =
        "Thunderstorm activity is currently detected. Outdoor activities may need extra caution.";
    } else if (current.weather_code >= 61) {
      aiTitle = "Rain is present";
      aiMessage = "Rainy conditions are currently affecting this location.";
    } else if (current.relative_humidity_2m >= 80) {
      aiTitle = "High humidity";
      aiMessage =
        "Humidity is currently high. The temperature may feel warmer than the actual reading.";
    } else {
      aiTitle = "Weather looks stable";
      aiMessage =
        "Current conditions appear relatively stable with no major weather disruption detected.";
    }
  }

  // ==========================================================
  // ASK AI — POST /api/ai/weather
  // ==========================================================

  const askAI = async (questionOverride?: string) => {
    const question = (questionOverride ?? aiQuestion).trim();

    if (!question) {
      return;
    }

    if (aiLoading) {
      return;
    }

    setAiError("");

    setChatMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: question,
        timestamp: new Date().toISOString(),
      },
    ]);

    setAiQuestion("");
    setAiLoading(true);

    try {
      const requestBody = {
        question,
        latitude,
        longitude,
        location_name: location,
      };

      const response = await fetch(AI_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const responseText = await response.text();

      if (!response.ok) {
        let errorMessage = `AI backend returned ${response.status}`;

        try {
          const errorData = JSON.parse(responseText);

          if (errorData?.detail) {
            errorMessage =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
          }
        } catch {
          // Keep default error message
        }

        throw new Error(errorMessage);
      }

      let data: {
        answer?: unknown;
        location?: unknown;
        extracted_city?: unknown;
      };

      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error("AI backend returned an invalid response.");
      }

      const answer = data?.answer;

      if (!answer || typeof answer !== "string") {
        throw new Error("AI backend returned an invalid response.");
      }

      const resolvedLocation =
        typeof data?.location === "string" ? data.location : undefined;

      const extractedCity =
        typeof data?.extracted_city === "string" ? data.extracted_city : null;

      setChatMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: answer,
          resolvedLocation,
          extractedCity,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error("AI ERROR:", err);

      const message =
        err instanceof Error
          ? err.message
          : "Unable to connect to AI Assistant.";

      setAiError(message);

      setChatMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "Sorry, I couldn't connect to the AI Assistant right now.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setAiLoading(false);
    }
  };

  const askSuggestion = (question: string) => {
    askAI(question);
  };

  // ==========================================================
  // ASK AI FROM TOP INSIGHT CARD — asks + scrolls to chat
  // ==========================================================

  const askFromInsightCard = () => {
    askSuggestion("Give me a brief analysis of the current weather.");

    setTimeout(() => {
      const target = document.getElementById("ai-assistant-section");

      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 100);
  };

  const handleAIKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askAI();
    }
  };

  // ==========================================================
  // CLEAR CHAT
  // ==========================================================

  const clearChat = () => {
    setChatMessages([]);
    setAiError("");
  };

  // ==========================================================
  // COPY AI ANSWER
  // ==========================================================

  const copyAnswer = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 1500);
    } catch (err) {
      console.error("COPY ERROR:", err);
    }
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <main className={`app ${isDay ? "day-mode" : "night-mode"}`}>
      {/* 3D CLOUD BACKGROUND */}
      <div className="cloud-background">
        <div className="cloud cloud-one" />
        <div className="cloud cloud-two" />
        <div className="cloud cloud-three" />
      </div>

      {/* HEADER */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">☁</div>
          <div>
            <h1>AI Weather</h1>
            <span>Intelligence Platform</span>
          </div>
        </div>

        <div className="topbar-actions">
          <button
            className="search-location-btn"
            onClick={() => setShowLocationSearch(true)}
            aria-label="Search location"
          >
            🔍
            <span>Search</span>
          </button>

          <div className="current-location">📍 {location}</div>

          <button
            className="icon-btn"
            aria-label="Toggle day and night mode"
            onClick={() => setIsDay((value) => !value)}
          >
            {isDay ? "☀" : "☾"}
          </button>
        </div>
      </header>

      {/* LOCATION SELECTION MODAL — Country -> State -> City only */}
      {showLocationSearch && (
        <div
          className="location-overlay"
          onClick={() => setShowLocationSearch(false)}
        >
          <div
            className="location-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="location-modal-header">
              <div>
                <span className="eyebrow">LOCATION SEARCH</span>
                <h2>Search Location</h2>
              </div>

              <button
                className="location-close"
                onClick={() => setShowLocationSearch(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="location-field">
              <label>Country</label>
              <select
                value={selectedCountry}
                onChange={(event) => handleCountryChange(event.target.value)}
              >
                <option value="">Select country</option>
                {countries.map((country) => (
                  <option key={country.isoCode} value={country.isoCode}>
                    {country.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="location-field">
              <label>Province / State</label>
              <select
                value={selectedState}
                disabled={!selectedCountry}
                onChange={(event) => handleStateChange(event.target.value)}
              >
                <option value="">Select province / state</option>
                {states.map((state) => (
                  <option key={state.isoCode} value={state.isoCode}>
                    {state.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="location-field">
              <label>City</label>
              <select
                value={selectedCity}
                disabled={!selectedState}
                onChange={(event) => setSelectedCity(event.target.value)}
              >
                <option value="">Select city</option>
                {cities.map((city, index) => (
                  <option key={`${city.name}-${index}`} value={city.name}>
                    {city.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="set-location-btn"
              disabled={!selectedCountry || !selectedState || !selectedCity}
              onClick={handleSetLocation}
            >
              Set Location
            </button>
          </div>
        </div>
      )}

      {/* DASHBOARD */}
      <div className="dashboard">
        {/* HERO */}
        <section className="hero-panel">
          <div className="hero-content">
            <span className="eyebrow">AI WEATHER INTELLIGENCE</span>
            <h2>
              Understand the weather.
              <br />
              <span>Before it happens.</span>
            </h2>
            <p>
              Real-time weather intelligence, forecasts, alerts and
              AI-powered insights in one place.
            </p>
          </div>

          <div className="live-status">
            <span className="status-dot" />
            {loading ? "Loading weather..." : "Live weather data"}
          </div>
        </section>

        {/* ERROR */}
        {error && (
          <div
            style={{
              padding: "16px",
              marginTop: "18px",
              borderRadius: "12px",
              background: "rgba(255, 80, 80, 0.15)",
            }}
          >
            ❌ {error}
          </div>
        )}

        {/* CURRENT + AI INSIGHT */}
        <section className="weather-grid">
          <article className="weather-card current-weather">
            <div className="card-header">
              <span>Current Weather</span>
              <span>
                {current
                  ? new Date(current.time).toLocaleTimeString([], {
                      hour: "numeric",
                      minute: "2-digit",
                    })
                  : "—"}
              </span>
            </div>

            {loading ? (
              <div className="temperature">Loading...</div>
            ) : current ? (
              <>
                <div className="temperature">
                  <strong>{Math.round(current.temperature_2m)}</strong>
                  <span>°C</span>
                </div>

                <p className="condition">
                  {currentInfo?.icon} {currentInfo?.text}
                </p>

                <div className="weather-meta">
                  <div>
                    <span>Feels like</span>
                    <strong>
                      {Math.round(current.apparent_temperature)}°C
                    </strong>
                  </div>

                  <div>
                    <span>Humidity</span>
                    <strong>{current.relative_humidity_2m}%</strong>
                  </div>

                  <div>
                    <span>Wind</span>
                    <strong>{current.wind_speed_10m} km/h</strong>
                  </div>
                </div>
              </>
            ) : (
              <div>No weather data</div>
            )}
          </article>

          <article className="weather-card ai-card">
            <div className="card-header">
              <span>AI Insight</span>
              <span className="ai-badge">AI</span>
            </div>

            <div className="ai-content">
              <div className="ai-icon">✦</div>

              <div>
                <h3>{aiTitle}</h3>
                <p>{aiMessage}</p>

                <button
                  className="ask-ai"
                  onClick={askFromInsightCard}
                  disabled={aiLoading}
                >
                  {aiLoading ? "Thinking..." : "Ask AI →"}
                </button>
              </div>
            </div>
          </article>
        </section>

        {/* HOURLY */}
        <section className="section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">FORECAST</span>
              <h2>Hourly Weather</h2>
            </div>

            <button
              className="text-button"
              onClick={() => setShowAllHourly((value) => !value)}
            >
              {showAllHourly ? "Show Less" : "View More →"}
            </button>
          </div>

          <div className="hourly-list">
            {loading ? (
              <div>Loading hourly forecast...</div>
            ) : visibleHourlyData.length === 0 ? (
              <div>No hourly data available.</div>
            ) : (
              visibleHourlyData.map((item, index) => (
                <div className="hour-card" key={`${item.time}-${index}`}>
                  <span>{item.time}</span>
                  <strong>{item.icon}</strong>
                  <b>{item.temperature}°</b>
                  <small>💧 {item.rain}%</small>
                </div>
              ))
            )}
          </div>
        </section>

        {/* TEMPERATURE GRAPH */}
        <section className="section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">ANALYTICS</span>
              <h2>24-Hour Temperature</h2>
            </div>
          </div>

          <div
            className="weather-card"
            style={{ height: "360px", padding: "20px" }}
          >
            {loading ? (
              <div>Loading temperature graph...</div>
            ) : hourlyChartData.length === 0 ? (
              <div>No temperature data available.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={hourlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis unit="°C" />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="temperature"
                    name="Temperature"
                    stroke="currentColor"
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        {/* MAP — real interactive OpenStreetMap via Leaflet */}
        <section className="section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">LIVE MAP</span>
              <h2>Weather Intelligence Map</h2>
            </div>
          </div>

          <WeatherMap
            latitude={latitude}
            longitude={longitude}
            locationName={location}
            temperature={current ? current.temperature_2m : null}
            conditionText={currentInfo?.text}
            conditionIcon={currentInfo?.icon}
          />
        </section>

        {/* DAILY FORECAST */}
        <section className="section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">EXTENDED FORECAST</span>
              <h2>7-Day Forecast</h2>
            </div>
          </div>

          <div className="daily-list">
            {loading ? (
              <div>Loading forecast...</div>
            ) : dailyData.length === 0 ? (
              <div>No forecast data available.</div>
            ) : (
              dailyData.map((item) => (
                <div className="daily-row" key={item.day}>
                  <span className="day">{item.day}</span>
                  <span className="daily-icon">{item.icon}</span>
                  <span className="daily-condition">{item.condition}</span>
                  <strong>{item.high}°</strong>
                  <span className="low">{item.low}°</span>
                  <span>💧 {item.rain}%</span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* AI ASSISTANT */}
        <section className="ai-assistant" id="ai-assistant-section">
          <div className="ai-assistant-header">
            <div>
              <span className="eyebrow">AI WEATHER ASSISTANT</span>
              <h2>Ask the weather anything.</h2>
              <p>
                Get intelligent answers based on real weather conditions and
                forecasts.
              </p>
            </div>

            {chatMessages.length > 0 && (
              <button
                className="clear-chat-btn"
                onClick={clearChat}
                disabled={aiLoading}
              >
                🗑 Clear chat
              </button>
            )}
          </div>

          <div className="suggestions">
            <button
              onClick={() => askSuggestion("Will it rain tomorrow?")}
              disabled={aiLoading}
            >
              Will it rain tomorrow?
            </button>

            <button
              onClick={() => askSuggestion("Is it good for cricket today?")}
              disabled={aiLoading}
            >
              Is it good for cricket?
            </button>

            <button
              onClick={() => askSuggestion("What should I wear today?")}
              disabled={aiLoading}
            >
              What should I wear?
            </button>

            <button
              onClick={() => askSuggestion("Should I travel this weekend?")}
              disabled={aiLoading}
            >
              Should I travel this weekend?
            </button>
          </div>

          {chatMessages.length > 0 && (
            <div className="ai-chat">
              {chatMessages.map((message, index) => {
                const isUser = message.role === "user";

                const showLocationBadge =
                  !isUser &&
                  message.resolvedLocation &&
                  message.extractedCity;

                return (
                  <div
                    key={index}
                    className={`chat-row ${isUser ? "chat-row-user" : "chat-row-assistant"}`}
                  >
                    <div className="chat-avatar" aria-hidden="true">
                      {isUser ? "🧑" : "✦"}
                    </div>

                    <div
                      className={`chat-bubble ${
                        isUser ? "user-message" : "assistant-message"
                      }`}
                    >
                      <div className="chat-bubble-top">
                        <span className="chat-role">
                          {isUser ? "You" : "AI Assistant"}
                        </span>
                        <span className="chat-time">
                          {formatChatTime(message.timestamp)}
                        </span>
                      </div>

                      <p>{message.content}</p>

                      {showLocationBadge && (
                        <div className="location-badge">
                          📍 Answered for {message.resolvedLocation}
                        </div>
                      )}

                      {!isUser && (
                        <button
                          className="copy-btn"
                          onClick={() => copyAnswer(message.content, index)}
                          aria-label="Copy answer"
                        >
                          {copiedIndex === index ? "Copied ✓" : "Copy"}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}

              {aiLoading && (
                <div className="chat-row chat-row-assistant">
                  <div className="chat-avatar" aria-hidden="true">
                    ✦
                  </div>

                  <div className="chat-bubble assistant-message">
                    <div className="chat-bubble-top">
                      <span className="chat-role">AI Assistant</span>
                    </div>

                    <div className="typing-dots" aria-label="AI is thinking">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>
          )}

          {aiError && (
            <div
              style={{
                marginTop: "14px",
                padding: "12px 14px",
                borderRadius: "10px",
                background: "rgba(255, 80, 80, 0.15)",
                border: "1px solid rgba(255, 80, 80, 0.25)",
              }}
            >
              ❌ {aiError}
            </div>
          )}

          <div className="chat-input">
            <input
              type="text"
              value={aiQuestion}
              onChange={(event) => setAiQuestion(event.target.value)}
              onKeyDown={handleAIKeyDown}
              placeholder="Ask about the weather..."
              disabled={aiLoading}
            />

            <button
              aria-label="Send"
              onClick={() => askAI()}
              disabled={aiLoading || !aiQuestion.trim()}
            >
              {aiLoading ? "..." : "→"}
            </button>
          </div>
               </section>

        {/* FOOTER */}
        <footer className="app-footer">
          <p>Built by <strong>Maryam Fahim</strong></p>
        </footer>
      </div>
    </main>
  );
}