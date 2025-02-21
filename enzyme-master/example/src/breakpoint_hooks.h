#pragma once
#include <map>

class BreakpointHook {
public:
    static const int MAX_HOOKS = 6;
    static bool addHook(void* targetAddr, void* replacementFunc, void** originalFunc);
    static bool removeHook(void* targetAddr);
private:
    static std::map<void*, std::pair<void*, void**>> hooks;
    static const uint32_t BREAKPOINT_INSTRUCTION = 0xD4200000;
};