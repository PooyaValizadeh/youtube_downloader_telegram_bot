TOKEN = "8323684344:AAG5HNlV6fyEXQbeIbgs6gZuXN6j3O-FJkU"

import telebot as tl
import os
from pytubefix import YouTube
from moviepy.editor import AudioFileClip, VideoFileClip

bot = tl.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "salam seied lind dade kon")


@bot.message_handler(func=lambda message: True, content_types=["text"])
def link(message):
    url = message.text
    print(f"url: {url}")
    try:
        yt = YouTube(url)
        bot.reply_to(message, "Select keifiat", reply_markup=qumark(yt))
    except Exception as e:
        print(f"error : {e}")


def qumark(yt):
    markup = tl.types.InlineKeyboardMarkup()
    streams = yt.streams.filter(mime_type="video/mp4")
    print("ohleleonlelas")
    for stream in streams:
        resolution = stream.resolution
        but_text = f"{resolution} - {stream.mime_type}"
        callbackdata = f"{stream.itag}|{yt.watch_url}"
        button = tl.types.InlineKeyboardButton(but_text, callback_data=callbackdata)
        markup.add(button)
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callbackm(call):
    itag, url = call.data.split("|")
    yt = YouTube(url)

    stream = yt.streams.get_by_itag(int(itag))

    video_filename = "video.mp4"
    audio_filename = "audio.mp4"
    final_filename = "final_video.mp4"

    stream.download(filename=video_filename)

    try:
        if stream.is_progressive:
            with open(video_filename, "rb") as video:
                bot.send_video(call.message.chat.id, video)

            os.remove(video_filename)

        else:
            audio_stream = yt.streams.filter(
                only_audio=True
            ).order_by("abr").desc().first()

            audio_stream.download(filename=audio_filename)

            video_clip = VideoFileClip(video_filename)
            audio_clip = AudioFileClip(audio_filename)

            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(
                final_filename,
                codec="libx264",
                audio_codec="aac"
            )

            with open(final_filename, "rb") as video:
                bot.send_video(call.message.chat.id, video)

            os.remove(video_filename)
            os.remove(audio_filename)
            os.remove(final_filename)

    except Exception as e:
        print(f"error: {e}")
        bot.reply_to(call.message, "faild")
bot.polling()
