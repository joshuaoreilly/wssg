"""
Generates Static Website

Markdown parsing operates under a few rules:
    1. All markup must begin and end on the same line
    2. Image references use the img folder as their root
    3. Hyperlinks to other parts of the website are done using the live link (no intelligent deduction here)
    4. No nested lists
    5. Page/file title must be on the first line of the file

Folder structure operates under a few rules:
    1. Website navbar are generated using folders in root of website
    2. Folders 'static' and 'public' are reserved for static content (images, pdfs, etc.) and the generated html website
    3. Markdown files must have the file extension .md
    4. The website uses a single css theme located in the root folder, called 'style.css'
"""

import os
import re
import shutil

"""
Parse style.css file and minify
"""
def create_style():
    style_html = ''
    if os.path.exists('style.css'):
        f_style = open('style.css','r')
        # strip all newlines, tabs and excess spaces
        style = re.sub(r'[\n\t]*', '', f_style.read())
        style = re.sub(r'\s{2,}', '', style)
        style_html = '<style>\n' + style + '\n</style>\n'
    return style_html

"""
Traverse files and directories in website root folder.
Builds the list of navbar elements and begins recursively
visiting subfolders.

root: absolute path to website root
style_html: minified CSS string to be inserted in <head></head>
"""
def traverse_dirs(root, style_html):
    files = os.listdir()
    # empty first element is for main page of website
    nav = ['']
    # first pass to build list of nav elements
    for f in files:
        if os.path.isdir(f):
            if f != 'static' and f != 'public' and f [0] != '.':
                nav.append(f)
            if f == 'static':
                shutil.copytree('static','public/static')
    # recursive function to pass over all files
    # ignore public folder and static folder, and dot files (.git)
    nav_html = create_nav(nav, '')
    for f in files:
        if os.path.isdir(f) and f != 'public' and f != 'static' and f[0] != '.':
            os.mkdir('public/' + f)
            traverse_dirs_recursive(nav, f, '../', style_html)
        elif f[-3:] == '.md':
            f_html = f[0:-3] + '.html'
            md_to_html(f, 'public/' + f_html, nav_html, style_html)

"""
Recursively traverse files and folders in current folder

nav: names of nav elements
current_path: indicates path relative to root of website
backtrack: sequence of ../, ../../, etc. to get back to root
style_html: css content (until I find a better way of handling this)
"""
def traverse_dirs_recursive(nav, current_path, backtrack, style_html):
    files = os.listdir(current_path)
    nav_html = create_nav(nav, backtrack)
    for f in files:
        # (file or dir)
        if os.path.isdir(current_path + '/' + f):
            os.mkdir('public/' + current_path + '/' + f)
            traverse_dirs_recursive(nav,
                    current_path + '/' + f,
                    backtrack + '../',
                    style_html)
        elif f[-3:] == '.md':
            f_html = f[0:-3] + '.html'
            md_to_html(current_path + '/' + f,
                    'public/' + current_path + '/' + f_html,
                    nav_html,
                    style_html)

"""
Create string containing navbar HTML code

nav: list of navigation options
backtrack: sequence of ../, ../../, etc. to get back to root
"""
def create_nav(nav, backtrack):
    nav_html = '<header>\n<nav>\n'
    # handle first header manually (to main page of website)
    nav_html += '<a href=\"' + backtrack + 'index.html\">Home</a>\n'
    # skip first element, handle it manually
    for i in nav[1:]:
        nav_html += '<a href=\"' \
                + backtrack \
                + i \
                + '/index.html' \
                + '\">' \
                + i \
                + '</a>\n'
    nav_html += '</nav>\n</header>\n'
    return nav_html

"""
Convert the given markdown file into an HTML file

file_md_path: path to target markdown file
file_html_path: path to location of created HTML file
style_html: string containing minified CSS
"""
def md_to_html(file_md_path, file_html_path, nav_html, style_html):
    f_md = open(file_md_path, 'r')
    f_html = open(file_html_path, 'w')
    
    # insert necessary HTML preamble
    f_html.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="theme-color" content="#c2f4d1">\n<link rel="icon" href="https://joshuaoreilly.com/static/favicon.png">\n')
    # sloppy way of getting title
    title = f_md.readline().strip('#').strip()
    f_html.write('<title>' + title + '</title>\n')
    f_md.close()
    f_md = open(file_md_path, 'r')
    f_html.write(style_html)
    f_html.write('</head>\n<body>\n')
    # insert header html
    f_html.write(nav_html)
    f_html.write('<main>\n')
    
    # open returns iterable object, allowing for easy line-by-line
    line = f_md.readline()
    while line:
        if line != '\n':
            line = handle_block(line, f_md, f_html)
        else:
            line = f_md.readline()
    
    # close open HTML tags
    f_html.write('</main>\n</body>\n</html>\n')

    f_md.close()
    f_html.close()

