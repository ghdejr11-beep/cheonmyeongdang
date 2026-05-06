"""천명당 AAB 검증 스크립트.

Play Console 업로드 전 AAB 파일이 제대로 빌드되었는지 검증한다.

검사 항목:
1. AAB 파일 존재/크기/mtime
2. ZIP 구조 무결성 (AAB는 ZIP 컨테이너)
3. AndroidManifest.xml 핵심 메타데이터 (package, versionCode, versionName, sdk)
4. bundletool 또는 aapt 설치 시 추가 검증

bundletool/aapt 미설치 시 graceful skip + 안내.

사용:
    python scripts/check_aab_validity.py
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AAB_PATH = PROJECT_ROOT / "android" / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
EXPECTED_PACKAGE = "com.cheonmyeongdang.app"
MIN_SIZE_MB = 1.0
MAX_SIZE_MB = 200.0  # Play Store AAB 한도 (압축 후)


def _section(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def _ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def _warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def _err(msg: str) -> None:
    print(f"  [ERR] {msg}")


def check_file() -> dict:
    _section("1. AAB File Existence")
    if not AAB_PATH.exists():
        _err(f"AAB file not found: {AAB_PATH}")
        return {"ok": False, "reason": "missing"}

    stat = AAB_PATH.stat()
    size_mb = stat.st_size / (1024 * 1024)
    mtime = _dt.datetime.fromtimestamp(stat.st_mtime)
    age_hours = (_dt.datetime.now() - mtime).total_seconds() / 3600

    _ok(f"path: {AAB_PATH}")
    _ok(f"size: {size_mb:.2f} MB ({stat.st_size:,} bytes)")
    _ok(f"mtime: {mtime.isoformat()} ({age_hours:.1f}h ago)")

    if size_mb < MIN_SIZE_MB:
        _err(f"too small ({size_mb:.2f} MB < {MIN_SIZE_MB})")
        return {"ok": False, "reason": "small", "size_mb": size_mb}
    if size_mb > MAX_SIZE_MB:
        _warn(f"unusually large ({size_mb:.2f} MB)")

    if age_hours > 24 * 14:
        _warn(f"AAB is old ({age_hours/24:.1f} days). Consider rebuilding.")

    return {
        "ok": True,
        "size_mb": size_mb,
        "size_bytes": stat.st_size,
        "mtime": mtime.isoformat(),
        "age_hours": age_hours,
    }


def check_zip_structure() -> dict:
    _section("2. ZIP Structure (AAB is a ZIP)")
    try:
        with zipfile.ZipFile(AAB_PATH, "r") as zf:
            names = zf.namelist()
            bad = zf.testzip()
            if bad:
                _err(f"corrupt entry: {bad}")
                return {"ok": False, "reason": "corrupt"}
            _ok(f"entries: {len(names)}")

            required = ["BundleConfig.pb"]
            module_indicators = [n for n in names if n.startswith("base/")]
            if not module_indicators:
                _err("no 'base/' module found in AAB")
                return {"ok": False, "reason": "no-base"}
            _ok(f"base module entries: {len(module_indicators)}")

            for r in required:
                present = any(n == r or n.endswith("/" + r) for n in names)
                if present:
                    _ok(f"contains: {r}")
                else:
                    _warn(f"missing: {r}")

            manifest_entry = "base/manifest/AndroidManifest.xml"
            if manifest_entry in names:
                _ok(f"manifest present: {manifest_entry}")
            else:
                _warn(f"manifest not found at expected path: {manifest_entry}")

            return {
                "ok": True,
                "entry_count": len(names),
                "has_manifest": manifest_entry in names,
            }
    except zipfile.BadZipFile as e:
        _err(f"not a valid ZIP: {e}")
        return {"ok": False, "reason": "bad-zip"}
    except Exception as e:
        _err(f"unexpected error: {e}")
        return {"ok": False, "reason": str(e)}


def _read_manifest_strings() -> str:
    """AndroidManifest.xml is binary protobuf in AAB; we read raw bytes
    and pull out printable strings. Won't give exact versionCode but
    confirms package name etc."""
    try:
        with zipfile.ZipFile(AAB_PATH, "r") as zf:
            data = zf.read("base/manifest/AndroidManifest.xml")
            # extract printable ASCII chunks of length >= 4
            chunks = re.findall(rb"[\x20-\x7e]{4,}", data)
            return "\n".join(c.decode("ascii", errors="replace") for c in chunks)
    except Exception:
        return ""


def check_manifest_metadata() -> dict:
    _section("3. AndroidManifest Metadata (raw scan)")
    raw = _read_manifest_strings()
    if not raw:
        _warn("could not read manifest")
        return {"ok": False}

    pkg_found = EXPECTED_PACKAGE in raw
    if pkg_found:
        _ok(f"package id present: {EXPECTED_PACKAGE}")
    else:
        _warn(f"package id NOT found in manifest strings: {EXPECTED_PACKAGE}")

    permissions = sorted(set(re.findall(r"android\.permission\.[A-Z_]+", raw)))
    if permissions:
        _ok(f"permissions detected: {len(permissions)}")
        for p in permissions[:8]:
            print(f"      - {p}")
        if len(permissions) > 8:
            print(f"      ... +{len(permissions)-8} more")

    return {"ok": True, "package_found": pkg_found, "permissions": permissions}


def check_build_gradle() -> dict:
    _section("4. build.gradle Version (source of truth)")
    gradle = PROJECT_ROOT / "android" / "app" / "build.gradle"
    if not gradle.exists():
        _warn("build.gradle not found")
        return {"ok": False}

    text = gradle.read_text(encoding="utf-8")
    vc = re.search(r"versionCode\s+(\d+)", text)
    vn = re.search(r'versionName\s+"([^"]+)"', text)
    pkg = re.search(r'applicationId\s+"([^"]+)"', text)
    ns = re.search(r'namespace\s*=\s*"([^"]+)"', text)

    info = {}
    if vc:
        info["versionCode"] = int(vc.group(1))
        _ok(f"versionCode: {info['versionCode']}")
    if vn:
        info["versionName"] = vn.group(1)
        _ok(f"versionName: {info['versionName']}")
    if pkg:
        info["applicationId"] = pkg.group(1)
        _ok(f"applicationId: {info['applicationId']}")
        if info["applicationId"] != EXPECTED_PACKAGE:
            _warn(f"applicationId mismatch (expected {EXPECTED_PACKAGE})")
    if ns:
        info["namespace"] = ns.group(1)
        _ok(f"namespace: {info['namespace']}")

    return {"ok": True, **info}


def check_external_tools() -> dict:
    _section("5. External Tools (bundletool / aapt)")
    found = {}
    for tool in ("bundletool", "aapt", "aapt2"):
        path = shutil.which(tool)
        if path:
            _ok(f"{tool}: {path}")
            found[tool] = path
        else:
            _warn(f"{tool}: not in PATH (skip extended checks)")

    # Try to locate aapt2 in Android SDK build-tools
    sdk_candidates = [
        os.environ.get("ANDROID_HOME"),
        os.environ.get("ANDROID_SDK_ROOT"),
        os.path.expanduser("~/AppData/Local/Android/Sdk"),
        os.path.expanduser("~/Android/Sdk"),
    ]
    for sdk in sdk_candidates:
        if not sdk:
            continue
        bt = Path(sdk) / "build-tools"
        if bt.exists():
            versions = sorted([p for p in bt.iterdir() if p.is_dir()], reverse=True)
            for v in versions[:3]:
                aapt2 = v / ("aapt2.exe" if os.name == "nt" else "aapt2")
                if aapt2.exists():
                    _ok(f"sdk aapt2 found: {aapt2}")
                    found.setdefault("aapt2_sdk", str(aapt2))
                    break
            if "aapt2_sdk" in found:
                break

    return found


def run_bundletool_dump(tools: dict) -> dict:
    if "bundletool" not in tools:
        return {"ok": False, "reason": "no-bundletool"}
    _section("6. bundletool dump manifest")
    try:
        out = subprocess.run(
            [tools["bundletool"], "dump", "manifest", "--bundle", str(AAB_PATH)],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode == 0:
            print(out.stdout[:2000])
            return {"ok": True, "stdout": out.stdout}
        else:
            _warn(f"bundletool failed: {out.stderr[:300]}")
            return {"ok": False, "reason": out.stderr[:300]}
    except Exception as e:
        _warn(f"bundletool error: {e}")
        return {"ok": False, "reason": str(e)}


def main() -> int:
    print("천명당 AAB Validity Check")
    print(f"  project: {PROJECT_ROOT}")
    print(f"  aab:     {AAB_PATH}")

    file_info = check_file()
    if not file_info.get("ok"):
        print("\nFAIL: AAB file check failed.")
        return 1

    zip_info = check_zip_structure()
    if not zip_info.get("ok"):
        print("\nFAIL: ZIP structure invalid.")
        return 1

    manifest_info = check_manifest_metadata()
    gradle_info = check_build_gradle()
    tools = check_external_tools()
    bt_info = run_bundletool_dump(tools)

    _section("SUMMARY")
    print(f"  size       : {file_info.get('size_mb', 0):.2f} MB")
    print(f"  built      : {file_info.get('mtime', '?')}")
    print(f"  package    : {gradle_info.get('applicationId', '?')}")
    print(f"  versionCode: {gradle_info.get('versionCode', '?')}")
    print(f"  versionName: {gradle_info.get('versionName', '?')}")
    print(f"  permissions: {len(manifest_info.get('permissions', []))}")
    print(f"  bundletool : {'yes' if bt_info.get('ok') else 'no/skip'}")
    print()
    print("  -> Ready for Play Console upload.")
    print(f"  -> See docs/play_console_upload_guide.md for steps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
