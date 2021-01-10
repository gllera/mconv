# Multimedia library converter

**WARNING!! The original multimedia files will be replaced with the converted versions so, you may prefer to check that the result will be what you expect with some test files first. Btw, the replacement is atomic so it won't get corrupted in case of error or forced exit.**

Easy and efficiently, analyze a whole multimedia library to make sure that everything match a desired format and convert what doesn't to make it match. The scans are cached to greately decrease resume/re-scan times. Nvidia hardware acceleration is supported too.

Extensions taken into account and target formats:
| Extension | A.format | A.bit_rate    | V.format | V.bit_rate |
| :---:     | :---:    | :---:         | :---:    | :---:      |
| .mp3      | mp3      | < 128.1kbps   | -        | -          |
| .mp4      | acc      | < 128.1kbps   | h264     | < 600kbps  |

**Note:** If a video stream from a `.mp4` file needs to be converted to reduce his `bit_rate`, his frame rate will be limited to `30fps` and his height/width resolution to `1280` to keep a nice image quality.

## Requisites
- python3
- ffmpeg (https://ffmpeg.org/download.html)

\* it basically works anywhere (`arm`, `x86`, `linux`, `windows`, ...)

## Installation
**Using pip:**
```bash
$ pip install mconv
```

## Usage
To convert multimedia files recursively at current path:
```
$ python -m mconv .
```
See help with:
```
$ python -m mconv -h
usage: mconv [-h] [-t M] [-j N] [-n] path

Multimedia library converter

positional arguments:
  path            Library path

optional arguments:
  -h, --help      show this help message and exit
  -t M, --tier M  Subgroups of tasks to process based on CPU demand: 1 (Low) - 3 (High).
  -j N, --jobs N  Number of paralell jobs
  -n, --nvidia    Use nvidia hardware when necessary
```
**Tiers details and his default `Jobs` value:**
- `1` - **Taks:** library scan, format reading and cache update. **Jobs:** `cpu_cores * 2`
- `2` - **Taks:** process audio streams. **Jobs:** `cpu_cores`
- `3` - **Taks:** process video streams. **Jobs:** `1`

\* If a video file needs video and audio streem conversion, it's tier `3` but if only needs audio conversion, it's tier `2`.

\* Default **Tier** value is `123` (all).

\* When multiple **Tiers** are selected, default **Jobs** value is the minimum of them.

## Tips and tricks
- Don't process all **Tiers** in the same execution or you won't be able to take advantage of all your cores efficiently. On a single machine, it's better to execute each **Tier** separated. In the future, this may be the default behaviour when multiple **Tiers** are defined.
- Once **Tier** `1` was executed, **Tier** `2` and **Tier** `3` can be executed safely at the same time (also on different machines with a NAS).
- Maximum **Jobs** with Nvidia hardware aceleration depends on GPU model. See "*Max # of concurrent sessions*" on "*Encoder*" at  https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new
- If a video can't be converted using Nvidia hardware acceleration, try without it, it may work...
- It's safe to delete `.tmp` folder created at library path when no **Tier** `2` or `3` are running.
- Use an external tool/script to bulk rename audio/video extensions to `.mp3/.mp4` to convert them with `mconv`.
