from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        create_payment_intent,
        reserve_offset,
    )


@workflow.defn
class StartPaymentTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        status_arr = []

        # Create payment intent
        payment_intent_result = await workflow.execute_activity(
            create_payment_intent, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(payment_intent_result["success"])

        data["payment_id"] = payment_intent_result["data"]

        # Reserve offset
        reserve_offset_result = await workflow.execute_activity(
            reserve_offset, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(reserve_offset_result["success"])

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
