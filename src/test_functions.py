import unittest

from functions import text_node_to_html_node, split_nodes_delimiter
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode

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


if __name__ == "__main__":
    unittest.main()