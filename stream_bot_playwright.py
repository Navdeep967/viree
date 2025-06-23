import asyncio
from playwright.async_api import async_playwright
import random
import time
import os

YOUTUBE_URL = "https://www.youtube.com/watch?v=gnKy3HDeTds"
MAX_VIEWERS = 5
WATCH_MIN_SECONDS = 60
WATCH_MAX_SECONDS = 180

# Load proxies
def load_proxies(file_path="proxies.txt"):
    proxies = []
    if not os.path.exists(file_path):
        print("❌ proxies.txt not found.")
        return proxies

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) == 4:
                ip, port, user, pwd = parts
                proxies.append(f"http://{user}:{pwd}@{ip}:{port}")
    return proxies

# Simulate viewer
async def launch_viewer(proxy_url, viewer_id):
    try:
        print(f"🟡 Viewer {viewer_id} starting with {proxy_url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": proxy_url}
            )
            context = await browser.new_context(
                user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) ViewerBot/{random.randint(1000,9999)}"
            )
            page = await context.new_page()
            await page.goto(YOUTUBE_URL, timeout=60000)

            print(f"✅ Viewer {viewer_id} watching live stream...")

            # Simulate human activity
            await page.mouse.move(random.randint(0, 500), random.randint(0, 300))
            watch_time = random.randint(WATCH_MIN_SECONDS, WATCH_MAX_SECONDS)
            print(f"⏳ Viewer {viewer_id} will stay for {watch_time} seconds")
            await asyncio.sleep(watch_time)

            print(f"🔁 Viewer {viewer_id} finished, restarting...")
            await browser.close()
            await launch_viewer(proxy_url, viewer_id)  # Restart loop

    except Exception as e:
        print(f"❌ Viewer {viewer_id} error: {e}")
        print(f"🔁 Retrying viewer {viewer_id} in 30s...")
        await asyncio.sleep(30)
        await launch_viewer(proxy_url, viewer_id)

# Main runner
async def main():
    proxies = load_proxies()
    if not proxies:
        print("❌ No proxies loaded.")
        return

    tasks = []
    for i in range(min(MAX_VIEWERS, len(proxies))):
        tasks.append(launch_viewer(proxies[i], i + 1))
        await asyncio.sleep(2)  # Stagger start

    await asyncio.gather(*tasks)

# Run it
if __name__ == "__main__":
    asyncio.run(main())
