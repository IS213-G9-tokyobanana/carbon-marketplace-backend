import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal.activities import (
        get_payment_object_by_milestone_id,
        update_project_milestone_status,
        update_user_offset,
    )


@workflow.defn
class PenaliseRewardTemporalWorkflow:
    def __repr__(self) -> str:
        return "PenaliseRewardTemporalWorkflow"

    @workflow.run
    async def refund(self, data: dict) -> dict:
        """
        Expected data:
        data: {
            project_id: string;
            milestone_id: string;
            payment_id: string;
            status: string
        }
        """
        results = []
        # returns a list of payment objects that paid for the milestone
        payment_object_response = await workflow.execute_activity(
            get_payment_object_by_milestone_id,
            data["milestone_id"],
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(payment_object_response)

        update_user_offset_response = await workflow.execute_activity(
            update_user_offset,
            data,
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(update_user_offset_response)

        update_project_milestone_status_response = await workflow.execute_activity(
            update_project_milestone_status,
            data,
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(seconds=5),
        )
        results.append(update_project_milestone_status_response)

        if all([r.get("success", False) for r in results]):
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
