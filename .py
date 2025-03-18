import re
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
from wordcloud import WordCloud
from textblob import TextBlob

class CulturalTrendAnalyzer:
    def __init__(self):
        self.trends = {}
        self.posts_data = []
        self.common_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'is', 'it', 'on', 'for'])
    
    def clean_text(self, text):
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return "Positive"
        elif analysis.sentiment.polarity < 0:
            return "Negative"
        else:
            return "Neutral"
    
    def extract_trends(self, text, timestamp, source="manual_input"):
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        meaningful_words = [word for word in words if word not in self.common_words and len(word) > 3]
        word_counts = Counter(meaningful_words)
        
        self.posts_data.append({
            'timestamp': timestamp,
            'text': text,
            'source': source,
            'sentiment': self.analyze_sentiment(text)
        })
        
        for word, count in word_counts.items():
            if word not in self.trends:
                self.trends[word] = {'mentions': 0, 'first_seen': timestamp}
            self.trends[word]['mentions'] += count
    
    def analyze_trends(self, min_mentions=3):
        return sorted(
            [{'trend': word, 'mentions': data['mentions'], 'first_seen': data['first_seen']} 
             for word, data in self.trends.items() if data['mentions'] >= min_mentions],
            key=lambda x: x['mentions'], reverse=True)
    
    def visualize_trends(self):
        words = {word: data['mentions'] for word, data in self.trends.items()}
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(words)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title("Trending Words")
        plt.show()
    
    def import_from_csv(self, filepath):
        try:
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                timestamp = pd.to_datetime(row['timestamp'])
                self.extract_trends(row['text'], timestamp, source="csv_import")
            print(f"Successfully imported {len(df)} posts from CSV")
        except Exception as e:
            print(f"Error importing CSV: {e}")
    
    def export_results(self, output_dir="outputs"):
        os.makedirs(output_dir, exist_ok=True)
        trends_df = pd.DataFrame(self.analyze_trends())
        trends_filepath = os.path.join(output_dir, f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        trends_df.to_csv(trends_filepath, index=False)
        posts_df = pd.DataFrame(self.posts_data)
        posts_filepath = os.path.join(output_dir, f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        posts_df.to_csv(posts_filepath, index=False)
        print(f"Results saved to {trends_filepath} and {posts_filepath}")

if __name__ == "__main__":
    analyzer = CulturalTrendAnalyzer()
    while True:
        print("\nOptions:")
        print("1. Enter posts manually")
        print("2. Import posts from CSV")
        print("3. Analyze trends")
        print("4. Visualize trends")
        print("5. Export results")
        print("6. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            while True:
                post = input("Enter post (or type 'done' to finish): ")
                if post.lower() == 'done':
                    break
                analyzer.extract_trends(post, datetime.now())
        elif choice == '2':
            filepath = input("Enter CSV file path: ")
            analyzer.import_from_csv(filepath)
        elif choice == '3':
            trends = analyzer.analyze_trends()
            if trends:
                for i, trend in enumerate(trends[:5], 1):
                    print(f"{i}. {trend['trend']} - {trend['mentions']} mentions (First seen: {trend['first_seen']})")
            else:
                print("No significant trends identified.")
        elif choice == '4':
            analyzer.visualize_trends()
        elif choice == '5':
            analyzer.export_results()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
