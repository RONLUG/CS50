import re

tags = ["Mathematic", "Physics", "Programming"]
yt_link_pattern = re.compile(r"(https?://)?(www\.)?(youtube\.com/watch\?).*v=(.+?)(&|$)")