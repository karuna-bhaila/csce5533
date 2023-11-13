from flask import Flask, request, render_template

from read import get_documents


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homepage.html', name='homepage')
    
@app.route('/query/', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        query_words = request.form.get('query_terms')

        if query_words != '':
            docs, matches, weights = get_documents(query_words.split())

            if len(docs) > 0:
                return render_template('result.html', docs=zip(docs,matches,weights), query_words=query_words)
            else:
                return render_template('error.html', query_words=query_words)
        else:
            return render_template('homepage.html', name='homepage')
       
@app.route('/query/result/<name>', methods=['GET'])
def result(name):
    return render_template(name)

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404
  
if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


