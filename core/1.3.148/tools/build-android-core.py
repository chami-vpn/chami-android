"""Build the Android AAR from the pinned Go module and Android NDK."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile


SOURCE = Path(__file__).resolve().parents[1] / "android" / "native"
NDK_VERSION = "30.0.16248370"
ABIS = {"armeabi-v7a", "arm64-v8a", "x86", "x86_64"}
GEO_RELEASE = "202611222203"
GEO_HASHES = {
    "geoip": "d4ec4c5e5d5a38c1399964ea9fd8c94288426a3b31b483904b67819fc07f4466",
    "geosite": "94e6f902cfa9d4d70ebf3c0138d9cc24175b51885c490cb673ee54f5e1b6ce6f",
}


def digest(path):
    with path.open("rb") as stream:
        checksum = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
        return checksum.hexdigest()


def add_routing_assets(aar, local_data, stage):
    # The app may override these with a newer release. A clean checkout still needs working routes.
    for name, expected in GEO_HASHES.items():
        filename = name + ".dat"
        data = local_data / filename
        if not data.is_file() or digest(data) != expected:
            data = stage / filename
            url = f"https://github.com/Loyalsoldier/v2ray-rules-dat/releases/download/{GEO_RELEASE}/{filename}"
            with urllib.request.urlopen(url, timeout=120) as source, data.open("wb") as target:
                shutil.copyfileobj(source, target)
            if digest(data) != expected:
                raise RuntimeError(f"Checksum mismatch for {filename}")
        entry = zipfile.ZipInfo("assets/" + filename)
        entry.compress_type = zipfile.ZIP_DEFLATED
        with data.open("rb") as source, aar.open(entry, "w") as target:
            shutil.copyfileobj(source, target)
    aar.writestr(zipfile.ZipInfo("assets/geo-release.json"), json.dumps({"release": GEO_RELEASE, **GEO_HASHES}))


def build(destination, force):
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / "libv2ray.aar"
    receipt = destination / "libv2ray.build.json"
    files = [SOURCE / "go.mod", SOURCE / "go.sum", *sorted(SOURCE.glob("*.go"))]
    inputs = {p.relative_to(SOURCE).as_posix(): digest(p) for p in files}
    inputs[Path(__file__).name] = digest(Path(__file__))
    if not force and archive.is_file() and receipt.is_file():
        try:
            if json.loads(receipt.read_text()) == {"inputs": inputs, "sha256": digest(archive)}:
                print("Android native core is up to date")
                return
        except (ValueError, OSError):
            pass

    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk:
        raise SystemExit("Set ANDROID_HOME to the Android SDK directory")
    ndk = Path(sdk) / "ndk" / NDK_VERSION
    if not ndk.is_dir():
        raise SystemExit(f'Install the pinned NDK with sdkmanager "ndk;{NDK_VERSION}"')
    go_version = next(line.split()[1] for line in (SOURCE / "go.mod").read_text().splitlines()
                      if line.startswith("go "))
    env = dict(os.environ, ANDROID_HOME=sdk, ANDROID_NDK_HOME=str(ndk),
               GOTOOLCHAIN=f"go{go_version}", GOWORK="off")
    # Stage on the destination volume so a failed or interrupted build preserves the last good AAR.
    with tempfile.TemporaryDirectory(dir=destination) as stage:
        stage = Path(stage).resolve()
        paths = [str(stage)]
        if env.get("JAVA_HOME"):
            paths.append(str(Path(env["JAVA_HOME"]) / "bin"))
        env["PATH"] = os.pathsep.join([*paths, env["PATH"]])

        def run(*args):
            subprocess.run(args, cwd=module, env=env, check=True)

        module = stage / "native"
        module.mkdir()
        for source in files:
            if source.parent == SOURCE:
                shutil.copyfile(source, module / source.name)
        run("go", "mod", "download")
        run("go", "mod", "verify")
        run("go", "build", "-mod=readonly", "-o", str(stage) + os.sep,
            "golang.org/x/mobile/cmd/gomobile", "golang.org/x/mobile/cmd/gobind")
        built = stage / archive.name
        gomobile = stage / ("gomobile.exe" if os.name == "nt" else "gomobile")
        run(str(gomobile), "bind", "-target=android", "-androidapi", "24", "-trimpath",
            "-ldflags=-s -w -buildid= -checklinkname=0", "-o", str(built), ".")
        with zipfile.ZipFile(built, "a") as aar:
            native = {n for n in aar.namelist() if n.startswith("jni/") and n.endswith(".so")}
            if native != {f"jni/{abi}/libgojni.so" for abi in ABIS}:
                raise RuntimeError("Missing or unexpected native libraries in Android AAR")
            library = stage / "libgojni.so"
            for name in sorted(native):
                with aar.open(name) as source, library.open("wb") as target:
                    shutil.copyfileobj(source, target)
                info = subprocess.check_output(["go", "version", "-m", str(library)], env=env, text=True)
                if info.splitlines()[0].split()[-1] != f"go{go_version}":
                    raise RuntimeError(f"Unexpected Go toolchain in {name}")
            add_routing_assets(aar, destination / "geo", stage)
        stamp = stage / receipt.name
        stamp.write_text(json.dumps({"inputs": inputs, "sha256": digest(built)}))
        built.replace(archive)
        stamp.replace(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build(args.destination.resolve(), args.force)
