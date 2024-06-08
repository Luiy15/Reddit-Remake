from flask import Flask, render_template, request
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os
import json
import lucene
from org.apache.lucene.store import SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher
import json

app = Flask(__name__)

def build_index(dir):
    print("indexing")
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    posts_directory = os.path.join(os.getcwd(), 'Posts')
    for filename in os.listdir(posts_directory):
        file_path = os.path.join(posts_directory, filename)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
        else:
            with open(file_path, 'r') as f:
                try:
                    content = f.read()
                    data = json.loads(content)


                    if data[0]:
                        for obj in data:
                            doc = Document()
                            doc.add(Field('title', str(obj['title']), contextType))
                            doc.add(Field('url', str(obj['url']), metaType))
                            doc.add(Field('author', str(obj['author']), metaType))
                            doc.add(Field('created_utc', str(obj['created_utc']), metaType))
                            doc.add(Field('content', str(obj['content']), contextType))
                            doc.add(Field('score', str(obj['score']), metaType))
                            writer.addDocument(doc)
                            print(obj['title'])
                    
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
    writer.close()
    print("indexing finished")

def search_whoosh(query_str, dir):
    print(query_str)
    vm_env = lucene.getVMEnv()
    if vm_env is not None:
        vm_env.attachCurrentThread()
    
    indexdir = NIOFSDirectory(Paths.get(dir))
    searcher = IndexSearcher(DirectoryReader.open(indexdir))
    
    queryParser = QueryParser("<default field>", StandardAnalyzer())
    special = "title:" + query_str+ " OR content:" + query_str

    results = searcher.search(queryParser.parse(special), 10).scoreDocs

    print(len(results))

    hits = []
    for res in results:

        doc = searcher.doc(res.doc)
        title = doc.get('title')
        print(title)
        author = doc.get('author')
        content = doc.get('content')
        hits.append([
            title, 
            author, 
            content, 
            res.score
        ])
    

    return hits

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        print(query)
        index_directory = os.path.join(os.getcwd(), 'new_index')
        results = search_whoosh(query, index_directory)
        return render_template('index.html', query=query, results=results)
    return render_template('index.html')

if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print("Starting Flask server...")
    index_directory = os.path.join(os.getcwd(), 'new_index')
    if not os.path.exists(index_directory):
        os.makedirs(index_directory)
    build_index(index_directory)
    app.run(debug=True, host='0.0.0.0', port=8080)