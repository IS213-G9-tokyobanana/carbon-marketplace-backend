from publisher import publishTask
from crontab import CronTab
from datetime import datetime, timedelta

def checkType(msg):
    print(msg)
    if msg['type'] == 'milestone.add':
        # Creation of a new milestone for a specific project
        projId = msg['data']['project_id']
        milestoneId = msg['resource_id']
        milestone = msg['data']['milestones'][0]
        addMilestoneJob(milestoneId, projId, milestone)
    elif msg['type'] == 'project.verify':
        # New project has been created and all milestones need to be added
        projId = msg['resource_id']
        milestone = msg['data']['milestones']
        addProject(projId, milestone)
    elif msg['type'] == 'offsets.reserve':
        # Start tracking the TTL for the offset (1hr)
        payment_id = msg['resource_id']
        projId = msg['data']['project_id']
        milestone_id = msg['data']['milestone_id']
        newOffsetTrack(payment_id, msg['data']['created_at'], projId, milestone_id)
    elif msg['type'] == 'offsets.commit' or msg['type'] == 'payment.failed':
        # Offset has been purchased, stop tracking the TTL OR
        # For when Stripe payment fails, need to remove the offset from cron as it will no longer be needed
        # Check if in Cron to see if need to remove.
        payment_id = msg['resource_id']
        removeOffsetTrack(payment_id)
    elif msg['type'] == 'milestone.reward' or msg['type'] == 'milestone.penalise':
        # Milestone has been rewarded, need to remove from cron
        milestone_id = msg['resource_id']
        projId = msg['data']['project_id']
        milestoneRemove(milestone_id, projId)
    elif msg['type'] == 'task.add':
        # Re-publish the task to the exchange
        publishTask('task.add')
        # print(msg)


# Function that looks for the Offset tracking and removes it from Cron
def removeOffsetTrack(payment_id):
    print('in scheduler removeOffsetTrack')
    cron = CronTab(user=True)
    cron.remove_all(comment=f'offset_{payment_id}')
    cron.write()

# Function that creates a new job to track TTL
def newOffsetTrack(payment_id, created_at, project_id, milestone_id):
    print('in scheduler newOffsetTrack')
    cron = CronTab(user=True)
    job  = cron.new(command=f'/usr/local/bin/python /app/publisher.py --type offset --proj {project_id} --mile {milestone_id}', comment=f'offset_{payment_id}')
    job.setall(datetime.fromisoformat(created_at) + timedelta(hours=1))
    # Can be used for testing, will schedule the job to run in 1 minute
    # job.setall(datetime.fromisoformat(due_date) + timedelta(minutes=1))
    cron.write()

# Function that is called when milestone have been rewarded
def milestoneRemove(milestone_id, project_id):
    # Need to check 2 conditions
    # 1. If upcoming and overdue both still in Cron
    # 2. If only overdue in Cron
    print('in scheduler milestoneRemove')
    cron = CronTab(user=True)
    cron.remove_all(comment=f'upcoming_{project_id}_{milestone_id}')
    cron.write()
    cron.remove_all(comment=f'overdue_{project_id}_{milestone_id}')
    cron.write()

# Function that is called when there is a new project. Will call addMilestoneJob() to add all milestones
def addProject(project_id, milestones):
    print('in scheduler addProject')
    for milestone in milestones:
        milestone_id = milestone['milestone_id']
        addMilestoneJob(milestone_id, project_id, milestone)

# Function that will be called repeatedly to add a new milestone job
# Cron job needs to track Upcoming milestone and Overdue milestone (1day after due)
def addMilestoneJob(milestone_id, project_id, milestone):
    print('in scheduler addMilestoneJob')
    due_date = milestone['due_date']
    cron = CronTab(user=True)
    job  = cron.new(command=f'/usr/local/bin/python /app/publisher.py --type upcoming --proj {project_id} --mile {milestone_id}', comment=f'upcoming_{project_id}_{milestone_id}')
    job.setall(datetime.fromisoformat(due_date) - timedelta(30))
    # Can be used for testing, will schedule the job to run in 1 minute
    # job.setall(datetime.fromisoformat(due_date) + timedelta(minutes=1))
    cron.write()

    job  = cron.new(command=f'/usr/local/bin/python /app/publisher.py --type overdue --proj {project_id} --mile {milestone_id}', comment=f'overdue_{project_id}_{milestone_id}')
    job.setall(datetime.fromisoformat(due_date) + timedelta(1))
    # Can be used for testing, will schedule the job to run in 1 minute
    # job.setall(datetime.fromisoformat(due_date) + timedelta(minutes=1))
    cron.write()