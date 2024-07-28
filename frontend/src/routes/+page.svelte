<script>
</script>

<div class="container">
  <form method="POST" class="form">
    <input
      type="email"
      placeholder="Enter email to notify"
      name="email"
      required
      id="email"
    />
    <label for="file" class="video-container">
      Drag and Drop Video
      <input
        type="file"
        placeholder="Select a video file"
        required
        dropzone="bind:this"
        name="file"
        id="file"
        accept="video/*"
      />
    </label>
    <button type="submit" class="submit-btn"> Convert </button>
  </form>
</div>

<style>
  .container {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .submit-btn {
    width: 100%;
    height: 40px;
    color: white;
    font-size: 16px;
    font-weight: bold;
    background-color: skyblue;
    border: none;
    border-radius: 5px;
    margin: 0px 5px 0px 5px;
  }

  #email {
    height: 40px;
    padding: 2px;
    font-size: 16px;
  }

  #file {
    width: 150px;
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
    width: 200px;
    height: 150px;
    border-radius: 5px;
    border: 2px solid gray;
    border-style: dashed;
    padding: 10px;
  }

  /* input {
    margin: 5px 0px 5px 0px;
    padding: 5px;
  } */

  .form {
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }
</style>
