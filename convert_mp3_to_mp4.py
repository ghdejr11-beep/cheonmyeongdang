import os
import subprocess
import sys

INPUT_FOLDER = r"C:\Users\hdh02\Desktop\playlist_auto\input_music"

def convert_mp3_to_mp4(input_folder):
    if not os.path.isdir(input_folder):
        print(f"폴더를 찾을 수 없습니다: {input_folder}")
        sys.exit(1)

    mp3_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".mp3")]

    if not mp3_files:
        print("변환할 .mp3 파일이 없습니다.")
        return

    print(f"총 {len(mp3_files)}개의 .mp3 파일을 변환합니다.\n")

    for filename in mp3_files:
        mp3_path = os.path.join(input_folder, filename)
        mp4_filename = os.path.splitext(filename)[0] + ".mp4"
        mp4_path = os.path.join(input_folder, mp4_filename)

        print(f"변환 중: {filename} -> {mp4_filename}")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", mp3_path,
            "-f", "lavfi",
            "-i", "color=c=black:s=1280x720:r=1",
            "-shortest",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            mp4_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  완료: {mp4_filename}")
        else:
            print(f"  오류 발생: {filename}")
            print(result.stderr[-500:] if result.stderr else "")

    print("\n모든 변환 작업이 완료되었습니다.")

if __name__ == "__main__":
    convert_mp3_to_mp4(INPUT_FOLDER)
