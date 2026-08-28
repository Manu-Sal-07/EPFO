import asyncio
from pfcompass.seed_demo_data import seed_demo_citizens

if __name__ == "__main__":
    asyncio.run(seed_demo_citizens())
