"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl, useMap } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import "leaflet.heat";
import { Phone, Navigation, Globe, AlertTriangle, Loader2, MapPin } from "lucide-react";
import FormularioDenuncia from "./FormularioDenuncia";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type LeafletWithHeat = typeof L & {
  heatLayer: (
    points: [number, number, number][],
    options: {
      radius: number;
      blur: number;
      maxZoom: number;
      gradient: Record<number, string>;
    }
  ) => L.Layer;
};

// ─── Iconos ───────────────────────────────────────────────────────────────────
const customIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// ─── Heatmap ──────────────────────────────────────────────────────────────────
function HeatmapLayer({ points }: { points: [number, number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (!map) return;
    const heatLayer = (L as LeafletWithHeat).heatLayer(points, {
      radius: 25, blur: 15, maxZoom: 10,
      gradient: { 0.4: "blue", 0.6: "cyan", 0.7: "lime", 0.8: "yellow", 1.0: "red" },
    }).addTo(map);
    return () => { map.removeLayer(heatLayer); };
  }, [map, points]);
  return null;
}

// ─── Denuncias cercanas en el popup ───────────────────────────────────────────
type Denuncia = {
  id_denuncia: number;
  tipo_delito: string;
  descripcion: string;
  ciudad: string;
  barrio?: string;
  estado: string;
  created_at: string;
};

