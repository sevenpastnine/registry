import { useState, useEffect } from 'react';

export interface UseFetchState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseFetchOptions<T> {
  headers?: HeadersInit;
  method?: string;
  body?: BodyInit;
  immediate?: boolean;
  // Function to transform the data before returning it
  transform?: (data: any) => T;
}

export interface UseFetchResult<T> {
  // The fetched data, null if not yet loaded
  data: T | null;
  // Loading state indicator
  loading: boolean;
  // Error object if the request failed, null otherwise
  error: Error | null;
  // Function to manually trigger a new fetch
  refetch: () => void;
}

export function useFetch<T>(url: string, options: UseFetchOptions<T> = {}): UseFetchResult<T> {
  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchData = async (signal?: AbortSignal) => {
    setState(prev => ({ ...prev, loading: true }));

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers: options.headers,
        body: options.body,
        signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      var data = await response.json();
      if (options.transform) { data = options.transform(data); }

      setState({ data, loading: false, error: null });
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return;
        }
        setState({ data: null, loading: false, error });
      }
    }
  };

  useEffect(() => {
    if (options.immediate === false) {
      return;
    }

    const controller = new AbortController();
    fetchData(controller.signal);

    return () => {
      controller.abort();
    };
  }, [url]);

  return {
    ...state,
    refetch: () => fetchData(),
  };
}
