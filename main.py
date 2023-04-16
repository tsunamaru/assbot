#!/usr/bin/env python3
# pylint: disable=multiple-imports, missing-function-docstring

import logging, os, subprocess, hashlib, random, string
import asyncio, aiohttp, aiofiles
from decouple import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from cfg import SUBSCRIBERS_ID

# if .env present, load it, otherwise load from environment
if os.path.exists(".env"):
    LOGLEVEL = config("LOGLEVEL", default="INFO")
    TOKEN = config("TOKEN")
    CHANNEL = config("CHANNEL")
    ADMIN = config("ADMIN")
    UPSTREAM = config("UPSTREAM", default=None)
else:
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO")
    TOKEN = os.environ.get("TOKEN")
    CHANNEL = os.environ.get("CHANNEL")
    ADMIN = os.environ.get("ADMIN")
    UPSTREAM = os.environ.get("UPSTREAM", None)

# Some static variables
TG_ADDRESS = f"https://t.me/{CHANNEL.split('@')[1]}/"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    encoding="utf-8",
    level=logging.getLevelName(LOGLEVEL),
)

COMMON_CONTENT_TYPES = [
    ContentType.TEXT,
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.AUDIO,
    ContentType.DOCUMENT,
    ContentType.STICKER,
    ContentType.ANIMATION,
]
ATTACH_CONTENT_TYPES = [
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.DOCUMENT,
    ContentType.AUDIO,
]
BAD_CONTENT_TYPES = [
    ContentType.VIDEO_NOTE,
    ContentType.VOICE,
]

BAD_WORDS = [
    "финка нквд",
    "образца 1939",
    "ножн",
    "клинок",
    "клинка",
    "дамаск",
    "кизляр",
    "заточк",
    "рукоять",
    "8938 303 05 05",
    "8988-646-2323",
    "8988 794 78 41",
    "79886444614",
    "nozhi_shop",
    "nozhishop",
    "barkrf",
    "arenda_odessa",
    "t.me/+",
    "t.me/joinchat",
    "#реклама",
    "#промо",
    "38 066 580 34 98",
    "38 093 119 29 84",
]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "test"])
async def start(message: types.Message):
    await message.reply(f"Просто пиши свою хуйню и я отправлю её в {CHANNEL}")


@dp.message_handler(commands=["whoami"])
async def whoami(message: types.Message):
    await message.reply(
        f"You are {message.from_user.username} and your ID is {message.from_user.id}"
    )


@dp.message_handler(commands=["uname"])
async def uname(message: types.Message):
    uname = subprocess.run(["uname", "-a"], stdout=subprocess.PIPE).stdout.decode(
        "utf-8"
    )
    await message.reply(uname)


@dp.message_handler(commands=["hash"])
async def hash(message: types.Message):
    if not UPSTREAM:
        await message.reply("UPSTREAM is not set!")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(
            UPSTREAM, headers={"User-Agent": "Mozilla/5.0"}
        ) as response:
            main_remote = await response.text()

    hash_remote = hashlib.sha256(main_remote.encode("utf-8")).hexdigest()
    async with aiofiles.open("main.py", "rb") as f:
        hash_local = hashlib.sha256(await f.read()).hexdigest()
        f.close()

    if hash_remote == hash_local:
        await message.reply(f"Hashes match!")
        logging.info("Hash check passed!")
    elif LOGLEVEL == "DEBUG":
        await message.reply(f"Hashes do not match, but DEBUG is set.")
    else:
        await message.reply(
            "Hashes do not match!\nRemote: {}\nLocal: {}".format(
                hash_remote, hash_local
            )
        )
        logging.error("Hash check failed!")


@dp.message_handler(commands=["loglevel"])
async def set_loglevel(message: types.Message):
    if message.from_user.username != str(ADMIN):
        await message.reply("You're not allowed to do this.")
        return

    global LOGLEVEL
    LOGLEVEL = message.text.split()[1].upper()

    if LOGLEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        await message.reply("Wrong value!")
        return

    logging.getLogger().setLevel(logging.getLevelName(LOGLEVEL))
    logging.info("Loglevel set to {}".format(LOGLEVEL))
    await message.reply("Loglevel set to {}".format(LOGLEVEL))


