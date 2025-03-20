from django.shortcuts import render
from django.core.cache import cache
import requests
import nltk
from nltk.tokenize import word_tokenize
from datetime import datetime
from .models import NewsArticle

# Ensure punkt_tab is downloaded
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

def fetch_and_process_news():
    api_key = '33e4180d7dd04c9ebea8bbff7cd197e5'  # Your NewsAPI key
    url = f'https://newsapi.org/v2/everything?q="natural disaster" OR earthquake OR flood OR hurricane OR wildfire OR tsunami OR cyclone OR tornado -politics -business -sports&apiKey={api_key}&language=en&sortBy=relevancy'

    response = requests.get(url)
    data = response.json()

    if data['status'] == 'ok':
        NewsArticle.objects.all().delete()  # Clear old articles (optional)

        articles_to_cache = []
        for article in data['articles']:
            title = article['title']
            description = article.get('description', '') or ''
            full_text = title + " " + description

            # Check if disaster-related using NLTK
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

        # Bulk create to save all articles at once
        if articles_to_cache:
            NewsArticle.objects.bulk_create(articles_to_cache)

        # Cache the articles (queryset serialized as a list of dicts)
        cached_articles = list(NewsArticle.objects.filter(is_disaster_related=True).values(
            'title', 'description', 'url', 'published_at', 'source', 'is_disaster_related'
        ))
        cache.set('disaster_news', cached_articles, 900)  # Cache for 15 minutes
        return cached_articles
    return []

def analyze_news(text):
    """
    Enhanced disaster check with NLTK: look for keywords with context and exclude non-disaster phrases.
    """
    text = text.lower()
    tokens = word_tokenize(text)
    disaster_keywords = {'disaster', 'earthquake', 'flood', 'hurricane', 'wildfire', 'tsunami', 'cyclone', 'tornado', 'storm'}
    exclude_phrases = {'flood of', 'storm of', 'earthquake in politics', 'hurricane of', 'wildfire of', 'tsunami of'}
    disaster_context = {'damage', 'evacuation', 'relief', 'victims', 'destroyed', 'warning', 'emergency'}

    has_disaster_keyword = any(token in disaster_keywords for token in tokens)
    if not has_disaster_keyword:
        return False

    text_str = " ".join(tokens)
    has_exclusion = any(phrase in text_str for phrase in exclude_phrases)
    has_context = any(token in disaster_context for token in tokens)

    return has_disaster_keyword and (has_context or not has_exclusion)

def news_list(request):
    # Check cache first
    cached_articles = cache.get('disaster_news')
    if cached_articles is None:
        # If not in cache, fetch and process news
        cached_articles = fetch_and_process_news()
    
    # Convert cached articles to a queryset-like format for the template
    articles = NewsArticle.objects.filter(is_disaster_related=True).order_by('-published_at')
    return render(request, 'news/news_list.html', {'articles': articles})