# YASKU: Yet Another Science Keppy Upy

YASKU is a Python tool to help you keep up to date with the latest publications in your favorite science fields. It searches PubMed for new articles on your chosen topics and can send notifications to a Discord channel using webhooks.

---

## Features

- Searches PubMed for new articles on your topics
- Sends article summaries to Discord via webhook (as rich embeds)
- Keeps a local cache and log of found articles
- Easy configuration with a YAML file in your home directory

---

## Installation

1. **Clone or Download** this repository:

   ```sh
   git clone <this-repo-url>
   cd YASKU
   ```
2. **Install Python dependencies** (Python 3.7+ recommended):

   ```sh
   pip install requests pyyaml tqdm
   ```

---

## Configuration

YASKU uses a YAML config file named `.yasku` in your home directory. The first run will create a default one if it doesn't exist.

Example `.yasku` file:

```yaml
defaultFolder: .yasku_cache
max_search: 10
topics:
  - RNAseq
  - CRISPR
  - Cancer
username: Yasku
discordWebhook: "REPLACE WITH YOUR DISCORD WEBHOOK"
```

- **defaultFolder**: Where to store cache and logs (relative to your home directory)
- **max_search**: Number of articles to fetch per topic
- **topics**: List of topics to track
- **username**: Name to display in Discord
- **discordWebhook**: Your Discord webhook URL (see below)

> **Note:** You must set a valid Discord webhook URL to receive notifications in Discord.

---

## Usage

Run the script:

```sh
python YASKU.py
```

- The script will search PubMed for each topic in your config.
- New articles will be logged in `log.txt` in your cache folder.
- Article details will be sent to your Discord channel as embeds (if webhook is set).

---

## Setting up a Discord Webhook

1. Go to your Discord server and create a webhook in the channel settings.
2. Copy the webhook URL.
3. Paste it into the `discordWebhook` field in your `.yasku` config file.

---

## Logs and Cache

- All found articles are cached in a pickle file in your cache folder.
- All new PMIDs and errors are logged in `log.txt` in the same folder.

---

## License

MIT License

---

## About

**YASKU** stands for "Yet Another Science Keppy Upy". It is designed to help scientists and enthusiasts stay up to date with the latest research in their fields.
