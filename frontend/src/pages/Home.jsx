import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Welcome to Voice Transcription App</h1>
      <p style={styles.subheading}>Record your voice and get instant text transcription.</p>
      
      <Link to="/home">
        <button style={styles.button}>Go to Recorder</button>
      </Link>
    </div>
  );
};

const styles = {
  container: {
    padding: '2rem',
    textAlign: 'center',
    fontFamily: 'sans-serif',
  },
  heading: {
    fontSize: '2.5rem',
    marginBottom: '1rem',
  },
  subheading: {
    fontSize: '1.2rem',
    marginBottom: '2rem',
    color: '#555',
  },
  button: {
    padding: '0.8rem 1.5rem',
    fontSize: '1rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  }
};

export default Home;

