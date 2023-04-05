from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import create_payment, reserve_offset


@workflow.defn
class StartPaymentTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        results = []

        # Reserve offset
        reserve_offset_response = await workflow.execute_activity(
            reserve_offset,
            data,
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(reserve_offset_response)

        # Save payment object
        payment_object_response = await workflow.execute_activity(
            create_payment,
            data,
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(payment_object_response)

        if all([resp.get("success", False) for resp in results]):
            return {
                "success": True,
                "data": {
                    "message": "Workflow executed successfully",
                    "resources": results,
                },
            }
        else:
            return {
                "success": False,
                "data": {"message": "Workflow execution failed", "resources": results},
            }
