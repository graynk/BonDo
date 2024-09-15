import os
import subprocess
import uuid
from typing import List

BAGUETTE = './baguette.mp4'

def run_ffmpeg(oh_voice: str, sabbath_voice: str) -> str:
    if oh_voice is None and sabbath_voice is None:
        return BAGUETTE
    output = str(uuid.uuid4()) + '.mp4'
    try:
        pipe = subprocess.Popen(construct_ffmpeg_args(oh_voice, sabbath_voice, output))
        pipe.wait()
    except Exception as ex:
        print(ex)
    for voice in [oh_voice, sabbath_voice]:
        if voice is not None:
            os.remove(voice)
    return output


def construct_ffmpeg_args(oh_voice: str, sabbath_voice: str, output: str) -> List[str]:
    filter_string = '[0:a]volume=1.0[a0]; '
    args = ['ffmpeg',
            '-i', BAGUETTE,
            '-filter_complex',
            '-map', '0:v',
            '-map', '[out]',
            '-preset', 'ultrafast',
            output]

    inputs = 1
    if oh_voice is not None:
        filter_string += '[{0}:a]adelay=1500|1500,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, oh_voice)
        args.insert(inputs * 2 - 1, '-i')
        filter_string += '[{0}:a]adelay=5500|5500,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, oh_voice)
        args.insert(inputs * 2 - 1, '-i')
    if sabbath_voice is not None:
        filter_string += '[{0}:a]adelay=3200|3200,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, sabbath_voice)
        args.insert(inputs * 2 - 1, '-i')

    for input_number in range(inputs):
        filter_string += '[a{}]'.format(input_number)
    filter_string += 'amix=inputs={}:duration=longest[out]'.format(inputs)
    args.insert(inputs * 2 + 2, filter_string)
    return args
