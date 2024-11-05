import os
import discord
from discord.ext import commands, tasks
import aiohttp
from dotenv import load_dotenv
import tweepy
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key and Discord token from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
X_API_KEY = os.getenv('X_API_KEY')
BASE_URL = 'https://public-api.birdeye.so'  # Correct base URL

# Twitter API credentials
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Create a client using the bearer token
twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Ensure message content intent is enabled
bot = commands.Bot(command_prefix="!", intents=intents)

# Set to track posted tokens
posted_tokens = set()

async def fetch_token_data():
    """Fetch token data from Birdeye API."""
    print("Fetching new token listings...")
    url = f'{BASE_URL}/defi/v2/tokens/new_listing'
    headers = {
        'X-API-KEY': X_API_KEY,
        'x-chain': 'solana'  # Specify the chain if needed
    }
    params = {
        'limit': 10
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    print("Successfully fetched new token listings.")
                    return data['data']['items']
            print("Failed to fetch new token listings.")
            return []

async def fetch_token_overview(address):
    """Fetch detailed token overview."""
    print(f"Fetching overview for token address: {address}")
    url = f'{BASE_URL}/defi/token_overview'
    headers = {
        'X-API-KEY': X_API_KEY,
        'x-chain': 'solana'
    }
    params = {
        'address': address
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    print(f"Successfully fetched overview for token address: {address}")
                    return data['data']
            print(f"Failed to fetch overview for token address: {address}")
            return None

async def fetch_token_security(address):
    """Fetch token security information."""
    print(f"Fetching security info for token address: {address}")
    url = f'{BASE_URL}/defi/token_security'
    headers = {
        'X-API-KEY': X_API_KEY,
        'x-chain': 'solana'
    }
    params = {
        'address': address
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    print(f"Successfully fetched security info for token address: {address}")
                    return data['data']
            print(f"Failed to fetch security info for token address: {address}")
            return None

def format_number(value, decimals=2):
    """Format numbers with commas and specified decimal places."""
    return f"{value:,.{decimals}f}"

def search_tweets(query, max_results=100):
    """Search for tweets containing the query."""
    try:
        # Use the client to search for tweets
        response = twitter_client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['author_id', 'public_metrics', 'created_at'],
            user_fields=['username', 'public_metrics'],
            expansions='author_id'
        )

        if not response.data:
            print("No tweets found.")
            return []

        users = {u['id']: u for u in response.includes['users']}
        tweets = []

        for tweet in response.data:
            user = users.get(tweet.author_id)
            if user:
                tweet_time = tweet.created_at.replace(tzinfo=timezone.utc)
                one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
                if tweet_time > one_hour_ago:
                    tweets.append({
                        'user': user['username'],
                        'followers': user['public_metrics']['followers_count'],
                        'tweet_url': f"https://twitter.com/{user['username']}/status/{tweet.id}",
                        'profile_url': f"https://twitter.com/{user['username']}"
                    })

        # Sort tweets by followers
        tweets.sort(key=lambda x: x['followers'], reverse=True)
        return tweets[:3]  # Return top 3 tweets

    except tweepy.errors.TweepyException as e:
        print(f"Error: {e}")
        return []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    fetch_and_post_tokens.start()  # Start the task when the bot is ready

@tasks.loop(minutes=1)
async def fetch_and_post_tokens():
    """Fetch new token listings and post to Discord if conditions are met."""
    channel = discord.utils.get(bot.get_all_channels(), name='degen-feed')  # Replace with your channel name
    if not channel:
        print("Channel not found.")
        return

    new_listings = await fetch_token_data()
    for token in new_listings:
        address = token['address']
        
        # Skip if the token has already been posted
        if address in posted_tokens:
            print(f"Token {address} has already been posted. Skipping.")
            continue

        overview = await fetch_token_overview(address)
        security = await fetch_token_security(address)
        
        if overview and security:
            # Extract necessary data
            symbol = overview.get('symbol', 'N/A')
            name = overview.get('name', 'N/A')
            price = overview.get('price', 0)
            liquidity = overview.get('liquidity', 0)
            mc = overview.get('mc', 0)
            volume_30m_usd = overview.get('v30mUSD', 0)
            volume_buy_1h_usd = overview.get('vBuy1hUSD', 0)
            volume_sell_1h_usd = overview.get('vSell1hUSD', 0)
            unique_wallet_30m = overview.get('uniqueWallet30m', 0)
            unique_wallet_1h = overview.get('uniqueWallet1h', 0)
            unique_view_1h = overview.get('uniqueView1h', 0)
            holder = overview.get('holder', 0)
            source = overview.get('source', 'N/A')
            mintable = security.get('ownerAddress') is not None
            mutable = security.get('mutableMetadata', False)

            # Check conditions
            if source == "pump.fun" and volume_30m_usd >= 100000:
                print(f"Preparing to send embed for token: {symbol} with address: {address}")

                # Determine emoji for source
                new_emoji = "🆕 💊"

                # Format numbers
                price_formatted = format_number(price, 8 if price < 1 else 4)
                liquidity_formatted = format_number(liquidity)
                mc_formatted = format_number(mc)
                volume_30m_usd_formatted = format_number(volume_30m_usd)
                volume_buy_1h_usd_formatted = format_number(volume_buy_1h_usd)
                volume_sell_1h_usd_formatted = format_number(volume_sell_1h_usd)

                # Search for tweets mentioning the token
                search_query = f"{symbol} OR {address}"
                tweets = search_tweets(search_query)

                # Create the embed message
                embed = discord.Embed(
                    title=f"{new_emoji} [{symbol}](https://pump.fun/{address}) [{mc_formatted}/{volume_buy_1h_usd_formatted}] - {name}/SOL",
                    description=(
                        f"💰 USD: ${price_formatted}\n"
                        f"💎 FDV: ${mc_formatted}\n"
                        f"💦 Liq: ${liquidity_formatted}\n"
                        f"📊 Vol 30m: ${volume_30m_usd_formatted}\n"
                        f"📊 Vol Buy 1h: ${volume_buy_1h_usd_formatted}\n"
                        f"📊 Vol Sell 1h: ${volume_sell_1h_usd_formatted}\n"
                        f"👥 Holders: {holder}\n"
                        f"👥 Unique Wallet 30m: {unique_wallet_30m}\n"
                        f"👥 Unique Wallet 1h: {unique_wallet_1h}\n"
                        f"👥 Unique View 1h: {unique_view_1h}\n"
                        f"🖨️ Mint: {'✅' if mintable else '🔥'} ⋅ LP: {'🔥' if mutable else '✅'}"
                    ),
                    color=0x00ff00
                )
                embed.set_thumbnail(url=overview.get('logoURI', ''))
                embed.set_footer(text=f"Address: {address}")

                # Add top tweets to the embed
                if tweets:
                    for tweet in tweets:
                        embed.add_field(
                            name=f"User: [{tweet['user']}]({tweet['profile_url']}) (Followers: {tweet['followers']})",
                            value=f"[View Tweet]({tweet['tweet_url']})",
                            inline=False
                        )

                await channel.send(embed=embed)
                print(f"Sent token info embed for {address}.")
                
                # Add the token address to the set of posted tokens
                posted_tokens.add(address)

# Run the bot
bot.run(DISCORD_TOKEN)
