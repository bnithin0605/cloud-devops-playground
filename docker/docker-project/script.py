import os
import re
from collections import Counter
import socket

DATA_PATH = "/home/data"
OUTPUT_PATH = "/home/data/output/result.txt"

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def clean_words(text):
    text = text.lower()
    words = re.findall(r"\b[a-zA-Z']+\b", text)
    return words

def split_contractions(text):
    text = text.lower()
    text = re.sub(r"'", " ", text)
    words = re.findall(r"\b[a-zA-Z]+\b", text)
    return words

def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def main():
    if_path = os.path.join(DATA_PATH, "IF.txt")
    ar_path = os.path.join(DATA_PATH, "AlwaysRememberUsThisWay.txt")

    if_text = read_file(if_path)
    ar_text = read_file(ar_path)

    if_words = clean_words(if_text)
    if_word_count = len(if_words)
    if_top3 = Counter(if_words).most_common(3)

    ar_words = split_contractions(ar_text)
    ar_word_count = len(ar_words)
    ar_top3 = Counter(ar_words).most_common(3)

    grand_total = if_word_count + ar_word_count
    ip_address = get_ip()

    with open(OUTPUT_PATH, "w") as f:
        f.write("Word Count Analysis\n")
        f.write("===================\n\n")
        f.write(f"Total words in IF.txt: {if_word_count}\n")
        f.write(f"Total words in AlwaysRememberUsThisWay.txt: {ar_word_count}\n")
        f.write(f"Grand Total Words: {grand_total}\n\n")

        f.write("Top 3 words in IF.txt:\n")
        for word, count in if_top3:
            f.write(f"{word}: {count}\n")

        f.write("\nTop 3 words in AlwaysRememberUsThisWay.txt (Contractions Split):\n")
        for word, count in ar_top3:
            f.write(f"{word}: {count}\n")

        f.write(f"\nContainer IP Address: {ip_address}\n")

    with open(OUTPUT_PATH, "r") as f:
        print(f.read())

if __name__ == "__main__":
    main()