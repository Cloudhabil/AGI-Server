"""
Substrate Compressor: ZIP-Based Metabolic Optimization

Converts the "naked" filesystem into compressed substrates to reduce:
- Memory footprint (fewer open file descriptors)
- I/O pressure (single ZIP index vs recursive scans)
- Inode exhaustion (468 files → 1 archive)

Architecture:
- SKILL_SYNTHESIZED → skills_v1.1.zip (read-only library)
- DATA_LEDGER → ledger_archive.zip (fossil records)
- EXPERIMENT_ACTIVE → remains naked (active metabolism)

Uses Python's zipimport for zero-friction integration.
"""

import zipfile
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import shutil


class SubstrateCompressor:
    """
    Compresses filesystem categories into ZIP substrates.
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self.archives_dir = self.root / "data" / "archives"
        self.archives_dir.mkdir(parents=True, exist_ok=True)

        # Compression manifest
        self.manifest_path = self.archives_dir / "compression_manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load or create compression manifest"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {
            "version": "1.1",
            "created": datetime.now().isoformat(),
            "archives": {}
        }

    def _save_manifest(self):
        """Save compression manifest"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def compress_skills_synthesized(self, version: str = "1.1") -> Path:
        """
        Compress skills/synthesized/ into skills_v{version}.zip

        Returns:
            Path to created archive
        """
        source_dir = self.root / "skills" / "synthesized"
        if not source_dir.exists():
            print(f"[COMPRESSOR] Source directory not found: {source_dir}")
            return None

        archive_name = f"skills_v{version}.zip"
        archive_path = self.archives_dir / archive_name

        print(f"[COMPRESSOR] Compressing SKILL_SYNTHESIZED...")
        print(f"  Source: {source_dir}")
        print(f"  Archive: {archive_path}")

        # Count files
        py_files = list(source_dir.glob("*.py"))
        print(f"  Files to compress: {len(py_files)}")

        if len(py_files) == 0:
            print("[COMPRESSOR] No files to compress")
            return None

        # Create ZIP archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add __init__.py to make it a package
            init_content = f'''"""
SKILL_SYNTHESIZED Archive v{version}
Compressed substrate containing {len(py_files)} synthesized skills.

This archive is directly importable via zipimport.
Usage:
    import sys
    sys.path.insert(0, 'data/archives/{archive_name}')
    from snowden_* import *
"""
__version__ = "{version}"
__compressed_at__ = "{datetime.now().isoformat()}"
__file_count__ = {len(py_files)}
'''
            zf.writestr("__init__.py", init_content)

            # Add all Python files
            for py_file in py_files:
                arcname = py_file.name
                zf.write(py_file, arcname)
                print(f"    + {arcname}")

        # Record in manifest
        self.manifest["archives"]["skills_synthesized"] = {
            "version": version,
            "path": str(archive_path.relative_to(self.root)),
            "file_count": len(py_files),
            "compressed_at": datetime.now().isoformat(),
            "original_size_mb": sum(f.stat().st_size for f in py_files) / 1024 / 1024,
            "compressed_size_mb": archive_path.stat().st_size / 1024 / 1024
        }
        self._save_manifest()

        original_mb = self.manifest["archives"]["skills_synthesized"]["original_size_mb"]
        compressed_mb = self.manifest["archives"]["skills_synthesized"]["compressed_size_mb"]
        ratio = (1 - compressed_mb / original_mb) * 100

        print(f"\n[COMPRESSOR] Compression complete:")
        print(f"  Original: {original_mb:.2f} MB")
        print(f"  Compressed: {compressed_mb:.2f} MB")
        print(f"  Savings: {ratio:.1f}%")

        return archive_path

    def compress_ledger_archive(self, keep_recent_days: int = 7) -> Path:
        """
        Compress historical DATA_LEDGER entries into ledger_archive.zip

        Args:
            keep_recent_days: Keep last N days as naked files

        Returns:
            Path to created archive
        """
        ledger_dir = self.root / "data" / "ledger"
        if not ledger_dir.exists():
            print(f"[COMPRESSOR] Ledger directory not found: {ledger_dir}")
            return None

        archive_path = self.archives_dir / "ledger_archive.zip"

        print(f"[COMPRESSOR] Compressing DATA_LEDGER (keeping recent {keep_recent_days} days)...")

        # Find ledger files older than threshold
        import time
        threshold = time.time() - (keep_recent_days * 24 * 60 * 60)

        old_files = [
            f for f in ledger_dir.glob("*.jsonl")
            if f.stat().st_mtime < threshold
        ]

        if len(old_files) == 0:
            print("[COMPRESSOR] No old ledger files to archive")
            return None

        print(f"  Files to archive: {len(old_files)}")

        # Create ZIP archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for ledger_file in old_files:
                arcname = ledger_file.name
                zf.write(ledger_file, arcname)
                print(f"    + {arcname}")

        # Record in manifest
        self.manifest["archives"]["ledger_archive"] = {
            "path": str(archive_path.relative_to(self.root)),
            "file_count": len(old_files),
            "compressed_at": datetime.now().isoformat(),
            "keep_recent_days": keep_recent_days,
            "compressed_size_mb": archive_path.stat().st_size / 1024 / 1024
        }
        self._save_manifest()

        print(f"\n[COMPRESSOR] Ledger archive complete:")
        print(f"  Archived: {len(old_files)} files")
        print(f"  Size: {self.manifest['archives']['ledger_archive']['compressed_size_mb']:.2f} MB")

        return archive_path

    def verify_archive(self, archive_path: Path) -> bool:
        """Verify ZIP archive integrity"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # Test archive integrity
                bad_file = zf.testzip()
                if bad_file is not None:
                    print(f"[COMPRESSOR] Corrupt file in archive: {bad_file}")
                    return False

                # List contents
                file_count = len(zf.namelist())
                print(f"[COMPRESSOR] Archive verified: {file_count} files")
                return True

        except Exception as e:
            print(f"[COMPRESSOR] Archive verification failed: {e}")
            return False

    def remove_compressed_originals(self, archive_type: str, backup: bool = True):
        """
        Remove original files after successful compression.

        Args:
            archive_type: 'skills_synthesized' or 'ledger_archive'
            backup: Create backup before deletion
        """
        if archive_type not in self.manifest["archives"]:
            print(f"[COMPRESSOR] No archive found for {archive_type}")
            return

        archive_info = self.manifest["archives"][archive_type]
        archive_path = self.root / archive_info["path"]

        # Verify archive first
        if not self.verify_archive(archive_path):
            print("[COMPRESSOR] Archive verification failed - aborting cleanup")
            return

        # Determine source directory
        if archive_type == "skills_synthesized":
            source_dir = self.root / "skills" / "synthesized"
        elif archive_type == "ledger_archive":
            source_dir = self.root / "data" / "ledger"
        else:
            print(f"[COMPRESSOR] Unknown archive type: {archive_type}")
            return

        # Create backup if requested
        if backup:
            backup_dir = self.archives_dir / f"{archive_type}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"[COMPRESSOR] Creating backup: {backup_dir}")
            shutil.copytree(source_dir, backup_dir)

        # Remove original files
        py_files = list(source_dir.glob("*.py"))
        print(f"[COMPRESSOR] Removing {len(py_files)} original files...")

        for f in py_files:
            f.unlink()
            print(f"    - {f.name}")

        print(f"[COMPRESSOR] Cleanup complete. Archive: {archive_path}")

    def get_stats(self) -> Dict:
        """Get compression statistics"""
        stats = {
            "total_archives": len(self.manifest["archives"]),
            "total_compressed_mb": 0,
            "total_savings_mb": 0,
            "archives": {}
        }

        for name, info in self.manifest["archives"].items():
            compressed_mb = info.get("compressed_size_mb", 0)
            original_mb = info.get("original_size_mb", compressed_mb)

            stats["total_compressed_mb"] += compressed_mb
            stats["total_savings_mb"] += (original_mb - compressed_mb)

            stats["archives"][name] = {
                "files": info.get("file_count", 0),
                "compressed_mb": compressed_mb,
                "savings_mb": original_mb - compressed_mb
            }

        return stats


def compress_substrate(root: Path = None, dry_run: bool = False):
    """
    Main compression workflow.

    Args:
        root: Repository root
        dry_run: If True, only report what would be compressed
    """
    if root is None:
        root = Path.cwd()

    print("=" * 80)
    print("SUBSTRATE COMPRESSOR - Metabolic Optimization")
    print("=" * 80)
    print()

    compressor = SubstrateCompressor(root)

    if dry_run:
        print("[DRY RUN] No files will be modified\n")

    # 1. Compress SKILL_SYNTHESIZED
    print("[1] Compressing SKILL_SYNTHESIZED...")
    if not dry_run:
        archive = compressor.compress_skills_synthesized()
        if archive:
            print(f"    Archive created: {archive}")

    # 2. Compress historical ledger (keep last 7 days)
    print("\n[2] Compressing historical DATA_LEDGER...")
    if not dry_run:
        archive = compressor.compress_ledger_archive(keep_recent_days=7)
        if archive:
            print(f"    Archive created: {archive}")

    # 3. Show statistics
    print("\n[3] Compression Statistics:")
    print("-" * 80)
    stats = compressor.get_stats()
    print(f"  Total archives: {stats['total_archives']}")
    print(f"  Total compressed: {stats['total_compressed_mb']:.2f} MB")
    print(f"  Total savings: {stats['total_savings_mb']:.2f} MB")

    for name, info in stats["archives"].items():
        print(f"\n  {name}:")
        print(f"    Files: {info['files']}")
        print(f"    Size: {info['compressed_mb']:.2f} MB")
        print(f"    Saved: {info['savings_mb']:.2f} MB")

    print("\n" + "=" * 80)
    print("Compression complete. Verify archives before removing originals.")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    compress_substrate(dry_run=dry_run)
