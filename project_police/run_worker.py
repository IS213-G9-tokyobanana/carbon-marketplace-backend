import asyncio
from temporal.worker import main

if __name__ == "__main__":
    print("Starting worker")
    asyncio.run(main())