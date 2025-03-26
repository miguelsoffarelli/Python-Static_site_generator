class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self):
        result = ""
        if self.props != None:
            for key, value in self.props.items():
                result += f' {key}="{value}"'
            return result
        else:
            return result
        
    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, [], props)
        if self.value == None:
            raise ValueError("Value is missing")

    def to_html(self):
        if self.value == None:
            raise ValueError("Value is missing")
        if self.tag == None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
        if self.tag == None:
            raise ValueError("Tag missing")
        if self.children == None:
            raise ValueError("Parent node must have children")
        
    def to_html(self):
        props = ""
        if self.tag == None or self.tag == "":
            raise ValueError("Tag missing")
        if self.children == None:
            raise ValueError("Parent node must have children")
        if self.props != None:
            props = self.props_to_html()
        opening_tag = f"<{self.tag}{props}>"
        closing_tag = f"</{self.tag}>"
        result = ""
        for child in self.children:
            result += child.to_html()
        return opening_tag + result + closing_tag