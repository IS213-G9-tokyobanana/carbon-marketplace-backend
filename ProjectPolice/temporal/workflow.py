from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from ProjectPolice.temporal.activities import remove_reserved_offset, get_payment_intent, send_to_notifier

@workflow.defn
class ProjectPoliceTemporalWorkflow:
    @workflow.run
    async def run(self, data: dict) -> list:
        # Execute activity to remove reserved offset
        result1 = await workflow.execute_activity(
            remove_reserved_offset, data, start_to_close_timeout=timedelta(seconds=5)
        )
        # Execute activity to retrieve payment intent
        result2 = await workflow.execute_activity(
            get_payment_intent, start_to_close_timeout=timedelta(seconds=5)
        )
        # Execute activity to send message to Notifier
        result3 = await workflow.execute_activity(
            send_to_notifier, data, start_to_close_timeout=timedelta(seconds=5)
        )
        return [result1, result2, result3]