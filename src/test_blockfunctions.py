import unittest

from blockfunctions import markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node, extract_title

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


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = """
    # Heading 1

    ## Heading 2

    ### Heading 3 with **bold**

    #### Heading 4

    ##### Heading 5

    ###### Heading 6

    Not a heading # with hash in the middle
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3 with <b>bold</b></h3><h4>Heading 4</h4><h5>Heading 5</h5><h6>Heading 6</h6><p>Not a heading # with hash in the middle</p></div>",
        )

    def test_lists(self):
        md = """
    - Item 1
    - Item 2
    - Item 3

    1. First
    2. Second
    3. Third
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul><ol><li>First</li><li>Second</li><li>Third</li></ol></div>",
        )

    def test_blockquote(self):
        md = """
    > This is a quote
    > with multiple lines
    > and **bold** text
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote with multiple lines and <b>bold</b> text</blockquote></div>",
        )

    def test_mixed_content(self):
        md = """
    # Main Title

    This is a paragraph with **bold** and _italic_ text.

    > Important quote here

    - List item 1
    - List item 2 with `code`
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Main Title</h1><p>This is a paragraph with <b>bold</b> and <i>italic</i> text.</p><blockquote>Important quote here</blockquote><ul><li>List item 1</li><li>List item 2 with <code>code</code></li></ul></div>",
        )

    def test_complex_code_block(self):
        md = """
    Here's a sample code:

    ```def hello_world():
        print("Hello, **not bold**!")
        # Comments _not italic_
        return None```


    End of example
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>Here's a sample code:</p><pre><code>def hello_world():\nprint(\"Hello, **not bold**!\")\n# Comments _not italic_\nreturn None</code></pre><p>End of example</p></div>",
        )

    def test_empty_lines(self):
        md = """

    # Title with empty line above


    Paragraph with empty lines around

    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Title with empty line above</h1><p>Paragraph with empty lines around</p></div>",
        )

    def test_emtpy_block(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_whitespace_block(self):
        md = " "
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_only_newlines_block(self):
        md = """



"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")


class TestExtractTitle(unittest.TestCase):
    def test_extract_title(self):
        md = """# This is markdown with a valid title.
        
        And this is just a paragraph."""

        self.assertEqual(extract_title(md), "This is markdown with a valid title.")

    def test_multiple_headings(self):
        md = """# This is a valid title heading.
        ### This is also a valid heading but not a title.
        ##### This is another not-title-heading."""

        self.assertEqual(extract_title(md), "This is a valid title heading.")

    def test_invalid_heading(self):
        md = "#This is an invalid header because it's missing the space after the '#'"
        with self.assertRaises(Exception):
            extract_title(md)

    def test_empty_md(self):
        md = ""
        with self.assertRaises(Exception):
            extract_title(md)

    def test_lower_level_header(self):
        md = "## This is a valid header but not a title"
        with self.assertRaises(Exception):
            extract_title(md)

    def test_title_with_nested_nodes(self):
        md = "# This is a valid title with **bold**, _italics_ and ```code``` inside."
        self.assertEqual(extract_title(md), "This is a valid title with bold, italics and code inside.")


if __name__ == "__main__":
    unittest.main()
