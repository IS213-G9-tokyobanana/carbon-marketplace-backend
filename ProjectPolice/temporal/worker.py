from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from temporal.activities import (
    remove_reserved_offset,
    get_buyer_id,
    send_to_notifier,
)
from temporal.workflow import ProjectPoliceTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[ProjectPoliceTemporalWorkflow],
        activities=[remove_reserved_offset, get_buyer_id, send_to_notifier],
    )
    await worker.run()