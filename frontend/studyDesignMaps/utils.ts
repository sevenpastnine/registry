/**
 * Throttle function to limit the rate of function calls
 * @param func The function to throttle
 * @param limit The minimum time between function calls in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;

  return function(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// Fixed palette of vibrant colors
export const COLOR_PALETTE = [
  "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef",
  "#ec4899", "#f43f5e", "#ef4444", "#f97316", "#f59e0b",
  "#eab308", "#84cc16", "#22c55e", "#10b981", "#14b8a6",
  "#06b6d4", "#0ea5e9"
];

/**
 * Get a color for a user that isn't already in use by other users
 * @param existingColors Array of colors already in use by other users
 * @returns A color from the palette that isn't in use
 */
export function getUserColor(existingColors: string[] = []): string {
  // Find available colors from the palette
  const availableColors = COLOR_PALETTE.filter(color => !existingColors.includes(color));
  
  // If we have available colors, use one of them
  if (availableColors.length > 0) {
    const selectedColor = availableColors[Math.floor(Math.random() * availableColors.length)];
    return selectedColor;
  }
  
  // If all colors are used, pick a random one from the palette
  const randomColor = COLOR_PALETTE[Math.floor(Math.random() * COLOR_PALETTE.length)];
  return randomColor;
}
