# from flask import Flask, render_template, jsonify, request

# print(dir(Flask))

from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

with app.test_request_context('/?name=John'):
    print(request.args.get('name'))  # Outputs: John