@dp.message_handler(commands=["send_poll"])
async def send_poll(message: types.Message):
    if message.from_user.username != str(ADMIN):
        await message.reply("You're not allowed to do this.")
        return

    poll = await message.reply_poll(
        "Опрос активности", options=["нажми сюда", "или сюда"], is_anonymous=False
    )

    for x in SUBSCRIBERS_ID:
        try:
            await asyncio.sleep(0.5)  # to avoid flood limit
            await bot.forward_message(
                chat_id=int(x),
                from_chat_id=message.chat.id,
                message_id=poll.message_id,
            )
            logging.info("Poll forwarded to {}".format(x))

        except Exception as e:
            logging.error("Error forwarding poll to {}: {}".format(x, e))


@dp.message_handler(commands=["stop_poll"])
async def stop_poll(message: types.Message):
    if message.from_user.username != str(ADMIN):
        await message.reply("You're not allowed to do this.")
        return

    if message.reply_to_message is None:
        await message.reply("Reply to poll you want to close.")
        return

    await bot.stop_poll(message.chat.id, message.reply_to_message.message_id)


@dp.message_handler(commands=["ping"])
async def ping(message: types.Message):
    if message.from_user.username != str(ADMIN):
        await message.reply("You're not allowed to do this.")
        return

    if len(message.text.split()) > 1:
        # verify that ping target is Telegram ID, otherwise return error
        target = message.text.split()[1] if message.text.split()[1].isdigit() else None

        if target is None:
            await message.reply("Target should be a Telegram ID!")
            return

        try:
            pingmsg = await bot.send_message(
                chat_id=int(target),
                text="Ping test, please ignore...",
                disable_notification=True,
            )
            logging.info("Ping succesfuly sent to {}".format(target))
            await bot.delete_message(chat_id=int(target), message_id=pingmsg.message_id)
            await message.reply("Ping succesfuly sent to {}".format(target))

        except Exception as e:
            logging.error("Error sending ping to {}: {}".format(target, e))
            await message.reply("Error sending ping to {}: {}".format(target, e))

    else:
        for x in SUBSCRIBERS_ID:
            try:
                await asyncio.sleep(0.5)  # to avoid flood limit
                pingmsg = await bot.send_message(
                    chat_id=int(x),
                    text="Ping test, please ignore...",
                    disable_notification=True,
                )
                logging.info("Ping succesfuly sent to {}".format(x))
                await bot.delete_message(chat_id=int(x), message_id=pingmsg.message_id)

            except Exception as e:
                logging.error("Error sending ping to {}: {}".format(x, e))


@dp.message_handler(commands=["rndstr"])
async def random_string(message: types.Message):
    if message.from_user.username != str(ADMIN):
        await message.reply("You're not allowed to do this.")
        return

    await message.reply(
        "".join(random.choices(string.ascii_letters + string.digits, k=16))
    )


@dp.message_handler(commands=["request_admin"])
async def request_admin(message: types.Message):
    sender_status = await bot.get_chat_member(CHANNEL, message.from_user.id)

    if sender_status["status"] in ["administrator", "creator"]:
        await message.reply("You're already an admin!")
        return

    if not sender_status["status"] in ["member", "restricted"]:
        await message.reply("Please join the channel first.")
        return

    admins = await bot.get_chat_administrators(CHANNEL)
    if len(admins) == 50:
        await message.reply(
            "Channel admin capacity is full, please wait until next activity poll takes place."
        )
        return

    admin_id = [x["user"]["id"] for x in admins if x["user"]["username"] == ADMIN][0]
    await bot.send_message(
        chat_id=admin_id,
        text="{} ({}) requested admin rights. ID: {}".format(
            message.from_user.full_name,
            message.from_user.username,
            message.from_user.id,
        ),
    )

    await message.reply(
        "Your request has been sent and will be processed within few hours.\n"
        + "Current channel admin capacity is: {}/50.".format(len(admins))
    )


@dp.message_handler(content_types=BAD_CONTENT_TYPES)
async def decline_msg(message: types.Message):
    await message.reply(f"Хуй будешь?")
    await message.delete()
    logging.info(
        f"Declined message from {message.from_user.username} with ID {message.from_user.id}, reason: {message.content_type}"
    )


@dp.channel_post_handler(content_types=BAD_CONTENT_TYPES)
async def delete_msg(message: types.Message):
    await message.delete()
    logging.info(
        f"Deleted post with ID {message.message_id}, reason: {message.content_type}"
    )


