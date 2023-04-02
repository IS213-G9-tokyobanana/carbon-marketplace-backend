import asyncio
from temporal.start_payment.start_payment_worker import main

if __name__ == "__main__":
    print("Starting start payment worker")
    asyncio.run(main())