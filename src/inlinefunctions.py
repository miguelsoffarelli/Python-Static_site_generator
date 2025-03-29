import re

from textnode import TextType, TextNode
from htmlnode import LeafNode


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
            raise Exception(f"Closing delimiter {delimiter} not found")
        
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


def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def split_nodes_image(old_nodes):
    result = []
    
    for node in old_nodes:
        
        if not node.text:
            continue
            
        images = extract_markdown_images(node.text)
        
        if not images:
            result.append(node)
            continue

        remaining_text = node.text
        
        for image in images:
            split_text = remaining_text.split(f"![{image[0]}]({image[1]})", 1)
            before = split_text[0]
            
            if before:
                result.append(TextNode(before, node.text_type))
            
            result.append(TextNode(image[0], TextType.IMAGE, image[1]))

            if len(split_text) > 1:
                remaining_text = split_text[1]
            else:
                remaining_text = ""

        if remaining_text:
            result.append(TextNode(remaining_text, node.text_type))

    return result


def split_nodes_link(old_nodes):
    result = []
    
    for node in old_nodes:
        
        if not node.text:
            continue
            
        links = extract_markdown_links(node.text)
        
        if not links:
            result.append(node)
            continue

        remaining_text = node.text
        
        for link in links:
            split_text = remaining_text.split(f"[{link[0]}]({link[1]})", 1)
            before = split_text[0]
            
            if before:
                result.append(TextNode(before, node.text_type))
            
            result.append(TextNode(link[0], TextType.LINK, link[1]))

            if len(split_text) > 1:
                remaining_text = split_text[1]
            else:
                remaining_text = ""

        if remaining_text:
            result.append(TextNode(remaining_text, node.text_type))

    return result


def text_to_textnodes(text):
    # Unreadable one-line nested solution to remind myself the importance of readability ☠️:
    # return split_nodes_delimiter(split_nodes_delimiter(split_nodes_delimiter(split_nodes_link(split_nodes_image([TextNode(text, TextType.NORMAL)])), "`", TextType.CODE), "_", TextType.ITALIC), "**", TextType.BOLD)
    
    images = split_nodes_image([TextNode(text, TextType.NORMAL)])
    links = split_nodes_link(images)
    code = split_nodes_delimiter(links, "`", TextType.CODE)
    italic = split_nodes_delimiter(code, "_", TextType.ITALIC)
    bold = split_nodes_delimiter(italic, "**", TextType.BOLD)
    return bold
    # Note: Nested nodes (for example "This is a text that has **bold text with _italic text_ nested inside**") 
    # will not be handled in this project (for the moment).