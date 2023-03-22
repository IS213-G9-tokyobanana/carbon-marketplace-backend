from publisher import publishTask
from crontab import CronTab

# TODO:
# [x] 1. CheckType of each message and call the appropriate function
# [] 2. Upcoming Milestone Funct
#   [] 2.1. addMilestoneJob()
#   [] 2.2. addProject()
#   [] 2.3. milestoneRewarded()
# [] 3. Overdue Milestone Funct
#   [] 3.1. addMilestoneJob()
#   [] 3.2. addProject()
#   [] 3.3. milestoneRewarded()
# [] 4. Reserve Offset Funct
#   [] 4.1. newOffsetTrack()
#   [] 4.2. removeOffsetTrack()
# [] 5. Re-Publish scheduler task Funct
#   [] 5.1. publishTask()


def checkType(msg):
    if msg['type'] == 'milestone.add':
        # Creation of a new milestone for a specific project
        addMilestoneJob()
    elif msg['type'] == 'project.verify':
        # New project has been created and all milestones need to be added
        addProject()
    elif msg['type'] == 'offsets.reserve':
        # Start tracking the TTL for the offset (1hr)
        newOffsetTrack()
    elif msg['type'] == 'offsets.commit' or msg['type'] == 'payment.failed':
        # Offset has been purchased, stop tracking the TTL OR
        # For when Stripe payment fails, need to remove the offset from cron as it will no longer be needed
        # Check if in Cron to see if need to remove.
        removeOffsetTrack()
    elif msg['type'] == 'milestone.rewarded':
        # Milestone has been rewarded, need to remove from cron
        milestoneRewarded()
    elif msg['type'] == 'task.add':
        # Re-publish the task to the exchange
        publishTask()


# Function that looks for the Offset tracking and removes it from Cron
def removeOffsetTrack():
    pass

# Function that creates a new job to track TTL
def newOffsetTrack():
    pass

# Function that is called when milestone have been rewarded
def milestoneRewarded():
    # Need to check 2 conditions
    # 1. If upcoming and overdue both still in Cron
    # 2. If only overdue in Cron
    pass

# Function that is called when there is a new project. Will call addMilestoneJob() to add all milestones
def addProject():
    # for milestone in milestones:
    #     addMilestoneJob()
    pass

# Function that will be called repeatedly to add a new milestone job
# Cron job needs to track Upcoming milestone and Overdue milestone (1day after due)
def addMilestoneJob(milestone, project_id):
    due_date = milestone['due_date']
    pass

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