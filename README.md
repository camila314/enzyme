# Enzyme

Enzyme is a jailbreak-free iOS code injection framework that allows you to statically inject code into iOS apps. Enzyme works using a byte-patching and code-generation system working together to allow you to hook functions.

## How do i use this?

### Enzyme is currently untested on windows.

Enzyme is a CMake utility. You include the `Enzyme.cmake` file into your own project. Check the example folder for how to set everything up. Hopefully documentation is coming soon, but I don't like writing docs so it might take a little bit.

## Are there dependencies?

Yes! It has the following dependencies:

- CMake 3.18+
- Python 3
- An iOS SDK
- Clang
- Rsync (for now)
- Ldid
