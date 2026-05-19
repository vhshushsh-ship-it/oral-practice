import { useState, useRef, useCallback, useEffect } from 'react';

export function useRecordingPlayback() {
  const [hasRecording, setHasRecording] = useState(false);
  const [isPlayingRecording, setIsPlayingRecording] = useState(false);
  const blobRef = useRef<Blob | null>(null);
  const urlRef = useRef<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const revoke = useCallback(() => {
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, []);

  useEffect(() => {
    return revoke;
  }, [revoke]);

  const storeRecording = useCallback((blob: Blob) => {
    revoke();
    blobRef.current = blob;
    setHasRecording(true);
  }, [revoke]);

  const playRecording = useCallback(() => {
    if (!blobRef.current) return;
    if (audioRef.current) {
      audioRef.current.pause();
    }
    urlRef.current = URL.createObjectURL(blobRef.current);
    const audio = new Audio(urlRef.current);
    audioRef.current = audio;
    setIsPlayingRecording(true);
    audio.onended = () => setIsPlayingRecording(false);
    audio.onerror = () => setIsPlayingRecording(false);
    audio.play().catch(() => setIsPlayingRecording(false));
  }, []);

  const stopPlayback = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlayingRecording(false);
  }, []);

  const clearRecording = useCallback(() => {
    stopPlayback();
    revoke();
    blobRef.current = null;
    setHasRecording(false);
  }, [stopPlayback, revoke]);

  return { hasRecording, isPlayingRecording, storeRecording, playRecording, stopPlayback, clearRecording };
}
