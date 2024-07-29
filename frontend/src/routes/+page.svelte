<script>
  let email = "";
  let file = null;

  let error = null;

  const handleFileChange = (event) => {
    const target = event.target;
    file = target.files?.[0] || null;
  };
  const handleSubmit = async (event) => {
    console.log(error);
    event.preventDefault();
    if (!file || !email) {
      error = "Please provide both a video file and your email.";
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);
    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("File uploaded successfully!");
      } else {
        error = "Failed to upload file.";
      }
    } catch (er) {
      console.error("Error uploading file:", er);
      error = "An error occurred while uploading the file.";
    }
  };
</script>

<div class="container">
  <h1>Video to Audio Converter</h1>
  <form on:submit|preventDefault={handleSubmit} class="form">
    <input
      type="email"
      placeholder="Enter email to notify"
      name="email"
      bind:value={email}
      required
      id="email"
    />
    <input
      type="file"
      placeholder="Select a video file"
      required
      hidden
      dropzone="bind:this"
      on:change={handleFileChange}
      name="file"
      id="file"
      accept="video/*"
    />
    <label for="file" class="video-container">
      {#if file != null}
        {file.name}
      {:else}
        Drag and Drop Video
      {/if}
    </label>

    {#if error != null}
      <div class="error-container">
        <p>{error}</p>
      </div>
    {/if}
    <button type="submit" class="submit-btn"> Convert </button>
  </form>
</div>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap");
  .container {
    height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .error-container {
    padding: 4px;
    margin: 4px;
    display: flex;
    justify-content: center;
    background-color: rgba(235, 109, 109, 0.438);
    border-radius: 5px;
    width: 100%;
  }

  .error-container p {
    color: red;
    font-size: 18px;
  }

  .submit-btn {
    width: 100%;
    margin: 5px;
    height: 40px;
    color: white;
    font-size: 16px;
    font-weight: bold;
    background-color: rgb(22, 166, 223);
    border: none;
    border-radius: 5px;
  }

  #email {
    height: 40px;
    padding: 2px;
    width: 100%;
    font-size: 16px;
  }

  .submit-btn:hover {
    background-color: rgb(107, 201, 238);
    transition: 0.2s ease-in-out;
  }

  .video-container {
    margin: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    width: 100%;
    height: 150px;
    border-radius: 5px;
    border: 2px solid gray;
    border-style: dashed;
  }

  /* input {
    margin: 5px 0px 5px 0px;
    padding: 5px;
  } */

  .form {
    padding: 10px;
    display: flex;
    width: 500px;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }
</style>
