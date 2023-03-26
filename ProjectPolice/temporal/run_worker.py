import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

import sys
import os

# add the path to the main directory of your project to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import the activity and workflow from our other files
from ProjectPolice.temporal.activities import remove_reserved_offset, get_payment_intent, send_to_notifier
from ProjectPolice.temporal.workflow import ProjectPoliceTemporalWorkflow


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233", namespace="default")

    # Run the worker
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[ProjectPoliceTemporalWorkflow],
        activities=[remove_reserved_offset, get_payment_intent, send_to_notifier],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
