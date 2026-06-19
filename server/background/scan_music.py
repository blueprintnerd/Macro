
import mutagen
from mutagen import File

def scan_metadata_from_file(path):
    metadata = {}
    try:
        audio = File(path, easy=True)
        if audio is not None:
            for key in audio.keys():
                val = audio[key]
                if isinstance(val, list) and len(val) > 0:
                    metadata[key] = val[0]
                else:
                    metadata[key] = str(val)
            if hasattr(audio, 'info') and audio.info is not None:
                if hasattr(audio.info, 'length'):
                    metadata['duration'] = audio.info.length
                if hasattr(audio.info, 'bitrate'):
                    metadata['bitrate'] = audio.info.bitrate
    except Exception:
        pass
    return metadata