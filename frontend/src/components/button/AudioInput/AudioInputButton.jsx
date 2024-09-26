import React, { useState, useRef, useEffect } from 'react';
import { FaMicrophone, FaStop } from 'react-icons/fa';

function AudioInputButton() {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [volume, setVolume] = useState(0);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleToggleRecording = async () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      audioContextRef.current.createMediaStreamSource(stream).connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        console.log("Size of audioBlob: ", audioBlob.size)
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioURL(audioUrl);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      analyze();
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
    cancelAnimationFrame(animationRef.current);
  };

  const analyze = () => {
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    setVolume(Math.min(average / 100, 1));
    animationRef.current = requestAnimationFrame(analyze);
  };

  useEffect(() => {
    return () => {
      cancelAnimationFrame(animationRef.current);
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#f0f0f0', gap: '20px' }}>
      <button
        onClick={handleToggleRecording}
        style={{
          width: '100px',
          height: '100px',
          borderRadius: '50%',
          backgroundColor: '#f00',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: 'none',
          cursor: 'pointer',
          transition: 'all 0.1s ease',
          transform: `scale(${1 + volume * 0.5})`,
          boxShadow: `
            0 0 ${30 + volume * 50}px ${volume * 25}px rgba(255, 0, 0, 0.6),
            0 0 ${50 + volume * 100}px ${volume * 50}px rgba(255, 0, 0, 0.4)
          `
        }}
      >
        {recording ? <FaStop size={50} color="#fff" /> : <FaMicrophone size={50} color="#fff" />}
      </button>
      {audioURL && (
        <div>
          <h3>Recorded Audio:</h3>
          <audio controls src={audioURL}></audio>
        </div>
      )}
    </div>
  );
}

export default AudioInputButton;