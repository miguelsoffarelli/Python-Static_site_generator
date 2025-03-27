from textnode import TextType, TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": f"{text_node.url}"})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": f"{text_node.url}", "alt": f"{text_node.text}"})
        case _:
            raise ValueError("Wrong text type")
        

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = []
    for node in old_nodes:
        if node.text_type != TextType.NORMAL:
            result.append(node)
            continue
        
        opener_index = node.text.find(delimiter)
        
        if opener_index == -1:
            result.append(node)
            continue
        
        closer_index = node.text.find(delimiter, opener_index + len(delimiter))

        if closer_index == -1:
            raise Exception(f"Closer delimiter {delimiter} not found")
        
        before = node.text[:opener_index]
        content = node.text[opener_index + len(delimiter):closer_index]
        after = node.text[closer_index + len(delimiter):]

        if before:
            result.append(TextNode(before, TextType.NORMAL))

        result.append(TextNode(content, text_type))

        if after:
            # Used recursion to check if there are more delimiter pairs in the "after" text
            remaining_node = TextNode(after, TextType.NORMAL)
            remaining_processed = split_nodes_delimiter([remaining_node], delimiter, text_type)
            result.extend(remaining_processed)

    return result
            