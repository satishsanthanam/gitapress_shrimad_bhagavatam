import json
import os
import unittest
from align_direct_md import parse_aligned_markdown


class TestAlignedMarkdownPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run the direct Markdown parser before running tests."""
        parse_aligned_markdown("markdown_aligned.md")

    def test_json_files_exist(self):
        """Verify all 6 chapter JSON files exist in mahatmya_json/."""
        for ch in range(1, 7):
            path = f"mahatmya_json/mahatmya_ch{ch:02d}.json"
            self.assertTrue(os.path.exists(path), f"Missing output file: {path}")

    def test_chapter_1_ranges(self):
        """Verify Chapter 1 verse range boundaries and colophon stripping."""
        with open("mahatmya_json/mahatmya_ch01.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check multi-verse block 4-8
        block_4_8 = next(item for item in data if item["verse_number"] == 4)
        self.assertEqual(block_4_8["verse_range"], "4-8")

        # Check final block 79-80 (verifying colophon ॥ १॥ is not picked as end range)
        last_block = data[-1]
        self.assertEqual(last_block["verse_number"], 79)
        self.assertEqual(last_block["verse_range"], "79-80")

    def test_chapter_3_ranges(self):
        """Verify Chapter 3 final block range calculation."""
        with open("mahatmya_json/mahatmya_ch03.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        last_block = data[-1]
        self.assertEqual(last_block["verse_number"], 73)
        self.assertEqual(last_block["verse_range"], "73-74")

    def test_chapter_5_ranges(self):
        """Verify Chapter 5 final block range calculation."""
        with open("mahatmya_json/mahatmya_ch05.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        last_block = data[-1]
        self.assertEqual(last_block["verse_number"], 87)
        self.assertEqual(last_block["verse_range"], "87-90")

    def test_chapter_6_ranges(self):
        """Verify Chapter 6 final block range calculation."""
        with open("mahatmya_json/mahatmya_ch06.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        last_block = data[-1]
        self.assertEqual(last_block["verse_number"], 98)
        self.assertEqual(last_block["verse_range"], "98-103")


if __name__ == "__main__":
    unittest.main()