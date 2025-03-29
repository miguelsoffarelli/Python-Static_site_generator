import re
from enum import Enum

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


        
    
    
            
