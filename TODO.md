# ToDo

- [ ] Some kind of YAML support to allow for loading javascript on request (such as the A-Star page)
- [ ] Add --- support
- [ ] Add LaTeX support
- [ ] Add footer html
- [ ] Add proper html sections (`<section>`, `<div>`, etc.)

## Completed

- [x] Add support for user input HTML in markdown (kind of just works already, as far as I can tell without doing any proper testing)
- [x] Allow for special characters (-,#, etc. caught by RegEx) in hyperlinks; otherwise, you can't have dashes in hyperlinks!
- [x] Add blockquote support
- [x] Remove use of RegEx for parsing (this introduced the issue below) and replace with character by character parsing (and proper state machine?)
- [X] Add code snippets/monospace fonts
- [X] Add images
- [X] Add hyperlinks
- [X] Add bold, italics
- [X] Add headers
- [X] Add directory traversal/path generation
- [X] Add CSS and CSS minification
