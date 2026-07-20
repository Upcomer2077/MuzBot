import asyncio
import sys

from config import DATABASE_PATH
from dungeon import DM
from type import YoutubeSearchResultDict


async def check():
    try:
        print("DB_PATH:", DATABASE_PATH)
        await DM.open_dungeon()
        res = await DM._get_slaves_count()
        print(f"Slaves count: {res}")

        count_enslaved = await DM.enslave_bulk(
            [
                YoutubeSearchResultDict(
                    video_id="0",
                    title="0",
                    artist="0",
                    duration="0",
                    duration_seconds=0,
                )
            ]
        )

        if count_enslaved > 0:
            print("Database check: passed")
            await DM.next_door(video_id="0")
            sys.exit(0)
        else:
            await DM.next_door(video_id="0")
            print("Database check: failed")
            sys.exit(1)
    except Exception as e:
        print(e)
    finally:
        await DM.next_door(video_id="0")
        await DM.close_dungeon()


if __name__ == "__main__":
    asyncio.run(check())
