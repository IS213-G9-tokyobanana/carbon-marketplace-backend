import time

# Import the workflow
from config.config import TEMPORAL_SERVICE_URL
from temporalio.client import Client


async def main(workflow, data, queue):
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL)

    # Execute a workflow
    workflow_result = await client.execute_workflow(
        workflow,
        data,
        id=f"{workflow}-workflow-{time.time()}",
        task_queue=queue,
    )

    if workflow_result["success"] == True:
        result = {
            "success": True,
            "data": {
                "message": "Workflow executed successfully",
                "resources": data,
            },
        }
    else:
        result = {
            "success": False,
            "data": {
                "message": "Workflow execution failed",
                "resources": data,
            },
        }
    print("Workflow result:", workflow_result)
    return result
