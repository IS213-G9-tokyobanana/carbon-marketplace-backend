from config.config import TEMPORAL_SERVICE_URL

# Import the activity and workflow from our other files
from temporal.activities import get_payment_object, publish_message, remove_offset
from temporal.payment_failed.payment_failed_workflow import (
    PaymentFailedTemporalWorkflow,
)
from temporalio.client import Client
from temporalio.worker import Worker


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="payment_failed",
        workflows=[PaymentFailedTemporalWorkflow],
        activities=[get_payment_object, remove_offset, publish_message],
    )
    await worker.run()
