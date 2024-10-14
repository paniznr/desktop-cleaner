from os import scandir, rename, makedirs
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# My changes:
# - Added a specific subfolder for Screen Shot images, since those are messy adn I want them separated
# - Commented code for sound effect and audio file cleanup, since I don't use those
# - If the organizational subfolders don't exist, the script creates them because otherwise I have to make them manually
  # This was actually a bug in my opinion: if you ran the code without subfolders created, a *file* would be created instead of a subfolder, and all files placed in this new file would be lost
# - Using "on_any_event" instead of "on_modified" so I can run this script once in a while to clean up, rather than always in the background

# ! FILL IN BELOW
# ? folder to track e.g. Windows: "C:\\Users\\UserName\\Downloads"
source_dir =     "/Users/paniznr/Desktop"
dest_dir_video = "/Users/paniznr/Desktop/videos"
dest_dir_ss =    "/Users/paniznr/Desktop/screen shots"
dest_dir_image = "/Users/paniznr/Desktop/images"
dest_dir_documents = "/Users/paniznr/Desktop/documents"
# Audio files aren't useful to me, they are commented
# dest_dir_sfx =   "/Users/paniznr/Downloads/test desktop cleaner/sfx"
# dest_dir_music = "/Users/paniznr/Downloads/test desktop cleaner/music"

# Creating subfolders if they don't exist
if not exists(dest_dir_video):
    makedirs(dest_dir_video)
if not exists(dest_dir_ss):
    makedirs(dest_dir_ss)
if not exists(dest_dir_image):
    makedirs(dest_dir_image)
if not exists(dest_dir_documents):
    makedirs(dest_dir_documents)
  
# ? supported image types
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# ? supported Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# ? supported Audio types
# audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# ? supported Document types
document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"]


def make_unique(dest, entry, name):
    filename, part, extension = entry.name.partition('.')
    counter = 1
    # * IF FILE EXISTS, ADDS NUMBER TO THE END OF THE FILENAME
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){part}{extension}"
        counter += 1

    return name


def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, entry, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    # ? THIS FUNCTION WILL RUN WHENEVER THERE IS A CHANGE IN "source_dir"
    # ? .upper is for not missing out on files with uppercase extensions
  
    # Using on_any_event instead of on_modified
    def on_any_event(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                # self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)

    # Unnecessary for me, commented
    # def check_audio_files(self, entry, name):  # * Checks all Audio Files
    #     if not exists(dest_dir_sfx):
    #         logging.info("directory doesn't exist")
    #         makedirs(dest_dir_sfx)
    #     for audio_extension in audio_extensions:
    #         if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
    #             if entry.stat().st_size < 10_000_000 or "SFX" in name:  # ? 10Megabytes
    #                 dest = dest_dir_sfx
    #             else:
    #                 dest = dest_dir_music
    #             move_file(dest, entry, name)
    #             logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):  # * Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_files(self, entry, name):  # * Checks all Screenshot Files
        if name.startswith('Screen Shot'):
            move_file(dest_dir_ss, entry, name)
            logging.info(f"Moved screenshot file: {name}")
        else:
            for image_extension in image_extensions:
                if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                    move_file(dest_dir_image, entry, name)
                    logging.info(f"Moved image file: {name}")

    def check_document_files(self, entry, name):  # * Checks all Document Files
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move_file(dest_dir_documents, entry, name)
                logging.info(f"Moved document file: {name}")


# ! NO NEED TO CHANGE BELOW CODE
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
