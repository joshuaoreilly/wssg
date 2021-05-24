# wssg, the Worst Static Site Generator

## What is wssg?

wssg is a simple, opinionated and incomplete static website generator.
It converts markdown files to HTML files using a strict file hierarchy.

## Should I use this?

Absolutely not; wssg is currently a fun little side project which, in its current form, isn't even close to feature complete and is chock-full of bugs (see `TODO.md` for an incomplete list).

## Installation

Place `wssg.py` wherever you'd like and create a bash alias to it.

## Usage

In order to use wssg, your markdown must have the following structure:

```
website/
	.wssg
	index.md
	style.css
	static/
	Folder1/
		index.md
		...
	Folder2/
		index.md
		...
	.../
```

wssg looks for the `.wssg` file to ensure it is run in the correct folder; the content of the file is not important.
Images, favicons, pdfs, and all other static content should be stored in the `static/` folder.
Folder names (other than `static/`) become the elements of the navbar; they link to their respective index files.

Images and links to other parts of your website should be done using relative links.
For example, a link to `test.png` in the index file of `Folder1/` would have the following form:

```
![caption](../static/test.png)
```

If you'd like an example site, visit `example/public/` or [joshuaoreilly.com](joshuaoreilly.com).
