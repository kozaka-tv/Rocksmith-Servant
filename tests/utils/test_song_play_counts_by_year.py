import runpy
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "utils"
    / "song_play_counts_by_year.py"
)


def test_song_play_counts_by_year(tmp_path, monkeypatch):
    setlist_dir = tmp_path / "setlist"
    output_dir = tmp_path / "statistics" / "song_count_by_year"
    working_dir = tmp_path / "work"

    setlist_dir.mkdir()
    working_dir.mkdir()

    (setlist_dir / "setlist_2025-01-01.txt").write_text(
        "Artist A - Song One\n"
        "Artist A - Song One\n"
        "Artist B - Song Two\n",
        encoding="utf-8",
    )

    (setlist_dir / "setlist_2026-01-01.txt").write_text(
        "Artist C - Song Three\n",
        encoding="utf-8",
    )

    # Run the script with temporary setlist and output directories.
    monkeypatch.chdir(working_dir)
    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

    stats_2025 = (output_dir / "song_count_2025.txt").read_text(
        encoding="utf-8"
    )
    stats_2026 = (output_dir / "song_count_2026.txt").read_text(
        encoding="utf-8"
    )

    assert "Year: 2025" in stats_2025
    assert "Total songs played: 3" in stats_2025
    assert "Distinct songs played: 2" in stats_2025
    assert "Distinct artists appeared: 2" in stats_2025
    assert "2 | Artist A - Song One" in stats_2025

    assert "Year: 2026" in stats_2026
    assert "Total songs played: 1" in stats_2026
    assert "Distinct songs played: 1" in stats_2026
