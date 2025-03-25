import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_text(self):
        node = TextNode("Hello", TextType.BOLD)
        self.assertEqual(node.text, "Hello")

    def test_type(self):
        node = TextNode("Hello", TextType.ITALIC)
        self.assertEqual(node.text_type, TextType.ITALIC)

    def test_url(self):
        node = TextNode("Hello", TextType.LINK, "https://some.url")
        self.assertEqual(node.url, "https://some.url")

    def test_different_text(self):
        node1 = TextNode("First text", TextType.BOLD)
        node2 = TextNode("Second text", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_different_type(self):
        node1 = TextNode("Hello", TextType.NORMAL)
        node2 = TextNode("Hello", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_different_url(self):
        node1 = TextNode("Hello", TextType.NORMAL, "https://first.url")
        node2 = TextNode("Hello", TextType.NORMAL, "https://second.url")
        self.assertNotEqual(node1, node2)

    def test_url_or_not(self):
        node1 = TextNode("Hello", TextType.LINK, "https://thisonehas.url")
        node2 = TextNode("Hello", TextType.LINK)
        self.assertNotEqual(node1, node2)

    def test_eq_url(self):
        node1 = TextNode("Hello", TextType.CODE, "https://the.url")
        node2 = TextNode("Hello", TextType.CODE, "https://the.url")
        self.assertEqual(node1, node2)

    def test_nonetype_url(self):
        node1 = TextNode("Hello", TextType.IMAGE, None)
        node2 = TextNode("Hello", TextType.IMAGE)
        self.assertEqual(node1, node2)

    def test_nonetype_url_or_url(self):
        node1 = TextNode("Hello", TextType.NORMAL, None)
        node2 = TextNode("Hello", TextType.NORMAL, "https://some.url")
        self.assertNotEqual(node1, node2)

    def test_default_url(self):
        node = TextNode("Hello", TextType.BOLD)
        self.assertIsNone(node.url)


if __name__ == "__main__":
    unittest.main()