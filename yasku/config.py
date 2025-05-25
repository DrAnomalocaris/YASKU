import os
import yaml

def main():
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, ".yasku")
    print("YASKU Configurator\n-------------------")
    webhook = input("Webhook url: ").strip()
    topics = []
    print("Enter topics (add topics one by one, press Enter on empty line to finish):")
    while True:
        topic = input("Topic: ").strip()
        if not topic:
            break
        topics.append(topic)
    config = {
        'defaultFolder': '.yasku_cache',
        'max_search': 10,
        'topics': topics if topics else ['RNAseq'],
        'discordWebhook': webhook,
        'username': 'Yasku',
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    print(f"\nConfig file written to: {config_path}")
    print("You can edit this file manually if you wish.")

if __name__ == "__main__":
    main()
