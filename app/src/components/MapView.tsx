import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { King, HistoricalEvent, Place } from "../data/types";

interface Props {
  king: King;
  events: HistoricalEvent[];
  selectedEventId: string | null;
  hoveredEventId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
}

function Recenter({ place }: { place: Place | null }) {
  const map = useMap();
  useEffect(() => {
    if (place) {
      map.flyTo([place.lat, place.lng], 6, { duration: 0.6 });
    }
  }, [place, map]);
  return null;
}

export default function MapView({
  king,
  events,
  selectedEventId,
  hoveredEventId,
  onSelect,
  onHover,
}: Props) {
  const placeById = Object.fromEntries(king.places.map((p) => [p.id, p]));

  // event count per place for radius scaling
  const countByPlace: Record<string, number> = {};
  for (const ev of events) {
    countByPlace[ev.placeId] = (countByPlace[ev.placeId] ?? 0) + 1;
  }

  const selectedEvent = events.find((e) => e.id === selectedEventId) ?? null;
  const selectedPlace = selectedEvent ? placeById[selectedEvent.placeId] : null;

  return (
    <div className="map-wrap">
      <MapContainer
        center={[30.5, 29.5]}
        zoom={5}
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {king.places.map((p) => {
          const n = countByPlace[p.id] ?? 0;
          const placeEvents = events.filter((e) => e.placeId === p.id);
          const isSelected =
            selectedEvent !== null && selectedEvent.placeId === p.id;
          const isHovered =
            hoveredEventId !== null &&
            events.find((e) => e.id === hoveredEventId)?.placeId === p.id;
          const r = 6 + Math.min(n, 6) * 2;
          return (
            <CircleMarker
              key={p.id}
              center={[p.lat, p.lng]}
              radius={isSelected ? r + 4 : isHovered ? r + 2 : r}
              pathOptions={{
                color: isSelected ? "#111" : "#8a4b0a",
                weight: isSelected ? 2 : 1,
                fillColor: "#d98c3d",
                fillOpacity: n === 0 ? 0.2 : 0.7,
              }}
              eventHandlers={{
                click: () => {
                  if (placeEvents[0]) onSelect(placeEvents[0].id);
                },
                mouseover: () => {
                  if (placeEvents[0]) onHover(placeEvents[0].id);
                },
                mouseout: () => onHover(null),
              }}
            >
              <Tooltip direction="top" offset={[0, -4]}>
                <div style={{ fontSize: 12 }}>
                  <strong>{p.nameJa}</strong>
                  <span style={{ color: "#777" }}> ({p.name})</span>
                  <br />
                  {n > 0 ? `${n} 件のイベント` : "関連地（参照用）"}
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
        <Recenter place={selectedPlace} />
      </MapContainer>
    </div>
  );
}
