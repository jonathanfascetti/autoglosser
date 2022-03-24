from flask_restful import Api, Resource, reqparse
import subprocess

class HelloApiHandler(Resource):
  # Hello world to show it's working
  def get(self):
    return {
      'resultStatus': 'SUCCESS',
      'message': "Hello Api Handler"
      }

  # Handle request from frontend
  # Accepts 'type' and 'message'
  # Type is update or not
  # Message is the query
  def post(self):
    # Read request
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str)
    parser.add_argument('message', type=str)
    args = parser.parse_args()
    print(args)
    request_type = args['type']
    request_json = args['message']

    # Process return 
    ret_status = request_type
    ret_msg = request_json

    if ret_msg:
      bytes = subprocess.Popen(['python3', '../autogloss.py', '"' + request_json + '"', request_type], stdout=subprocess.PIPE)
      out, err = bytes.communicate()
      message = out.decode("utf-8")
    else:
      message = "No Msg"
    
    final_ret = {"status": "Success", "message": message}

    return final_ret