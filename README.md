<p align="center">
  <img src="https://user-images.githubusercontent.com/30778939/226750505-c32cd3cb-cf7e-4197-8efc-5dc1037a4274.png" alt="GitMate">
</p>
<p align="center">
    <em>GitMate is your companion to generate commit messages, PR titles and descriptions using ChatGPT.</em>
</p>

______________________________________________________________________

### Installation

```console
pip install gitmate
```

______________________________________________________________________

### Usage

1. Add your API keys and model type

   ```console
   gitmate connect
   ```

1. Verify your keys

   ```console
   gitmate verify
   ```

1. Create a commit

   ```diff
   git add some_file.py
   - git commit -m "commit message"
   + gitmate commit
   ```

1. Create a PR

   ```diff
   - gh pr create -t "some title" -b "some description"
   + gitmate create-pr

   ```

______________________________________________________________________

### Demo

https://user-images.githubusercontent.com/30778939/226752630-aec2c8f8-c06f-4123-8023-a0b764ac21fd.mp4
