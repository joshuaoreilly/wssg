"""
Generates Static Website

Operates under a couple very simple (but restrictive rules):
    1. All markup must begin and end on the same line
    2. Image references use the img folder as their root
    3. Hyperlinks to other parts of the website are done using the live link (no intelligent deduction here)
    4. Headers no deeper than level 3 (### or <h3>)
    5. No nested lists

ToDo:
    - [ ] Add support for code snippets/monospace fonts (`` and ``` ```)
    - [ ] Add support for links and images
    - [ ] Add header and footer html
    - [ ] Everything associated with file paths, referencing images and other articles, etc.
"""

import os
import io
import re

"""
Regular expression (Regex) to parse markdown
Supports headers, links, images, bold, italics
outer () to keep the "splitting content"
outer [] to split by everything between them
split by !, #, *, [, ], (, )
+ to keep groups of these together (so **, ![, ###, etc.)
"""
md_pattern = re.compile(r'([-!#\*\[\]\(\)]+)')

def get_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            files.append(os.path.join(dirpath,f))
    return files

def parse_md(file_md_path, file_html_path):
    f_md = open(file_md_path, 'r')
    f_html = open(file_html_path, 'w')

    # stack to close html expressions for the whole file
    file_stack = []
    # stack to close html expressions for the current line
    line_stack = []

    # boolean variables to control state
    is_unordered_list = False
    is_ordered_list = False
    is_header = False
    is_paragraph = False
    
    # open returns iterable object, allowing for easy line-by-line
    for line in f_md:
        # remove newline characters
        line = line.rstrip()
        line_split = re.split(md_pattern,line)
        # special characters will be padded in the list on either side with '' (empty character); remove these using list comprehension
        line_split = [i for i in line_split if i != '']
        print(line_split) 
        # Blank line
        if len(line_split) == 0:
            if is_ordered_list or is_unordered_list or is_paragraph:
                f_html.write(file_stack.pop())
                f_html.write('\n')
            is_ordered_list = False
            is_unordered_list = False
            is_paragraph = False
            is_header = False
        # Content line
        else:
            for i, val in enumerate(line_split):
                # Header
                if val[0] == '#' and i == 0:
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
                elif val == '-' and i == 0:
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
    
    f_md.close()
    f_html.close()

def generate():
    root = os.getcwd()
    files = get_files(root) 

if __name__ == "__main__":
    # generate(site_path)
    parse_md('md.md','md.html')
