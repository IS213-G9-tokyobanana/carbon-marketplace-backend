import time
from datetime import timedelta

from config.config import TEMPORAL_SERVICE_URL
from temporalio.client import Client


async def main(workflow, data, queue):
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL)

    # Execute a workflow
    return await client.execute_workflow(
        workflow,
        data,
        id=f"{queue}-{int(time.time())}",
        task_queue=queue,
        execution_timeout=timedelta(seconds=100),
    )
