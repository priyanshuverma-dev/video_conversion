<script lang="ts">
  import { onMount } from 'svelte';
  let email: string = '';
  let file: File | null = null;

  const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    file = target.files?.[0] || null;
  };

  const handleSubmit = async (event: Event) => {
    event.preventDefault();
    if (!file || !email) {
      alert('Please provide both a video file and your email.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('email', email);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert('File uploaded successfully!');
      } else {
        alert('Failed to upload file.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };
</script>

<main>
  <h1>Video to Audio Converter</h1>
  <form on:submit|preventDefault={handleSubmit}>
    <input type="email" bind:value={email} placeholder="Enter your email" required />
    <input type="file" accept="video/*" on:change={handleFileChange} required />
    <button type="submit">Upload</button>
  </form>
</main>

<style>
  main {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  h1 {
    color: #ff3e00;
    font-size: 1.5em;
  }

  input {
    margin: 0.5em 0;
    padding: 0.5em;
    width: 100%;
  }

  button {
    padding: 0.5em 1em;
    background-color: #ff3e00;
    color: white;
    border: none;
    cursor: pointer;
  }

  button:hover {
    background-color: #e63800;
  }
</style>
