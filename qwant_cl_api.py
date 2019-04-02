import asyncio
import aiohttp
import csv
import asyncpgsa


class QvantSearch():

    url = 'https://api.qwant.com/api/search/{keyword}?count={count}&offset={offset}&{query}&t={keyword}&uiv=1'
    headers = {
    # 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Encoding' : 'gzip, deflate',
    # 'Accept-Language' : 'en-US,en;q=0.5',
    # 'Connection' : 'keep-alive',
    # 'Cookie' : '',
    'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'

    }

    def __init__(self, keyword='images', offset=0, count=1, session=None):
        self.keyword = keyword
        self.offset = offset
        # self.query = query
        self.count = count
        if session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        else:
            self.session = session

    async def get_images(self, query):
        self.keyword = 'images'
        self.query = {'q' : query}
        query1 = urllib.parse.urlencode(self.query)
        query_url = self.url.format(
            keyword = self.keyword,
            count = self.count,
            offset = self.offset,
            query = query1
            )
        print('-',query1,'----=', query_url)
        data = await self._fetch(query_url)
        return data


    async def _fetch(self,send):
        print(send)
        async with self.session.get(send) as response:
            print('-----', response)
            if response.content_type == 'text/html':
                data = await response.text()
            if response.content_type == 'application/json':
                data =  await response.json()
            if response.content_type == 'text/xml':
                data = await response.text()

        return data

    async def close(self):
        """Close the aiohttp Session"""
        await self.session.close()


    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close()


class Sereliz():

    @classmethod
    async def pars(cls, data):
        try:
            data = data['data']['result']['items'][0]['media']
        except Exception:
            data = ''
        return data


    @classmethod
    def write_csv(cls, data):

        with open('img1.csv', 'a') as f:
            writer = csv.writer(f)

            writer.writerow( ( data['title'],
                            data['url']  ) )


async def main():
    db = await asyncpgsa.create_pool(dsn='postgresql://kola:test@localhost:5432/demo')
    async with db.acquire() as conn:
        query = 'Select title from game'
        result = await conn.fetch(query)

        # result.reverse()

    db.close()
    async with QvantSearch() as cl:
        for title in result:
            title1 = f"xbox 360 front cover {title['title']}"
            print(title1)
            try:
                data = await cl.get_images(title1)
            except Exception:
                data = ''
            data = await Sereliz.pars(data)
            dd = {'title': title['title'],
                'url' : data}
            Sereliz.write_csv(dd)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = [
            # loop.create_task(main3()),
            loop.create_task(main())
        ]
    wait_tasks = asyncio.wait(task)
    loop.run_until_complete(wait_tasks)