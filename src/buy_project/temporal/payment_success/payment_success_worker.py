from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from temporal.activities import (
    get_payment_intent,
    commit_offset,
    add_pending_offset,
    publish_message,
)
from temporal.payment_success.payment_success_workflow import PaymentSuccessTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="payment-success-queue",
        workflows=[PaymentSuccessTemporalWorkflow],
        activities=[get_payment_intent, commit_offset, add_pending_offset, publish_message],
    )
    await worker.run()
