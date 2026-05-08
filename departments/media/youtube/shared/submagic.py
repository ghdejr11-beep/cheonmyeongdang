#!/usr/bin/env python3
"""
Submagic API 래퍼 — 쇼츠 후처리 (동적 자막 + B-roll + BGM + 씬 전환).

사용:
    from submagic import SubmagicClient
    sm = SubmagicClient()
    if sm.enabled:
        project_id = sm.create_project(local_mp4, title="...", language="en")
        result_url = sm.wait_and_get_result(project_id)
        sm.download(result_url, out_path)

키 없으면 enabled=False → 호출 쪽에서 원본 그대로 사용.

참고: API는 파일 업로드 또는 URL 둘 다 지원. Pollinations 이미지 합성본은 로컬
파일이므로 multipart 업로드 사용.
"""
import sys, os, json, time, urllib.request, urllib.parse, urllib.error, mimetypes, uuid
from pathlib import Path

BASE = "https://api.submagic.co/v1"
SECRETS = Path(r"D:\cheonmyeongdang\.secrets")


def _load_key():
    if not SECRETS.exists():
        return None
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if line.startswith("SUBMAGIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    return None


def _multipart_body(fields, file_field, file_path, filename=None):
    boundary = f"----Submagic{uuid.uuid4().hex}"
    lines = []
    for k, v in fields.items():
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{k}"')
        lines.append("")
        lines.append(str(v))
    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"
    filename = filename or Path(file_path).name
    lines.append(f"--{boundary}")
    lines.append(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"')
    lines.append(f"Content-Type: {mime}")
    lines.append("")
    head = ("\r\n".join(lines) + "\r\n").encode("utf-8")
    with open(file_path, "rb") as f:
        body = head + f.read() + f"\r\n--{boundary}--\r\n".encode("utf-8")
    ct = f"multipart/form-data; boundary={boundary}"
    return body, ct


class SubmagicError(Exception):
    pass


class SubmagicClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or _load_key()
        self.enabled = bool(self.api_key)

    def _headers(self, extra=None):
        h = {"x-api-key": self.api_key, "Accept": "application/json"}
        if extra:
            h.update(extra)
        return h

    def create_project(self, video_path=None, video_url=None, title="shorts",
                       language="en", template_name="Hormozi 3",
                       magic_brolls=True, magic_zooms=True, magic_brolls_percentage=50,
                       dictionary=None, webhook_url=None):
        if not self.enabled:
            raise SubmagicError("SUBMAGIC_API_KEY missing in .secrets")

        url = f"{BASE}/projects"
        fields = {
            "title": title,
            "language": language,
            "templateName": template_name,
            "magicBrolls": "true" if magic_brolls else "false",
            "magicZooms": "true" if magic_zooms else "false",
            "magicBrollsPercentage": str(magic_brolls_percentage),
        }
        if dictionary:
            fields["dictionary"] = ",".join(dictionary)
        if webhook_url:
            fields["webhookUrl"] = webhook_url

        if video_url:
            fields["videoUrl"] = video_url
            data = json.dumps(fields).encode("utf-8")
            req = urllib.request.Request(url, data=data,
                                         headers=self._headers({"Content-Type": "application/json"}),
                                         method="POST")
        else:
            body, ct = _multipart_body(fields, "video", video_path)
            req = urllib.request.Request(url, data=body,
                                         headers=self._headers({"Content-Type": ct}),
                                         method="POST")

        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise SubmagicError(f"create_project HTTP {e.code}: {e.read().decode(errors='ignore')[:500]}")

        pid = resp.get("project", {}).get("id") or resp.get("id")
        if not pid:
            raise SubmagicError(f"no project id in response: {resp}")
        return pid

    def get_project(self, project_id):
        url = f"{BASE}/projects/{project_id}"
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise SubmagicError(f"get_project HTTP {e.code}: {e.read().decode(errors='ignore')[:300]}")

    def wait_and_get_result(self, project_id, max_wait_sec=900, poll_sec=10):
        """폴링 → 완료되면 결과 URL 반환."""
        start = time.time()
        while True:
            p = self.get_project(project_id)
            project = p.get("project", p)
            status = (project.get("status") or "").lower()
            out_url = project.get("downloadUrl") or project.get("outputUrl") or project.get("videoUrl")
            if status in ("completed", "done", "success", "ready") and out_url:
                return out_url
            if status in ("failed", "error"):
                raise SubmagicError(f"project {project_id} failed: {project}")
            if time.time() - start > max_wait_sec:
                raise SubmagicError(f"timeout after {max_wait_sec}s, last status: {status}")
            time.sleep(poll_sec)

    def download(self, url, out_path):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=600) as r, open(out_path, "wb") as f:
            f.write(r.read())
        return out_path


def post_process_shorts(local_mp4, title, language="en", out_path=None):
    """
    편의 래퍼. API 키 없으면 None 반환 (호출 쪽에서 원본 그대로 사용).

    반환: 처리된 mp4 경로 (Path) 또는 None
    """
    sm = SubmagicClient()
    if not sm.enabled:
        return None

    out_path = out_path or (Path(local_mp4).with_name(Path(local_mp4).stem + "_submagic.mp4"))
    try:
        print(f"  🎨 Submagic: 업로드 → {Path(local_mp4).name}")
        pid = sm.create_project(video_path=local_mp4, title=title, language=language)
        print(f"     project {pid} 생성, 처리 대기…")
        url = sm.wait_and_get_result(pid, max_wait_sec=900, poll_sec=10)
        sm.download(url, out_path)
        print(f"     ✅ {out_path.name} ({out_path.stat().st_size/1024/1024:.1f} MB)")
        return out_path
    except SubmagicError as e:
        print(f"     ⚠️ Submagic 실패: {e} — 원본 사용")
        return None


if __name__ == "__main__":
    sm = SubmagicClient()
    print(f"enabled: {sm.enabled}")
    if len(sys.argv) > 1:
        mp4 = Path(sys.argv[1])
        result = post_process_shorts(mp4, title=mp4.stem, language="en")
        print(f"result: {result}")
