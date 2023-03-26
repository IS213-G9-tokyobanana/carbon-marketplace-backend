import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from activities import remove_reserved_offset, get_payment_intent, send_to_notifier
from workflow import ProjectPoliceTemporalWorkflow


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
