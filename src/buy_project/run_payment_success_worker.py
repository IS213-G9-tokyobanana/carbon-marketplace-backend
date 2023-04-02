import asyncio
from temporal.payment_success.payment_success_worker import main

if __name__ == "__main__":
    print("Starting payment success worker")
    asyncio.run(main())