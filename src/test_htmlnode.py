import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

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


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://example.com", "class": "button"})
        self.assertIn('href="https://example.com"', node.to_html())
        self.assertIn('class="button"', node.to_html())
        self.assertIn(">Click me!<", node.to_html())

    def test_leaf_no_tag(self):
        node = LeafNode(None, "Just plain text")
        self.assertEqual(node.to_html(), "Just plain text")

    def test_leaf_empty_value(self):
        with self.assertRaises(ValueError):
            node = LeafNode("p", None)

    def test_leaf_self_closing(self):
        node = LeafNode("img", "", {"src": "image.jpg"})
        self.assertIn('src="image.jpg"', node.to_html())

    def test_leaf_special_chars(self):
        node = LeafNode("p", "Text with <tags> & ampersands")
        self.assertEqual(node.to_html(), "<p>Text with <tags> & ampersands</p>")

    def test_leaf_multiple_props(self):
        node = LeafNode("input", "", {"type": "text", "id": "username", "placeholder": "Enter username"})
        html = node.to_html()
        self.assertIn('type="text"', html)
        self.assertIn('id="username"', html)
        self.assertIn('placeholder="Enter username"', html)

    def test_leaf_constructor_validation(self):
        with self.assertRaises(ValueError):
            LeafNode("div", None)


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
    )
        

    def test_parent_with_multiple_children(self):
        parent_node = ParentNode("ul", [
            LeafNode("li", "Item 1"),
            LeafNode("li", "Item 2"),
            LeafNode("li", "Item 3")
        ])
        self.assertEqual(parent_node.to_html(), "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>")

    def test_deeply_nested_structure(self):
        grandchild = LeafNode("b", "Important text")
        child1 = ParentNode("div", [grandchild])
        child2 = LeafNode("span", "Regular text")
        parent = ParentNode("section", [child1, child2])
        self.assertEqual(parent.to_html(), "<section><div><b>Important text</b></div><span>Regular text</span></section>")

    def test_with_props(self):
        child = LeafNode("a", "Click me", {"href": "https://boot.dev"})
        parent = ParentNode("div", [child], {"class": "container"})
        self.assertEqual(parent.to_html(), '<div class="container"><a href="https://boot.dev">Click me</a></div>')

    def test_empty_children_list(self):
        parent = ParentNode("div", [])
        self.assertEqual(parent.to_html(), "<div></div>")

    def test_missing_tag_raises_error(self):
        with self.assertRaises(ValueError):
            ParentNode(None, [LeafNode("span", "test")]).to_html()

    def test_none_children_raises_error(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()

    def test_mixed_leaf_and_parent_children(self):
        leaf1 = LeafNode("b", "Bold")
        parent_child = ParentNode("div", [LeafNode("i", "Italic")])
        leaf2 = LeafNode("u", "Underline")
        parent = ParentNode("section", [leaf1, parent_child, leaf2])
        self.assertEqual(parent.to_html(), "<section><b>Bold</b><div><i>Italic</i></div><u>Underline</u></section>")

    def test_with_text_nodes(self):
        parent = ParentNode("p", [
            LeafNode("b", "Bold"),
            LeafNode(None, " and "),
            LeafNode("i", "italic"),
            LeafNode(None, " text")
        ])
        self.assertEqual(parent.to_html(), "<p><b>Bold</b> and <i>italic</i> text</p>")

    def test_complex_props(self):
        parent = ParentNode("form", [
            LeafNode("input", "", {"type": "text", "placeholder": "Enter name"})
        ], {"method": "post", "action": "/submit"})
        self.assertEqual(parent.to_html(), 
                        '<form method="post" action="/submit"><input type="text" placeholder="Enter name"></input></form>')
        
    def test_deeply_nested_complex_structure(self):
        html = ParentNode("html", [
            ParentNode("head", [
                LeafNode("title", "My Page")
            ]),
            ParentNode("body", [
                ParentNode("header", [
                    LeafNode("h1", "Welcome")
                ]),
                ParentNode("main", [
                    LeafNode("p", "This is content"),
                    ParentNode("ul", [
                        LeafNode("li", "Item 1"),
                        LeafNode("li", "Item 2")
                    ])
                ]),
                LeafNode("footer", "© 2023")
            ])
        ])
        expected = "<html><head><title>My Page</title></head><body><header><h1>Welcome</h1></header><main><p>This is content</p><ul><li>Item 1</li><li>Item 2</li></ul></main><footer>© 2023</footer></body></html>"
        self.assertEqual(html.to_html(), expected)

    def test_malformed_children_handled_gracefully(self):
        try:
            ParentNode("div", [None, LeafNode("span", "valid")]).to_html()
            self.fail("Should have raised an error with None as a child")
        except:
            pass
    
    def test_empty_tag_but_not_none(self):
        with self.assertRaises(ValueError):
            ParentNode("", [LeafNode("p", "test")]).to_html()

    def test_special_characters_in_props(self):
        parent = ParentNode("div", [LeafNode("p", "Test")], {"data-test": "value&<>"})
        self.assertEqual(parent.to_html(), '<div data-test="value&<>"><p>Test</p></div>')

    def test_parent_node_without_children_list(self):
        with self.assertRaises(TypeError):
            ParentNode("div")

    def test_extremely_deep_nesting(self):
        # Create a deeply nested structure to test recursion limits
        leaf = LeafNode("span", "Deep")
        node = leaf
        for i in range(20):  # 20 levels deep
            node = ParentNode("div", [node])
        # If this doesn't raise RecursionError, the implementation handles deep nesting well
        html = node.to_html()
        self.assertIn("<span>Deep</span>", html)
        self.assertEqual(html.count("<div>"), 20)

    def test_parent_node_with_many_children(self):
        # Test with a large number of children
        children = [LeafNode("span", f"Child {i}") for i in range(100)]
        parent = ParentNode("div", children)
        html = parent.to_html()
        for i in range(100):
            self.assertIn(f"<span>Child {i}</span>", html)

    def test_parent_node_inherits_html_node(self):
        # Test that ParentNode is a subclass of HTMLNode
        self.assertTrue(issubclass(ParentNode, HTMLNode))