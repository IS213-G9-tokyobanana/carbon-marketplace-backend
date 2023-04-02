from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import get_payment_intent, remove_offset, publish_message


@workflow.defn
class PaymentFailedTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        status_arr = []

        data["payment_status"] = "success"

        # Get payment intent
        payment_intent_result = await workflow.execute_activity(
            get_payment_intent, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(payment_intent_result["success"])

        data = payment_intent_result

        # Remove offset
        remove_offset_result = await workflow.execute_activity(
            remove_offset, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(remove_offset_result["success"])

        # Publish message
        publish_message_result = await workflow.execute_activity(
            publish_message, data, start_to_close_timeout=timedelta(seconds=5)
        )
        status_arr.append(publish_message_result["success"])

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
