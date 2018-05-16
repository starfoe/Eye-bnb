"""
Simple flask app.
"""
from flask import (Flask,
                   jsonify,
                   render_template,
                   request)
from ec2.prophet_db import web_query

app = Flask(__name__)


@app.route('/')
def single_page():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def prediction():
    data = request.json#get input passed by json file
    url_input = data.get('single_id')
#     highest_exp = data.get('highest_exp')
    feature_path = 'features\Boston-Massachusetts-US\Boston_all.pickle'
    if url_input:
#         result_apt,result_img = web_query(url_input, feature_path)
        result = web_query(url_input, feature_path)
#     elif highest_exp:
#         result = web_query(None, highest_exp)
#     else:
#         result = web_query()# if no query coming in ,then return hottest apartment

    return jsonify({'inputs': result})#save to jsonify and go back to the webpage
#     return jsonify({'apt_id':result_apt,'img_path':result_img})


def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
