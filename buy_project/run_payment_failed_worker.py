import asyncio
from temporal.payment_failed.payment_failed_worker import main

if __name__ == "__main__":
    print("Starting payment failed worker")
    asyncio.run(main())