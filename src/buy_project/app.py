import asyncio
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from temporal.payment_failed.payment_failed_workflow import (
    PaymentFailedTemporalWorkflow,
)
from temporal.payment_success.payment_success_workflow import (
    PaymentSuccessTemporalWorkflow,
)
from temporal.run_workflow import main
from temporal.start_payment.start_payment_workflow import StartPaymentTemporalWorkflow

app = Flask(__name__)
CORS(app)


@app.route("/checkout", methods=["POST"])
def checkout():
    """For backend to reserve offset and create payment object

    Expected data:
    data: {
        payment_id: string; // stripe checkout session id
        quantity_tco2e: number;
        project_id: string;
        milestone_id: string;
        owner_id: string;
        buyer_id: string;
    }
    """

    data = request.get_json()
    try:
        result = asyncio.run(
            main(StartPaymentTemporalWorkflow, data, "start_payment_test")
        )
    except Exception as e:
        logging.error(e)
        return jsonify(success=False, data=dict(message=str(e), resources=data))
    return result


@app.route("/webhook", methods=["POST"])
def handle_payment_status():
    """
    Expected data:
    data: {
        payment_id: string; // stripe checkout session id
        status: "open" | "complete" | "expired"; // stripe checkout session status
    }
    """
    data = request.get_json()
    if not (data.get("status") and data.get("payment_id")):
        return jsonify(
            success=False,
            data=dict(message="Missing parameters in data, needs (payment_id, status)"),
        )
    if data["status"] not in ["open", "complete", "expired"]:
        return jsonify(
            success=False,
            data=dict(
                message="Invalid status in data, needs one of (open, complete, expired)"
            ),
        )

    if data["status"] == "complete":
        workflow = PaymentSuccessTemporalWorkflow
        task_queue = f"payment_success"
    else:
        workflow = PaymentFailedTemporalWorkflow
        task_queue = f"payment_failed"

    try:
        result = asyncio.run(main(workflow, data, task_queue))
    except Exception as e:
        logging.error(e)
        return jsonify(success=False, data=dict(message=str(e), resources=data))
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
