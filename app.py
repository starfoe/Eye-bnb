"""
Simple flask app.
"""
from flask import (Flask,
                   jsonify,
                   render_template,
                   request)
from eyebnb_ec2.web_query import *
 
app = Flask(__name__)


@app.route('/')
def single_page():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def prediction():
    data = request.json#get input passed by json file
    print(data)
    url_input = data.get('single_id')
#     highest_exp = data.get('highest_exp')
    feature_path = 'features/Boston-Massachusetts-US/Boston_feature_new_all.pickle'
    if url_input:
        print('get an url:{}'.format(url_input))
#         result_apt,result_img = web_query(url_input, feature_path)
        result = web_query(url_input, feature_path)
        print(result)
    return render_template('pictureGrids.html',data=result)



def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
