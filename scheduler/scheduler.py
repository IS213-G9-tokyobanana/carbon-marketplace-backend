from publisher import publishTask
from crontab import CronTab
from datetime import datetime, timedelta

# TODO:
# [x] 1. CheckType of each message and call the appropriate function
# [] 2. Upcoming Milestone Funct
#   [x] 2.1. addMilestoneJob()
#   [x] 2.2. addProject()
#   [] 2.3. milestoneRewarded()
# [] 3. Overdue Milestone Funct
#   [x] 3.1. addMilestoneJob()
#   [x] 3.2. addProject()
#   [] 3.3. milestoneRewarded()
# [] 4. Reserve Offset Funct
#   [] 4.1. newOffsetTrack()
#   [] 4.2. removeOffsetTrack()
# [] 5. Re-Publish scheduler task Funct
#   [] 5.1. publishTask()


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
        projId = msg['data']['project_id']
        milestoneId = msg['resource_id']
        milestone = msg['data']['milestones']
        addProject(milestoneId, projId, milestone)
    elif msg['type'] == 'offsets.reserve':
        # Start tracking the TTL for the offset (1hr)
        payment_id = msg['resource_id']
        newOffsetTrack(payment_id, msg['data']['created_at'])
    elif msg['type'] == 'offsets.commit' or msg['type'] == 'payment.failed':
        # Offset has been purchased, stop tracking the TTL OR
        # For when Stripe payment fails, need to remove the offset from cron as it will no longer be needed
        # Check if in Cron to see if need to remove.
        payment_id = msg['resource_id']
        removeOffsetTrack(payment_id)
    elif msg['type'] == 'milestone.rewarded':
        # Milestone has been rewarded, need to remove from cron
        milestone_id = msg['resource_id']
        milestoneRewarded(milestone_id)
    elif msg['type'] == 'task.add':
        # Re-publish the task to the exchange
        publishTask()


# Function that looks for the Offset tracking and removes it from Cron
def removeOffsetTrack(payment_id):
    pass

# Function that creates a new job to track TTL
def newOffsetTrack(payment_id, created_at):
    pass

# Function that is called when milestone have been rewarded
def milestoneRewarded(milestone_id):
    # Need to check 2 conditions
    # 1. If upcoming and overdue both still in Cron
    # 2. If only overdue in Cron
    pass

# Function that is called when there is a new project. Will call addMilestoneJob() to add all milestones
def addProject(milestone_id, project_id, milestones):
    print('in scheduler addProject')
    for milestone in milestones:
        milestone_id = milestone['milestone_id']
        addMilestoneJob(milestone_id, project_id, milestone)

# Function that will be called repeatedly to add a new milestone job
# Cron job needs to track Upcoming milestone and Overdue milestone (1day after due)
def addMilestoneJob(milestone_id, project_id, milestone):
    print('in scheduler addMilestoneJob')
    due_date = milestone['due_date']
    date, time = due_date.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    cron = CronTab(user=True)
    job  = cron.new(command='python publisher', comment=f'upcoming_{project_id}_{milestone_id}')
    job.setall(datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)) - timedelta(30))
    cron.write()

    job  = cron.new(command='python publisher', comment=f'overdue_{project_id}_{milestone_id}')
    job.setall(datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)) + timedelta(1))
    cron.write()    

def test_cron():
    print('in scheduler test cron')
    cron = CronTab(user=True)
    job  = cron.new(command='echo hello_world', comment='test1')
    job.minute.every(3)
    cron.write()
    job  = cron.new(command='echo hello_world2', comment='test2')
    job.minute.every(5)
    cron.write()
    cron.remove_all(comment='test1')
    cron.write()
    print('in scheduler after cron')

if __name__ == "__main__":
    pass