function DenunciasCercanas({ lat, lon, ciudad }: { lat: number; lon: number; ciudad: string }) {
  const [denuncias, setDenuncias] = useState<Denuncia[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/denuncias/cercanas?lat=${lat}&lon=${lon}&radio_km=20&limit=5`)
      .then((r) => r.json())
      .then((data) => setDenuncias(Array.isArray(data) ? data : []))
      .catch(() => {
        // Demo fallback
        setDenuncias([
          { id_denuncia: 1, tipo_delito: "Robo / Hurto", descripcion: "Robo de celular en transporte público.", ciudad, barrio: "Centro", estado: "RECIBIDA", created_at: new Date().toISOString() },
          { id_denuncia: 2, tipo_delito: "Acoso Sexual", descripcion: "Acoso verbal en vía pública.", ciudad, barrio: "Chapinero", estado: "EN_REVISION", created_at: new Date(Date.now() - 3600000).toISOString() },
        ]);
      })
      .finally(() => setLoading(false));
  }, [ciudad, lat, lon]);

  const estadoColor: Record<string, string> = {
    RECIBIDA: "text-yellow-400",
    EN_REVISION: "text-blue-400",
    CERRADA: "text-green-400",
  };

  return (
    <div className="mt-3 border-t border-white/10 pt-3">
      <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
        <AlertTriangle className="w-3 h-3 text-red-400" />
        Últimas denuncias en {ciudad}
      </p>
      {loading ? (
        <div className="flex justify-center py-2">
          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
        </div>
      ) : denuncias.length === 0 ? (
        <p className="text-[10px] text-gray-500 text-center py-2">Sin denuncias recientes.</p>
      ) : (
        <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto">
          {denuncias.map((d) => (
            <div key={d.id_denuncia} className="bg-white/5 rounded-lg p-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-white">{d.tipo_delito}</span>
                <span className={`text-[9px] ${estadoColor[d.estado] || "text-gray-400"}`}>{d.estado}</span>
              </div>
              <p className="text-[10px] text-gray-400 mt-0.5 line-clamp-2">{d.descripcion}</p>
              {d.barrio && (
                <p className="text-[9px] text-gray-600 flex items-center gap-1 mt-0.5">
                  <MapPin className="w-2 h-2" /> {d.barrio}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Mapa Principal ───────────────────────────────────────────────────────────
export default function Map() {
  const [mounted, setMounted] = useState(false);
  const [formularioData, setFormularioData] = useState<{ lat: number; lon: number; ciudad: string } | null>(null);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return (
    <div className="w-full h-full bg-[#080c14] flex items-center justify-center text-gray-500 text-sm">
      Iniciando motor de mapas…
    </div>
  );

  const markers = [
    { id: 1, lat: 4.6097, lng: -74.0817, name: "Alcaldía Mayor de Bogotá", cat: "Gubernamental", ciudad: "Bogotá", tel: "195", url: "https://bogota.gov.co" },
    { id: 2, lat: 6.2442, lng: -75.5812, name: "Gobernación de Antioquia", cat: "Gubernamental", ciudad: "Medellín", tel: "018000", url: "https://antioquia.gov.co" },
    { id: 3, lat: 10.3910, lng: -75.4794, name: "Policía Metropolitana Cartagena", cat: "Seguridad", ciudad: "Cartagena", tel: "123", url: "https://policia.gov.co" },
    { id: 4, lat: 3.4516, lng: -76.5320, name: "Estación de Policía Cali Centro", cat: "Seguridad", ciudad: "Cali", tel: "112", url: "https://policia.gov.co" },
    { id: 5, lat: 11.0041, lng: -74.8070, name: "Gobernación del Atlántico", cat: "Gubernamental", ciudad: "Barranquilla", tel: "018000", url: "https://atlantico.gov.co" },
    { id: 6, lat: 7.1193, lng: -73.1227, name: "Alcaldía de Bucaramanga", cat: "Gubernamental", ciudad: "Bucaramanga", tel: "111", url: "https://bucaramanga.gov.co" },
    { id: 7, lat: 4.1420, lng: -73.6266, name: "Policía Nacional Villavicencio", cat: "Seguridad", ciudad: "Villavicencio", tel: "123", url: "https://policia.gov.co" },
    { id: 8, lat: 1.2136, lng: -77.2811, name: "Estación Policía Pasto", cat: "Seguridad", ciudad: "Pasto", tel: "112", url: "https://policia.gov.co" },
    { id: 9, lat: 8.7480, lng: -75.8814, name: "Alcaldía de Montería", cat: "Gubernamental", ciudad: "Montería", tel: "123", url: "https://monteria.gov.co" },
    { id: 10, lat: -4.2153, lng: -69.9406, name: "Oficina Policial Leticia", cat: "Seguridad", ciudad: "Leticia", tel: "112", url: "https://policia.gov.co" },
    { id: 11, lat: 5.3378, lng: -72.3959, name: "Gobernación de Casanare", cat: "Gubernamental", ciudad: "Yopal", tel: "018000", url: "https://casanare.gov.co" },
    { id: 12, lat: 2.4448, lng: -76.6147, name: "Policía Cauca", cat: "Seguridad", ciudad: "Popayán", tel: "123", url: "https://policia.gov.co" },
    { id: 13, lat: 5.0689, lng: -75.5174, name: "Alcaldía de Manizales", cat: "Gubernamental", ciudad: "Manizales", tel: "112", url: "https://manizales.gov.co" },
    { id: 14, lat: 4.5339, lng: -75.6811, name: "Gobernación del Quindío", cat: "Gubernamental", ciudad: "Armenia", tel: "018000", url: "https://quindio.gov.co" },
    { id: 15, lat: 12.5847, lng: -81.7006, name: "Policía San Andrés", cat: "Seguridad", ciudad: "San Andrés", tel: "123", url: "https://policia.gov.co" },
  ];

  const crimeHeatmapData: [number, number, number][] = [
    [4.6097, -74.0817, 1.0], [4.6200, -74.0900, 0.8], [4.5900, -74.0800, 0.9],
    [6.2442, -75.5812, 0.9], [6.2500, -75.5700, 0.7], [6.2600, -75.5600, 0.6],
    [3.4516, -76.5320, 0.95], [3.4400, -76.5400, 0.85],
    [10.9639, -74.7964, 0.8], [10.9700, -74.8000, 0.7],
    [7.1193, -73.1227, 0.6],
  ];

  return (
    <>
      <MapContainer
        center={[4.5709, -74.2973]}
        zoom={5.5}
        className="w-full h-full z-0"
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        />
        <ZoomControl position="bottomright" />
        <HeatmapLayer points={crimeHeatmapData} />

        <MarkerClusterGroup chunkedLoading>
          {markers.map((marker) => (
            <Marker key={marker.id} position={[marker.lat, marker.lng]} icon={customIcon}>
              <Popup className="custom-popup" minWidth={250} maxHeight={480}>
                <div className="p-1">
                  <h3 className="font-bold text-base text-white mb-1">{marker.name}</h3>
                  <span className="text-xs font-semibold bg-blue-600/30 text-blue-300 px-2 py-0.5 rounded-full">
                    {marker.cat}
                  </span>

                  {/* Acciones */}
                  <div className="mt-3 grid grid-cols-4 gap-2">
                    <a href={`tel:${marker.tel}`} className="flex flex-col items-center justify-center p-2 rounded glass-button text-xs text-gray-300 hover:text-white" title="Llamar">
                      <Phone size={15} className="mb-1" />
                    </a>
                    <a
                      href={`https://www.google.com/maps/dir/?api=1&destination=${marker.lat},${marker.lng}`}
                      target="_blank" rel="noreferrer"
                      className="flex flex-col items-center justify-center p-2 rounded glass-button text-xs text-gray-300 hover:text-white"
                      title="Cómo llegar"
                    >
                      <Navigation size={15} className="mb-1" />
                    </a>
                    <a href={marker.url} target="_blank" rel="noreferrer" className="flex flex-col items-center justify-center p-2 rounded glass-button text-xs text-gray-300 hover:text-white" title="Web oficial">
                      <Globe size={15} className="mb-1" />
                    </a>
                    {/* Botón REPORTAR desde el marcador */}
                    <button
                      onClick={() => setFormularioData({ lat: marker.lat, lon: marker.lng, ciudad: marker.ciudad })}
                      className="flex flex-col items-center justify-center p-2 rounded bg-red-600/20 border border-red-600/40 text-red-400 hover:bg-red-600/40 transition-colors"
                      title="Reportar hecho aquí"
                    >
                      <AlertTriangle size={15} className="mb-1" />
                    </button>
                  </div>

                  {/* Denuncias cercanas cargadas desde la API */}
                  <DenunciasCercanas lat={marker.lat} lon={marker.lng} ciudad={marker.ciudad} />
                </div>
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>

      {/* Modal de formulario (lanzado desde marcador o desde navbar) */}
      {formularioData && (
        <FormularioDenuncia
          onClose={() => setFormularioData(null)}
          defaultLat={formularioData.lat}
          defaultLon={formularioData.lon}
          defaultCiudad={formularioData.ciudad}
        />
      )}
    </>
  );
}
