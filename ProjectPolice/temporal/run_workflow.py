import asyncio
from temporalio.client import Client

# Import the workflow
from ProjectPolice.temporal.workflow import ProjectPoliceTemporalWorkflow


async def main(data):
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    result = await client.execute_workflow(
        ProjectPoliceTemporalWorkflow.run,
        data,
        id="project-workflow8",
        task_queue="my-task-queue",
    )

    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())
