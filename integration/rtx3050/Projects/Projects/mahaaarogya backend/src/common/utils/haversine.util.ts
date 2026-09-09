/** Haversine formula: returns distance in kilometers */
export function haversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/** Rough estimate: straight-line km → driving minutes (assumes ~40 km/h in city) */
export function estimateDrivingMinutes(distanceKm: number): number {
  const AVERAGE_CITY_SPEED_KMH = 40;
  return Math.ceil((distanceKm / AVERAGE_CITY_SPEED_KMH) * 60);
}
