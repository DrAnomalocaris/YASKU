# yasku/main.py

import os
import yaml
import pickle
import requests
import time
from tqdm import tqdm
from datetime import datetime


def main():
    # Determine the path to the .yasku config file in the user's home directory
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, ".yasku")

    config = {}
    default_config = {
        'defaultFolder': '.yasku_cache',
        'max_search': 10,
        'topics': ['RNAseq'],
        "discordWebhook": "REPLACE WITH YOUR DISCORD WEBHOOK",
        "username": "Yasku",
    }

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                print(f"Error parsing .yasku config: {e}")
    else:
        print(f"No .yasku config file found in {home_dir}, creating default config.")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
        config = default_config.copy()

    # Ensure the default folder exists
    cache_folder = os.path.join(home_dir, config.get('defaultFolder', '.yasku_cache'))
    os.makedirs(cache_folder, exist_ok=True)

    # Prepare the pickle file path
    pickle_path = os.path.join(cache_folder, 'topics.pkl')

    # If the pickle file does not exist, create it with the topics from config
    if not os.path.exists(pickle_path):
        print(f"Creating new pickle file at {pickle_path}")
        topics_dict = {topic: {} for topic in config.get('topics', [])}
        with open(pickle_path, 'wb') as pf:
            pickle.dump(topics_dict, pf)
    else:
        # If the pickle file exists, open and load it
        with open(pickle_path, 'rb') as pf:
            topics_dict = pickle.load(pf)

    def log_error(message):
        """Append an error message to log.txt in the cache folder with a timestamp."""
        log_path = os.path.join(cache_folder, 'log.txt')
        with open(log_path, 'a', encoding='utf-8') as logf:
            logf.write(f"ERROR {datetime.now().isoformat()}\t{message}\n")

    def search_ncbi(topic, max_results=10):
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': topic,
            'retmax': max_results,
            'retmode': 'json'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('esearchresult', {}).get('idlist', [])
        else:
            error_msg = f"NCBI search failed for {topic} (status {response.status_code})"
            print(error_msg)
            log_error(error_msg)
            return []

    def fetch_pubmed_details(pmids):
        if not pmids:
            return []
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            error_msg = f"Failed to fetch details for PMIDs: {pmids} (status {response.status_code})"
            print(error_msg)
            log_error(error_msg)
            return []
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(response.content)
        except Exception as e:
            error_msg = f"XML parsing error for PMIDs {pmids}: {e}"
            print(error_msg)
            log_error(error_msg)
            return []
        articles = []
        for article in root.findall('.//PubmedArticle'):
            pmid = article.findtext('.//PMID')
            title = article.findtext('.//ArticleTitle')
            abstract = article.findtext('.//Abstract/AbstractText')
            date = article.findtext('.//PubDate/Year')
            authors = []
            for author in article.findall('.//Author'):
                last = author.findtext('LastName') or ''
                first = author.findtext('ForeName') or ''
                if last or first:
                    authors.append(f"{first} {last}".strip())
            articles.append({
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'date': date,
                'authors': authors
            })
        return articles

    def send_discord_webhook_embed(article, webhook_url=None, username=None):
        if webhook_url is None:
            webhook_url = config.get('discordWebhook')
        if username is None:
            username = config.get('username', 'Yasku')
        if not webhook_url or webhook_url == 'REPLACE WITH YOUR DISCORD WEBHOOK':
            print("Discord webhook URL is not set in the config file.")
            return False
        authors = article.get('authors', [])
        if len(authors) > 4:
            author_str = ', '.join(authors[:4]) + ', et al.'
        else:
            author_str = ', '.join(authors)
        url = f"https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid','')}/"
        embed = {
            "title": article.get('title', 'No Title'),
            "url": url,
            "description": article.get('abstract', 'No Abstract'),
            "fields": [
                {"name": "Authors", "value": author_str, "inline": False},
                {"name": "Year", "value": article.get('date', 'N/A'), "inline": True},
                {"name": "PMID", "value": article.get('pmid', ''), "inline": True}
            ]
        }
        data = {
            "username": username,
            "embeds": [embed]
        }
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code in (200, 204):
                print(f"Embed sent {article.get('pmid','')} to Discord webhook.")
                return True
            else:
                error_msg = f"Failed to send embed: {response.status_code} {response.text}"
                print(error_msg)
                log_error(error_msg)
                return False
        except Exception as e:
            error_msg = f"Error sending embed to Discord webhook: {e}"
            print(error_msg)
            log_error(error_msg)
            return False

    max_search = config.get('max_search', 10)
    print(f"Starting search for topics: {', '.join(config.get('topics', []))}")
    print(f"Max search results set to {max_search}")

    for topic in config.get('topics', []):
        print(f"Topic: {topic}", end=' ')
        start_time = time.time()
        pmids = search_ncbi(topic, max_search)
        if not topic in topics_dict:
            topics_dict[topic] = {}
        new_pmids = [pmid for pmid in pmids if pmid not in topics_dict[topic]]
        # Log new PMIDs to log.txt
        log_path = os.path.join(cache_folder, 'log.txt')
        with open(log_path, 'a', encoding='utf-8') as logf:
            logf.write(f"{datetime.now().isoformat()}\t{topic}\t{new_pmids}\n")
        if new_pmids:
            print(f"\t Found {len(new_pmids)} new articles")
        else:
            print("\t No new articles found.")
        if new_pmids:
            details = fetch_pubmed_details(new_pmids)
            for article in details:
                topics_dict[topic][article['pmid']] = article
                send_discord_webhook_embed(article, config.get('discordWebhook'), f"{config.get('username')} - {topic}")
                with open(pickle_path, 'wb') as pf:
                    pickle.dump(topics_dict, pf)
        elapsed = time.time() - start_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
