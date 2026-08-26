export type DensityLevel = 'LANCAR' | 'SEDANG' | 'PADAT' | 'MACET';

export interface VehicleBreakdown {
  motorcycle: number;
  car: number;
  bus: number;
  truck: number;
}

export interface DirectionMetrics {
  total_smp: number;
  smp_per_minute: number;
  density_level: DensityLevel;
  breakdown: VehicleBreakdown;
}

export interface VehicleEvent {
  id: string;
  timestamp: string;
  direction: 'inbound' | 'outbound';
  vehicle_type: 'motorcycle' | 'car' | 'bus' | 'truck';
  smp: number;
}

export interface TrafficMetrics {
  timestamp: number;
  fps: number;
  inbound: DirectionMetrics;
  outbound: DirectionMetrics;
  recent_events: VehicleEvent[];
}

export interface ROICoordinates {
  inbound: [number, number][];
  outbound: [number, number][];
}
