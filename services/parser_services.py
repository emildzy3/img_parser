import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Callable

import aiofiles
import aiohttp
import settings
from bs4 import BeautifulSoup


def cancel_task(tasks: asyncio.Task) -> None:
    [task.cancel() for task in tasks]


def create_tasks(function: Callable, *args) -> asyncio.Task:
    return [asyncio.create_task(function(*args)) for _ in range(settings.COUNT_WORKER)]


async def put_page_url(
    url_queue: asyncio.Queue,
    session: aiohttp.ClientSession,
) -> None:
    response = await _make_request(
        url=settings.URL_TO_GET_RANDOM_HTML_WITH_IMG,
        session=session,
    )
    if response:
        await url_queue.put(response.url)
    return None


async def get_img_from_page(
    url_queue: asyncio.Queue,
    image_queue: asyncio.Queue,
    session: aiohttp.ClientSession,
):
    while True:
        page_url = await url_queue.get()
        response = await _make_request(
            url=page_url,
            session=session,
        )
        if not response:
            print('NOT RESPONSE')
            continue
        html = await response.text()

        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            img_url = await loop.run_in_executor(
                pool,
                _parse_img_url,
                html,
            )
        if img_url:
            await image_queue.put(img_url)
        url_queue.task_done()


def _parse_img_url(
    html: str,
) -> str | None:
    soup = BeautifulSoup(html, 'lxml')
    full_url = None
    block_with_img = soup.select_one('div#comic>img')
    if block_with_img:
        url_without_protocol = block_with_img.get('src')
        full_url = 'https:' + url_without_protocol
    return full_url


async def create_file_by_img(
    image_queue: asyncio.Queue,
    session: aiohttp.ClientSession,
):
    while True:
        img_url = await image_queue.get()
        img = await _make_request(
            url=img_url,
            session=session,
        )
        filename = img_url.split('/')[-1]
        filename_with_dir = settings.SAVE_IMG_PATH + '/' + filename
        async with aiofiles.open(filename_with_dir, 'wb') as f:
            async for chanck in img.content.iter_chunked(settings.SIZE_CHUNKED):
                await f.write(chanck)
        image_queue.task_done()


async def _make_request(
    url: str,
    session: aiohttp.ClientSession,
) -> aiohttp.ClientResponse | None:
    try:
        response = await session.get(url)
    except TimeoutError:
        print('TimeoutError')
        return None
    if response.ok:
        return response
    print(f'ERROR {response.status}')
    return None
