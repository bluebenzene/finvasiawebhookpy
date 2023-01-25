from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os

load_dotenv()

user = os.environ['userid']
password = os.environ['password']
twoFA = os.environ['twoFA']
vendor_code = os.environ['vendor_code']
imei = os.environ['imei']

app = Flask(__name__)


@app.route(f'/webhook/fin/{user}', methods=['POST'])
def handle_post_request():
    data = request.get_json()
    print("Tradingview log")
    print(data[0])
    print(data[0].get('simple'))


    return '200'


if __name__ == '__main__':
    print("hello")
    app.run(host='0.0.0.0', port=80)