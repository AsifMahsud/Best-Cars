from cloudant.client import Cloudant
from flask import Flask, jsonify, request, abort
import json

# Load Cloudant service credentials
with open('../../.creds.json', 'r') as file:
    creds = json.load(file)

cloudant_username = creds['COURCE_USERNAME']
cloudant_api_key = creds['IAM_API_KEY']
cloudant_url = creds['COUCH_URL']

client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)
session = client.session()
print('Databases:', client.all_dbs())
db = client['reviews']
app = Flask(__name__)

@app.route('/api/review', methods=['GET'])
def get_reviews():
    dealership_id = request.args.get('dealerId')
    
    if dealership_id:
        try:
            dealership_id = int(dealership_id)  # Convert dealerId to integer
            selector = {'dealership': dealership_id}
            result = db.get_query_result(selector)
            data_list = [doc for doc in result]
            
            if not data_list:
                return jsonify({"error": "dealerId does not exist"}), 404

        except ValueError:
            return jsonify({"error": "'dealerId' parameter must be an integer"}), 400
    else:
        # Fetch all documents when no dealership_id is provided
        data_list = [doc for doc in db.all_docs(include_docs=True)['rows']]

    return jsonify(data_list)

@app.route('/api/review', methods=['POST'])
def post_review():
    if not request.json:
        abort(400, description='Invalid JSON data')

    review_data = request.json
    required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']

    for field in required_fields:
        if field not in review_data:
            abort(400, description=f'Missing required field: {field}')

    try:
        db.create_document(review_data)
        return jsonify({"message": "Review posted successfully"}), 201
    except Exception as e:
        return jsonify({"error": "Something went wrong on the server", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
