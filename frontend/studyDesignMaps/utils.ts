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

export function getUserColor() {
  // Fixed palette of vibrant colors
  const palette = [
    "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef",
    "#ec4899", "#f43f5e", "#ef4444", "#f97316", "#f59e0b",
    "#eab308", "#84cc16", "#22c55e", "#10b981", "#14b8a6",
    "#06b6d4", "#0ea5e9"
  ];

  // Select a random color from the palette
  const randomIndex = Math.floor(Math.random() * palette.length);
  return palette[randomIndex];
}
