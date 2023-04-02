from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from temporal.activities import (
    remove_reserved_offset,
    get_buyer_id,
    send_to_notifier,
)
from temporal.rollback_workflow import RollbackTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Create a worker that will poll the given task queue
    worker = Worker(
        client,
        task_queue="rollback-task-queue",
        workflows=[RollbackTemporalWorkflow],
        activities=[
            remove_reserved_offset,
            get_buyer_id,
            send_to_notifier,
        ],
    )

    # Start polling for tasks
    await worker.run()
