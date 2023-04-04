from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        get_payment_id,
        get_buyer_id,
        send_to_user,
        patch_milestone,
    )


@workflow.defn
class PenaliseRewardTemporalWorkflow:
    @workflow.run
    async def refund(self, data: dict) -> dict:
        status_arr = []
        result1 = await workflow.execute_activity(
            get_payment_id, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(result1["success"])
        data["data"]["payment_id"] = result1["data"]["payment_data"]["payment_id"]

        # Execute activity to retrieve buyer id
        result2 = await workflow.execute_activity(
            get_buyer_id, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(result2["success"])
        data["data"]["buyer_id"] = result2["data"]["payment_data"]["buyer_id"]

        # Execute activity to remove reserved offset
        result3 = await workflow.execute_activity(
            patch_milestone,
            data,
            start_to_close_timeout=timedelta(seconds=5),
        )
        status_arr.append(result3["success"])

        # Execute activity to send message to Notifier
        result4 = await workflow.execute_activity(
            send_to_user, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(result4["success"])

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