@dp.message_handler(
    lambda message: message.text
    and sum(list(map(lambda word: word in message.text.lower(), BAD_WORDS)))
)
async def decline_msg(message: types.Message):
    await message.reply(f"Хуй будешь?")
    await message.delete()
    logging.info(
        f"Declined message from {message.from_user.username} with ID {message.from_user.id}, reason: fuzzy match: {message.text}"
    )


@dp.message_handler(
    lambda message: message.caption
    and sum(list(map(lambda word: word in message.caption.lower(), BAD_WORDS))),
    content_types=ATTACH_CONTENT_TYPES,
)
async def decline_msg(message: types.Message):
    await message.reply(f"Хуй будешь?")
    await message.delete()
    logging.info(
        f"Declined message from {message.from_user.username} with ID {message.from_user.id}, reason: fuzzy match: {message.caption}"
    )


@dp.channel_post_handler(
    lambda message: message.text
    and sum(list(map(lambda word: word in message.text.lower(), BAD_WORDS)))
)
async def delete_msg(message: types.Message):
    await message.delete()
    logging.info(
        f"Deleted post with ID {message.message_id}, reason: fuzzy match: {message.text}"
    )


@dp.channel_post_handler(
    lambda message: message.caption
    and sum(list(map(lambda word: word in message.caption.lower(), BAD_WORDS))),
    content_types=ATTACH_CONTENT_TYPES,
)
async def delete_msg(message: types.Message):
    await message.delete()
    logging.info(
        f"Deleted post with ID {message.message_id}, reason: fuzzy match: {message.caption}"
    )


@dp.message_handler(content_types=COMMON_CONTENT_TYPES)
async def msg(message: types.Message):
    sender_status = await bot.get_chat_member(CHANNEL, message.from_user.id)
    if not sender_status["status"] in ["administrator", "creator", "member"]:
        await message.reply(f"Refusing to forward your message, reason: not subscribed")
        logging.info(
            f"Declined message from {message.from_user.username} with ID {message.from_user.id}, reason: not subscribed"
        )
        return

    if message.text and TG_ADDRESS in message.text:
        try:
            link = str(message.text.split("\n")[0])
            msg_id = int(link.split(TG_ADDRESS)[1])
            clean_message = message.text.split(link)[1]

            if len(clean_message) == 0:
                await message.reply(f"Empty message!")
                return

            await bot.send_message(
                chat_id=CHANNEL, text=clean_message, reply_to_message_id=msg_id
            )

            return

        except Exception as e:
            await message.reply(f"Error: {e}")
            return

    elif message.caption and TG_ADDRESS in message.caption:
        try:
            link = str(message.caption.split("\n")[0])
            msg_id = int(link.split(TG_ADDRESS)[1])
            clean_message = message.caption.split(link)[1]

            if message.content_type == ContentType.PHOTO:
                await bot.send_photo(
                    chat_id=CHANNEL,
                    photo=message.photo[-1].file_id,
                    caption=clean_message,
                    reply_to_message_id=msg_id,
                )
            elif message.content_type == ContentType.VIDEO:
                await bot.send_video(
                    chat_id=CHANNEL,
                    video=message.video.file_id,
                    caption=clean_message,
                    reply_to_message_id=msg_id,
                )
            elif message.content_type == ContentType.AUDIO:
                await bot.send_audio(
                    chat_id=CHANNEL,
                    audio=message.audio.file_id,
                    caption=clean_message,
                    reply_to_message_id=msg_id,
                )
            elif message.content_type == ContentType.ANIMATION:
                await bot.send_animation(
                    chat_id=CHANNEL,
                    animation=message.animation.file_id,
                    caption=clean_message,
                    reply_to_message_id=msg_id,
                )
            elif message.content_type == ContentType.DOCUMENT:
                await bot.send_document(
                    chat_id=CHANNEL,
                    document=message.document.file_id,
                    caption=clean_message,
                    reply_to_message_id=msg_id,
                )

            return

        except Exception as e:
            await message.reply(f"Error: {e}")
            return

    try:
        await bot.copy_message(
            chat_id=CHANNEL, from_chat_id=message.chat.id, message_id=message.message_id
        )
    except Exception as e:
        await message.reply(f"Error: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