"""
Handle single-depth (no nesting) block
"""
def handle_block(line, f_md, f_html):
    # what each line in the block must start with in order to continue the block
    markdown_prefix = ''
    # what each line will be prefixed/suffixed with in the output file
    html_prefix = ''
    html_suffix = ''
    # what will be placed at the end of the block
    block_suffix = ''

    # find out what kind of block we're in
    if line[0:2] == '> ':
        f_html.write('<blockquote>\n')
        markdown_prefix = '> '
        html_prefix = ''
        html_suffix = ''
        block_suffix = '</blockquote>\n'
    elif line[0:2] == '- ':
        f_html.write('<ul>\n')
        markdown_prefix = '- '
        html_prefix = '<li>'
        html_suffix = '</li>'
        block_suffix = '</ul>\n'
    elif re.match(r"^\d+\. ", line) != None:
        f_html.write('<ol>\n')
        markdown_prefix = 'ol'
        html_prefix = '<li>'
        html_suffix = '</li>'
        block_suffix = '</ol>\n'
    elif re.match(r"#+ ", line) != None:
        regex_match = re.match(r"#+ ", line)
        markdown_prefix = 'header'
        html_prefix = f'<h{len(regex_match[0])}>'
        html_suffix = f'</h{len(regex_match[0])}>'
        block_suffix = ''
    elif line[0:3] == '```':
        markdown_prefix = '```'
        f_html.write('<pre><code>')
        block_suffix = '</code></pre>\n'
    else:
        # basic text paragraph
        f_html.write('<p>\n')
        block_suffix = '</p>\n'
        pass

    code_block = False
    end_of_block_found = False
    while not end_of_block_found:
        # check if current block has ended
        if markdown_prefix == 'ol':
            if re.match(r"^\d+\. ", line) == None:
                end_of_block_found = True
            else:
                line = line.removeprefix(re.match(r"^\d+\. ", line)[0])
        elif markdown_prefix == 'header':
            if re.match(r"#+ ", line) == None:
                end_of_block_found = True
            else:
                line = line.removeprefix(re.match(r"#+ ", line)[0])
        elif markdown_prefix == '> ':
            if line[0:2] != '> ':
                end_of_block_found = True
            else:
                line = line[2:]
        elif markdown_prefix == '- ':
            if line[0:2] != '- ':
                end_of_block_found = True
            else:
                line = line[2:]
        elif markdown_prefix == '```':
            # special case: multiline code have line with just ```
            if line[0:3] == '```':
                line = '\n'
                if code_block:
                    end_of_block_found = True
                else:
                    code_block = True
        elif not line or line == '\n':
            end_of_block_found = True

        if end_of_block_found:
            # since md_to_html reads a new line after handling a block, go back one line
            f_html.write(block_suffix)
            return line
        else:
            if markdown_prefix == '```':
                f_html.write(line)
            else:
                f_html.write(html_prefix + handle_line(line).rstrip() + html_suffix + '\n')
            line = f_md.readline()

def handle_line(line):
    html = ''
    line_stack = ['']
    index = 0
    while index < len(line):
        char = line[index]
        if char == '`':
            if line_stack[-1] == '</code>':
                html += line_stack.pop()
            else:
                html += '<code>'
                line_stack.append('</code>')
        elif char == '*':
            if index+2 < len(line) and line[index+1] == '*' and line[index+2] == '*':
                index += 2
                if line_stack[-1] == '</i></b>':
                    html += line_stack.pop()
                else:
                    html += '<b><i>'
                    line_stack.append('</i></b>')
            elif index+1 < len(line) and line[index+1] == '*':
                index += 1
                if line_stack[-1] == '</b>':
                    html += line_stack.pop()
                else:
                    html += '<b>'
                    line_stack.append('</b>')
            else:
                if line_stack[-1] == '</i>':
                        html += line_stack.pop()
                else:
                    html += '<i>'
                    line_stack.append('</i>')
        elif char == '\\':
            if index+1 < len(line):
                index += 1
                next_char = line[index]
                html += next_char
        elif char == '!':
            if index+1 < len(line):
                if line[index+1] == '[':
                    alt_text, link, new_index = handle_link(index+2, line)
                    index = new_index
                    html += f'<img src="{link}" alt="{alt_text}">'
                else:
                    html += char
            else:
                html += '!'
        elif char == '[':
            if index+1 < len(line):
                alt_text, link, new_index = handle_link(index+1, line)
                index = new_index
                html += f'<a href="{link}">{alt_text}</a>'
            else:
                html += char
        else:
            html += char
        index += 1
    while len(line_stack) != 0:
        html += line_stack.pop()
    return html

"""
Handle both images and URLs, since both contain an alt text and a link
"""
def handle_link(index, line):
    end_found = False
    alt_text_done = False
    alt_text = ''
    link = ''
    while not end_found:
        char = line[index]
        if char == ']' and (index+1) < len(line):
            next_char = line[index+1]
            if next_char == '(':
                alt_text_done = True
                index += 1
            else:
                alt_text += ']'
        elif char == ')' and alt_text_done:
            end_found = True
        else:
            if not alt_text_done:
                alt_text += char
            else:
                link += char
        index += 1
        if index >= len(line):
            end_found = True
            # minus one since handle_line automatically increments index at the end of each loop iteration
    return alt_text, link, index-1

"""
Remove existing public folder, create new one.
Begin file and directory traversal
"""
def prepare_dir():
    # check if program called in website folder containing .wssg file
    if os.path.exists('.wssg'):
        # generate(site_path)
        if os.path.exists('public'):
            for root, dirs, files in os.walk('public', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir('public')
        os.mkdir('public')
        style_html = create_style()
        traverse_dirs(os.getcwd(), style_html)
    else:
        print('No .wssg file found, exiting')

if __name__ == "__main__":
    prepare_dir()
