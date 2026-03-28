import os
import subprocess
import sys
from pathlib import Path


def convert_mp4_to_mp3(input_dir: str) -> None:
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"폴더를 찾을 수 없습니다: {input_dir}")
        sys.exit(1)

    mp4_files = list(input_path.glob("*.mp4"))

    if not mp4_files:
        print("MP4 파일이 없습니다.")
        return

    print(f"총 {len(mp4_files)}개의 MP4 파일을 변환합니다.\n")

    success = 0
    failed = 0

    for mp4_file in mp4_files:
        mp3_file = mp4_file.with_suffix(".mp3")
        print(f"변환 중: {mp4_file.name} -> {mp3_file.name}")

        result = subprocess.run(
            [
                "ffmpeg",
                "-i", str(mp4_file),
                "-vn",
                "-acodec", "libmp3lame",
                "-q:a", "2",
                str(mp3_file),
                "-y",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode == 0:
            print(f"  완료: {mp3_file.name}")
            success += 1
        else:
            print(f"  실패: {mp4_file.name}")
            failed += 1

    print(f"\n변환 완료: 성공 {success}개 / 실패 {failed}개")


if __name__ == "__main__":
    input_dir = r"C:\Users\hdh02\Desktop\playlist_auto\input_music"

    if len(sys.argv) > 1:
        input_dir = sys.argv[1]

    convert_mp4_to_mp3(input_dir)
