"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { Search, Activity, TrendingUp, AlertTriangle } from "lucide-react";
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import PanelDenuncias from "@/components/PanelDenuncias";
import FormularioDenuncia from "@/components/FormularioDenuncia";

// El mapa debe cargarse sin SSR
const DynamicMap = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-[#080c14] flex items-center justify-center animate-pulse">Iniciando motor de mapas y analítica...</div>
});

const mockCrimeData = [
  { city: "Bogotá", risk: 85 },
  { city: "Cali", risk: 78 },
  { city: "Medellín", risk: 65 },
  { city: "B/quilla", risk: 50 },
];

const mockTrendData = [
  { time: "00:00", crimes: 12 }, { time: "04:00", crimes: 5 }, 
  { time: "08:00", crimes: 15 }, { time: "12:00", crimes: 25 },
  { time: "16:00", crimes: 30 }, { time: "20:00", crimes: 45 },
];

const COLORS = ['#ef4444', '#dc2626', '#f97316', '#eab308'];

export default function Home() {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  return (
    <main className="w-full h-screen flex flex-col relative overflow-hidden">
      
      {/* Top Navigation Bar */}
      <nav className="absolute top-0 left-0 w-full h-16 glass-panel z-10 flex items-center justify-between px-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]">
            P
          </div>
          <div>
            <h1 className="font-bold text-lg text-white leading-tight">PIPAC</h1>
            <p className="text-xs text-blue-300">Plataforma Nacional de Colombia</p>
          </div>
        </div>
        
        <div className="flex-1 max-w-xl mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Buscar entidades, trámites, departamentos..." 
              className="w-full bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
            <button
              onClick={() => setMostrarFormulario(true)}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold text-sm px-4 py-1.5 rounded-full transition-colors shadow-[0_0_15px_rgba(239,68,68,0.3)] hover:shadow-[0_0_20px_rgba(239,68,68,0.5)]"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              Reportar
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600" />
          </div>
      </nav>

      {/* Main Content Area */}
      <div className="flex-1 w-full relative">
        {/* Map Background */}
        <div className="absolute inset-0">
          <DynamicMap />
        </div>

        {/* Floating Dashboard (Left) */}
        <div className="absolute top-20 left-4 w-96 flex flex-col gap-4 z-10 h-[calc(100vh-6rem)] overflow-y-auto pointer-events-none pb-4">
          
          <div className="glass-panel p-4 rounded-xl pointer-events-auto">
            <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-red-500" /> Índice Predictivo de Riesgo
            </h2>
            <div className="h-40 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockCrimeData}>
                  <XAxis dataKey="city" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.1)' }} contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="risk" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-xl pointer-events-auto">
            <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-blue-500" /> Proyección Horaria (IA)
            </h2>
            <div className="h-32 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockTrendData}>
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Line type="monotone" dataKey="crimes" stroke="#3b82f6" strokeWidth={3} dot={{ r: 3, fill: '#3b82f6' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel p-4 rounded-xl pointer-events-auto border-l-4 border-l-yellow-500">
            <h3 className="font-bold text-white flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4 text-yellow-500" /> Alerta de Prevención
            </h3>
            <p className="text-xs text-gray-300">
              El modelo XGBoost proyecta un incremento del 15% en hurto a personas en la localidad de Chapinero (Bogotá) entre las 18:00 y 21:00 horas. Se recomienda priorizar patrullaje.
            </p>
          </div>

          {/* Panel de Denuncias, Tasas y Últimos Eventos */}
          <PanelDenuncias />

        </div>

      </div>
      {mostrarFormulario && (
        <FormularioDenuncia onClose={() => setMostrarFormulario(false)} />
      )}
    </main>
  );
}
