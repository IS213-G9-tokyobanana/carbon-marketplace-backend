from datetime import timedelta

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import create_payment, reserve_offset


@workflow.defn
class StartPaymentTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        results = []

        # Create payment object
        payment_object_response = await workflow.execute_activity(
            create_payment,
            data["payment_id"],
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(payment_object_response)

        # Reserve offset
        reserve_offset_response = await workflow.execute_activity(
            reserve_offset,
            payment_object_response["data"],
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(reserve_offset_response)

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
