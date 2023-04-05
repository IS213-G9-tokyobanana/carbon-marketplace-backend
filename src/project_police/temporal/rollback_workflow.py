from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        get_payment_object_by_milestone_id,
        notify_buyer_payment_failed,
        remove_reserved_offset_by_payment_id,
    )


@workflow.defn
class RollbackTemporalWorkflow:
    def __repr__(self) -> str:
        return "PenaliseRewardTemporalWorkflow"

    @workflow.run
    async def rollback(self, data: dict) -> dict:
        """
        Expected data:
        data: {
            project_id: string;
            milestone_id: string;
            payment_id: string;
        }
        """
        results = []
        # Execute activity to retrieve buyer id from a particular payment intent
        payment_object_response = await workflow.execute_activity(
            get_payment_object_by_milestone_id,
            data["milestone_id"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(payment_object_response)

        # Execute activity to remove reserved offset
        remove_reserved_offset_response = await workflow.execute_activity(
            remove_reserved_offset_by_payment_id,
            data["payment_id"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(remove_reserved_offset_response)

        # Execute activity to send message to Notifier
        publish_to_notifier_response = await workflow.execute_activity(
            notify_buyer_payment_failed,
            {**payment_object_response["data"], **data},
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(publish_to_notifier_response)

        if all(results):
            return {
                "success": True,
                "data": {
                    "message": "Workflow executed successfully",
                    "results": results,
                },
            }
        else:
            return {
                "success": False,
                "data": {"message": "Workflow execution failed", "results": results},
            }
