from temporalio.client import Client

# Import the workflow
from temporal.workflow import ProjectPoliceTemporalWorkflow
from config.config import TEMPORAL_SERVICE_URL


async def main(data):
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_SERVICE_URL)

    # Execute a workflow
    workflow_result = await client.execute_workflow(
        ProjectPoliceTemporalWorkflow.run,
        data,
        id="project-workflow-test",
        task_queue="my-task-queue",
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
