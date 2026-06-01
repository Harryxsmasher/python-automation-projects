import os
import zipfile
import sys
import time
import subprocess

# ✅ Ensure tqdm is installed
try:
    from tqdm import tqdm
except ImportError:
    print("Installing required package: tqdm...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    from tqdm import tqdm


# ✅ FIXED safe_path (handles both local + network paths)
def safe_path(path):
    if os.name == 'nt':
        path = os.path.abspath(path)

        if path.startswith("\\\\"):  # UNC path
            path = path.lstrip("\\")
            return "\\\\?\\UNC\\" + path
        else:
            return "\\\\?\\" + path

    return path


def get_valid_path(prompt):
    while True:
        path = input(prompt).strip('"').strip()
        if os.path.exists(path):
            return path
        print("❌ Invalid path. Try again.\n")


def unzip_files(source_path, destination_path):
    zip_files = [f for f in os.listdir(source_path) if f.lower().endswith(".zip")]

    if not zip_files:
        print("❌ No ZIP files found!")
        return

    output_root = os.path.join(destination_path, "unzipped")
    os.makedirs(output_root, exist_ok=True)

    print(f"\n📂 Output Folder: {output_root}")

    total_start = time.time()
    total_files = len(zip_files)

    for idx, zip_name in enumerate(zip_files, start=1):
        zip_start = time.time()

        zip_path = os.path.join(source_path, zip_name)

        # ✅ Limit length (important for safety)
        folder_name = os.path.splitext(zip_name)[0][:50]

        extract_folder = os.path.join(output_root, folder_name)

        extract_folder_safe = safe_path(extract_folder)

        print(f"\n📦 [{idx}/{total_files}] Processing: {zip_name}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                members = zip_ref.infolist()

                with tqdm(total=len(members), desc="Extracting", unit="file") as pbar:

                    for member in members:
                        member_path = os.path.normpath(member.filename)

                        # ✅ Skip unsafe paths
                        if ".." in member_path or member_path.startswith(("/", "\\")):
                            continue

                        target_path = os.path.join(extract_folder, member_path)
                        target_path_safe = safe_path(target_path)

                        if member.is_dir():
                            os.makedirs(target_path_safe, exist_ok=True)
                        else:
                            os.makedirs(os.path.dirname(target_path_safe), exist_ok=True)

                            with zip_ref.open(member) as source, open(target_path_safe, "wb") as target:
                                target.write(source.read())

                        pbar.update(1)

        except Exception as e:
            print(f"❌ Failed: {zip_name}")
            print(f"   Reason: {e}")
            continue

        # ✅ Timing
        zip_time = time.time() - zip_start
        avg_time = (time.time() - total_start) / idx
        remaining = avg_time * (total_files - idx)

        print(f"✅ Done in {zip_time:.2f}s | ⏳ Remaining: {remaining:.2f}s")

    total_time = time.time() - total_start

    print("\n" + "=" * 50)
    print(f"🎉 ALL DONE in {total_time:.2f} seconds")
    print("=" * 50)


def main():
    print("=" * 60)
    print("📦 ENTERPRISE BULK ZIP EXTRACTION TOOL")
    print("=" * 60)

    source_path = get_valid_path(
        "\n👉 Enter SOURCE folder (ZIP files location): "
    )

    destination_path = get_valid_path(
        "👉 Enter DESTINATION folder: "
    )

    unzip_files(source_path, destination_path)


if __name__ == "__main__":
    main()