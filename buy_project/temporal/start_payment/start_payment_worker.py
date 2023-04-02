from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from temporal.activities import (
    create_payment_intent,
    reserve_offset,
)
from temporal.start_payment.start_payment_workflow import StartPaymentTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="start-payment-queue",
        workflows=[StartPaymentTemporalWorkflow],
        activities=[create_payment_intent, reserve_offset],
    )
    await worker.run()
