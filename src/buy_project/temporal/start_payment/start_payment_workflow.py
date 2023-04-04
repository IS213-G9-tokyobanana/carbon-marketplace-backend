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

        client_secret = payment_intent_result.get("data")
        if not client_secret:
            return {
                "success": False,
                "data": {
                    "message": "Failed to retrieve client secret",
                    "resources": payment_intent_result,
                },
            }

        data["client_secret"] = client_secret
        data["payment_id"] = data["client_secret"].split("_secret_")[0]

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
