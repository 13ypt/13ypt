import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { King, HistoricalEvent, Place, Layer } from "../data/types";

const LAYER_COLORS: Record<Layer, string> = {
  political: "#c04040",
  regional: "#2f8f6e",
  religious: "#7a3ca1",
};

interface Props {
  king: King;
  events: HistoricalEvent[]; // already filtered
  selectedEventId: string | null;
  hoveredEventId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
}

function Recenter({ place }: { place: Place | null }) {
  const map = useMap();
  useEffect(() => {
    if (place) map.flyTo([place.lat, place.lng], 6, { duration: 0.6 });
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

  // For each place, count events and determine dominant layer color
  const perPlace: Record<string, { count: number; layers: Set<Layer>; events: HistoricalEvent[] }> = {};
  for (const ev of events) {
    if (!ev.placeId) continue;
    if (!perPlace[ev.placeId])
      perPlace[ev.placeId] = { count: 0, layers: new Set(), events: [] };
    perPlace[ev.placeId].count++;
    perPlace[ev.placeId].layers.add(ev.layer);
    perPlace[ev.placeId].events.push(ev);
  }

  const selectedEvent = events.find((e) => e.id === selectedEventId) ?? null;
  const selectedPlace = selectedEvent?.placeId
    ? placeById[selectedEvent.placeId] ?? null
    : null;

  return (
    <div className="map-wrap">
      <MapContainer
        center={[30.5, 29.5]}
        zoom={4}
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {king.places.map((p) => {
          const pdata = perPlace[p.id];
          if (!pdata) return null;
          const n = pdata.count;
          const dominantLayer: Layer =
            [...pdata.layers][0] ?? ("political" as Layer);
          const fillColor = LAYER_COLORS[dominantLayer];
          const isSelected =
            selectedEvent !== null && selectedEvent.placeId === p.id;
          const isHovered =
            hoveredEventId !== null &&
            events.find((e) => e.id === hoveredEventId)?.placeId === p.id;
          const r = 6 + Math.min(n, 8) * 1.8;
          return (
            <CircleMarker
              key={p.id}
              center={[p.lat, p.lng]}
              radius={isSelected ? r + 4 : isHovered ? r + 2 : r}
              pathOptions={{
                color: isSelected ? "#111" : "#333",
                weight: isSelected ? 2 : 1,
                fillColor,
                fillOpacity: 0.6,
                dashArray: p.approximate ? "4 3" : undefined,
              }}
              eventHandlers={{
                click: () => {
                  if (pdata.events[0]) onSelect(pdata.events[0].id);
                },
                mouseover: () => {
                  if (pdata.events[0]) onHover(pdata.events[0].id);
                },
                mouseout: () => onHover(null),
              }}
            >
              <Tooltip direction="top" offset={[0, -4]}>
                <div style={{ fontSize: 12 }}>
                  <strong>{p.nameJa}</strong>
                  <span style={{ color: "#777" }}> ({p.name})</span>
                  <br />
                  {n} 件のイベント
                  {p.approximate && <em> ・概位置</em>}
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
