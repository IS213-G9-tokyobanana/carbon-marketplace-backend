from crontab import CronTab
from datetime import datetime, timedelta
from classes.enums import MessageType, TaskType
from publisher import republish_task


time_format = "%Y-%m-%dT%H:%M:%SZ"
PYTHON_EXE = '/usr/local/bin/python'
PUBLISHER_SCRIPT = '/app/publisher.py'

def schedule_jobs(message: dict):
    # print(f'message received: {message}')
    type = message['type']
    data = message['data']
    if type == MessageType.MILESTONE_ADD.value:
        # Creation of a new milestone for a specific project
        milestone = data['project']['milestones'][0]
        handle_milestone_add(milestone)

    elif type == MessageType.PROJECT_VERIFY.value:
        # New project has been created and all milestones need to be added
        milestones = data['project']['milestones']
        for milestone in milestones:
            handle_milestone_add(milestone)

    elif type == MessageType.OFFSETS_RESERVE.value:
        # Start tracking the TTL for the offset (1hr)
        payment_id = message['resource_id']
        project_id = data['project']['id']
        milestone_id = data['reserved_offset']['milestone_id']
        created_at = data['reserved_offset']['created_at']
        create_track_payment_job(payment_id, created_at, project_id, milestone_id)

    elif type == MessageType.OFFSETS_COMMIT.value or type == MessageType.PAYMENT_FAILED.value:
        # Offset has been purchased, stop tracking the TTL OR
        # For when Stripe payment fails, need to remove the offset from cron as it will no longer be needed
        # Check if in Cron to see if need to remove.
        payment_id = message['resource_id']
        comment = f'{TaskType.PAYMENT_OVERDUE.value}_{payment_id}'
        remove_job(comment=comment)
        
    elif type == MessageType.MILESTONE_REWARD.value or type == MessageType.MILESTONE_PENALISE.value:
        # Milestone has been rewarded, need to remove current upcoming and overdue cron jobs
        milestone_id = message['resource_id']
        project_id = data['project']['id']
        comment = f'{TaskType.MILESTONE_UPCOMING.value}_{milestone_id}'
        remove_job(comment=comment)
        comment = f'{TaskType.MILESTONE_OVERDUE.value}_{milestone_id}'
        remove_job(comment=comment)
        
    elif type in TaskType.values(): # elif the type is one of the published task type that supervisor publishes back
        # Re-publish the task to the exchange
        republish_task(message=message)        


# Function that looks for the Offset tracking and removes it from Cron
def remove_job(comment):
    print('in scheduler remove_job')
    cron = CronTab(user=True)
    cron.remove_all(comment=comment)
    cron.write()


# Function that creates a new job to track TTL
def create_track_payment_job(payment_id, created_at, project_id, milestone_id):
    cron = CronTab(user=True)
    type = TaskType.PAYMENT_OVERDUE.value
    job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --project {project_id} --milestone {milestone_id} --payment {payment_id}', comment=f'{type}_{payment_id}')
    time_to_run = datetime.strptime(created_at, time_format) + timedelta(hours=1)
    job.setall(time_to_run)
    cron.write()
    print(f'Created {type} job to run at {time_to_run} (UTC)')
    
    # Uncomment below to test
    # job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --project {project_id} --milestone {milestone_id} --payment {payment_id}', comment=f'{type}_{payment_id}')
    # test_time = datetime.utcnow() + timedelta(minutes=1)
    # job.setall(test_time)
    # cron.write()
    # print(f'Created {type} job to run at {str(test_time)} (UTC)')


def handle_milestone_add(milestone: dict):
    # Function that will be called repeatedly to add a new milestone job
    # Cron job needs to track Upcoming milestone and Overdue milestone (1day after due)
    create_milestone_job(milestone=milestone, job_type=TaskType.MILESTONE_UPCOMING)
    create_milestone_job(milestone=milestone, job_type=TaskType.MILESTONE_OVERDUE)
    

def create_milestone_job(milestone: dict, job_type: TaskType):
    if job_type == TaskType.MILESTONE_UPCOMING.value:
        due_date = milestone['due_date']
        due_date = datetime.strptime(due_date, time_format)
        milestone_id = milestone['id']
        project_id = milestone['project_id']
        type = TaskType.MILESTONE_UPCOMING.value

        cron = CronTab(user=True)
        job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --milestone {milestone_id} --project {project_id}', comment=f'{type}_{milestone_id}')
        time_to_run = due_date - timedelta(30)
        job.setall(time_to_run)
        cron.write()
        print(f'Created {type} job to run at {str(time_to_run)} (UTC)')
        
        # Uncomment below for testing
        # test_time = datetime.utcnow() + timedelta(minutes=1) # Can be used for testing, will schedule the job to run in 1 minute
        # job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --milestone {milestone_id} --project {project_id}', comment=f'{type}_{milestone_id}')
        # job.setall(test_time)
        # cron.write()
        # print(f'Created {type} job to run at {str(test_time)} (UTC)')
    
    elif job_type == TaskType.MILESTONE_OVERDUE.value:
        due_date = milestone['due_date']
        due_date = datetime.strptime(due_date, time_format)
        milestone_id = milestone['id']
        project_id = milestone['project_id']
        type = TaskType.MILESTONE_OVERDUE.value

        cron = CronTab(user=True)
        job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --milestone {milestone_id} --project {project_id}', comment=f'{type}_{milestone_id}')
        time_to_run = due_date + timedelta(1)
        job.setall(time_to_run)
        cron.write()
        print(f'Created {type} job to run at {str(time_to_run)} (UTC)')
        
        # Uncomment below for testing
        # test_time = datetime.utcnow() + timedelta(minutes=1)
        # job  = cron.new(command=f'{PYTHON_EXE} {PUBLISHER_SCRIPT} --type {type} --milestone {milestone_id} --project {project_id}', comment=f'{type}_{milestone_id}')
        # job.setall(test_time)
        # cron.write()
        # print(f'Created {type} job to run at {str(test_time)} (UTC)')
