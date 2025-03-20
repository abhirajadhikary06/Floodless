from django.shortcuts import render
from django.core.cache import cache
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk import bigrams
from datetime import datetime
from .models import NewsArticle

# Ensure punkt_tab is downloaded
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

def fetch_and_process_news():
    api_key = '33e4180d7dd04c9ebea8bbff7cd197e5'
    url = f'https://newsapi.org/v2/everything?q="natural disaster" OR earthquake OR flood OR hurricane OR wildfire OR tsunami OR cyclone OR tornado -politics -business -sports&apiKey={api_key}&language=en&sortBy=relevancy'

    response = requests.get(url)
    data = response.json()
    print("API Response:", data)  # Debug

    if data['status'] == 'ok':
        NewsArticle.objects.all().delete()

        articles_to_cache = []
        for article in data['articles']:
            title = article['title']
            description = article.get('description', '') or ''
            full_text = title + " " + description

            is_disaster = analyze_news(full_text)

            if is_disaster and not NewsArticle.objects.filter(url=article['url']).exists():
                news_article = NewsArticle(
                    title=title,
                    description=description,
                    url=article['url'],
                    published_at=datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    source=article['source']['name'],
                    is_disaster_related=True
                )
                articles_to_cache.append(news_article)

        if articles_to_cache:
            NewsArticle.objects.bulk_create(articles_to_cache)

        cached_articles = list(NewsArticle.objects.filter(is_disaster_related=True).values(
            'title', 'description', 'url', 'published_at', 'source', 'is_disaster_related'
        ))
        #print("Cached articles:", cached_articles)  # Debug
        cache.set('disaster_news', cached_articles, 900)
        return cached_articles
    return []

def analyze_news(text):
    text = text.lower()
    tokens = word_tokenize(text)
    disaster_keywords = {'disaster', 'earthquake', 'flood', 'hurricane', 'wildfire', 'tsunami', 'cyclone', 'tornado', 'storm'}
    exclude_phrases = {'flood of', 'storm of', 'earthquake in politics', 'hurricane of', 'wildfire of', 'tsunami of'}
    exclude_words = {'tiktok', 'smartphone'}
    disaster_context = {'damage', 'evacuation', 'relief', 'victims', 'destroyed', 'warning', 'emergency'}

    has_disaster_keyword = any(token in disaster_keywords for token in tokens)
    text_str = " ".join(tokens)
    has_exclusion_phrase = any(phrase in text_str for phrase in exclude_phrases)
    has_exclusion_word = any(word in tokens for word in exclude_words)
    bigram_list = [" ".join(bg) for bg in bigrams(tokens)]
    has_context = any(bg in disaster_context or bg in disaster_keywords for bg in bigram_list)

    print(f"Text: {text[:100]}... | Keyword: {has_disaster_keyword} | Exclusion Phrase: {has_exclusion_phrase} | Exclusion Word: {has_exclusion_word} | Context: {has_context}")

    # Relaxed condition: disaster keyword alone is enough if no exclusions
    if not has_disaster_keyword or has_exclusion_phrase or has_exclusion_word:
        return False
    return True  # Accept if it has a disaster keyword and no exclusions, context optional

def news_list(request):
    cached_articles = cache.get('disaster_news')
    if cached_articles is None:
        print("Cache miss, fetching news...")
        cached_articles = fetch_and_process_news()
    else:
        print("Cache hit, using cached articles:", cached_articles)
    articles = NewsArticle.objects.filter(is_disaster_related=True).order_by('-published_at')
    print("Database articles:", list(articles.values()))
    return render(request, 'news/news_list.html', {'articles': articles})