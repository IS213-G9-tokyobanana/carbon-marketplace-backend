import asyncio
from temporal.penalise_reward_worker import main

if __name__ == "__main__":
    print("Starting worker")
    asyncio.run(main())