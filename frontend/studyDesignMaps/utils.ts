import { useEffect, useRef } from 'react';

export function stringToColor(str: string) {
  let colour = '#';
  let hash = 0;

  for (const char of str) {
    hash = char.charCodeAt(0) + (hash << 5) - hash;
  }

  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    colour += value.toString(16).substring(-2);
  }

  return colour.substring(0, 7);
}

/**
 * A custom hook that ensures the callback is not executed on the first render.
 * This is useful in React's strict mode where effects are run twice on mount.
 *
 * @template T - The type of the dependencies array.
 * @param {() => (void | (() => void))} callback - The effect callback function.
 * @param {T[]} [deps=[]] - The dependencies array for the effect.
 * @returns {void}
 */

export function useStrictModeAwareEffect<T>(
  callback: () => (void | (() => void)),
  deps: T[] = []
): void {
  const isFirstRender = useRef<boolean>(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    return callback();
  }, deps);
}
