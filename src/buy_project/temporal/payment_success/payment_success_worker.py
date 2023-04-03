from config.config import TEMPORAL_SERVICE_URL

# Import the activity and workflow from our other files
from temporal.activities import (
    add_pending_offset,
    commit_offset,
    get_payment_intent,
    publish_message,
)
from temporal.payment_success.payment_success_workflow import (
    PaymentSuccessTemporalWorkflow,
)
from temporalio.client import Client
from temporalio.worker import Worker


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="payment_success",
        workflows=[PaymentSuccessTemporalWorkflow],
        activities=[
            get_payment_intent,
            commit_offset,
            add_pending_offset,
            publish_message,
        ],
    )
    await worker.run()
