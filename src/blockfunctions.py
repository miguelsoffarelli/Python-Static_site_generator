import re
from enum import Enum
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from inlinefunctions import text_to_textnodes, text_node_to_html_node

def markdown_to_blocks(markdown):
    # Strip the raw markdown from trailing whitespaces/empty lines
    clean_markdown = markdown.strip()
    # Used regex to make sure the text is split into blocks when there's an empty line in between,
    # independently if the empty line is a new line or one or many whitespaces.
    # Using .split() would fail in cases where the empty space between blocks wasn't exclusively new lines (\n).
    blocks = re.split(r'\n\s*\n', clean_markdown)
    result = []
    
    for block in blocks:
        # Strip each block from trailing whitespaces
        clean_block = block.strip()
        # Split each block into lines to handle multiple line blocks
        lines = clean_block.split('\n')
        # Strip each line from trailing whitespaces
        processed_block = '\n'.join(line.strip() for line in lines)
        # Check if the block is not empty to filter excess of new lines
        if processed_block:
            result.append(processed_block)
    
    return result


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    lines = [line.strip() for line in block.split('\n') if line.strip()]

    def is_heading(block):
        return re.match(r'^#{1,6} ', block.strip()) is not None
        
    def is_code(block):
        return re.match(r'^```[\s\S]*```$', block.strip()) is not None
    
    def is_quote(block):
        if not lines:
            return False
        # This helped me learn that .startswith() will return true to anything if the passed block is empty,
        # so first I check that there's actually a non-empty line to check
        for line in lines:
            if not line.startswith(">"):
                return False
        return True
    
    def is_unordered_list(block):
        if len(lines) < 2:
            return False
        for line in lines:
            if not line.startswith("- "):
                return False
        return True
    
    def is_ordered_list(block):
        if len(lines) < 2:
            return False
        for i, line in enumerate(lines, 1):
            if not line.startswith(f"{i}. "):
                return False
        return True

    check_type = {
        is_heading: BlockType.HEADING,
        is_code: BlockType.CODE,
        is_quote: BlockType.QUOTE,
        is_unordered_list: BlockType.UNORDERED_LIST,
        is_ordered_list: BlockType.ORDERED_LIST
    }

    for check_func, block_type in check_type.items():
        if check_func(block):
            return block_type

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent_node = ParentNode("div", [])
    
    for block in blocks:
        block_type = block_to_block_type(block)
        node = block_to_html_node(block, block_type)
        parent_node.children.append(node)

    return parent_node


def block_to_html_node(block, block_type):
    match block_type:
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return ul_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return ol_to_html_node(block)
    
def paragraph_to_html_node(block):
    text = block.replace("\n", " ")
    paragraph_node = ParentNode("p", [])
    children = text_to_children(text)
    paragraph_node.children = children
    
    return paragraph_node

def heading_to_html_node(block):
    header_level = 0
    for char in block:
        # We can safely assume there won't be more than 6 "#"s and the syntax will be correct,
        # otherwise block_type wouldn't be "heading" and this function won't be called.
        if char == "#":
            header_level += 1
        else:
            break
    
    content = block[header_level + 1:].strip()
    heading_node = ParentNode(f"h{header_level}", [])
    children = text_to_children(content)
    heading_node.children = children
    
    return heading_node

def code_to_html_node(block):
    content = block.strip()[3:-3]
    text_node = TextNode(content, TextType.CODE)
    code_node = text_node_to_html_node(text_node)
    parent_node = ParentNode("pre", [code_node])
    
    return parent_node

def quote_to_html_node(block):
    lines = block.split("\n")
    # Process each line to remove '>' and join them with spaces
    processed_text = ""
    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            # Remove the '>' and any space after it
            line = line[1:].lstrip()
        processed_text += line + " "
    # Create the blockquote node with children from the processed text
    children = text_to_children(processed_text.strip())
    
    return ParentNode("blockquote", children)


def ul_to_html_node(block):
    items = block.split("\n")
    li_nodes = []
    for item in items:
        if not item.strip():
            continue
        content = item.lstrip("- ").strip()
        children = text_to_children(content)
        li_node = ParentNode("li", children)
        li_nodes.append(li_node)
    ul_node = ParentNode("ul", li_nodes)
    return ul_node

def ol_to_html_node(block):
    items = block.split("\n")
    li_nodes = []
    for item in items:
        if not item.strip():
            continue
        content = item.split(".", 1)[1].strip()
        children = text_to_children(content)
        li_node = ParentNode("li", children)
        li_nodes.append(li_node)
    ol_node = ParentNode("ol", li_nodes)
    return ol_node

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for node in text_nodes:
        html_node = text_node_to_html_node(node)
        html_nodes.append(html_node)
    return html_nodes
    
def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    
    for block in blocks:
        if block_to_block_type(block) == BlockType.HEADING:
            # Split the heading block into lines to extract the title line only and not the whole block.
            lines = block.split("\n")
            for line in lines:
                if line.strip().startswith("# "):
                    # Split the line into text nodes for cases where the title includes
                    # inner nodes (for example: "# This is a title with **bold** text inside."),
                    # which will be useful to use it for the html title tag (In which case I assume the intention
                    # would be it's content to be "This is a title with bold text inside." instead of "This is a
                    # title with **bold** text inside.").
                    nodes = text_to_textnodes(line.strip()[2:])
                    title = ""
                    # And then join only the text value of each node into the final result.
                    for node in nodes:
                        title += node.text

                    return title
    
    raise Exception("No title found")

            
