import meilisearch
import json

client = meilisearch.Client('http://search:7700')

json_file = open('movies.json')
movies = json.load(json_file)
client.index('movies').add_documents(movies)