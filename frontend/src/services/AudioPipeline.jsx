import React, { useRef, useState } from "react";
import { FaMicrophone } from "react-icons/fa";

const AudioPipeline = () => {
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [disabled, setDisabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingTimeoutRef = useRef(null);
  const isAudioPlayingRef = useRef(false);

  const startRecording = async () => {
    console.log("Step 1: Requesting microphone access...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      audioChunksRef.current = [];
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        console.log("Step 2: Recording stopped, processing audio blob...");
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        handleAudioBlob(audioBlob);
      };

      mediaRecorderRef.current.start(1000);
      setIsRecording(true);

      recordingTimeoutRef.current = setTimeout(() => {
        if (isRecording) {
          stopRecording();
        }
      }, 25000);
      console.log("Step 1: Microphone recording started.");
    } catch (err) {
      console.error("Microphone access error:", err);
      setError("Microphone access denied.");
    }
  };

  const stopRecording = () => {
    console.log("Step 2: Stopping recording...");
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearTimeout(recordingTimeoutRef.current);
    }
  };

  const toggleRecording = () => {
    setError(null);
    if (disabled || !chatStarted) return;

    if (isRecording) {
      console.log("Step 2: Toggle - stopping recording.");
      stopRecording();
    } else {
      console.log("Step 1: Toggle - starting recording.");
      startRecording();
    }
  };

  const handleAudioBlob = async (audioBlob) => {
    setLoading(true);
    setDisabled(true);
    try {
      console.log("Step 3: Sending audio to /transcribe...");
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.webm");

      const transcriptionRes = await fetch("http://localhost:3001/transcribe/", {
        method: "POST",
        body: formData,
      });

      if (!transcriptionRes.ok) throw new Error(await transcriptionRes.text());
      const transcriptionData = await transcriptionRes.json();
      const transcribedText = transcriptionData.transcription || "";

      setTranscription(transcribedText);
      console.log("Step 3: Received transcription:", transcribedText);

      const secondPayload = {
        sender: "test_user",
        message: transcribedText,
      };

      console.log("Step 4: Sending message to Rasa webhook...");
      console.log("Payload:", JSON.stringify(secondPayload));
      const secondRes = await fetch("http://localhost:5005/webhooks/rest/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(secondPayload),
      });

      if (!secondRes.ok) throw new Error(await secondRes.text());
      const secondData = await secondRes.json();

      for (const message of secondData) {
        if (!message.text) continue;

        const thirdPayload = {
          text: message.text,
          lang: "Hindi",
        };

        console.log("Step 5: Sending text to TTS service...");
        console.log("Payload:", JSON.stringify(thirdPayload));
        const thirdRes = await fetch("http://localhost:5050/speak/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(thirdPayload),
        });

        if (!thirdRes.ok) throw new Error(await thirdRes.text());
        const blob  = await thirdRes.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        console.log("Step 5: Received audio URL:", audioUrl);
        isAudioPlayingRef.current = true;
        audio.play()
          .catch((err) => console.error("Audio play error:", err))
          .finally(() => {
            isAudioPlayingRef.current = false;
      });
        
      }
    } catch (err) {
      console.error("Processing error:", err.message);
      setError("Error: " + err.message);
      setTranscription("");
    } finally {
      setLoading(false);
      setDisabled(false);
    }
  };



  return (
    <div style={{ textAlign: "center", padding: "4rem" }}>
      <h1>🎙 Voice Chat Assistant</h1>

      {!chatStarted ? (
        <button
          onClick={() => setChatStarted(true)}
          style={{
            fontSize: "2rem",
            padding: "1.5rem 3rem",
            borderRadius: "50px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
        >
          Start Chat
        </button>
      ) : (
        <>
          <button
            onClick={toggleRecording}
            disabled={disabled || isAudioPlayingRef.current}
            style={{
              backgroundColor: isRecording ? "red" : "green",
              color: "white",
              fontSize: "3rem",
              borderRadius: "50%",
              width: "150px",
              height: "150px",
              border: "none",
              cursor: disabled ? "not-allowed" : "pointer",
              marginBottom: "2rem"
            }}
          >
            <FaMicrophone />
          </button>

          <br />
          <button
            onClick={() => setChatStarted(false)}
            disabled={isAudioPlayingRef.current}
            style={{
              padding: "1rem 2rem",
              fontSize: "1.25rem",
              backgroundColor: "#dc3545",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: isAudioPlayingRef.current ? "not-allowed" : "pointer",
              opacity: isAudioPlayingRef.current ? 0.5 : 1
            }}
          >
            End Chat
          </button>
        </>
      )}

      {loading && <p>⏳ Processing...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {transcription && (
        <p style={{ marginTop: "1rem" }}>
          <strong>Transcription:</strong> {transcription}
        </p>
      )}
    </div>
  );
};

export default AudioPipeline;
