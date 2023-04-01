from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        remove_reserved_offset,
        get_buyer_id,
        send_to_notifier,
    )


@workflow.defn
class ProjectPoliceTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        status_arr = []
        # Execute activity to retrieve payment intent
        result1 = await workflow.execute_activity(
            get_buyer_id, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(result1["success"])
        # buyer_id = result1["data"]["buyer_id"]
        # Execute activity to remove reserved offset
        result2 = await workflow.execute_activity(
            remove_reserved_offset,
            data,
            start_to_close_timeout=timedelta(seconds=5),
        )
        status_arr.append(result2["success"])
        # Execute activity to send message to Notifier
        result3 = await workflow.execute_activity(
            send_to_notifier, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(result3["success"])

        if all(status_arr):
            return {
                "success": True,
                "data": {
                    "message": "Workflow executed successfully",
                    "resources": data,
                },
            }
        else:
            return {
                "success": False,
                "data": {"message": "Workflow execution failed", "resources": data},
            }
