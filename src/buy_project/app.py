from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from temporal.run_workflow import main
from temporal.start_payment.start_payment_workflow import StartPaymentTemporalWorkflow
from temporal.payment_failed.payment_failed_workflow import (
    PaymentFailedTemporalWorkflow,
)
from temporal.payment_success.payment_success_workflow import (
    PaymentSuccessTemporalWorkflow,
)
import asyncio
import stripe
import logging

app = Flask(__name__)
CORS(app)


@app.route("/webhook", methods=["POST"])
def webhook():
    event = None
    payload = request.get_data()  # retrieves raw body data
    signature = request.headers["stripe-signature"]

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, environ.get("STRIPE_ENDPOINT_SECRET")
        )
    except ValueError as err:
        # Invalid payload
        raise err
    except stripe.error.SignatureVerificationError as err:
        # Invalid signature
        raise err

    # Handle events
    if event["type"] == "payment_intent.succeeded":
        payment_details = event["data"]["object"]
        result = asyncio.run(
            main(payment_details, PaymentSuccessTemporalWorkflow, "payment_success")
        )
    elif event["type"] == "payment_intent.failed":
        payment_details = event["data"]["object"]
        result = asyncio.run(
            main(payment_details, PaymentFailedTemporalWorkflow, "payment_failed")
        )
    else:
        print(f"Unhandled event type {event}")

    return result


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    try:
        result = asyncio.run(main(data, StartPaymentTemporalWorkflow, "start_payment"))
    except Exception as e:
        logging.error(e)
        return jsonify(success=False)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
