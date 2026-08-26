"use client";

import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// ============================================================
// TYPES
// ============================================================

export type WeatherMapProps = {
  latitude: number;
  longitude: number;
  locationName: string;
  temperature?: number | null;
  conditionText?: string;
  conditionIcon?: string;
};

// ============================================================
// RECENTER HELPER
// Moves the map view whenever latitude/longitude changes,
// without remounting the whole MapContainer.
// ============================================================

function RecenterMap({
  latitude,
  longitude,
}: {
  latitude: number;
  longitude: number;
}) {
  const map = useMap();

  useEffect(() => {
    map.setView([latitude, longitude], map.getZoom(), {
      animate: true,
    });
  }, [latitude, longitude, map]);

  return null;
}

// ============================================================
// CUSTOM MARKER ICON
// Uses a divIcon built from CSS classes already defined in
// globals.css (.weather-map-marker / .weather-map-marker-inner)
// instead of Leaflet's default marker images. This avoids the
// well-known "broken marker icon" issue that happens with
// Leaflet + Webpack/Next.js bundling.
// ============================================================

function createWeatherIcon(icon: string) {
  return L.divIcon({
    className: "weather-map-marker",
    html: `<div class="weather-map-marker-inner"><span>${icon}</span></div>`,
    iconSize: [42, 42],
    iconAnchor: [21, 42],
    popupAnchor: [0, -42],
  });
}

// ============================================================
// MAIN COMPONENT
// ============================================================

export default function WeatherMap({
  latitude,
  longitude,
  locationName,
  temperature,
  conditionText,
  conditionIcon,
}: WeatherMapProps) {
  const safeLat = Number.isFinite(latitude) ? latitude : 33.72148;
  const safeLon = Number.isFinite(longitude) ? longitude : 73.04329;

  const markerIcon = createWeatherIcon(conditionIcon || "📍");

  const badgeDetail =
    typeof temperature === "number"
      ? `${Math.round(temperature)}°C${conditionText ? ` · ${conditionText}` : ""}`
      : `${safeLat.toFixed(2)}, ${safeLon.toFixed(2)}`;

  return (
    <div className="real-map-wrapper">
      <div className="map-location-badge">
        <span>{conditionIcon || "📍"}</span>
        <div>
          <strong>{locationName}</strong>
          <small>{badgeDetail}</small>
        </div>
      </div>

      <MapContainer
  key={`${safeLat}-${safeLon}`}
  center={[safeLat, safeLon]}
  zoom={11}
  scrollWheelZoom={true}
  className="real-map"
>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <Marker position={[safeLat, safeLon]} icon={markerIcon}>
          <Popup>
            <div className="map-popup">
              <strong>{locationName}</strong>
              {typeof temperature === "number" && (
                <span>
                  {Math.round(temperature)}°C
                  {conditionText ? ` — ${conditionText}` : ""}
                </span>
              )}
            </div>
          </Popup>
        </Marker>

        <RecenterMap latitude={safeLat} longitude={safeLon} />
      </MapContainer>
    </div>
  );
}