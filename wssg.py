"""
Generates Static Website

Markdown parsing operates under a few rules:
    1. All markup must begin and end on the same line
    2. Image references use the img folder as their root
    3. Hyperlinks to other parts of the website are done using the live link (no intelligent deduction here)
    4. Headers no deeper than level 3 (### or <h3>)
    5. No nested lists
    6. Links using []() will have no markup in the link text enclosed in []
    7. No exclamation marks at the end of an image or link (since the ! will get grouped with the ) by RegEx

Folder structure operates under a few rules:
    1. Website navbar are generated using folders in root of website
    2. Folders 'static' and 'public' are reserved for static content (images, pdfs, etc.) and the generated html website
    3. Markdown files must have the file extension .md
    4. The website uses a single css theme located in the root folder, called 'style.css'
"""

import os
import io
import re
import shutil

"""
Regular expression (Regex) to parse markdown
Supports nav, links, images, bold, italics
outer () to keep the "splitting content"
outer [] to split by everything between them
split by !, #, *, [, ], (, ), \u0060 (backtick, doesn't work using `)
+ to keep groups of these together (so **, ![, ###, etc.)
"""
md_pattern = re.compile(r'([-!#\*\[\]\(\)\u0060]+)')

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
    f_html.write('<!DOCTYPE html>\n<head>\n<meta charset="utf-8"/>\n')
    f_html.write(style_html)
    f_html.write('</head>\n<html>\n<body>\n')
    # insert header html
    f_html.write(nav_html)
    f_html.write('<main>')

    # stack to close html expressions for the whole file
    file_stack = []
    # stack to close html expressions for the current line
    line_stack = []

    # boolean variables to control state
    is_unordered_list = False
    is_ordered_list = False
    is_header = False
    is_paragraph = False
    is_link = False
    is_image = False
    is_code = False

    # variables to store hyperlinks/image links and alt text while parsing
    alt_string = ''
    link_string = ''
    
    # open returns iterable object, allowing for easy line-by-line
    for line in f_md:
        # remove newline characters
        line = line.rstrip()
        line_split = re.split(md_pattern,line)
        # special characters will be padded in the list on either side with '' (empty character); remove these using list comprehension
        line_split = [i for i in line_split if i != '']
        # Blank line
        if len(line_split) == 0:
            if is_ordered_list or is_unordered_list or is_paragraph:
                f_html.write(file_stack.pop())
                f_html.write('\n')
            is_ordered_list = False
            is_unordered_list = False
            is_paragraph = False
            is_header = False
            is_code = False
        # Content line
        else:
            for i, val in enumerate(line_split):
                # Header
                if i == 0 and val[0] == '#':
                    is_header = True
                    val_len = len(val)
                    if val_len == 1:
                        f_html.write('<h1>')
                        line_stack.append('</h1>')
                    elif val_len == 2:
                        f_html.write('<h2>')
                        line_stack.append('</h2>')
                    elif val_len == 3:
                        f_html.write('<h3>')
                        line_stack.append('</h3>')
                # Unordered List
                elif i == 0 and val == '-':
                    if is_ordered_list:
                        f_html.write('<li>')
                    else:
                        is_ordered_list = True
                        f_html.write('<ul>\n<li>')
                        file_stack.append('</ul>')
                    line_stack.append('</li>')
                # Ordered List
                elif i == 0 and val[0].isdigit() and val[1] == '.':
                    if is_unordered_list:
                        f_html.write('<li>')
                    else:
                        is_unordered_list = True
                        f_html.write('<ol>\n<li>')
                        file_stack.append('</ol>')
                    f_html.write(val[2:])
                    line_stack.append('</li>')
                # Code block
                elif i == 0 and val == '```':
                    if is_code:
                        is_code = False
                        f_html.write('</code></pre>')
                    else:
                        is_code = True
                        f_html.write('<pre><code>')
                elif is_code:
                    f_html.write(val)
                # Image opening
                elif val == '![' and line_split[i+2] == '](' and line_split[i+4] == ')':
                    is_image = True
                # Image middle through end
                elif is_image:
                    # center of image, ignore it
                    if val == '](':
                        pass
                    # end of image, create the string and write it to the file
                    elif val == ')':
                        is_image = False
                        f_html.write('<img src=\"' + link_string + '\" alt=\"' + alt_string + '\">')
                        alt_string = ''
                        link_string = ''
                    # alt text
                    elif line_split[i+1] == '](':
                        alt_string = val
                    # link text is the only other position
                    else:
                        link_string = val
                # Other text
                else:
                    # Paragraph
                    if not (is_header or is_ordered_list or is_unordered_list):
                        if not is_paragraph:
                            is_paragraph = True
                            f_html.write('<p>\n')
                            file_stack.append('</p>')
                    # Bold
                    if val == '**':
                        # if we're at the closing **
                        if (len(line_stack) != 0 and line_stack[-1] == '</b>'):
                            f_html.write(line_stack.pop())
                        # we're at the opening **
                        else:
                            f_html.write('<b>')
                            line_stack.append('</b>')
                    # Italics
                    elif val == '*':
                        # if we're at the closing *
                        if (len(line_stack) != 0 and line_stack[-1] == '</i>'):
                            f_html.write(line_stack.pop())
                        # we're at the opening *
                        else:
                            f_html.write('<i>')
                            line_stack.append('</i>')
                    # Bold and Italics
                    elif val == '***':
                        # if we're at the closing ***
                        if (len(line_stack) != 0 and line_stack[-1] == '</i></b>'):
                            f_html.write(line_stack.pop())
                        # we're at the opening ***
                        else:
                            f_html.write('<i><b>')
                            line_stack.append('</i></b>')
                    # Monospace
                    elif val == '`':
                        # if we're at the closing `
                        if (len(line_stack) != 0 and line_stack[-1] == '</code>'):
                            f_html.write(line_stack.pop())
                        # we're at the opening `
                        else:
                            f_html.write('<code>')
                            line_stack.append('</code>')
                    # Link opening
                    elif val == '[' and line_split[i+2] == '](' and line_split[i+4] == ')':
                        is_link = True
                    # Link middle through end
                    elif is_link:
                        # center of link, ignore it
                        if val == '](':
                            pass
                        # end of link, create the string and write it to the file
                        elif val == ')':
                            is_link = False
                            f_html.write('<a href=\"' + link_string + '\" target="_blank">' + alt_string + '</a>')
                            alt_string = ''
                            link_string = ''
                        # alt text
                        elif line_split[i+1] == '](':
                            alt_string = val
                        # link text is the only other position
                        else:
                            link_string = val
                    # Regular text or special characters caught by RegEx
                    # such as individual [ or ], !, etc.
                    else:
                        f_html.write(val)
                
            # Empty the line stack
            while len(line_stack) > 0:
                f_html.write(line_stack.pop())
            f_html.write('\n')
    
    # Empty the file stack
    while len(file_stack) > 0:
        f_html.write(file_stack.pop())
        f_html.write('\n')
    
    # close open HTML tags
    f_html.write('</main>\n</body>\n</html>\n')

    f_md.close()
    f_html.close()

"""
Remove existing public folder, create new one.
Begin file and directory traversal
"""
def prepare_dir():
    # generate(site_path)
    if os.path.exists('public'):
        for root, dirs, files in os.walk('public', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir('public')
    os.mkdir('public')
    style_html = ''
    if os.path.exists('style.css'):
        f_style = open('style.css','r')
        # strip all newlines, tabs and excess spaces
        style = re.sub(r'[\n\t]*', '', f_style.read())
        style = re.sub(r'\s{2,}', '', style)
        style_html = '<style>\n' + style + '\n</style>\n'
    traverse_dirs(os.getcwd(), style_html)

if __name__ == "__main__":
    prepare_dir()
