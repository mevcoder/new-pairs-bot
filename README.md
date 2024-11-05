```markdown
# Discord Bot with Twitter Integration

This project is a Discord bot that fetches new token listings from the Birdeye API and monitors Twitter for mentions of these tokens. It posts updates to a specified Discord channel, including token information and relevant tweets.

## Features

-  Fetches new token listings from the Birdeye API.
-  Monitors Twitter for mentions of token symbols or contract addresses.
-  Posts token information and top tweets to a Discord channel.
-  Uses asynchronous HTTP requests to ensure non-blocking operations.

## Prerequisites

-  Python 3.8 or higher
-  A Discord bot token
-  Birdeye API key
-  Twitter API bearer token
-  A VPS or local machine to run the bot

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the project root with the following content:

   ```plaintext
   DISCORD_TOKEN=your_discord_token
   X_API_KEY=your_birdeye_api_key
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   ```

## Running the Bot

1. **Activate the Virtual Environment**

   ```bash
   source venv/bin/activate
   ```

2. **Run the Bot**

   ```bash
   python your_bot_script.py
   ```

## Deployment on a VPS

1. **Set Up a VPS**

   Choose a VPS provider and set up an instance with Python and Git installed.

2. **Clone the Repository and Set Up**

   Follow the setup instructions above on your VPS.

3. **Keep the Bot Running**

   Use `screen` or `tmux` to keep the bot running even after disconnecting from SSH:

   ```bash
   screen -S discord-bot
   python your_bot_script.py
   ```

   Detach from the screen session with `Ctrl + A`, then `D`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

-  [Discord.py](https://discordpy.readthedocs.io/en/stable/) for Discord bot functionality.
-  [Tweepy](https://www.tweepy.org/) for Twitter API integration.
-  [aiohttp](https://docs.aiohttp.org/en/stable/) for asynchronous HTTP requests.
```

### Explanation

-  **Overview**: Provides a brief description of the project and its features.
-  **Prerequisites**: Lists the necessary tools and accounts needed to run the bot.
-  **Setup Instructions**: Guides users through cloning the repository, setting up a virtual environment, installing dependencies, and configuring environment variables.
-  **Running the Bot**: Instructions for running the bot locally.
-  **Deployment**: Steps for deploying the bot on a VPS and keeping it running.
-  **Contributing**: Encourages contributions to the project.
-  **License**: Mentions the project's license.
