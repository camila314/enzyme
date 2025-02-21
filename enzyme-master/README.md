# Enzyme

Enzyme is a jailbreak-free iOS code injection framework that allows you to statically inject code into iOS apps. Enzyme works using a byte-patching and code-generation system working together to allow you to hook functions.

## Features

- Function hooking through byte-patching
- Software breakpoint hooks (up to 6 simultaneous hooks)
- Code cave utilization
- Static code injection
- Memory management utilities

## How do i use this?

### Enzyme is currently untested on windows.

Enzyme is a CMake utility. You include the `Enzyme.cmake` file into your own project. Check the example folder for how to set everything up.

### Basic Usage Example
```python
import enzyme

p = enzyme.setup(
    code_caves = ( (0xc7bb0, 0xc7c0c) ),
    data_caves = (0x5ef041,0x5ef035),
    bss_cave = 0x7cdb90,
    dlopen_stub = 0x5ae02c,
    dlsym_stub = 0x5ae038
)

# Hook example
p.hook(0x10df78, "CCScheduler_update")

# Patch example
p.patch(0x544078, "ret")

enzyme.finish(p)
```
### Breakpoint Hooks Example
```cpp
// In your source file:
#include "breakpoint_hooks.h"

void $CCScheduler_update(void* schedulerObject, float deltaTime) {
    static void* original = nullptr;
    if (!original) {
        CCScheduler_update(schedulerObject, deltaTime / 2);
        return;
    }
    ((void(*)(void*, float))original)(schedulerObject, deltaTime / 2);
}
 ```
```

## Are there dependencies?

Yes! It has the following dependencies:

- CMake 3.18+
- Python 3
- An iOS SDK
- Clang
- Rsync (for now)
- Ldid
