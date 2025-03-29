import unittest

from blockfunctions import markdown_to_blocks, BlockType, block_to_block_type

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_multiple_newlines(self):
        md = """
    This is a **paragraph**


    This is another paragraph that's more than one line below   
       
    This is another paragraph and the line below contains whitespaces  
    And this is another line of the same paragraph
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is a **paragraph**",
                "This is another paragraph that's more than one line below",
                "This is another paragraph and the line below contains whitespaces\nAnd this is another line of the same paragraph"
            ]
        )
        
    def test_empty_input(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_single_block(self):
        md = "Just one block with no newlines"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just one block with no newlines"])

    def test_only_whitespace(self):
        md = "   \n   \n   \n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_block(self):
        block = """# This block is a heading.
This is another line of the same heading block.

And this too.
"""
        self.assertEqual(BlockType.HEADING, block_to_block_type(block))

    def test_code_block(self):
        block = """```This is a code block.      It has spaces in the middle.
        
        And empty lines too```"""
        self.assertEqual(BlockType.CODE, block_to_block_type(block))

    def test_quote_block(self):
        block = """>This block has quotes
        >Another quote
        >And another"""
        self.assertEqual(BlockType.QUOTE, block_to_block_type(block))

    def test_ul_block(self):
        block = """- This
        - is
        - an
        - unordered
        - list"""
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type(block))

    def test_ol_block(self):
        block = """1. This
        2. is
        3. an
        4. ordered
        5. list"""
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(block))

    def test_paragraph_block(self):
        block = """Just a paragraph"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_empty_block(self):
        empty_block = ""
        whitespaces_block = "    "
        empty_lines_block = "\n \n   \n "
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(empty_block))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(whitespaces_block))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(empty_lines_block))

    def test_mixed_block(self):
        block = """# This block is a heading
        - and it shouldn't be confused with an unordered list
        >or a quote"""
        self.assertEqual(BlockType.HEADING, block_to_block_type(block))

    def test_not_an_unordered_list(self):
        block = "- This block only has one line so it shouldn't be considered a list of any kind"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_max_heading(self):
        block = "###### This is a heading with six #s"
        self.assertEqual(BlockType.HEADING, block_to_block_type(block))

    def test_max_plus_one_heading(self):
        block = "####### This shoudn't be a heading because it has too many #s"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_malformed_blocks(self):
        malformed_code = "```This code block doesn't have closing backticks"
        malformed_heading = "#This heading doesn't have a space after the delimiter"
        malformed_quote = """>This is a quote
        But this isn't"""
        malformed_ul1 = """- This unordered list
        is missing
        - a hyphen"""
        malformed_ul2 = """-This ordered list
        -is missing the spaces after the delimiters"""
        malformed_ol1 = """1. This ordered list
        3. Is missing the number 2"""
        malformed_ol2 = """1.This ordered list
        2.Is missing the spaces after the delimiters"""
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_code))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_heading))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_quote))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_ul1))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_ul2))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_ol1))
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(malformed_ol2))

    def test_irregular_blocks(self):
        block1 = "     # This heading block has whitespaces before it's markers"
        block2 = """


## This heading block has empty lines before it's markeres"""
        self.assertEqual(BlockType.HEADING, block_to_block_type(block1))
        self.assertEqual(BlockType.HEADING, block_to_block_type(block2))
