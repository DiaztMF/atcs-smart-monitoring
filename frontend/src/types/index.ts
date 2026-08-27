export type DensityLevel = 'LANCAR' | 'SEDANG' | 'PADAT' | 'MACET';

export interface VehicleBreakdown {
  motorcycle: number;
  car: number;
  bus: number;
  truck: number;
}

export type VehicleBreakdownCounts = VehicleBreakdown;

export interface DirectionMetrics {
  total_smp: number;
  smp_per_minute: number;
  density_level: DensityLevel;
  breakdown: VehicleBreakdown;
}

export type VehicleType = 'motorcycle' | 'car' | 'bus' | 'truck';
export type DirectionType = 'IN' | 'OUT';

export interface VehicleEvent {
  id: string;
  timestamp: string;
  direction: 'inbound' | 'outbound';
  vehicle_type: VehicleType;
  smp: number;
}

export interface DetectionLogEvent {
  id: string;
  time: string;
  type: VehicleType;
  direction: DirectionType;
  lane: string;
  status: string;
}

export interface TrafficMetrics {
  timestamp: number;
  fps: number;
  inbound: DirectionMetrics;
  outbound: DirectionMetrics;
  recent_events: VehicleEvent[];
}

export type Point = [number, number];

export interface ROICoordinates {
  inbound: Point[];
  outbound: Point[];
}

export interface CCTVPreset {
  id: string;
  name: string;
  location: string;
  url: string;
}

export interface ActiveStreamSource {
  name: string;
  url: string;
}

export interface StreamSourceInfo {
  active_source: ActiveStreamSource;
  presets: CCTVPreset[];
}
