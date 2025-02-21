#include "breakpoint_hooks.h"
#include <sys/mman.h>

std::map<void*, std::pair<void*, void**>> BreakpointHook::hooks;

bool BreakpointHook::addHook(void* targetAddr, void* replacementFunc, void** originalFunc) {
    if (hooks.size() >= MAX_HOOKS) return false;
    
    // Save original bytes
    uint32_t* target = static_cast<uint32_t*>(targetAddr);
    *originalFunc = targetAddr;
    
    // Make memory writable
    mprotect(targetAddr,
                    sizeof(uint32_t), PROT_READ | PROT_WRITE);
    
    // Insert breakpoint
    *target = BREAKPOINT_INSTRUCTION;
    
    // Store hook information
    hooks[targetAddr] = std::make_pair(replacementFunc, originalFunc);
    
    // Restore memory protection
    mprotect((void*)targetAddr,
                    sizeof(uint32_t), PROT_READ | PROT_EXEC);
    
    return true;
}

bool BreakpointHook::removeHook(void* targetAddr) {
    auto it = hooks.find(targetAddr);
    if (it == hooks.end()) return false;
    
    // Remove breakpoint & restore original bytes
    if (mprotect(targetAddr, sizeof(uint32_t), 
                 PROT_READ | PROT_WRITE) != 0) {
        return false;
    }
    
    *(uint32_t*)targetAddr = *(uint32_t*)(it->second.second);
    
    // Restore original protection
    mprotect(targetAddr, sizeof(uint32_t), 
             PROT_READ | PROT_EXEC);
             
    hooks.erase(it);
    return true;
}