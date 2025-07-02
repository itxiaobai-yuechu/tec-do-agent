from src.utils import html_to_text

if __name__ == "__main__":
    html_content = """
<div class="raw-message hideM"><pre class="fake-pre">你好！有什么我可以帮助你的吗？</pre></div><div class="md-message">\n\n你好！有什么我可以帮助你的吗？\n</div>
    """
    print(html_to_text(html_content))
