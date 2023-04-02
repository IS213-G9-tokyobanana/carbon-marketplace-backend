from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from temporal.activities import (
    get_payment_id,
    get_buyer_id,
    patch_milestone,
    send_to_user,
)
from temporal.penalise_reward_workflow import PenaliseRewardTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL, namespace="default")

    # Create a worker that will poll the given task queue
    worker = Worker(
        client,
        task_queue="penalise-reward-task-queue",
        workflows=[PenaliseRewardTemporalWorkflow],
        activities=[
            get_payment_id,
            get_buyer_id,
            patch_milestone,
            send_to_user,
        ],
    )

    # Start polling for tasks
    await worker.run()
