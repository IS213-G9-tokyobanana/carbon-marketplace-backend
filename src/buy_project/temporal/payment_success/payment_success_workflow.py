from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        add_pending_offset,
        commit_offset,
        get_payment_object,
        publish_message,
    )


@workflow.defn
class PaymentSuccessTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> dict:
        """
        Expected data:
        data: {
            payment_id: string; // stripe checkout session id
            status: "open" | "complete" | "expired"; // stripe checkout session status
        }
        """
        results = []
        # Get payment intent
        payment_object_response = await workflow.execute_activity(
            get_payment_object,
            data["payment_id"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(payment_object_response)

        # Commit offset
        commit_offset_result = await workflow.execute_activity(
            commit_offset,
            payment_object_response["data"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(commit_offset_result)

        # Add pending offset
        add_pending_offset_result = await workflow.execute_activity(
            add_pending_offset,
            payment_object_response["data"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(add_pending_offset_result)

        # Publish message
        publish_message_result = await workflow.execute_activity(
            publish_message,
            dict(
                data={**data, **payment_object_response["data"]},
                resource_id=data["payment_id"],
                success=all([r.get("success", False) for r in results]),
                payment_succeeded=True,
            ),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(publish_message_result)

        return dict(
            success=all([r.get("success", False) for r in results]),
            data=results,
        )
