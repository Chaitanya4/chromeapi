from flask import Flask
from nltk import download
from flask import request
from newspaper import Article
import json
from flask import jsonify
from flask_cors import CORS
from modzy import ApiClient
API_URL="https://app.modzy.com/api"
API_KEY="vI080k8e9RUJ8mCCKdBj.Bqz3fPY9dyz56lvh1eiA"
client = ApiClient(base_url=API_URL, api_key=API_KEY)
# This is needed for nltk to work (used to summarize article)
download('punkt')

app= Flask(__name__) 

# This enables CORS (allows API to be called from another server)
# Not recommended if info needs to be secure
CORS(app)


@app.route('/')
def index():
    return "<h1>Welcome to the text summary API. Add query?article={INSERT ARTICLE URL HERE} to get article summary</h1>" 

@app.route("/query")
def query():

    # Gets article URL
    url = request.args.get('article')
    
    # Create article object
    article = Article(url, 
    keep_article_html= False, #, “set to True if you want to preserve html of body text”

    http_success_only=True, #, default True, “set to False to capture non 2XX responses as well”

    MIN_WORD_COUNT=300, #, default 300, “num of word tokens in article text”

    MIN_SENT_COUNT=7, #, default 7, “num of sentence tokens”

    MAX_TITLE=200, #, default 200, “num of chars in article title”

    MAX_TEXT=100000, # , default 100000, “num of chars in article text”

    MAX_KEYWORDS=35, #, default 35, “num of keywords in article”

    MAX_AUTHORS=10, #, default 10, “num of author names in article”

    MAX_SUMMARY=5000, # , default 5000, “num of chars of the summary”

    MAX_SUMMARY_SENT=5, #, default 5, “num of sentences in summary”

    MAX_FILE_MEMO=20000, # , default 20000, “python setup.py sdist bdist_wininst upload”

    memoize_articles=True, # , default True, “cache and save articles run after run”

    fetch_images=True, #, default True, “set this to false if you don’t care about getting images”

    follow_meta_refresh=True, #, default False, “follows a redirect url in a meta refresh html tag”

    image_dimension_ration=True, # , default 16/9.0, “max ratio for height/width, we ignore if greater”

    language='en', #, default ‘en’, “run newspaper.languages() to see available options.”""""""

    # browser_user_agent, default ‘newspaper/%s’ % __version__

    request_timeout=7, #, default 7

    number_threads=10, # , default 10, “number of threads when mthreading”

    verbose=False# , default False, “turn this on when debugging”
    )

    # Get article
    article.download()
    article.parse()

    # Summarize Article
    article.nlp()
    summary_job = client.jobs.submit_text('rs2qqwbjwb', '0.0.2', {'input.txt': article.text})
    summary_result = client.results.block_until_complete(summary_job, timeout=None)
    entity_recognition_job = client.jobs.submit_text('a92fc413b5', '0.0.12', {'input.txt': summary_result['results']['job']['results.json']['summary']})
    entity_recognition_result = client.results.block_until_complete(entity_recognition_job, timeout=None)
    entities = []
    for word in entity_recognition_result["results"]['job']['results.json']:
            if word[1] !='O':
                entities.append(word[0])
    text_topics_job = client.jobs.submit_text('m8z2mwe3pt', '0.0.1', {'input.txt': article.text})
    text_topics_result = client.results.block_until_complete(text_topics_job, timeout=None)
   
    
    # Create dictionary 
    test = {
        "summary": "%s" %summary_result['results']['job']['results.json']['summary'],
        "text topics": "%s" %text_topics_result['results']['job']['results.json'],
        "entity recognition": "%s" %entities
    }

    # Convert dict to JSON & return
    return jsonify(test)