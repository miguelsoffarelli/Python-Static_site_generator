import unittest

from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://google.com", "target": "_blank"})
        assert node.props_to_html() == ' href="https://google.com" target="_blank"'

    def test_empty_props_to_html(self):
        node = HTMLNode(props=None)
        assert node.props_to_html() == ""

    def test_special_char_props(self):
        node = HTMLNode(props={"data-test": "value with spaces", "class": "item-1"})
        assert ' data-test="value with spaces"' in node.props_to_html()
        assert ' class="item-1"' in node.props_to_html()

    def test_node_creation(self):
        node1 = HTMLNode(tag="div")
        assert node1.tag == "div"
        assert node1.value is None

        node2 = HTMLNode(tag="p", value="Hello")
        assert node2.tag == "p"
        assert node2.value == "Hello"

        child = HTMLNode(tag="span", value="Child")
        node3 = HTMLNode(tag="div", children=[child])
        assert node3.children[0].tag == "span"

    def test_repr(self):
        node = HTMLNode(tag="a", value="Click me", props={"href": "#"})
        repr_str = repr(node)
        assert "tag=a" in repr_str
        assert "value=Click me" in repr_str
        assert "href" in repr_str

    def test_no_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_repr_contains_all_attributes(self):
        node = HTMLNode(tag="div", value="content", children=[], props={"class": "container"})
        repr_str = repr(node)
        self.assertTrue("tag=div" in repr_str)
        self.assertTrue("value=content" in repr_str)
        self.assertTrue("children=[]" in repr_str)
        self.assertTrue("props={'class': 'container'}" in repr_str or "props={\'class\': \'container\'}" in repr_str)