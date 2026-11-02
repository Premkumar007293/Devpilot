import { useEffect } from 'react';

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: { ctrlOrMeta?: boolean } = {}
) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      const matchCtrlOrMeta = options.ctrlOrMeta
        ? event.ctrlKey || event.metaKey
        : true;

      if (matchCtrlOrMeta && event.key.toLowerCase() === key.toLowerCase()) {
        event.preventDefault();
        callback();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [key, callback, options.ctrlOrMeta]);
}
