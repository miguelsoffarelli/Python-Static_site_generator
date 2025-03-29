import unittest

from functions import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes,markdown_to_blocks
from textnode import TextNode, TextType


class TestTextToHTML(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.NORMAL)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold text")
        self.assertEqual(html_node.props, None)

    def test_italic(self):
        node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic text")
        self.assertEqual(html_node.props, None)

    def test_code(self):
        node = TextNode("print('Hello World')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello World')")
        self.assertEqual(html_node.props, None)

    def test_link(self):
        node = TextNode("Click me", TextType.LINK, "https://boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click me")
        self.assertEqual(html_node.props, {"href": "https://boot.dev"})

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")  # Empty string for image value
        self.assertEqual(html_node.props, {
            "src": "https://example.com/image.png",
            "alt": "Alt text"
        })

    def test_invalid_text_type(self):
        invalid_type = "not_a_valid_type"
        node = TextNode("Some text", invalid_type)
        with self.assertRaises(Exception):
            text_node_to_html_node(node)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter_basic(self):
        node = TextNode("This is text with a `code block` word", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        assert len(new_nodes) == 3
        assert new_nodes[0].text == "This is text with a "
        assert new_nodes[0].text_type == TextType.NORMAL
        assert new_nodes[1].text == "code block"
        assert new_nodes[1].text_type == TextType.CODE
        assert new_nodes[2].text == " word"
        assert new_nodes[2].text_type == TextType.NORMAL

    def test_split_nodes_delimiter_multiple(self):
        node = TextNode("This has **bold** and `code` text", TextType.NORMAL)
        # First split by bold
        intermediate_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        # Then split the result by code
        new_nodes = split_nodes_delimiter(intermediate_nodes, "`", TextType.CODE)
        assert len(new_nodes) == 5  # Should be 5 nodes total

    def test_split_nodes_without_delimiter(self):
        node = TextNode("Plain text with no delimiters", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        assert len(new_nodes) == 1
        assert new_nodes[0].text == "Plain text with no delimiters"
        assert new_nodes[0].text_type == TextType.NORMAL

    def test_split_with_bold_delimiter(self):
        # Test basic bold delimiter case
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[1].text, "bolded phrase")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, " in the middle")
        self.assertEqual(new_nodes[2].text_type, TextType.NORMAL)
    
    def test_split_with_code_delimiter(self):
        # Test code delimiter
        node = TextNode("This is text with a `code block` word", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " word")

    def test_split_with_italic_delimiter(self):
        # Test italic delimiter
        node = TextNode("This is text with an _italicized phrase_ in the middle", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with an ")
        self.assertEqual(new_nodes[1].text, "italicized phrase")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(new_nodes[2].text, " in the middle")
    
    def test_multiple_delimiter_pairs(self):
        # Test multiple delimiter pairs in one text
        node = TextNode("**Bold** normal **more bold**", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[0].text, "Bold")
        self.assertEqual(new_nodes[1].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[1].text, " normal ")
        self.assertEqual(new_nodes[2].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, "more bold")

    def test_missing_closing_delimiter(self):
        # Test missing closing delimiter (should raise exception)
        node = TextNode("This text has **unclosed bold", TextType.NORMAL)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)
    
    def test_empty_content_within_delimiters(self):
        # Test empty content between delimiters
        node = TextNode("This has an **** empty bold", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This has an ")
        self.assertEqual(new_nodes[1].text, "")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, " empty bold")

    def test_consecutive_delimiters(self):
        # Test consecutive delimiter pairs
        node = TextNode("**Bold**_italic_", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Bold")
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[1].text, "italic")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)
    
    def test_mixed_node_types(self):
        # Test with a mix of text and non-text nodes
        text_node = TextNode("This has **bold**", TextType.NORMAL)
        bold_node = TextNode("Already Bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([text_node, bold_node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This has ")
        self.assertEqual(new_nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[1].text, "bold")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, "Already Bold")
        self.assertEqual(new_nodes[2].text_type, TextType.BOLD)

    def test_delimiter_at_beginning(self):
        # Test delimiter at the beginning of text
        node = TextNode("**Bold** text", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Bold")
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[1].text, " text")
        self.assertEqual(new_nodes[1].text_type, TextType.NORMAL)
    
    def test_delimiter_at_end(self):
        # Test delimiter at the end of text
        node = TextNode("Some **Bold**", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Some ")
        self.assertEqual(new_nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[1].text, "Bold")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        matches = extract_markdown_images("This is text with ![image one](https://i.imgur.com/zjjcJKZ.png) and ![image two](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("image one", "https://i.imgur.com/zjjcJKZ.png"), ("image two", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_no_images(self):
        matches = extract_markdown_images("This is a text with no images")
        self.assertListEqual([], matches)

    def test_wrong_syntax_images(self):
        no_closing_parenthesis = extract_markdown_images("This is a text with an ![image](https://i.imgur.com/zjjcJKZ.png without closing parenthesis")
        link_only = extract_markdown_images("This is a text with just a link (https://i.imgur.com/zjjcJKZ.png)")
        no_link = extract_markdown_images("This is a text with an ![image] with no link")
        no_exclamation_mark = extract_markdown_images("This is a text with an [image](https://i.imgur.com/zjjcJKZ.png) without exclamation mark")
        no_opening_square_bracket = extract_markdown_images("This is a text with an !image](https://i.imgur.com/zjjcJKZ.png) with no openin square bracket")
        self.assertListEqual([], no_closing_parenthesis)
        self.assertListEqual([], link_only)
        self.assertListEqual([], no_link)
        self.assertListEqual([], no_exclamation_mark)
        self.assertListEqual([], no_opening_square_bracket)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        matches = extract_markdown_links("This is a text with a link [to google](www.google.com)")
        self.assertListEqual([("to google", "www.google.com")], matches)

    def test_multiple_links(self):
        matches = extract_markdown_links("This is a text with links [to youtube](www.youtube.com) and [to netflix](www.netflix.com)")
        self.assertListEqual([("to youtube", "www.youtube.com"), ("to netflix", "www.netflix.com")], matches)

    def test_no_links(self):
        matches = extract_markdown_links("This is a text with no links")
        self.assertListEqual([], matches)

    def test_wrong_syntax_links(self):
        no_closing_parenthesis = extract_markdown_links("This is a text with a [link](www.google.com with no closing parenthesis")
        link_only = extract_markdown_links("This is a link with no anchor text (www.google.com)")
        no_link = extract_markdown_links("This is a text with just an [anchor text]")
        no_closing_square_bracket = extract_markdown_links("This is a text with a [link(www.google.com) with no closing square bracket")
        self.assertListEqual([], no_closing_parenthesis)
        self.assertListEqual([], link_only)
        self.assertListEqual([], no_link)
        self.assertListEqual([], no_closing_square_bracket)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_nodes_image_no_images(self):
        node = TextNode(
            "This is text with no images",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [node],
            new_nodes,
        )

    def test_split_nodes_image_at_beginning(self):
        node = TextNode(
            "![first image](https://example.com/first.jpg) followed by text",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first image", TextType.IMAGE, "https://example.com/first.jpg"),
                TextNode(" followed by text", TextType.NORMAL)
            ],
            new_nodes,
        )

    def test_split_nodes_image_at_end(self):
        node = TextNode(
            "This is text followed by ![last image](https://example.com/last.jpg)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text followed by ", TextType.NORMAL),
                TextNode("last image", TextType.IMAGE, "https://example.com/last.jpg"),
            ],
            new_nodes,
        )

    def test_split_nodes_image_multiple_nodes(self):
        node1 = TextNode(
            "This is text with an ![image](https://example.com/1.jpg)",
            TextType.NORMAL,
        )
        node2 = TextNode(
            "This is more text with ![another image](https://example.com/2.jpg)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node1, node2])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://example.com/1.jpg"),
                TextNode("This is more text with ", TextType.NORMAL),
                TextNode("another image", TextType.IMAGE, "https://example.com/2.jpg"),
            ],
            new_nodes,
        )

    def test_split_nodes_image_empty_text(self):
        node = TextNode("", TextType.NORMAL)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [],  # Should return an empty list for an empty node
            new_nodes,
        )

    def test_split_nodes_image_only(self):
        node = TextNode(
            "![standalone image](https://example.com/standalone.jpg)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("standalone image", TextType.IMAGE, "https://example.com/standalone.jpg"),
            ],
            new_nodes,
        )

    def test_split_nodes_image_adjacent(self):
        node = TextNode(
            "![first](https://example.com/first.jpg)![second](https://example.com/second.jpg)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.IMAGE, "https://example.com/first.jpg"),
                TextNode("second", TextType.IMAGE, "https://example.com/second.jpg"),
            ],
            new_nodes,
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_nodes_link_basic(self):
        node = TextNode(
            "This is text with a [link](https://example.com)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_multiple(self):
        node = TextNode(
            "This is a [first link](https://example.com/1) and a [second link](https://example.com/2)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is a ", TextType.NORMAL),
                TextNode("first link", TextType.LINK, "https://example.com/1"),
                TextNode(" and a ", TextType.NORMAL),
                TextNode("second link", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_no_links(self):
        node = TextNode(
            "This is text with no links",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [node],  
            new_nodes,
        )

    def test_split_nodes_link_at_beginning(self):
        node = TextNode(
            "[first link](https://example.com/first) followed by text",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first link", TextType.LINK, "https://example.com/first"),
                TextNode(" followed by text", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_nodes_link_at_end(self):
        node = TextNode(
            "This is text followed by [last link](https://example.com/last)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text followed by ", TextType.NORMAL),
                TextNode("last link", TextType.LINK, "https://example.com/last"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_multiple_nodes(self):
        node1 = TextNode(
            "This is text with a [link](https://example.com/1)",
            TextType.NORMAL,
        )
        node2 = TextNode(
            "This is more text with [another link](https://example.com/2)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node1, node2])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://example.com/1"),
                TextNode("This is more text with ", TextType.NORMAL),
                TextNode("another link", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_empty_text(self):
        node = TextNode("", TextType.NORMAL)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [],  # Should return an empty list for an empty node
            new_nodes,
        )

    def test_split_nodes_link_only(self):
        node = TextNode(
            "[standalone link](https://example.com/standalone)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("standalone link", TextType.LINK, "https://example.com/standalone"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_adjacent(self):
        node = TextNode(
            "[first](https://example.com/first)[second](https://example.com/second)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.LINK, "https://example.com/first"),
                TextNode("second", TextType.LINK, "https://example.com/second"),
            ],
            new_nodes,
        )

    def test_split_nodes_link_different_text_types(self):
        node1 = TextNode(
            "This is [bold link](https://example.com/bold)",
            TextType.BOLD,
        )
        node2 = TextNode(
            "This is [italic link](https://example.com/italic)",
            TextType.ITALIC,
        )
        new_nodes = split_nodes_link([node1, node2])
        self.assertListEqual(
            [
                TextNode("This is ", TextType.BOLD),
                TextNode("bold link", TextType.LINK, "https://example.com/bold"),
                TextNode("This is ", TextType.ITALIC),
                TextNode("italic link", TextType.LINK, "https://example.com/italic"),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_all_node_types(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        result = text_to_textnodes(text)
        self.assertEqual(
            [
                TextNode("This is ", TextType.NORMAL),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.NORMAL),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.NORMAL),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.NORMAL),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        result)

    def test_plain_text(self):
        text = "This is just plain text without bold, italic, code, links or images"
        result = text_to_textnodes(text)
        self.assertEqual([TextNode("This is just plain text without bold, italic, code, links or images", TextType.NORMAL)], result)

    def test_lone_node_type(self):
        bold = "**This is fully bold text**"
        italic = "_This is all italic text_"
        code = "`This is only code text`"
        link = "[this is only a link](www.google.com)"
        image = "![image only](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual([TextNode("This is fully bold text", TextType.BOLD)], text_to_textnodes(bold))
        self.assertEqual([TextNode("This is all italic text", TextType.ITALIC)], text_to_textnodes(italic))
        self.assertEqual([TextNode("This is only code text", TextType.CODE)], text_to_textnodes(code))
        self.assertEqual([TextNode("this is only a link", TextType.LINK, "www.google.com")], text_to_textnodes(link))
        self.assertEqual([TextNode("image only", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg")], text_to_textnodes(image))

    def test_boundaries(self):
        bold = "**Bold text** in thee beggingin... in thee... inni thi binningee... in... in the beninging..."
        link = "This text ends with [a link](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        result_bold = text_to_textnodes(bold)
        result_link = text_to_textnodes(link)
        self.assertEqual([
            TextNode("Bold text", TextType.BOLD),
            TextNode(" in thee beggingin... in thee... inni thi binningee... in... in the beninging...", TextType.NORMAL)
            ],
            result_bold)
        self.assertEqual([
            TextNode("This text ends with ", TextType.NORMAL),
            TextNode("a link", TextType.LINK, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        ],
        result_link)

    def test_empty_text(self):
        text = ""
        result = text_to_textnodes(text)
        self.assertEqual([], result)

    def test_empty_delimiters(self):
        text = "**** _ _"
        result = text_to_textnodes(text)
        self.assertEqual([TextNode("", TextType.BOLD), TextNode(" ", TextType.NORMAL), TextNode(" ", TextType.ITALIC)], result)

    def test_wrong_delimiters(self):
        text1 = "**I forgot to close the delimiter"
        text2 = "I forgot to open the delimiter_"
        text3 = "![this image](www.doesnthavetheclosingparenthesis.com"

        with self.assertRaises(Exception) as context1:
            text_to_textnodes(text1)
        self.assertEqual(str(context1.exception), "Closing delimiter ** not found")

        with self.assertRaises(Exception) as context2:
            text_to_textnodes(text2)
        self.assertEqual(str(context2.exception), "Closing delimiter _ not found")

        no_url_parenthesis = text_to_textnodes(text3)
        self.assertEqual(
            no_url_parenthesis,
            [TextNode("![this image](www.doesnthavetheclosingparenthesis.com", TextType.NORMAL)],
        )


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




if __name__ == "__main__":
    unittest.main()