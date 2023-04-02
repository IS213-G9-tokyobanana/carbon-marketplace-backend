from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ

import stripe

app = Flask(__name__)
CORS(app)


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.get_data()  # retrieves raw body data
    signature = request.headers["stripe-signature"]

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, environ.get('STRIPE_ENDPOINT_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle events
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(payment_intent)
    elif event['type'] == 'payment_intent.failed':
        payment_intent = event['data']['object']
        print(payment_intent)
    else:
        print(event)

    return jsonify(
        success=True
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
