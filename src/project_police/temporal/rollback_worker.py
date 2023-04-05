from config.config import TEMPORAL_SERVICE_URL

# Import the activity and workflow from our other files
from temporal.activities import (
    get_payment_object_by_milestone_id,
    notify_buyer_payment_failed,
    remove_reserved_offset_by_payment_id,
)
from temporal.rollback_workflow import RollbackTemporalWorkflow
from temporalio.client import Client
from temporalio.worker import Worker


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Create a worker that will poll the given task queue
    worker = Worker(
        client,
        task_queue="rollback-task-queue",
        workflows=[RollbackTemporalWorkflow],
        activities=[
            get_payment_object_by_milestone_id,
            notify_buyer_payment_failed,
            remove_reserved_offset_by_payment_id,
        ],
    )

    # Start polling for tasks
    await worker.run()
