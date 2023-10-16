import asyncio

import aiohttp
import services, settings


async def main():
    url_queue = asyncio.Queue()
    image_queue = asyncio.Queue()
    session_timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT_SESSION)
    session = aiohttp.ClientSession(timeout=session_timeout)

    parse_url_tasks = services.create_tasks(
        services.put_page_url,
        url_queue,
        session,
    )
    parse_img_tasks = services.create_tasks(
        services.get_img_from_page,
        url_queue,
        image_queue,
        session,
    )
    save_file_task = services.create_tasks(
        services.create_file_by_img,
        image_queue,
        session,
    )

    await asyncio.gather(
        *parse_url_tasks,
    )
    await url_queue.join()
    await image_queue.join()

    services.cancel_task(parse_url_tasks)
    services.cancel_task(parse_img_tasks)
    services.cancel_task(save_file_task)
    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
